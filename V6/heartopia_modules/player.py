import threading, time, os, ctypes
from .config import state, MAP_22, MAP_15, TRANS

pydirectinput = None
try:
    import pydirectinput
    pydirectinput.PAUSE = 0; pydirectinput.FAILSAFE = False
except ImportError: pass

def parse(path):
    if not os.path.exists(path): return []
    # Violin uses the comprehensive 22-Key physical layout configuration mapping
    keys = set(MAP_15.values()) if "_15K" in path else set(MAP_22.values())
    cmds = []
    
    lines = []
    for enc in ['utf-8', 'gbk', 'latin-1']:
        try:
            with open(path, 'r', encoding=enc) as f: lines = f.readlines()
            break
        except UnicodeDecodeError: continue
    if not lines:
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f: lines = f.readlines()
        except: return []

    i = 0; n = len(lines)
    while i < n:
        l = lines[i].strip()
        if "DELAY" in l:
            try: cmds.append(('D', int("".join(filter(str.isdigit, l)))))
            except: pass
            i += 1
        elif "Keyboard" in l:
            batch = []
            while i < n:
                if not lines[i].strip() or "DELAY" in lines[i] or "Keyboard" not in lines[i]: break
                p = lines[i].strip().split(':')
                if len(p) >= 3:
                    k = TRANS.get(p[1].strip(), p[1].strip().lower())
                    if k in keys: batch.append((k, p[2].strip()))
                i += 1
            if batch: cmds.append(('B', batch))
        else: i += 1
    return cmds

def worker(path, speed, snap, start_pct, loop):
    if not pydirectinput: return
    cmds = parse(path)
    if not cmds:
        with state.lock:
            state.playing = False
            state.status = "Error parsing file"
        return
    
    with state.lock:
        state.spd, state.snap, state.loop = speed, snap, loop
    idx = int(len(cmds) * (start_pct / 100.0))
    
    for x in range(3, 0, -1):
        if state.stop_req: return
        with state.lock: state.status = f"Starting in {x}..."
        time.sleep(1)
    
    with state.lock:
        state.status = f"Playing: {os.path.basename(path)[:-4]}"
    
    first = True
    fg_win = ctypes.windll.user32.GetForegroundWindow
    start_hwnd = fg_win()
    active = set()
    
    while (first or state.loop) and not state.stop_req:
        first = False
        n_cmds = len(cmds)
        for i in range(idx, n_cmds):
            if state.stop_req: break
            
            if fg_win() != start_hwnd: 
                with state.lock: state.paused = True
                
            while state.paused:
                with state.lock: state.status = "Paused"
                if active: 
                    for k in list(active): pydirectinput.keyUp(k)
                    active.clear()
                time.sleep(0.1)
                if state.stop_req: break
                if not state.paused: start_hwnd = fg_win()
            
            with state.lock: state.prog = i / n_cmds
            typ, val = cmds[i]
            
            if typ == 'D':
                if val >= state.snap:
                    d = (val / 1000.0) / state.spd
                    if d > 0: time.sleep(d)
            elif typ == 'B':
                downs = [k for k, act in val if act == "KeyDown"]
                ups = [k for k, act in val if act == "KeyUp"]
                
                for k in downs:
                    pydirectinput.keyDown(k)
                    active.add(k)
                for k in ups:
                    pydirectinput.keyUp(k)
                    active.discard(k)
        
        if not state.loop: break
        idx = 0
        
    for k in list(active): pydirectinput.keyUp(k)
    
    with state.lock:
        state.playing = False
        state.status = "Stopped"
        state.prog = 0
    
    next_song = None
    with state.lock:
        if not state.stop_req and state.queue:
            next_song = state.queue.pop(0)
            state.song = next_song
            state.playing = True

    if next_song:
        time.sleep(1)
        threading.Thread(target=worker, args=(os.path.join(state.conf["note_folder"], next_song), state.spd, state.snap, 0, False), daemon=True).start()

def toggle_play(data=None):
    with state.lock:
        if state.playing: 
            state.paused = not state.paused
            return
        if not state.song or state.song == "None": return
        
        state.playing, state.paused, state.stop_req = True, False, False
        s = float(data.get('speed', state.spd)) if data else state.spd
        sn = int(data.get('snap', state.snap)) if data else state.snap
        l = bool(data.get('loop', state.loop)) if data else state.loop
        sk = int(data.get('seek', 0)) if data else 0
        
    threading.Thread(target=worker, args=(os.path.join(state.conf["note_folder"], state.song), s, sn, sk, l), daemon=True).start()

def stop_play(): 
    with state.lock:
        state.stop_req = True
        state.playing = False
        state.paused = False
        state.prog = 0
        state.status = "Stopped"