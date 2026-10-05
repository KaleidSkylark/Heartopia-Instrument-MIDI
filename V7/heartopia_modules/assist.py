import threading
import time
import ctypes
from ctypes import wintypes
import os
import json
import random
import mmap
from .config import CONFIG_FILE

pyautogui = None
try:
    import pyautogui
    pyautogui.PAUSE = 0
    pyautogui.FAILSAFE = False
except ImportError:
    pass

user32 = ctypes.windll.user32
user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
user32.MapVirtualKeyW.argtypes = [ctypes.c_uint, ctypes.c_uint]
user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
user32.GetSystemMetrics.argtypes = [ctypes.c_int]

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_ulonglong)
    ]

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.c_ulonglong)
    ]

class INPUT(ctypes.Structure):
    class _U(ctypes.Union):
        _fields_ = [
            ("ki", KEYBDINPUT),
            ("mi", MOUSEINPUT)
        ]
    _fields_ = [
        ("type", wintypes.DWORD),
        ("u", _U)
    ]

def safe_int(val):
    try:
        return int(val)
    except:
        return 0

def is_pressed(vk_code):
    vk = safe_int(vk_code)
    if vk == 0:
        return False
    return bool(user32.GetAsyncKeyState(vk) & 32768)

def send_input_vk(vk_code, press=True):
    vk = safe_int(vk_code)
    if vk == 0:
        return None
        
    if vk == 1: # Left mouse button
        flags = 2 if press else 4
        inp = INPUT(type=0, u=INPUT._U(mi=MOUSEINPUT(dx=0, dy=0, mouseData=0, dwFlags=flags, time=0, dwExtraInfo=0)))
    elif vk == 2: # Right mouse button
        flags = 8 if press else 16
        inp = INPUT(type=0, u=INPUT._U(mi=MOUSEINPUT(dx=0, dy=0, mouseData=0, dwFlags=flags, time=0, dwExtraInfo=0)))
    elif vk == 4: # Middle mouse button
        flags = 32 if press else 64
        inp = INPUT(type=0, u=INPUT._U(mi=MOUSEINPUT(dx=0, dy=0, mouseData=0, dwFlags=flags, time=0, dwExtraInfo=0)))
    elif vk == 5: # X1 mouse button
        mouse_data = 1
        flags = 128 if press else 256
        inp = INPUT(type=0, u=INPUT._U(mi=MOUSEINPUT(dx=0, dy=0, mouseData=mouse_data, dwFlags=flags, time=0, dwExtraInfo=0)))
    elif vk == 6: # X2 mouse button
        mouse_data = 2
        flags = 128 if press else 256
        inp = INPUT(type=0, u=INPUT._U(mi=MOUSEINPUT(dx=0, dy=0, mouseData=mouse_data, dwFlags=flags, time=0, dwExtraInfo=0)))
    else: # Keyboard
        scan = user32.MapVirtualKeyW(vk, 0)
        flags = 8 if press else (8 | 2)
        inp = INPUT(type=1, u=INPUT._U(ki=KEYBDINPUT(wVk=vk, wScan=scan, dwFlags=flags, time=0, dwExtraInfo=0)))
        
    user32.SendInput(1, ctypes.pointer(inp), ctypes.sizeof(inp))

def hardware_click_at(x, y):
    screen_w = user32.GetSystemMetrics(0)
    screen_h = user32.GetSystemMetrics(1)
    
    abs_x = int(x * 65535 / screen_w)
    abs_y = int(y * 65535 / screen_h)
    
    inputs = (INPUT * 3)()
    inputs[0].type = 0
    inputs[0].u.mi.dx = abs_x
    inputs[0].u.mi.dy = abs_y
    inputs[0].u.mi.dwFlags = 32769 # MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE
    
    inputs[1].type = 0
    inputs[1].u.mi.dwFlags = 2 # MOUSEEVENTF_LEFTDOWN
    
    inputs[2].type = 0
    inputs[2].u.mi.dwFlags = 4 # MOUSEEVENTF_LEFTUP
    
    user32.SendInput(3, inputs, ctypes.sizeof(INPUT))

def hardware_mouse_down_at(x, y):
    screen_w = user32.GetSystemMetrics(0)
    screen_h = user32.GetSystemMetrics(1)
    
    abs_x = int(x * 65535 / screen_w)
    abs_y = int(y * 65535 / screen_h)
    
    inputs = (INPUT * 2)()
    inputs[0].type = 0
    inputs[0].u.mi.dx = abs_x
    inputs[0].u.mi.dy = abs_y
    inputs[0].u.mi.dwFlags = 32769 # MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE
    
    inputs[1].type = 0
    inputs[1].u.mi.dwFlags = 2 # MOUSEEVENTF_LEFTDOWN
    
    user32.SendInput(2, inputs, ctypes.sizeof(INPUT))

def hardware_mouse_up():
    inputs = (INPUT * 1)()
    inputs[0].type = 0
    inputs[0].u.mi.dwFlags = 4 # MOUSEEVENTF_LEFTUP
    
    user32.SendInput(1, inputs, ctypes.sizeof(INPUT))

class SharedMemoryManager:
    def __init__(self, name="Local\\MyFarmSharedMemory", size=256):
        self.size = size
        self.name = name
        self.shm = None
        self.setup()
        
    def setup(self):
        try:
            self.shm = mmap.mmap(-1, self.size, tagname=self.name, access=mmap.ACCESS_WRITE)
        except Exception as e:
            print(f"[Memory] Shared memory setup failed: {e}")
            
    def write_byte(self, offset, value):
        if self.shm:
            try:
                self.shm.seek(offset)
                self.shm.write_byte(int(value))
            except Exception as e:
                print(f"[Memory] Failed to write to shared memory: {e}")

def hardware_dual_click(x1, y1, x2, y2):
    # Click the Eye icon first
    hardware_click_at(x1, y1)
    # Sleep a tiny bit so the game registers the click on the Eye before we move to and click the Check icon
    time.sleep(0.02)
    # Click the Check icon
    hardware_click_at(x2, y2)


def get_windows():
    titles = []
    
    def foreach_window(hwnd, lParam):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                t = buff.value
                if t.strip():
                    titles.append(t)
        return True
        
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows(WNDENUMPROC(foreach_window), 0)
    return sorted(list(set(titles)))

class AssistState:
    def __init__(self):
        self.connected = False
        self.hwnd = None
        self.window_name = 'Heartopia'
        self.walk_active = False
        self.cam_active = False
        self.cook_active = False
        self.snow_active = False
        self.harvest_active = False
        self.jump_active = False
        
        self.walk_vk = 87
        self.mouse_btn = 2
        
        self.walk_hotkey = 112
        self.cam_hotkey = 113
        self.cook_hotkey = 117
        self.snow_hotkey = 118
        self.build_hotkey = 121 # F10
        self.harvest_hotkey = 114 # F3
        self.jump_hotkey = 119 # F8
        
        self.harvest_vk = 70 # F Key
        self.harvest_mode = 'spam'
        self.harvest_duration = 5.0
        self.harvest_spam_interval = 0.1
        
        self.confidence = 0.8
        self.use_grayscale = False
        
        self.img_stove = ''
        self.img_start = ''
        self.img_heat = ''
        self.img_serve = ''
        self.img_recipe = ''
        self.img_snow_add = ''
        self.img_snow_start = ''
        self.img_snow_puzzle = ''
        self.img_snow_get = ''
        self.img_build_eye = ''
        self.img_build_check = ''
        
        self.running = True
        self.state_walk_sent = False
        self.state_cam_sent = False
        self.last_pulse = 0
        self.logs = []
        self.mem = SharedMemoryManager()
        
        self.load_config()

    def log(self, msg):
        formatted = f"[Assist] {msg}"
        print(formatted)
        self.logs.append(formatted)

    def save_config(self):
        full_data = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    full_data = json.load(f)
            except:
                pass
                
        data = {
            'walk_hotkey': self.walk_hotkey,
            'cam_hotkey': self.cam_hotkey,
            'cook_hotkey': self.cook_hotkey,
            'snow_hotkey': self.snow_hotkey,
            'build_hotkey': self.build_hotkey,
            'harvest_hotkey': self.harvest_hotkey,
            'jump_hotkey': self.jump_hotkey,
            'confidence': self.confidence,
            'use_grayscale': self.use_grayscale,
            'mouse_btn': self.mouse_btn,
            'harvest_vk': self.harvest_vk,
            'harvest_mode': self.harvest_mode,
            'harvest_duration': self.harvest_duration,
            'harvest_spam_interval': self.harvest_spam_interval,
            'assist_images': {
                'stove': self.img_stove,
                'start': self.img_start,
                'heat': self.img_heat,
                'serve': self.img_serve,
                'recipe': self.img_recipe,
                'snow_add': self.img_snow_add,
                'snow_start': self.img_snow_start,
                'snow_puzzle': self.img_snow_puzzle,
                'snow_get': self.img_snow_get,
                'build_eye': self.img_build_eye,
                'build_check': self.img_build_check
            }
        }
        full_data.update(data)
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(full_data, f, indent=4)
        except Exception as e:
            print(f"Save failed: {e}")

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            self.save_config()
            return
            
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
            self.walk_hotkey = data.get('walk_hotkey', 112)
            self.cam_hotkey = data.get('cam_hotkey', 113)
            self.cook_hotkey = data.get('cook_hotkey', 117)
            self.snow_hotkey = data.get('snow_hotkey', 118)
            self.harvest_hotkey = data.get('harvest_hotkey', 114)
            self.jump_hotkey = data.get('jump_hotkey', 119)
            self.confidence = data.get('confidence', 0.8)
            self.use_grayscale = data.get('use_grayscale', False)
            self.mouse_btn = data.get('mouse_btn', 2)
            self.harvest_vk = data.get('harvest_vk', 70)
            self.harvest_mode = data.get('harvest_mode', 'spam')
            self.harvest_duration = data.get('harvest_duration', 5.0)
            self.harvest_spam_interval = data.get('harvest_spam_interval', 0.1)
            
            imgs = data.get('assist_images', {})
            self.img_stove = imgs.get('stove', '')
            self.img_start = imgs.get('start', '')
            self.img_heat = imgs.get('heat', '')
            self.img_serve = imgs.get('serve', '')
            self.img_recipe = imgs.get('recipe', '')
            self.img_snow_add = imgs.get('snow_add', '')
            self.img_snow_start = imgs.get('snow_start', '')
            self.img_snow_puzzle = imgs.get('snow_puzzle', '')
            self.img_snow_get = imgs.get('snow_get', '')
            self.img_build_eye = imgs.get('build_eye', '')
            self.img_build_check = imgs.get('build_check', '')
            self.build_hotkey = data.get('build_hotkey', 121)
        except Exception as e:
            print(f"Load failed: {e}")

assist_state = AssistState()


# -----------------------------------------------------------------------
# BUILD GLITCH & AUTO HARVEST MODULES
# -----------------------------------------------------------------------
def perform_build_glitch():
    p_eye = assist_state.img_build_eye
    p_chk = assist_state.img_build_check
    if not (p_eye and os.path.exists(p_eye) and p_chk and os.path.exists(p_chk)):
        assist_state.log("ERR: Build images missing")
        return
    try:
        conf = float(assist_state.confidence)
        gray = bool(assist_state.use_grayscale)
        # Locate Eye and Check on entire screen using configured settings
        loc_eye = pyautogui.locateCenterOnScreen(p_eye, confidence=conf, grayscale=gray)
        loc_chk = pyautogui.locateCenterOnScreen(p_chk, confidence=conf, grayscale=gray)
        if loc_eye and loc_chk:
            hardware_dual_click(loc_eye.x, loc_eye.y, loc_chk.x, loc_chk.y)
            assist_state.log("BUILD GLITCH FIRED")
        else:
            assist_state.log("ERR: Build imgs not found")
    except Exception as e:
        assist_state.log(f"ERR: {e}")

def harvest_loop():
    while assist_state.running:
        if assist_state.harvest_active and assist_state.connected and assist_state.hwnd and (user32.GetForegroundWindow() == assist_state.hwnd):
            if assist_state.harvest_mode == 'hold':
                assist_state.log(f"Harvesting: Holding key {assist_state.harvest_vk} for {assist_state.harvest_duration}s")
                send_input_vk(assist_state.harvest_vk, True)
                start_time = time.time()
                while time.time() - start_time < assist_state.harvest_duration:
                    if not assist_state.harvest_active or not assist_state.connected or not assist_state.running:
                        break
                    time.sleep(0.1)
                send_input_vk(assist_state.harvest_vk, False)
                assist_state.log("Harvesting: Key released")
                time.sleep(0.5)
            else:
                # Spam Mode
                send_input_vk(assist_state.harvest_vk, True)
                time.sleep(0.05)
                send_input_vk(assist_state.harvest_vk, False)
                # Wait for spam interval
                start_time = time.time()
                while time.time() - start_time < assist_state.harvest_spam_interval:
                    if not assist_state.harvest_active or not assist_state.connected or not assist_state.running:
                        break
                    time.sleep(0.05)
        else:
            time.sleep(0.2)

def jump_loop():
    while assist_state.running:
        if assist_state.jump_active and assist_state.connected and assist_state.hwnd and (user32.GetForegroundWindow() == assist_state.hwnd):
            send_input_vk(32, True)
            time.sleep(0.05)
            send_input_vk(32, False)
            start_time = time.time()
            while time.time() - start_time < 0.1:
                if not assist_state.jump_active or not assist_state.connected or not assist_state.running:
                    break
                time.sleep(0.02)
        else:
            time.sleep(0.2)


def connect_to_window(window_name):
    hwnd = user32.FindWindowW(None, window_name)
    if hwnd:
        assist_state.hwnd = hwnd
        assist_state.window_name = window_name
        assist_state.connected = True
        return True
    return False

def disconnect():
    assist_state.connected = False
    if assist_state.state_walk_sent:
        send_input_vk(assist_state.walk_vk, False)
        assist_state.state_walk_sent = False
    if assist_state.state_cam_sent:
        send_input_vk(assist_state.mouse_btn, False)
        assist_state.state_cam_sent = False
        
    send_input_vk(assist_state.harvest_vk, False)
    send_input_vk(32, False)
    assist_state.walk_active = False
    assist_state.cam_active = False
    assist_state.cook_active = False
    assist_state.snow_active = False
    assist_state.harvest_active = False
    assist_state.jump_active = False

def hotkey_loop():
    lt = {'walk': 0, 'cam': 0, 'cook': 0, 'snow': 0, 'build': 0, 'harvest': 0, 'jump': 0}
    while assist_state.running:
        time.sleep(0.01)
        curr = time.time()
        try:
            if assist_state.connected:
                if is_pressed(assist_state.walk_hotkey) and (curr - lt['walk'] > 0.4):
                    assist_state.walk_active = not assist_state.walk_active
                    lt['walk'] = curr
                if is_pressed(assist_state.cam_hotkey) and (curr - lt['cam'] > 0.4):
                    assist_state.cam_active = not assist_state.cam_active
                    lt['cam'] = curr
                if is_pressed(assist_state.cook_hotkey) and (curr - lt['cook'] > 0.4):
                    assist_state.cook_active = not assist_state.cook_active
                    lt['cook'] = curr
                if is_pressed(assist_state.snow_hotkey) and (curr - lt['snow'] > 0.4):
                    assist_state.snow_active = not assist_state.snow_active
                    lt['snow'] = curr
                if is_pressed(assist_state.harvest_hotkey) and (curr - lt['harvest'] > 0.4):
                    assist_state.harvest_active = not assist_state.harvest_active
                    lt['harvest'] = curr
                if is_pressed(assist_state.jump_hotkey) and (curr - lt['jump'] > 0.4):
                    assist_state.jump_active = not assist_state.jump_active
                    lt['jump'] = curr
                if is_pressed(assist_state.build_hotkey) and (curr - lt['build'] > 0.5):
                    threading.Thread(target=perform_build_glitch, daemon=True).start()
                    lt['build'] = curr
        except:
            pass


def input_loop():
    while assist_state.running:
        time.sleep(0.01)
        curr = time.time()
        if assist_state.connected and assist_state.hwnd and (user32.GetForegroundWindow() == assist_state.hwnd):
            if (curr - assist_state.last_pulse > 1.5):
                if assist_state.walk_active:
                    send_input_vk(assist_state.walk_vk, True)
                if assist_state.cam_active:
                    send_input_vk(assist_state.mouse_btn, True)
                assist_state.last_pulse = curr
                
            if assist_state.walk_active:
                if not assist_state.state_walk_sent:
                    send_input_vk(assist_state.walk_vk, True)
                    assist_state.state_walk_sent = True
            else:
                if assist_state.state_walk_sent:
                    send_input_vk(assist_state.walk_vk, False)
                    assist_state.state_walk_sent = False
                    
            if assist_state.cam_active:
                if not assist_state.state_cam_sent:
                    send_input_vk(assist_state.mouse_btn, True)
                    assist_state.state_cam_sent = True
            else:
                if assist_state.state_cam_sent:
                    send_input_vk(assist_state.mouse_btn, False)
                    assist_state.state_cam_sent = False
        else:
            if assist_state.state_walk_sent:
                send_input_vk(assist_state.walk_vk, False)
                assist_state.state_walk_sent = False
            if assist_state.state_cam_sent:
                send_input_vk(assist_state.mouse_btn, False)
                assist_state.state_cam_sent = False

def check_click(attr_name):
    if not pyautogui:
        return False
    path = getattr(assist_state, attr_name, '')
    if path and os.path.exists(path):
        try:
            conf = float(assist_state.confidence)
            gray = assist_state.use_grayscale
            pos = pyautogui.locateCenterOnScreen(path, confidence=conf, grayscale=gray)
            if pos:
                hardware_click_at(pos.x, pos.y)
                return True
        except:
            return False
    return False

def click_all_targets(attr_name):
    if not pyautogui:
        return False
    path = getattr(assist_state, attr_name, '')
    if path and os.path.exists(path):
        try:
            conf = float(assist_state.confidence)
            gray = assist_state.use_grayscale
            matches = list(pyautogui.locateAllOnScreen(path, confidence=conf, grayscale=gray))
            if matches:
                for box in matches:
                    cx = box.left + box.width // 2
                    cy = box.top + box.height // 2
                    hardware_click_at(cx, cy)
                    time.sleep(0.01)
                return True
        except:
            return False
    return False

def cook_loop():
    while assist_state.running:
        if assist_state.cook_active and assist_state.connected and assist_state.hwnd and (user32.GetForegroundWindow() == assist_state.hwnd):
            clicked = False
            if check_click('img_heat'):
                clicked = True
            elif check_click('img_serve'):
                clicked = True
            elif check_click('img_start'):
                clicked = True
            elif check_click('img_recipe'):
                clicked = True
            elif check_click('img_stove'):
                clicked = True
                
            if not clicked:
                time.sleep(0.05)
        else:
            time.sleep(0.5)

def snow_loop():
    while assist_state.running:
        if assist_state.snow_active and assist_state.connected and assist_state.hwnd and (user32.GetForegroundWindow() == assist_state.hwnd):
            found = False
            if check_click('img_snow_get'):
                time.sleep(0.2)
                found = True
            if click_all_targets('img_snow_puzzle'):
                found = True
                time.sleep(0.05)
            if check_click('img_snow_start'):
                time.sleep(0.2)
                found = True
            if check_click('img_snow_add'):
                time.sleep(0.2)
                found = True
                
            if not found:
                time.sleep(0.05)
        else:
            time.sleep(0.5)

def start_assist_service():
    threading.Thread(target=hotkey_loop, daemon=True).start()
    threading.Thread(target=input_loop, daemon=True).start()
    threading.Thread(target=cook_loop, daemon=True).start()
    threading.Thread(target=snow_loop, daemon=True).start()
    threading.Thread(target=harvest_loop, daemon=True).start()
    threading.Thread(target=jump_loop, daemon=True).start()

