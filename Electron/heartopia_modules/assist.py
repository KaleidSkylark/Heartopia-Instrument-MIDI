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

pydirectinput = None
try:
    import pydirectinput
    pydirectinput.PAUSE = 0
    pydirectinput.FAILSAFE = False
except ImportError:
    pass

try:
    from PIL import Image
except ImportError:
    Image = None

_image_cache = {}

def get_cached_image(path, grayscale=False):
    if not path or not os.path.exists(path):
        return None
    key = (os.path.abspath(path), bool(grayscale))
    if key in _image_cache:
        return _image_cache[key]
    if Image is None:
        return path
    try:
        im = Image.open(path)
        if grayscale:
            im = im.convert('L')
        else:
            im = im.convert('RGB')
        _image_cache[key] = im
        return im
    except Exception as e:
        print(f"[ImageCache] Failed to load {path}: {e}")
        return path

def preload_images(paths, grayscale=False):
    for p in paths:
        if p and os.path.exists(p):
            get_cached_image(p, grayscale)


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

VK_MAP = {
    'F1': 112, 'F2': 113, 'F3': 114, 'F4': 115, 'F5': 116, 'F6': 117,
    'F7': 118, 'F8': 119, 'F9': 120, 'F10': 121, 'F11': 122, 'F12': 123,
    'M4': 5, 'MOUSE4': 5, 'XBUTTON1': 5,
    'M5': 6, 'MOUSE5': 6, 'XBUTTON2': 6,
    'SPACE': 32, 'TAB': 9, 'ENTER': 13, 'ESC': 27, 'ESCAPE': 27
}
for c in range(ord('A'), ord('Z') + 1):
    VK_MAP[chr(c)] = c
for c in range(ord('0'), ord('9') + 1):
    VK_MAP[chr(c)] = c

def safe_int(val):
    try:
        return int(val)
    except:
        return 0

def parse_vk(val):
    if isinstance(val, int):
        return val
    if not val:
        return 0
    s = str(val).strip().upper()
    if s.isdigit():
        return int(s)
    if s in VK_MAP:
        return VK_MAP[s]
    return safe_int(val)

def is_pressed(vk_code):
    vk = parse_vk(vk_code)
    if vk == 0:
        return False
    return bool(user32.GetAsyncKeyState(vk) & 32768)

def send_input_vk(vk_code, press=True):
    vk = safe_int(vk_code)
    if vk == 0:
        return None

    # CRITICAL SECURITY GUARD: Never send any simulated keystrokes or clicks if Heartopia is not the active focused window!
    if not is_target_active():
        return None
        
    if vk == 1: # Left mouse button
        flags = 2 if press else 4
        inp = INPUT(type=0, u=INPUT._U(mi=MOUSEINPUT(dx=0, dy=0, mouseData=0, dwFlags=flags, time=0, dwExtraInfo=0)))
        user32.SendInput(1, ctypes.pointer(inp), ctypes.sizeof(inp))
        if pydirectinput:
            try:
                if press: pydirectinput.mouseDown(button='left')
                else: pydirectinput.mouseUp(button='left')
            except Exception: pass
    elif vk == 2: # Right mouse button
        flags = 8 if press else 16 # MOUSEEVENTF_RIGHTDOWN = 8, MOUSEEVENTF_RIGHTUP = 16
        inp = INPUT(type=0, u=INPUT._U(mi=MOUSEINPUT(dx=0, dy=0, mouseData=0, dwFlags=flags, time=0, dwExtraInfo=0)))
        user32.SendInput(1, ctypes.pointer(inp), ctypes.sizeof(inp))
        try:
            user32.mouse_event(flags, 0, 0, 0, 0)
        except Exception:
            pass
        if pydirectinput:
            try:
                if press: pydirectinput.mouseDown(button='right')
                else: pydirectinput.mouseUp(button='right')
            except Exception: pass
    elif vk == 4: # Middle mouse button
        flags = 32 if press else 64
        inp = INPUT(type=0, u=INPUT._U(mi=MOUSEINPUT(dx=0, dy=0, mouseData=0, dwFlags=flags, time=0, dwExtraInfo=0)))
        user32.SendInput(1, ctypes.pointer(inp), ctypes.sizeof(inp))
    elif vk == 5: # X1 mouse button
        mouse_data = 1
        flags = 128 if press else 256
        inp = INPUT(type=0, u=INPUT._U(mi=MOUSEINPUT(dx=0, dy=0, mouseData=mouse_data, dwFlags=flags, time=0, dwExtraInfo=0)))
        user32.SendInput(1, ctypes.pointer(inp), ctypes.sizeof(inp))
    elif vk == 6: # X2 mouse button
        mouse_data = 2
        flags = 128 if press else 256
        inp = INPUT(type=0, u=INPUT._U(mi=MOUSEINPUT(dx=0, dy=0, mouseData=mouse_data, dwFlags=flags, time=0, dwExtraInfo=0)))
        user32.SendInput(1, ctypes.pointer(inp), ctypes.sizeof(inp))
    else: # Keyboard
        scan = user32.MapVirtualKeyW(vk, 0)
        flags = 8 if press else (8 | 2) # KEYEVENTF_SCANCODE = 8, KEYEVENTF_KEYUP = 2
        inp = INPUT(type=1, u=INPUT._U(ki=KEYBDINPUT(wVk=vk, wScan=scan, dwFlags=flags, time=0, dwExtraInfo=0)))
        user32.SendInput(1, ctypes.pointer(inp), ctypes.sizeof(inp))
        if pydirectinput and (65 <= vk <= 90 or 48 <= vk <= 57):
            try:
                ch = chr(vk).lower()
                if press: pydirectinput.keyDown(ch)
                else: pydirectinput.keyUp(ch)
            except Exception: pass

def hardware_click_at(x, y):
    if not is_target_active():
        return
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
    if not is_target_active():
        return
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
    if not is_target_active():
        return
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


def get_proc_name_by_hwnd(hwnd):
    try:
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if not pid.value:
            return ""
        h_proc = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid.value)
        if not h_proc:
            return ""
        try:
            buf = ctypes.create_unicode_buffer(1024)
            size = wintypes.DWORD(1024)
            if ctypes.windll.kernel32.QueryFullProcessImageNameW(h_proc, 0, buf, ctypes.byref(size)):
                return os.path.basename(buf.value).lower()
        finally:
            ctypes.windll.kernel32.CloseHandle(h_proc)
    except Exception:
        pass
    return ""

def is_heartopia_window(hwnd):
    if not user32.IsWindow(hwnd) or not user32.IsWindowVisible(hwnd):
        return False
    proc = get_proc_name_by_hwnd(hwnd)
    if proc == "xdt.exe":
        rect = wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        if (rect.right - rect.left > 100) and (rect.bottom - rect.top > 100):
            return True
    return False

def get_windows():
    titles = []
    def foreach_window(hwnd, lParam):
        if is_heartopia_window(hwnd):
            titles.append("Heartopia (xdt.exe)")
        return True
        
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows(WNDENUMPROC(foreach_window), 0)
    if not titles:
        return ["Heartopia (Game Not Running)"]
    return sorted(list(set(titles)))

PARENT_REF_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TREE_ROCK_BUSH_DIR = os.path.join(PARENT_REF_DIR, 'Tree&Rock&BushReference')

def get_default_harvest_images():
    targets = []
    if os.path.exists(TREE_ROCK_BUSH_DIR):
        try:
            files = [os.path.join(TREE_ROCK_BUSH_DIR, f) for f in sorted(os.listdir(TREE_ROCK_BUSH_DIR))
                     if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.webp'))]
            if files:
                targets = files
        except Exception:
            pass
    if not targets:
        # Fallback to older reference dir if needed
        old_dir = os.path.join(PARENT_REF_DIR, 'Tree&RockReference')
        if os.path.exists(old_dir):
            try:
                targets = [os.path.join(old_dir, f) for f in sorted(os.listdir(old_dir))
                           if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            except Exception:
                pass
    return targets

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
        self.tree_rock_active = False
        self.jump_active = False
        
        self.walk_vk = 87
        self.mouse_btn = 2
        
        self.walk_hotkey = 112     # F1
        self.cam_hotkey = 113      # F2
        self.harvest_hotkey = 114  # F3
        self.cook_hotkey = 117     # F6
        self.snow_hotkey = 118     # F7
        self.jump_hotkey = 119     # F8
        self.tree_rock_hotkey = 120 # F9 (Legacy alias)
        
        self.harvest_vk = 70 # F Key
        self.harvest_method = 'spam' # 'spam' or 'vision'
        self.harvest_mode = 'spam'
        self.harvest_duration = 5.0
        self.harvest_spam_interval = 0.1
        
        self.confidence = 0.8
        self.use_grayscale = False
        
        # Cooking Reference Images
        self.img_stove = os.path.join(PARENT_REF_DIR, 'CookingReference', 'stove.png')
        self.img_start = os.path.join(PARENT_REF_DIR, 'CookingReference', 'start_cooking.png')
        self.img_heat = os.path.join(PARENT_REF_DIR, 'CookingReference', 'heat.png')
        self.img_serve = os.path.join(PARENT_REF_DIR, 'CookingReference', 'served.png')
        self.img_recipe = os.path.join(PARENT_REF_DIR, 'CookingReference', 'recipe.png')
        
        # Snow Puzzle Reference Images
        self.img_snow_add = os.path.join(PARENT_REF_DIR, 'SnowReference', 'add_snow.png')
        self.img_snow_start = os.path.join(PARENT_REF_DIR, 'SnowReference', 'start_snow.png')
        self.img_snow_puzzle = os.path.join(PARENT_REF_DIR, 'SnowReference', 'snow_puzzle.png')
        self.img_snow_get = os.path.join(PARENT_REF_DIR, 'SnowReference', 'get_snow.png')

        # Unified Bulk Harvest Images (Crops, Trees, Rocks, Bushes)
        self.harvest_images = get_default_harvest_images()
        preload_images(self.harvest_images, self.use_grayscale)
        
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

    def set_harvest_images(self, img_list):
        if isinstance(img_list, list):
            self.harvest_images = [p for p in img_list if os.path.exists(p)]
            preload_images(self.harvest_images, self.use_grayscale)
            self.save_config()
            self.log(f"Updated harvest images: {len(self.harvest_images)} targets cached in memory.")

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
            'harvest_hotkey': self.harvest_hotkey,
            'tree_rock_hotkey': self.tree_rock_hotkey,
            'jump_hotkey': self.jump_hotkey,
            'confidence': self.confidence,
            'use_grayscale': self.use_grayscale,
            'mouse_btn': self.mouse_btn,
            'harvest_vk': self.harvest_vk,
            'harvest_method': self.harvest_method,
            'harvest_mode': self.harvest_mode,
            'harvest_duration': self.harvest_duration,
            'harvest_spam_interval': self.harvest_spam_interval,
            'harvest_images': self.harvest_images,
            'assist_images': {
                'stove': self.img_stove,
                'start': self.img_start,
                'heat': self.img_heat,
                'serve': self.img_serve,
                'recipe': self.img_recipe,
                'snow_add': self.img_snow_add,
                'snow_start': self.img_snow_start,
                'snow_puzzle': self.img_snow_puzzle,
                'snow_get': self.img_snow_get
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
            self.walk_hotkey = parse_vk(data.get('walk_hotkey', 112))
            self.cam_hotkey = parse_vk(data.get('cam_hotkey', 113))
            self.cook_hotkey = parse_vk(data.get('cook_hotkey', 117))
            self.snow_hotkey = parse_vk(data.get('snow_hotkey', 118))
            self.harvest_hotkey = parse_vk(data.get('harvest_hotkey', 114))
            self.tree_rock_hotkey = parse_vk(data.get('tree_rock_hotkey', 120))
            self.jump_hotkey = parse_vk(data.get('jump_hotkey', 119))
            self.confidence = data.get('confidence', 0.8)
            self.use_grayscale = data.get('use_grayscale', False)
            self.mouse_btn = parse_vk(data.get('mouse_btn', 2))
            self.harvest_vk = parse_vk(data.get('harvest_vk', 70))
            self.harvest_method = data.get('harvest_method', 'spam')
            self.harvest_mode = data.get('harvest_mode', 'spam')
            self.harvest_duration = data.get('harvest_duration', 5.0)
            self.harvest_spam_interval = data.get('harvest_spam_interval', 0.1)
            
            loaded_harvest = data.get('harvest_images')
            if loaded_harvest and isinstance(loaded_harvest, list):
                valid = [p for p in loaded_harvest if os.path.exists(p)]
                if valid:
                    self.harvest_images = valid
            if not self.harvest_images:
                self.harvest_images = get_default_harvest_images()
            preload_images(self.harvest_images, self.use_grayscale)

            imgs = data.get('assist_images', {})
            if imgs.get('stove'): self.img_stove = imgs['stove']
            if imgs.get('start'): self.img_start = imgs['start']
            if imgs.get('heat'): self.img_heat = imgs['heat']
            if imgs.get('serve'): self.img_serve = imgs['serve']
            if imgs.get('recipe'): self.img_recipe = imgs['recipe']
            if imgs.get('snow_add'): self.img_snow_add = imgs['snow_add']
            if imgs.get('snow_start'): self.img_snow_start = imgs['snow_start']
            if imgs.get('snow_puzzle'): self.img_snow_puzzle = imgs['snow_puzzle']
            if imgs.get('snow_get'): self.img_snow_get = imgs['snow_get']
            preload_images([self.img_stove, self.img_start, self.img_heat, self.img_serve, self.img_recipe,
                            self.img_snow_add, self.img_snow_start, self.img_snow_puzzle, self.img_snow_get], self.use_grayscale)
        except Exception as e:
            print(f"Load failed: {e}")

    def update_hotkeys(self, hotkeys_dict):
        if not isinstance(hotkeys_dict, dict):
            return
        if 'walk' in hotkeys_dict: self.walk_hotkey = parse_vk(hotkeys_dict['walk'])
        if 'cam' in hotkeys_dict: self.cam_hotkey = parse_vk(hotkeys_dict['cam'])
        if 'harvest' in hotkeys_dict: self.harvest_hotkey = parse_vk(hotkeys_dict['harvest'])
        if 'tree_rock' in hotkeys_dict: self.tree_rock_hotkey = parse_vk(hotkeys_dict['tree_rock'])
        if 'cook' in hotkeys_dict: self.cook_hotkey = parse_vk(hotkeys_dict['cook'])
        if 'snow' in hotkeys_dict: self.snow_hotkey = parse_vk(hotkeys_dict['snow'])
        if 'jump' in hotkeys_dict: self.jump_hotkey = parse_vk(hotkeys_dict['jump'])
        self.save_config()
        self.log(f"Hotkeys updated: Walk={self.walk_hotkey}, Cam={self.cam_hotkey}, Harvest={self.harvest_hotkey}")

assist_state = AssistState()

state_change_callback = None

def register_state_callback(cb):
    global state_change_callback
    state_change_callback = cb

def notify_state_changed():
    if state_change_callback:
        try:
            state_change_callback({
                "connected": assist_state.connected,
                "window_name": assist_state.window_name,
                "walk_active": assist_state.walk_active,
                "cam_active": assist_state.cam_active,
                "harvest_active": assist_state.harvest_active,
                "tree_rock_active": assist_state.harvest_active,
                "cook_active": assist_state.cook_active,
                "snow_active": assist_state.snow_active,
                "jump_active": assist_state.jump_active,
                "confidence": assist_state.confidence,
                "use_grayscale": assist_state.use_grayscale,
                "harvest_method": assist_state.harvest_method,
                "harvest_mode": assist_state.harvest_mode,
                "harvest_images": assist_state.harvest_images,
                "harvest_images_count": len(assist_state.harvest_images)
            })
        except Exception:
            pass

def is_target_active():
    fg = user32.GetForegroundWindow()
    if not fg:
        return False

    proc = get_proc_name_by_hwnd(fg)
    if proc == 'xdt.exe':
        if assist_state.hwnd != fg:
            assist_state.hwnd = fg
            assist_state.connected = True
        return True

    return False

def harvest_loop():
    last_vision_scan = 0
    state_harvest_sent = False
    while assist_state.running:
        if assist_state.harvest_active and is_target_active():
            state_harvest_sent = True
            method = getattr(assist_state, 'harvest_method', 'spam')

            # ──── METHOD A: SPAM / KEY HOLD METHOD ────
            if method == 'spam':
                if assist_state.harvest_mode == 'hold':
                    send_input_vk(assist_state.harvest_vk, True)
                    start_time = time.time()
                    while time.time() - start_time < assist_state.harvest_duration:
                        if not assist_state.harvest_active or not assist_state.running or not is_target_active() or getattr(assist_state, 'harvest_method', 'spam') != 'spam':
                            break
                        time.sleep(0.08)
                    send_input_vk(assist_state.harvest_vk, False)
                    time.sleep(0.3)
                else:
                    # Repeated keystroke spam
                    send_input_vk(assist_state.harvest_vk, True)
                    time.sleep(0.04)
                    send_input_vk(assist_state.harvest_vk, False)
                    start_time = time.time()
                    while time.time() - start_time < assist_state.harvest_spam_interval:
                        if not assist_state.harvest_active or not assist_state.running or not is_target_active() or getattr(assist_state, 'harvest_method', 'spam') != 'spam':
                            break
                        time.sleep(0.02)

            # ──── METHOD B: VISION DETECTION METHOD (Trees, Rocks, Bushes, Crops) ────
            elif method == 'vision':
                curr = time.time()
                if curr - last_vision_scan > 0.15 and pyautogui and assist_state.harvest_images:
                    last_vision_scan = curr
                    conf = float(assist_state.confidence)
                    gray = bool(assist_state.use_grayscale)
                    for p in assist_state.harvest_images:
                        if not assist_state.harvest_active or not is_target_active() or getattr(assist_state, 'harvest_method', 'spam') != 'vision':
                            break
                        target = get_cached_image(p, gray)
                        if target is not None:
                            try:
                                pos = pyautogui.locateCenterOnScreen(target, confidence=conf, grayscale=gray)
                                if pos and is_target_active() and assist_state.harvest_active:
                                    # Target detected on screen! Interact with harvest key
                                    send_input_vk(assist_state.harvest_vk, True)
                                    time.sleep(0.06)
                                    send_input_vk(assist_state.harvest_vk, False)
                                    time.sleep(0.12)
                                    break
                            except Exception:
                                pass
                time.sleep(0.04)
        else:
            if state_harvest_sent:
                send_input_vk(assist_state.harvest_vk, False)
                state_harvest_sent = False
            time.sleep(0.15)

def tree_rock_loop():
    # Merged into unified harvest_loop for zero-overhead
    while assist_state.running:
        time.sleep(1.0)

def jump_loop():
    state_jump_sent = False
    while assist_state.running:
        if assist_state.jump_active and is_target_active():
            state_jump_sent = True
            send_input_vk(32, True)
            time.sleep(0.05)
            send_input_vk(32, False)
            start_time = time.time()
            while time.time() - start_time < 0.1:
                if not assist_state.jump_active or not assist_state.running or not is_target_active():
                    break
                time.sleep(0.02)
        else:
            if state_jump_sent:
                send_input_vk(32, False)
                state_jump_sent = False
            time.sleep(0.15)

def walk_loop():
    state_walk_sent = False
    last_pulse = 0
    while assist_state.running:
        time.sleep(0.015)
        curr = time.time()
        is_active = is_target_active()

        if assist_state.walk_active and is_active:
            if not state_walk_sent:
                send_input_vk(assist_state.walk_vk, True)
                state_walk_sent = True
                last_pulse = curr
            elif curr - last_pulse > 1.5:
                send_input_vk(assist_state.walk_vk, True)
                last_pulse = curr
        else:
            if state_walk_sent:
                send_input_vk(assist_state.walk_vk, False)
                state_walk_sent = False

def cam_loop():
    state_cam_sent = False
    last_pulse = 0
    while assist_state.running:
        time.sleep(0.015)
        curr = time.time()
        is_active = is_target_active()

        if assist_state.cam_active and is_active:
            if not state_cam_sent:
                send_input_vk(assist_state.mouse_btn, True)
                state_cam_sent = True
                last_pulse = curr
            elif curr - last_pulse > 1.5:
                send_input_vk(assist_state.mouse_btn, True)
                last_pulse = curr
        else:
            if state_cam_sent:
                send_input_vk(assist_state.mouse_btn, False)
                state_cam_sent = False

def connect_to_window(window_name=None):
    found_hwnd = None
    found_title = None

    def search_enum(h, ctx):
        nonlocal found_hwnd, found_title
        if is_heartopia_window(h):
            found_hwnd = h
            found_title = "Heartopia (xdt.exe)"
            return False
        return True

    WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows(WNDPROC(search_enum), 0)

    if found_hwnd:
        assist_state.hwnd = found_hwnd
        assist_state.window_name = found_title or "Heartopia"
        assist_state.connected = True
        notify_state_changed()
        return True
    return False

def disconnect():
    assist_state.connected = False
    send_input_vk(assist_state.walk_vk, False)
    send_input_vk(assist_state.mouse_btn, False)
    send_input_vk(assist_state.harvest_vk, False)
    send_input_vk(32, False)
    assist_state.walk_active = False
    assist_state.cam_active = False
    assist_state.cook_active = False
    assist_state.snow_active = False
    assist_state.harvest_active = False
    assist_state.tree_rock_active = False
    assist_state.jump_active = False
    notify_state_changed()

def hotkey_loop():
    lt = {'walk': 0, 'cam': 0, 'cook': 0, 'snow': 0, 'harvest': 0, 'tree_rock': 0, 'jump': 0}
    while assist_state.running:
        time.sleep(0.015)
        # CRITICAL FIX: Ignore hotkeys if user is not actively focused on Heartopia!
        if not is_target_active():
            continue

        curr = time.time()
        try:
            # Auto Walk [F1]
            if is_pressed(assist_state.walk_hotkey) and (curr - lt['walk'] > 0.4):
                lt['walk'] = curr
                assist_state.walk_active = not assist_state.walk_active
                notify_state_changed()

            # Cam Lock [F2]
            if is_pressed(assist_state.cam_hotkey) and (curr - lt['cam'] > 0.4):
                lt['cam'] = curr
                assist_state.cam_active = not assist_state.cam_active
                notify_state_changed()

            # Auto Harvest (Crops, Trees, Rocks & Bushes) [F3]
            if is_pressed(assist_state.harvest_hotkey) and (curr - lt['harvest'] > 0.4):
                lt['harvest'] = curr
                assist_state.harvest_active = not assist_state.harvest_active
                assist_state.tree_rock_active = assist_state.harvest_active
                notify_state_changed()

            # Auto Cook [F6]
            if is_pressed(assist_state.cook_hotkey) and (curr - lt['cook'] > 0.4):
                lt['cook'] = curr
                assist_state.cook_active = not assist_state.cook_active
                notify_state_changed()

            # Snow Bot [F7]
            if is_pressed(assist_state.snow_hotkey) and (curr - lt['snow'] > 0.4):
                lt['snow'] = curr
                assist_state.snow_active = not assist_state.snow_active
                notify_state_changed()

            # Auto Jump [F8]
            if is_pressed(assist_state.jump_hotkey) and (curr - lt['jump'] > 0.4):
                lt['jump'] = curr
                assist_state.jump_active = not assist_state.jump_active
                notify_state_changed()

            # Optional / Legacy Tree & Rock hotkey [F9] toggles unified Auto Harvest
            if is_pressed(assist_state.tree_rock_hotkey) and (curr - lt['tree_rock'] > 0.4):
                lt['tree_rock'] = curr
                assist_state.harvest_active = not assist_state.harvest_active
                assist_state.tree_rock_active = assist_state.harvest_active
                notify_state_changed()
        except Exception:
            pass

def check_click(attr_name):
    if not pyautogui:
        return False
    path = getattr(assist_state, attr_name, '')
    if path and os.path.exists(path) and is_target_active():
        try:
            conf = float(assist_state.confidence)
            gray = bool(assist_state.use_grayscale)
            target = get_cached_image(path, gray)
            if target is None:
                target = path
            pos = pyautogui.locateCenterOnScreen(target, confidence=conf, grayscale=gray)
            if pos and is_target_active():
                hardware_click_at(pos.x, pos.y)
                return True
        except:
            return False
    return False

def click_all_targets(attr_name):
    if not pyautogui:
        return False
    path = getattr(assist_state, attr_name, '')
    if path and os.path.exists(path) and is_target_active():
        try:
            conf = float(assist_state.confidence)
            gray = bool(assist_state.use_grayscale)
            target = get_cached_image(path, gray)
            if target is None:
                target = path
            matches = list(pyautogui.locateAllOnScreen(target, confidence=conf, grayscale=gray))
            if matches and is_target_active():
                for box in matches:
                    if not is_target_active():
                        break
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
        if assist_state.cook_active and is_target_active():
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
        if assist_state.snow_active and is_target_active():
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
    threading.Thread(target=walk_loop, daemon=True).start()
    threading.Thread(target=cam_loop, daemon=True).start()
    threading.Thread(target=cook_loop, daemon=True).start()
    threading.Thread(target=snow_loop, daemon=True).start()
    threading.Thread(target=harvest_loop, daemon=True).start()
    threading.Thread(target=tree_rock_loop, daemon=True).start()
    threading.Thread(target=jump_loop, daemon=True).start()

