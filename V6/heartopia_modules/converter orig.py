import os, statistics
from .config import state, MAP_22, MAP_15

mido = None
try: import mido
except ImportError: pass

def process_conversion(files, target, pitch):
    if not mido: return "Error: mido missing."
    logs = []
    
    for f in files:
        if not f or not f.filename: continue
        safe = "".join([c for c in f.filename if c.isalnum() or c in "._- "])
        tmp = os.path.join(state.conf["note_folder"], f"temp_{safe}")
        f.save(tmp)
        
        modes = [False, True] if target == "Both" else ([True] if target == "15K" else [False])
        
        for is15 in modes:
            try:
                mid = mido.MidiFile(tmp)
                evs = []
                for t in mid.tracks:
                    tm = 0
                    for m in t:
                        tm += m.time
                        if m.type in ['note_on', 'note_off', 'set_tempo']:
                            if hasattr(m, 'note'): m.note = max(0, min(127, m.note))
                            evs.append((tm, m))
                evs.sort(key=lambda x: x[0])
                raw = [m.note for _, m in evs if m.type == 'note_on']
                if not raw: logs.append(f"⚠️ Skipped {f.filename}"); continue
                
                med = statistics.median(raw)
                
                # --- AUTO-TRANSPOSITION LOGIC ---
                if is15:
                    # Target C5 (72) range, favor C-Major scale (all white keys)
                    tc = 72 + (pitch * 12); c_maj = {0,2,4,5,7,9,11}
                    shift = max(range(-6,6), key=lambda s: sum(1 for n in raw if ((n+s)%12) in c_maj))
                    trans = shift + int(round((tc - (med + shift)) / 12.0)) * 12
                    
                    # Pre-calculate valid 15K MIDI notes from the map keys
                    valid_15k_notes = sorted(list(MAP_15.keys()))
                else:
                    trans = int(round((66 + (pitch * 12) - med) / 12.0)) * 12
                
                out = []; last = 0; act = set(); tempo = 500000
                keymap = MAP_15 if is15 else MAP_22
                
                for tm, m in evs:
                    if tm > last:
                        ms = int(((tm - last) * tempo) / (mid.ticks_per_beat * 1000))
                        out.append(f"DELAY : {ms}")
                    last = tm
                    if m.type == 'set_tempo': tempo = m.tempo; continue
                    if m.type not in ['note_on', 'note_off']: continue
                    
                    target_note = m.note + trans
                    
                    # --- 15K SMART FOLDING ---
                    if is15:
                        k_val = None
                        # 1. Try exact match first
                        if target_note in keymap:
                            k_val = keymap[target_note]
                        else:
                            # 2. Smart Fold: Find closest valid note sharing the same pitch class (C->C, D->D)
                            candidates = [n for n in valid_15k_notes if n % 12 == target_note % 12]
                            
                            # 3. If no pitch class match (Black Key), try neighbors (+/- 1 semitone)
                            if not candidates:
                                candidates_lower = [n for n in valid_15k_notes if n % 12 == (target_note - 1) % 12]
                                candidates_upper = [n for n in valid_15k_notes if n % 12 == (target_note + 1) % 12]
                                candidates = candidates_lower + candidates_upper
                            
                            # 4. Pick the candidate physically closest to the target pitch to preserve melody contour
                            if candidates:
                                best_note = min(candidates, key=lambda x: abs(x - target_note))
                                k_val = keymap.get(best_note)
                    else:
                        # --- 22K STANDARD LOGIC (UNTOUCHED) ---
                        k_val = keymap.get(target_note)
                        if not k_val:
                            k_val = keymap.get(target_note + 12) or keymap.get(target_note - 12)
                    
                    if k_val:
                        k = k_val.upper()
                        
                        if is15:
                            # 15K: TAP MODE (Fixes sync/ghost notes)
                            # We ignore note-off and purely tap on note-on.
                            if m.type == 'note_on' and m.velocity > 0:
                                out.append(f"Keyboard : {k} : KeyDown")
                                out.append(f"Keyboard : {k} : KeyUp")
                        else:
                            # 22K: SUSTAIN MODE (Preserves dragging/holding)
                            if m.type == 'note_on' and m.velocity > 0:
                                if k in act: out.append(f"Keyboard : {k} : KeyUp\nDELAY : 15")
                                out.append(f"Keyboard : {k} : KeyDown"); act.add(k)
                            else:
                                out.append(f"Keyboard : {k} : KeyUp"); act.discard(k)
                
                name = f.filename.rsplit('.', 1)[0] + ("_15K.txt" if is15 else "_22K.txt")
                with open(os.path.join(state.conf["note_folder"], name), 'w') as o: o.write("\n".join(out))
                logs.append(f"✅ Created: {name}")
            except Exception as e: logs.append(f"❌ Error {f.filename}: {e}")
        if os.path.exists(tmp): os.remove(tmp)
    return "\n".join(logs)