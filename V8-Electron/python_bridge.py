import sys, os, json, time, threading, ctypes
from ctypes import wintypes

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stdin, 'reconfigure'):
        sys.stdin.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

# Ensure current directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from heartopia_modules.config import state, MAP_22, MAP_15, TRANS
from heartopia_modules.converter import process_conversion
import heartopia_modules.player as player_mod

try:
    import heartopia_modules.assist as assist_mod
    assist_mod.register_state_callback(lambda s: emit("assist_state_update", state=s))
    assist_mod.start_assist_service()
except Exception as e:
    assist_mod = None

try:
    import pydirectinput
    pydirectinput.PAUSE = 0
    pydirectinput.FAILSAFE = False
except ImportError:
    pydirectinput = None

def emit(event_type, **kwargs):
    try:
        payload = {"type": event_type, **kwargs}
        sys.stdout.write(json.dumps(payload) + "\n")
        sys.stdout.flush()
    except Exception:
        pass

# ─── Native Virtual Keycode Mapping for Global Hotkeys ───
KEY_TO_VK = {
    'F1': 0x70, 'F2': 0x71, 'F3': 0x72, 'F4': 0x73, 'F5': 0x74, 'F6': 0x75,
    'F7': 0x76, 'F8': 0x77, 'F9': 0x78, 'F10': 0x79, 'F11': 0x7A, 'F12': 0x7B,
    'SPACE': 0x20, 'RETURN': 0x0D, 'ENTER': 0x0D, 'TAB': 0x09, 'ESCAPE': 0x1B, 'ESC': 0x1B,
    'NUMPAD0': 0x60, 'NUMPAD1': 0x61, 'NUMPAD2': 0x62, 'NUMPAD3': 0x63,
    'NUMPAD4': 0x64, 'NUMPAD5': 0x65, 'NUMPAD6': 0x66, 'NUMPAD7': 0x67,
    'NUMPAD8': 0x68, 'NUMPAD9': 0x69,
    'NUM0': 0x60, 'NUM1': 0x61, 'NUM2': 0x62, 'NUM3': 0x63,
    'NUM4': 0x64, 'NUM5': 0x65, 'NUM6': 0x66, 'NUM7': 0x67,
    'NUM8': 0x68, 'NUM9': 0x69,
    'MULTIPLY': 0x6A, 'ADD': 0x6B, 'SEPARATOR': 0x6C, 'SUBTRACT': 0x6D, 'DECIMAL': 0x6E, 'DIVIDE': 0x6F,
    'CAPSLOCK': 0x14, 'CAPS': 0x14, 'PAGEUP': 0x21, 'PAGEDOWN': 0x22, 'END': 0x23, 'HOME': 0x24,
    'LEFT': 0x25, 'UP': 0x26, 'RIGHT': 0x27, 'DOWN': 0x28, 'INSERT': 0x2D, 'DELETE': 0x2E,
    '`': 0xC0, '~': 0xC0, '-': 0xBD, '=': 0xBB, '[': 0xDB, ']': 0xDD, '\\': 0xDC, ';': 0xBA, '\'': 0xDE,
    ',': 0xBC, '.': 0xBE, '/': 0xBF
}
for c in range(ord('A'), ord('Z') + 1):
    KEY_TO_VK[chr(c)] = c
for c in range(ord('0'), ord('9') + 1):
    KEY_TO_VK[chr(c)] = c

def parse_vks(key_name):
    if not key_name:
        return []
    clean = str(key_name).strip().upper()
    no_space = clean.replace(' ', '').replace('_', '')
    vks = set()

    # 1. Direct match in KEY_TO_VK
    if clean in KEY_TO_VK:
        vks.add(KEY_TO_VK[clean])
    if no_space in KEY_TO_VK:
        vks.add(KEY_TO_VK[no_space])

    # 2. Single digit '0'..'9': match main keyboard row AND numpad (NumLock ON & OFF)
    if len(no_space) == 1 and no_space in '0123456789':
        digit = no_space
        vks.add(ord(digit)) # Main row: 0x30 - 0x39
        vks.add(0x60 + int(digit)) # Numpad with NumLock ON
        numpad_off = {
            '0': 0x2D, '1': 0x23, '2': 0x28, '3': 0x22, '4': 0x25,
            '5': 0x0C, '6': 0x27, '7': 0x24, '8': 0x26, '9': 0x21,
        }
        if digit in numpad_off:
            vks.add(numpad_off[digit])

    # 3. Numpad prefix: 'NUMPAD7', 'NUM7', 'NUMPAD+', etc.
    if no_space.startswith('NUM'):
        suffix = no_space.replace('NUMPAD', '').replace('NUM', '')
        if suffix in '0123456789':
            digit = suffix
            vks.add(0x60 + int(digit)) # NumLock ON
            numpad_off = {
                '0': 0x2D, '1': 0x23, '2': 0x28, '3': 0x22, '4': 0x25,
                '5': 0x0C, '6': 0x27, '7': 0x24, '8': 0x26, '9': 0x21,
            }
            if digit in numpad_off:
                vks.add(numpad_off[digit])
        elif suffix in ('+', 'ADD', 'PLUS'):
            vks.add(0x6B) # VK_ADD
            vks.add(0xBB) # VK_OEM_PLUS
        elif suffix in ('-', 'SUB', 'SUBTRACT', 'MINUS'):
            vks.add(0x6D) # VK_SUBTRACT
            vks.add(0xBD) # VK_OEM_MINUS
        elif suffix in ('*', 'MUL', 'MULTIPLY'):
            vks.add(0x6A) # VK_MULTIPLY
        elif suffix in ('/', 'DIV', 'DIVIDE'):
            vks.add(0x6F) # VK_DIVIDE
            vks.add(0xBF) # VK_OEM_2
        elif suffix in ('.', 'DEC', 'DECIMAL', 'DEL', 'DELETE'):
            vks.add(0x6E) # VK_DECIMAL
            vks.add(0xBE) # VK_OEM_PERIOD
            vks.add(0x2E) # VK_DELETE
        elif suffix in ('ENTER', 'RETURN'):
            vks.add(0x0D) # VK_RETURN

    # 4. Standard symbols
    if clean == '+' or no_space == '+':
        vks.add(0x6B); vks.add(0xBB)
    elif clean == '-' or no_space == '-':
        vks.add(0x6D); vks.add(0xBD)
    elif clean == '*' or no_space == '*':
        vks.add(0x6A)
    elif clean == '/' or no_space == '/':
        vks.add(0x6F); vks.add(0xBF)
    elif clean == '.' or no_space == '.':
        vks.add(0x6E); vks.add(0xBE); vks.add(0x2E)

    return list(vks)

hotkey_play_vks = [KEY_TO_VK.get('F4', 0x73)]
hotkey_stop_vks = [KEY_TO_VK.get('F5', 0x74)]
hotkeys_paused = False
paused_timestamp = 0.0

try:
    _cfg_file = os.path.join(os.path.dirname(__file__), 'config.json')
    if os.path.exists(_cfg_file):
        with open(_cfg_file, 'r', encoding='utf-8') as _f:
            _c = json.load(_f)
            if _c.get('hotkey_play'):
                _parsed_p = parse_vks(_c['hotkey_play'])
                if _parsed_p:
                    hotkey_play_vks = _parsed_p
            if _c.get('hotkey_stop'):
                _parsed_s = parse_vks(_c['hotkey_stop'])
                if _parsed_s:
                    hotkey_stop_vks = _parsed_s
except Exception:
    pass

def get_window_list():
    if assist_mod and hasattr(assist_mod, "get_windows"):
        return assist_mod.get_windows()
    return ["Heartopia (xdt.exe)"]

def check_keys_pressed(vk_list):
    if not vk_list:
        return False
    for vk in vk_list:
        if vk and (ctypes.windll.user32.GetAsyncKeyState(vk) & 0x8000):
            return True
    return False

def hotkey_listener_thread():
    global hotkey_play_vks, hotkey_stop_vks, hotkeys_paused, paused_timestamp
    was_play_pressed = False
    was_stop_pressed = False
    last_play_time = 0.0
    last_stop_time = 0.0

    while True:
        time.sleep(0.012) # ~80Hz polling
        if hotkeys_paused:
            if paused_timestamp > 0 and (time.time() - paused_timestamp) > 5.0:
                hotkeys_paused = False
                paused_timestamp = 0.0
            else:
                time.sleep(0.04)
                continue
        now = time.time()
        try:
            # Edge-triggered Play/Pause detection
            is_play_pressed = check_keys_pressed(hotkey_play_vks)
            if is_play_pressed and not was_play_pressed:
                if (now - last_play_time) > 0.4:
                    last_play_time = now
                    print(f"[Python Bridge] Native Hotkey Triggered: PLAY/PAUSE (vks={hotkey_play_vks})", flush=True)
                    emit("hotkey_pressed", action="play")
            was_play_pressed = is_play_pressed

            # Edge-triggered Stop detection
            is_stop_pressed = check_keys_pressed(hotkey_stop_vks)
            if is_stop_pressed and not was_stop_pressed:
                if (now - last_stop_time) > 0.4:
                    last_stop_time = now
                    print(f"[Python Bridge] Native Hotkey Triggered: STOP (vks={hotkey_stop_vks})", flush=True)
                    with state.lock:
                        state.stop_req = True
                        state.playing = False
                        state.paused = False
                    emit("status", is_playing=False, is_paused=False, progress=0, status="Stopped", current_song="None")
                    emit("hotkey_pressed", action="stop")
            was_stop_pressed = is_stop_pressed
        except Exception:
            pass

current_player_thread = None

def run_play_thread(file_path, speed, snap, start_pct, loop):
    if not pydirectinput:
        emit("status", is_playing=False, is_paused=False, progress=0, status="pydirectinput missing", current_song="None")
        return

    try:
        cmds = player_mod.parse(file_path)
    except Exception as e:
        print(f"[Python Bridge] Parse exception on {file_path}: {e}", flush=True)
        cmds = []

    if not cmds:
        print(f"[Python Bridge] Song parse returned empty for path: {file_path} (exists={os.path.exists(file_path) if file_path else False})", flush=True)
        emit("status", is_playing=False, is_paused=False, progress=0, status=f"Error parsing: {os.path.basename(file_path) if file_path else 'None'}", current_song="None")
        return

    song_name = os.path.basename(file_path)
    with state.lock:
        state.stop_req = False
        state.paused = False
        state.playing = True
        state.song = song_name
        state.spd = float(speed)
        state.snap = int(snap)
        state.loop = bool(loop)
        state.prog = 0.0

    emit("status", is_playing=True, is_paused=False, progress=0, status="Starting in 3s...", current_song=song_name)
    for count in range(3, 0, -1):
        if state.stop_req:
            emit("status", is_playing=False, is_paused=False, progress=0, status="Stopped", current_song=song_name)
            return
        emit("status", is_playing=True, is_paused=False, progress=0, status=f"Starting in {count}s...", current_song=song_name)
        time.sleep(1)

    emit("status", is_playing=True, is_paused=False, progress=0, status=f"Playing: {song_name}", current_song=song_name)

    fg_win = ctypes.windll.user32.GetForegroundWindow
    start_hwnd = fg_win()
    active_keys = set()
    n_cmds = len(cmds)
    idx = int(n_cmds * (start_pct / 100.0))
    first_run = True

    try:
        while (first_run or state.loop) and not state.stop_req:
            first_run = False
            for i in range(idx, n_cmds):
                if state.stop_req:
                    break

                # Auto pause if focused window changed (allow Heartopia if connected via assist)
                curr_win = fg_win()
                is_target_game = False
                if assist_mod and hasattr(assist_mod, "assist_state") and assist_mod.assist_state:
                    if getattr(assist_mod.assist_state, "connected", False) and getattr(assist_mod.assist_state, "hwnd", None):
                        if curr_win == assist_mod.assist_state.hwnd:
                            is_target_game = True

                if curr_win != start_hwnd and not is_target_game:
                    with state.lock:
                        state.paused = True

                if state.paused:
                    emit("status", is_playing=True, is_paused=True, progress=(i / n_cmds), status="Paused", current_song=song_name)
                    if active_keys:
                        for k in list(active_keys):
                            try: pydirectinput.keyUp(k)
                            except Exception: pass
                        active_keys.clear()
                    while state.paused and not state.stop_req:
                        time.sleep(0.06)
                    if not state.stop_req:
                        start_hwnd = fg_win()
                        emit("status", is_playing=True, is_paused=False, progress=(i / n_cmds), status=f"Playing: {song_name}", current_song=song_name)

                typ, val = cmds[i]
                prog = i / n_cmds
                with state.lock:
                    state.prog = prog

                # Emit progress periodically
                if i % 5 == 0:
                    emit("status", is_playing=True, is_paused=False, progress=prog, status=f"Playing: {song_name}", current_song=song_name)

                if typ == 'D':
                    if val >= state.snap:
                        dur = (val / 1000.0) / state.spd
                        if dur > 0:
                            time.sleep(dur)
                elif typ == 'B':
                    downs = [k for k, act in val if act == "KeyDown"]
                    ups = [k for k, act in val if act == "KeyUp"]

                    for k in downs:
                        pydirectinput.keyDown(k)
                        active_keys.add(k)
                    for k in ups:
                        pydirectinput.keyUp(k)
                        active_keys.discard(k)

            idx = 0 # loop restarts from beginning

    finally:
        for k in list(active_keys):
            try:
                pydirectinput.keyUp(k)
            except Exception:
                pass
        active_keys.clear()
        with state.lock:
            state.playing = False
            state.paused = False
            state.prog = 0.0
            state.status = "Stopped"
        emit("status", is_playing=False, is_paused=False, progress=0, status="Finished / Stopped", current_song=song_name)

class FakeUploadedFile:
    def __init__(self, full_path):
        self.filename = os.path.basename(full_path)
        self.path = full_path
    def save(self, dest):
        import shutil
        shutil.copy2(self.path, dest)

def handle_convert(files, target, pitch, note_folder):
    try:
        if not note_folder:
            note_folder = state.conf.get("note_folder", "")
        if note_folder and not os.path.exists(note_folder):
            try:
                os.makedirs(note_folder, exist_ok=True)
            except Exception as e:
                emit("convert_result", ok=False, message=f"Failed to create notes folder: {str(e)}")
                return

        state.conf["note_folder"] = note_folder
        valid_files = [p for p in files if p and os.path.isfile(p)]
        if not valid_files:
            emit("convert_result", ok=False, message="No valid or accessible MIDI files found.")
            return

        logs = []
        try:
            import mido
        except ImportError:
            mido = None

        if not mido:
            emit("convert_result", ok=False, message="Python 'mido' package is not installed. Please use the built-in native MIDI converter.")
            return

        import statistics

        try:
            pitch_val = int(pitch) if pitch is not None else 0
        except Exception:
            pitch_val = 0

        if target == "Both":
            modes = [(False, False), (True, False)]
        elif target == "15K":
            modes = [(True, False)]
        elif target == "Violin":
            modes = [(False, True)]
        else:
            modes = [(False, False)]

        for file_path in valid_files:
            file_name = os.path.basename(file_path)
            for is15, is_violin in modes:
                try:
                    mid = mido.MidiFile(file_path)
                    evs = []
                    for t in mid.tracks:
                        tm = 0
                        for m in t:
                            tm += m.time
                            if m.type in ['note_on', 'note_off', 'set_tempo']:
                                if hasattr(m, 'note'):
                                    m.note = max(0, min(127, m.note))
                                evs.append((tm, m))
                    evs.sort(key=lambda x: x[0])
                    raw = [m.note for _, m in evs if m.type == 'note_on']
                    if not raw:
                        logs.append(f"⚠️ Skipped {file_name}: No notes found")
                        continue

                    med = statistics.median(raw)
                    if is15:
                        tc = 72 + (pitch_val * 12); c_maj = {0,2,4,5,7,9,11}
                        shift = max(range(-6,6), key=lambda s: sum(1 for n in raw if ((n+s)%12) in c_maj))
                        trans = shift + int(round((tc - (med + shift)) / 12.0)) * 12
                        valid_15k_notes = sorted(list(MAP_15.keys()))
                    else:
                        trans = int(round((66 + (pitch_val * 12) - med) / 12.0)) * 12

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
                        if m.type == 'set_tempo':
                            tempo = m.tempo
                            continue
                        if m.type not in ['note_on', 'note_off']:
                            continue

                        target_note = m.note + trans

                        if is15:
                            k_val = None
                            if target_note in keymap:
                                k_val = keymap[target_note]
                            else:
                                closest = min(valid_15k_notes, key=lambda x: abs(x - target_note))
                                k_val = keymap[closest]

                            if m.type == 'note_on' and m.velocity > 0:
                                if k_val not in pending_chord_keys:
                                    pending_chord_keys.append(k_val)
                        else:
                            if is_violin:
                                closest = min(keymap.keys(), key=lambda x: abs(x - target_note))
                                k = keymap[closest]
                                is_on = (m.type == 'note_on' and m.velocity > 0)
                                if is_on and k not in act:
                                    out.append(f"Keyboard : {k} : KeyDown")
                                    act.add(k)
                                elif not is_on and k in act:
                                    out.append(f"Keyboard : {k} : KeyUp")
                                    act.discard(k)
                            else:
                                if target_note in keymap:
                                    k = keymap[target_note]
                                    is_on = (m.type == 'note_on' and m.velocity > 0)
                                    if is_on and k not in act:
                                        out.append(f"Keyboard : {k} : KeyDown")
                                        act.add(k)
                                    elif not is_on and k in act:
                                        out.append(f"Keyboard : {k} : KeyUp")
                                        act.discard(k)

                    if is15 and pending_chord_keys:
                        for k in pending_chord_keys: out.append(f"Keyboard : {k} : KeyDown")
                        for k in pending_chord_keys: out.append(f"Keyboard : {k} : KeyUp")

                    for k in list(act):
                        out.append(f"Keyboard : {k} : KeyUp")

                    suffix = "_15K" if is15 else ("_Violin" if is_violin else "_22K")
                    base_name = os.path.splitext(file_name)[0]
                    clean_name = "".join([c for c in base_name if c.isalnum() or c in " ._-"]).strip()
                    if not clean_name:
                        clean_name = "Song"
                    save_name = f"{clean_name}{suffix}.txt"
                    save_path = os.path.join(note_folder, save_name)

                    with open(save_path, 'w', encoding='utf-8') as out_f:
                        out_f.write("\n".join(out))

                    logs.append(f"✅ Converted: {save_name}")

                except Exception as ex:
                    logs.append(f"❌ Failed {file_name}: {str(ex)}")

        emit("convert_result", ok=True, message="\n".join(logs) if logs else "No files converted.")
    except Exception as e:
        emit("convert_result", ok=False, message=f"Error: {str(e)}")

def main():
    global current_player_thread, hotkey_play_vks, hotkey_stop_vks, hotkeys_paused, paused_timestamp
    threading.Thread(target=hotkey_listener_thread, daemon=True).start()
    emit("ready")

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception:
            continue

        cmd = req.get("cmd")

        if cmd == "play":
            with state.lock:
                state.stop_req = True
                state.paused = False
            if current_player_thread and current_player_thread.is_alive():
                current_player_thread.join(timeout=1.0)

            file_path = req.get("path")
            speed = float(req.get("speed", 1.0))
            snap = int(req.get("snap", 0))
            start_pct = float(req.get("seek", 0))
            loop = bool(req.get("loop", False))

            current_player_thread = threading.Thread(
                target=run_play_thread,
                args=(file_path, speed, snap, start_pct, loop),
                daemon=True
            )
            current_player_thread.start()

        elif cmd == "pause_resume":
            with state.lock:
                state.paused = not state.paused
                paused = state.paused
            emit("status", is_playing=state.playing, is_paused=paused, progress=state.prog, status="Paused" if paused else "Playing", current_song=state.song)

        elif cmd == "stop":
            with state.lock:
                state.stop_req = True
                state.playing = False
                state.paused = False
                state.prog = 0.0
                state.status = "Stopped"
            emit("status", is_playing=False, is_paused=False, progress=0, status="Stopped", current_song="None")

        elif cmd == "update_params":
            if "speed" in req:
                state.spd = float(req["speed"])
            if "snap" in req:
                state.snap = int(req["snap"])
            if "loop" in req:
                state.loop = bool(req["loop"])

        elif cmd == "set_hotkeys":
            p = req.get("play")
            s = req.get("stop")
            if p:
                hotkey_play_vks = parse_vks(p)
            if s:
                hotkey_stop_vks = parse_vks(s)
            print(f"[Python Bridge] Synced hotkeys: play={p}->{hotkey_play_vks}, stop={s}->{hotkey_stop_vks}", flush=True)

        elif cmd == "pause_hotkeys":
            hotkeys_paused = bool(req.get("paused", False))
            paused_timestamp = time.time() if hotkeys_paused else 0.0
            print(f"[Python Bridge] Hotkeys paused state: {hotkeys_paused}", flush=True)

        elif cmd == "convert":
            files = req.get("files", [])
            target = req.get("target", "Both")
            pitch = int(req.get("pitch", 0))
            folder = req.get("folder", "")
            threading.Thread(target=handle_convert, args=(files, target, pitch, folder), daemon=True).start()

        # ─── Assist Automation Commands ───
        elif cmd == "assist_get_windows":
            wins = get_window_list()
            emit("assist_windows", windows=wins)

        elif cmd == "assist_connect":
            win_name = req.get("window", "Heartopia")
            ok = False
            if assist_mod:
                ok = assist_mod.connect_to_window(win_name)
            emit("assist_connect_result", ok=ok, window=win_name)

        elif cmd == "assist_disconnect":
            if assist_mod:
                assist_mod.disconnect()
            emit("assist_disconnect_result", ok=True)

        elif cmd == "assist_toggle":
            feat = req.get("feature")
            if assist_mod and assist_mod.assist_state:
                ast = assist_mod.assist_state
                if feat in ("harvest", "tree_rock"):
                    ast.harvest_active = not ast.harvest_active
                    ast.tree_rock_active = ast.harvest_active
                else:
                    attr = f"{feat}_active"
                    if hasattr(ast, attr):
                        curr = getattr(ast, attr)
                        setattr(ast, attr, not curr)
                emit("assist_state_update", state={
                    "connected": ast.connected,
                    "window_name": ast.window_name,
                    "walk_active": ast.walk_active,
                    "cam_active": ast.cam_active,
                    "harvest_active": ast.harvest_active,
                    "tree_rock_active": ast.harvest_active,
                    "cook_active": ast.cook_active,
                    "snow_active": ast.snow_active,
                    "jump_active": ast.jump_active,
                    "confidence": ast.confidence,
                    "use_grayscale": ast.use_grayscale,
                    "harvest_method": getattr(ast, 'harvest_method', 'spam'),
                    "harvest_mode": getattr(ast, 'harvest_mode', 'spam'),
                    "harvest_images": ast.harvest_images,
                    "harvest_images_count": len(ast.harvest_images)
                })

        elif cmd == "assist_build_glitch":
            emit("assist_build_result", ok=False, error="Build glitch removed")

        elif cmd == "assist_set_images":
            if assist_mod and assist_mod.assist_state:
                imgs = req.get("images", {})
                for k, v in imgs.items():
                    attr = f"img_{k}"
                    if hasattr(assist_mod.assist_state, attr):
                        setattr(assist_mod.assist_state, attr, v)
                assist_mod.assist_state.save_config()
                emit("assist_images_saved", ok=True)
            else:
                emit("assist_images_saved", ok=False)

        elif cmd == "assist_set_harvest_images":
            if assist_mod and assist_mod.assist_state:
                imgs = req.get("images", [])
                assist_mod.assist_state.set_harvest_images(imgs)
                emit("assist_harvest_images_saved", ok=True, count=len(assist_mod.assist_state.harvest_images))
            else:
                emit("assist_harvest_images_saved", ok=False)

        elif cmd == "assist_update_config":
            if assist_mod and assist_mod.assist_state:
                if "confidence" in req:
                    assist_mod.assist_state.confidence = float(req["confidence"])
                if "use_grayscale" in req:
                    assist_mod.assist_state.use_grayscale = bool(req["use_grayscale"])
                if "harvest_method" in req:
                    assist_mod.assist_state.harvest_method = req["harvest_method"]
                if "harvest_mode" in req:
                    assist_mod.assist_state.harvest_mode = req["harvest_mode"]
                if "harvest_vk" in req:
                    assist_mod.assist_state.harvest_vk = int(req["harvest_vk"])
                if "harvest_duration" in req:
                    assist_mod.assist_state.harvest_duration = float(req["harvest_duration"])
                if "harvest_spam_interval" in req:
                    assist_mod.assist_state.harvest_spam_interval = float(req["harvest_spam_interval"])
                if "mouse_btn" in req:
                    assist_mod.assist_state.mouse_btn = int(req["mouse_btn"])
                if "harvest_images" in req:
                    assist_mod.assist_state.set_harvest_images(req["harvest_images"])
                assist_mod.assist_state.save_config()
                emit("assist_config_saved", ok=True)

        elif cmd == "assist_update_hotkeys":
            if assist_mod and assist_mod.assist_state:
                hotkeys = req.get("hotkeys", {})
                assist_mod.assist_state.update_hotkeys(hotkeys)
                emit("assist_hotkeys_updated", ok=True)
            else:
                emit("assist_hotkeys_updated", ok=False)

        elif cmd == "assist_status":
            if assist_mod and assist_mod.assist_state:
                ast = assist_mod.assist_state
                emit("assist_status_result", state={
                    "connected": ast.connected,
                    "window_name": ast.window_name,
                    "walk_active": ast.walk_active,
                    "cam_active": ast.cam_active,
                    "harvest_active": ast.harvest_active,
                    "tree_rock_active": ast.harvest_active,
                    "cook_active": ast.cook_active,
                    "snow_active": ast.snow_active,
                    "jump_active": ast.jump_active,
                    "confidence": ast.confidence,
                    "use_grayscale": ast.use_grayscale,
                    "harvest_method": getattr(ast, 'harvest_method', 'spam'),
                    "harvest_mode": getattr(ast, 'harvest_mode', 'spam'),
                    "harvest_vk": ast.harvest_vk,
                    "harvest_duration": ast.harvest_duration,
                    "harvest_spam_interval": ast.harvest_spam_interval,
                    "mouse_btn": ast.mouse_btn,
                    "harvest_images": ast.harvest_images,
                    "harvest_images_count": len(ast.harvest_images),
                    "images": {
                        "stove": ast.img_stove,
                        "start": ast.img_start,
                        "heat": ast.img_heat,
                        "serve": ast.img_serve,
                        "recipe": ast.img_recipe,
                        "snow_add": ast.img_snow_add,
                        "snow_start": ast.img_snow_start,
                        "snow_puzzle": ast.img_snow_puzzle,
                        "snow_get": ast.img_snow_get
                    }
                })
            else:
                emit("assist_status_result", state={})

        elif cmd == "exit":
            with state.lock:
                state.stop_req = True
            break

if __name__ == "__main__":
    main()
