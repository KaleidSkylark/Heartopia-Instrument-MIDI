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
        
        # Determine tracking mode based on interface selection
        # Options: "Both", "22K", "15K", "Violin"
        if target == "Both":
            modes = [(False, False), (True, False)] # (is15k, is_violin)
        elif target == "15K":
            modes = [(True, False)]
        elif target == "Violin":
            modes = [(False, True)] # Violin utilizes 22K map base for range but forces full sustain tracking
        else:
            modes = [(False, False)]
        
        for is15, is_violin in modes:
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
                    tc = 72 + (pitch * 12); c_maj = {0,2,4,5,7,9,11}
                    shift = max(range(-6,6), key=lambda s: sum(1 for n in raw if ((n+s)%12) in c_maj))
                    trans = shift + int(round((tc - (med + shift)) / 12.0)) * 12
                    valid_15k_notes = sorted(list(MAP_15.keys()))
                else:
                    trans = int(round((66 + (pitch * 12) - med) / 12.0)) * 12
                
                out = []; last = 0; act = set(); tempo = 500000
                keymap = MAP_15 if is15 else MAP_22
                
                pending_chord_keys = []
                
                for tm, m in evs:
                    if tm > last:
                        if is15 and pending_chord_keys:
                            for k in pending_chord_keys: out.append(f"Keyboard : {k} : KeyDown")
                            for k in pending_chord_keys: out.append(f"Keyboard : {k} : KeyUp")
                            pending_chord_keys = []
                            
                        ms = int(((tm - last) * tempo) / (mid.ticks_per_beat * 1000))
                        out.append(f"DELAY : {ms}")
                    
                    last = tm
                    if m.type == 'set_tempo': tempo = m.tempo; continue
                    if m.type not in ['note_on', 'note_off']: continue
                    
                    target_note = m.note + trans
                    
                    if is15:
                        k_val = None
                        if target_note in keymap:
                            k_val = keymap[target_note]
                        else:
                            candidates = [n for n in valid_15k_notes if n % 12 == target_note % 12]
                            if not candidates:
                                candidates_lower = [n for n in valid_15k_notes if n % 12 == (target_note - 1) % 12]
                                candidates_upper = [n for n in valid_15k_notes if n % 12 == (target_note + 1) % 12]
                                candidates = candidates_lower + candidates_upper
                            
                            if candidates:
                                best_note = min(candidates, key=lambda x: abs(x - target_note))
                                k_val = keymap.get(best_note)
                    else:
                        k_val = keymap.get(target_note)
                        if not k_val:
                            k_val = keymap.get(target_note + 12) or keymap.get(target_note - 12)
                    
                    if k_val:
                        k = k_val.upper()
                        if is15:
                            if m.type == 'note_on' and m.velocity > 0:
                                if k not in pending_chord_keys:
                                    pending_chord_keys.append(k)
                        else:
                            # --- VIOLIN & 22K SUSTAIN MODE ---
                            # Note-on event turns note on, note-off event releases it
                            if m.type == 'note_on' and m.velocity > 0:
                                if k in act: 
                                    out.append(f"Keyboard : {k} : KeyUp\nDELAY : 15")
                                out.append(f"Keyboard : {k} : KeyDown")
                                act.add(k)
                            else:
                                out.append(f"Keyboard : {k} : KeyUp")
                                act.discard(k)
                
                if is15 and pending_chord_keys:
                    for k in pending_chord_keys: out.append(f"Keyboard : {k} : KeyDown")
                    for k in pending_chord_keys: out.append(f"Keyboard : {k} : KeyUp")
                
                # Dynamic naming convention tag placement
                if is_violin:
                    suffix = "_Violin.txt"
                elif is15:
                    suffix = "_15K.txt"
                else:
                    suffix = "_22K.txt"
                    
                name = f.filename.rsplit('.', 1)[0] + suffix
                with open(os.path.join(state.conf["note_folder"], name), 'w', encoding='utf-8') as o: 
                    o.write("\n".join(out))
                logs.append(f"✅ Created: {name}")
            except Exception as e: logs.append(f"❌ Error {f.filename}: {e}")
        if os.path.exists(tmp): os.remove(tmp)
    return "\n".join(logs)