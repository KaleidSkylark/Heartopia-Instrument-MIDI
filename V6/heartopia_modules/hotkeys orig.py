import ctypes, time
from .config import state
from .player import toggle_play, stop_play

def listener():
    get_key = ctypes.windll.user32.GetAsyncKeyState
    wp = ws = False
    DEFAULT_PLAY = 0x73 # F4
    DEFAULT_STOP = 0x74 # F5
    
    while True:
        try:
            vk_p = state.vk_play if state.vk_play else DEFAULT_PLAY
            vk_s = state.vk_stop if state.vk_stop else DEFAULT_STOP
            p = (get_key(vk_p) & 0x8000) != 0
            if p and not wp: toggle_play()
            wp = p
            s = (get_key(vk_s) & 0x8000) != 0
            if s and not ws: stop_play()
            ws = s
        except Exception as e: pass
        time.sleep(0.05)