import customtkinter as ctk
import threading
import time
import ctypes
from ctypes import wintypes
import json
import os
import mmap
import sys
from tkinter import filedialog
import pyautogui
from pynput import mouse, keyboard
import datetime

# --- FORCE ADMIN ---
def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

# --- DISABLE SAFETIES ---
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

# --- THEME CONFIG ---
CYBER_THEME = {
    "bg_main": "#0B0B0B", "bg_card": "#141414", "bg_input": "#1F1F1F",
    "primary": "#00E5FF", "secondary": "#FF0055", "text_main": "#E0E0E0",
    "text_dim": "#444444", "terminal_bg": "#000000", "terminal_fg": "#00FF41",
    "border": "#333333", "chroma_key": "#000001"
}

CONFIG_FILE = "heartopia_config.json"
DEFAULT_CONFIG = {
    "window": "Heartopia",
    "overlay_enabled": True, "overlay_pos": "Top-Right",
    "walk_vk": 0x57, "walk_name": "W",      
    "walk_trig": 0x70, "walk_trig_name": "F1",
    "cam_trig": 0x71,  "cam_trig_name": "F2", 
    "loot_vk": 0x20, "loot_name": "Space",      
    "loot_trig": 0x72, "loot_trig_name": "F3",
    "loot_mode": "spam",
    "loot_spam_interval": 0.1,
    "cook_trig": 0x73, "cook_trig_name": "F4",
    "dll_farm_trig": 0x74, "dll_farm_name": "F5",
    "dll_cook_trig": 0x75, "dll_cook_name": "F6",
    "dll_ui_trig": 0x76,   "dll_ui_name": "F7",
    "dll_time_trig": 0x77, "dll_time_name": "F8",
    "snow_trig": 0x78,     "snow_trig_name": "F9",
    "build_trig": 0x79,    "build_trig_name": "F10", 
    "ice_trig": 0x7A,      "ice_trig_name": "F11", 
    "speed_farm": 10, "speed_cook": 10, "speed_time": 10,
    "mouse_btn": "Right",
    "presets": {"Oyster Mushroom": 155.0},
    "current_preset": "Oyster Mushroom",
    "img_stove": "", "img_start": "", "img_heat": "", "img_serve": "", "img_recipe": "",
    "img_snow": "", 
    "img_build_eye": "", "img_build_check": "", 
    "img_ice_1": "", "img_ice_2": "", "img_ice_3": "", "img_ice_4": "", 
    "cook_confidence": 0.8
}
cfg = DEFAULT_CONFIG.copy()

def load_config():
    global cfg
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                saved = json.load(f)
                for k, v in DEFAULT_CONFIG.items():
                    if k not in saved: saved[k] = v
                cfg = saved
    except: pass

def save_config():
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=4)
    except: pass

# --- WINAPI ---
user32 = ctypes.windll.user32
user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
user32.MapVirtualKeyW.argtypes = [ctypes.c_uint, ctypes.c_uint]
user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]

def set_click_through(hwnd):
    try:
        GWL_EXSTYLE = -20
        WS_EX_LAYERED = 0x00080000
        WS_EX_TRANSPARENT = 0x00000020
        style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED | WS_EX_TRANSPARENT)
    except: pass

class KEYBDINPUT(ctypes.Structure): _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD), ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.c_ulonglong)]
class MOUSEINPUT(ctypes.Structure): _fields_ = [("dx", ctypes.c_long), ("dy", ctypes.c_long), ("mouseData", ctypes.c_ulong), ("dwFlags", ctypes.c_ulong), ("time", ctypes.c_ulong), ("dwExtraInfo", ctypes.c_ulonglong)]
class INPUT(ctypes.Structure):
    class _U(ctypes.Union): _fields_ = [("ki", KEYBDINPUT), ("mi", MOUSEINPUT)]
    _fields_ = [("type", wintypes.DWORD), ("u", _U)]

def safe_int(val):
    try: return int(val)
    except: return 0

def is_pressed(vk_code):
    vk = safe_int(vk_code)
    if vk == 0: return False
    return user32.GetAsyncKeyState(vk) & 0x8000

def send_input_vk(vk_code, press=True):
    vk = safe_int(vk_code)
    if vk == 0: return
    if vk == 0x01: flags = 0x0002 if press else 0x0004; inp = INPUT(0, INPUT._U(mi=MOUSEINPUT(0, 0, 0, flags, 0, 0)))
    elif vk == 0x02: flags = 0x0008 if press else 0x0010; inp = INPUT(0, INPUT._U(mi=MOUSEINPUT(0, 0, 0, flags, 0, 0)))
    elif vk == 0x04: flags = 0x0020 if press else 0x0040; inp = INPUT(0, INPUT._U(mi=MOUSEINPUT(0, 0, 0, flags, 0, 0)))
    else: 
        scan = user32.MapVirtualKeyW(vk, 0)
        flags = 0x0008 | (0x0002 if not press else 0) 
        inp = INPUT(1, INPUT._U(ki=KEYBDINPUT(vk, scan, flags, 0, 0))) 
    user32.SendInput(1, ctypes.pointer(inp), ctypes.sizeof(inp))

def hardware_click_at(x, y):
    screen_w = user32.GetSystemMetrics(0); screen_h = user32.GetSystemMetrics(1)
    abs_x = int(x * 65535 / screen_w); abs_y = int(y * 65535 / screen_h)
    inputs = (INPUT * 3)()
    inputs[0].type = 0; inputs[0].u.mi.dx = abs_x; inputs[0].u.mi.dy = abs_y; inputs[0].u.mi.dwFlags = 0x8001
    inputs[1].type = 0; inputs[1].u.mi.dwFlags = 0x0002 
    inputs[2].type = 0; inputs[2].u.mi.dwFlags = 0x0004
    user32.SendInput(3, inputs, ctypes.sizeof(INPUT))

# --- INSTANT DUAL CLICK (BATCHED) ---
def hardware_dual_click(x1, y1, x2, y2):
    screen_w = user32.GetSystemMetrics(0); screen_h = user32.GetSystemMetrics(1)
    ax1 = int(x1 * 65535 / screen_w); ay1 = int(y1 * 65535 / screen_h)
    ax2 = int(x2 * 65535 / screen_w); ay2 = int(y2 * 65535 / screen_h)
    inputs = (INPUT * 6)()
    inputs[0].type = 0; inputs[0].u.mi.dx = ax1; inputs[0].u.mi.dy = ay1; inputs[0].u.mi.dwFlags = 0x8001 
    inputs[1].type = 0; inputs[1].u.mi.dwFlags = 0x0002 
    inputs[2].type = 0; inputs[2].u.mi.dwFlags = 0x0004 
    inputs[3].type = 0; inputs[3].u.mi.dx = ax2; inputs[3].u.mi.dy = ay2; inputs[3].u.mi.dwFlags = 0x8001 
    inputs[4].type = 0; inputs[4].u.mi.dwFlags = 0x0002
    inputs[5].type = 0; inputs[5].u.mi.dwFlags = 0x0004
    user32.SendInput(6, inputs, ctypes.sizeof(INPUT))

def get_windows():
    titles = []
    def foreach_window(hwnd, lParam):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0: buff = ctypes.create_unicode_buffer(length + 1); user32.GetWindowTextW(hwnd, buff, length + 1); titles.append(buff.value)
        return True
    user32.EnumWindows(ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)(foreach_window), 0)
    return sorted(list(set(titles)))

# --- MEMORY MANAGER ---
class SharedMemoryManager:
    def __init__(self, name="Local\\MyFarmSharedMemory", size=256):
        self.size = size; self.name = name; self.shm = None; self.setup()
    def setup(self):
        try:
            self.shm = mmap.mmap(-1, self.size, tagname=self.name, access=mmap.ACCESS_WRITE)
            self.shm.seek(0)
            if self.shm.read_byte() == 0 and self.shm[5] == 0:
                self.write_byte(5, cfg.get("speed_time", 10)) 
                self.write_byte(6, cfg.get("speed_cook", 10))
                self.write_byte(7, cfg.get("speed_farm", 10))
        except: pass
    def write_byte(self, offset, value):
        if self.shm:
            try: self.shm.seek(offset); self.shm.write_byte(int(value))
            except: pass

# --- FIXED GHOST OVERLAY ---
class DynamicGhost(ctk.CTkToplevel):
    def __init__(self, master, target_hwnd, **kwargs):
        super().__init__(master, **kwargs)
        self.target_hwnd = target_hwnd
        self.running = True
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(fg_color=CYBER_THEME["chroma_key"])
        self.attributes("-transparentcolor", CYBER_THEME["chroma_key"]) 
        self.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
        set_click_through(hwnd)
        self.list_frame = ctk.CTkFrame(self, fg_color=CYBER_THEME["chroma_key"])
        self.list_frame.pack(fill="both", expand=True)
        
        self.labels = {}
        self.keys = ["Time Dilation", "UI Bypass", "Memory Farm", "Memory Cook", 
                     "Auto Walk", "Cam Lock", "Harvester", "AI Chef", "Snow AI", "Ice Glitch"]
        
        for k in self.keys:
            l = ctk.CTkLabel(self.list_frame, text=k.upper(), font=("Roboto", 11, "bold"), 
                             text_color=CYBER_THEME["primary"], fg_color=CYBER_THEME["chroma_key"])
            self.labels[k] = l
        
        self.tracker_loop()

    def update_status(self, states):
        for l in self.labels.values():
            l.pack_forget()
            
        priority = [
            ("Time Dilation", states.get("time", False)),
            ("UI Bypass",     states.get("ui", False)),
            ("Memory Farm",   states.get("mfarm", False)),
            ("Memory Cook",   states.get("mcook", False)),
            ("Auto Walk",     states.get("walk", False)),
            ("Cam Lock",      states.get("cam", False)),
            ("Harvester",     states.get("loot", False)),
            ("AI Chef",       states.get("cook", False)),
            ("Snow AI",       states.get("snow", False)),
            ("Ice Glitch",    states.get("ice", False)),
        ]
        
        mode = cfg.get("overlay_pos", "Top-Right")
        align = "e" if "Right" in mode else "w"
        
        for name, active in priority:
            if active and name in self.labels:
                self.labels[name].pack(anchor=align, pady=1, padx=5)

    def tracker_loop(self):
        if not self.running: return
        try:
            active_hwnd = user32.GetForegroundWindow()
            if active_hwnd != self.target_hwnd: self.withdraw(); self.after(200, self.tracker_loop); return
            rect = wintypes.RECT(); result = user32.GetWindowRect(self.target_hwnd, ctypes.byref(rect))
            if result == 0 or rect.left <= -32000: self.withdraw()
            else:
                self.deiconify()
                gw_x, gw_y = rect.left, rect.top
                gw_w = rect.right - rect.left
                mode = cfg.get("overlay_pos", "Top-Right")
                if mode == "Top-Left": x = gw_x + 20; y = gw_y + 40
                else: x = gw_x + gw_w - 140; y = gw_y + 40
                self.geometry(f"120x220+{x}+{y}")
        except: self.withdraw()
        self.after(15, self.tracker_loop)
    def kill(self): self.running = False; self.destroy()

# --- COMPONENTS ---
class CyberFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        kwargs.setdefault("fg_color", CYBER_THEME["bg_card"]); kwargs.setdefault("border_color", CYBER_THEME["border"]); kwargs.setdefault("border_width", 1); kwargs.setdefault("corner_radius", 6); super().__init__(master, **kwargs)

class LogConsole(ctk.CTkTextbox):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(state="disabled", font=("Consolas", 11), text_color=CYBER_THEME["terminal_fg"], fg_color=CYBER_THEME["terminal_bg"], border_color=CYBER_THEME["primary"], border_width=1)
    def log(self, msg):
        self.configure(state="normal"); self.insert("end", f"> [{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}\n"); self.see("end"); self.configure(state="disabled")

class BindBtn(ctk.CTkButton):
    def __init__(self, master, code_key, name_key, cb, logger=None, **kwargs):
        super().__init__(master, text=str(cfg.get(name_key, "?")), command=self.listen, **kwargs)
        self.code_key = code_key; self.name_key = name_key; self.cb = cb; self.listening = False; self.logger = logger
        self.configure(width=70, height=24, font=("Roboto Medium", 10), fg_color="transparent", border_color=CYBER_THEME["text_dim"], border_width=1, text_color=CYBER_THEME["text_main"], hover_color=CYBER_THEME["bg_input"])
    def listen(self):
        if self.listening: return
        self.listening = True; self.configure(text="...", border_color=CYBER_THEME["secondary"], text_color=CYBER_THEME["secondary"])
        threading.Thread(target=self._thread, daemon=True).start()
    
    def _get_key_name(self, vk):
        if vk == 0x01: return "L_CLICK"
        if vk == 0x02: return "R_CLICK"
        if vk == 0x04: return "M_CLICK"
        if vk == 0x05: return "XBTN_1"
        if vk == 0x06: return "XBTN_2"
        if 96 <= vk <= 105: return f"NUM_{vk-96}"
        try: return chr(vk)
        except: return f"VK_{vk}"

    def _thread(self):
        time.sleep(0.2); self.found_vk = None; self.found_name = None; stop_event = threading.Event()
        def on_key(key):
            try:
                vk = key.vk if hasattr(key, 'vk') else key.value.vk
                if vk: self.found_vk = vk; self.found_name = self._get_key_name(vk); stop_event.set()
            except: pass
        def on_clk(x, y, button, pressed):
            if not pressed: return
            try:
                if button == mouse.Button.left: vk = 0x01
                elif button == mouse.Button.right: vk = 0x02
                elif button == mouse.Button.middle: vk = 0x04
                elif button == mouse.Button.x1: vk = 0x05
                elif button == mouse.Button.x2: vk = 0x06
                else: return
                self.found_vk = vk; self.found_name = self._get_key_name(vk); stop_event.set()
            except: pass
        k_l = keyboard.Listener(on_press=on_key); m_l = mouse.Listener(on_click=on_clk)
        k_l.start(); m_l.start(); stop_event.wait(); k_l.stop(); m_l.stop()
        time.sleep(0.1); self.listening = False
        if self.found_name: 
            self.configure(text=self.found_name, border_color=CYBER_THEME["primary"], text_color=CYBER_THEME["primary"])
            self.cb(self.code_key, self.found_vk, self.name_key, self.found_name)
        else: self.configure(text="?", border_color=CYBER_THEME["secondary"])

class ImgSelect(ctk.CTkFrame):
    def __init__(self, master, label, config_key, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.config_key = config_key
        ctk.CTkLabel(self, text=label, font=("Roboto", 11), text_color=CYBER_THEME["text_dim"], width=80, anchor="w").pack(side="left")
        self.btn_sel = ctk.CTkButton(self, text="BROWSE", width=60, height=20, fg_color=CYBER_THEME["bg_input"], hover_color=CYBER_THEME["primary"], font=("Roboto", 9, "bold"), command=self.select_file); self.btn_sel.pack(side="left", padx=5)
        self.lbl_file = ctk.CTkLabel(self, text="NONE", font=("Consolas", 10), text_color="#555", width=90, anchor="w"); self.lbl_file.pack(side="left", padx=5)
        self.update_label()
    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if path: cfg[self.config_key] = path; save_config(); self.update_label()
    def update_label(self):
        path = cfg.get(self.config_key, ""); self.lbl_file.configure(text=os.path.basename(path)[:10]+".." if path else "NONE", text_color=CYBER_THEME["primary"] if path else "#555")

# --- MAIN APP ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        load_config()
        self.mem = SharedMemoryManager()
        self.logger = None; self.overlay = None
        
        ctk.set_appearance_mode("Dark")
        self.title("HEARTOPIA // EXECUTER")
        self.geometry("480x780") 
        self.resizable(False, False)
        self.configure(fg_color=CYBER_THEME["bg_main"])

        self.hwnd = 0; self.connected = False; self.running = True
        self.s_walk = False; self.s_cam = False; self.s_loot = False; self.s_cook = False
        self.s_snow = False; self.s_ice = False
        self.s_time = False; self.s_ui = False; self.s_mfarm = False; self.s_mcook = False
        self.state_walk_sent = False; self.state_cam_sent = False; self.last_pulse = 0
        
        self.setup_ui()
        self.logger.log("SYSTEM INITIALIZED [ADMIN_MODE: ACTIVE]")
        
        threading.Thread(target=self.input_loop, daemon=True).start()
        threading.Thread(target=self.loot_loop, daemon=True).start()
        threading.Thread(target=self.cook_loop, daemon=True).start()
        threading.Thread(target=self.snow_loop, daemon=True).start()
        threading.Thread(target=self.ice_loop, daemon=True).start()

    def setup_ui(self):
        header = CyberFrame(self, height=70, fg_color="transparent", border_width=0)
        header.pack(fill="x", padx=15, pady=10)
        
        ov_frame = ctk.CTkFrame(header, fg_color="transparent"); ov_frame.pack(side="top", fill="x", pady=5)
        ctk.CTkLabel(ov_frame, text="HUD OVERLAY:", font=("Roboto", 10, "bold"), text_color=CYBER_THEME["text_dim"]).pack(side="left")
        self.sw_overlay = ctk.CTkSwitch(ov_frame, text="ENABLE", font=("Roboto", 10), progress_color=CYBER_THEME["primary"], command=self.update_overlay_state); 
        self.sw_overlay.pack(side="left", padx=10); 
        if cfg.get("overlay_enabled", False): self.sw_overlay.select()
        self.om_ov_pos = ctk.CTkOptionMenu(ov_frame, values=["Top-Left", "Top-Right"], width=90, height=22, font=("Roboto", 10), fg_color=CYBER_THEME["bg_input"], button_color=CYBER_THEME["bg_input"], command=self.update_overlay_pos)
        self.om_ov_pos.set(cfg.get("overlay_pos", "Top-Right")); self.om_ov_pos.pack(side="right")

        win_frame = ctk.CTkFrame(header, fg_color="transparent"); win_frame.pack(side="top", fill="x", pady=5)
        self.wins = get_windows()
        val = cfg["window"] if cfg["window"] in self.wins else (self.wins[0] if self.wins else "")
        self.om_win = ctk.CTkOptionMenu(win_frame, values=self.wins, width=220, height=28, fg_color=CYBER_THEME["bg_input"], button_color=CYBER_THEME["bg_input"], button_hover_color=CYBER_THEME["primary"], dropdown_fg_color=CYBER_THEME["bg_card"])
        self.om_win.set(val); self.om_win.pack(side="left")
        ctk.CTkButton(win_frame, text="↻", width=28, height=28, fg_color=CYBER_THEME["bg_input"], hover_color=CYBER_THEME["primary"], command=self.refresh).pack(side="left", padx=5)
        self.btn_conn = ctk.CTkButton(win_frame, text="LINK", width=80, height=28, fg_color=CYBER_THEME["primary"], hover_color="#00B8CC", text_color="black", font=("Roboto", 10, "bold"), command=self.toggle_conn); self.btn_conn.pack(side="right")

        self.tabs = ctk.CTkTabview(self, fg_color="transparent", segmented_button_fg_color=CYBER_THEME["bg_input"], segmented_button_selected_color=CYBER_THEME["primary"], segmented_button_selected_hover_color=CYBER_THEME["primary"], segmented_button_unselected_color=CYBER_THEME["bg_input"], segmented_button_unselected_hover_color=CYBER_THEME["bg_card"], text_color="white")
        self.tabs.pack(fill="both", expand=True, padx=15, pady=0)
        
        # --- TAB SETUP ---
        tab_dll = self.tabs.add("MEMORY")
        tab_bot = self.tabs.add("AUTOMATION")
        tab_cook = self.tabs.add("COOKING")
        tab_snow = self.tabs.add("SNOW")
        tab_build = self.tabs.add("BUILD")
        tab_ice = self.tabs.add("ICE") 

        def add_dll(p, t, b, vk, nk, update_fn):
            f = CyberFrame(p, height=40); f.pack(fill="x", pady=3)
            ctk.CTkLabel(f, text=t, font=("Roboto", 11, "bold"), text_color=CYBER_THEME["text_main"]).pack(side="left", padx=10, pady=8)
            def tog(): 
                v=s.get(); self.mem.write_byte(b, v); self.logger.log(f"MEM [{b}]: {v}"); update_fn(); self.upd_state()
            BindBtn(f, vk, nk, self.save_bind, logger=self.logger).pack(side="right", padx=10)
            s = ctk.CTkSwitch(f, text="", width=35, progress_color=CYBER_THEME["primary"], command=tog); s.pack(side="right"); return s
        
        self.sw_mem_farm = add_dll(tab_dll, "AUTO FARM (B1)", 1, "dll_farm_trig", "dll_farm_name", lambda: None)
        self.sw_mem_cook = add_dll(tab_dll, "AUTO COOK (B2)", 2, "dll_cook_trig", "dll_cook_name", lambda: None)
        self.sw_mem_ui = add_dll(tab_dll, "UI BYPASS (B3)", 3, "dll_ui_trig", "dll_ui_name", lambda: None)
        self.sw_mem_time = add_dll(tab_dll, "TIME DILATION (B4)", 4, "dll_time_trig", "dll_time_name", lambda: None)
        
        ctk.CTkFrame(tab_dll, height=1, fg_color=CYBER_THEME["border"]).pack(fill="x", pady=10)
        
        def add_sl(p, t, b, config_key):
            f = ctk.CTkFrame(p, fg_color="transparent"); f.pack(fill="x", pady=1)
            ctk.CTkLabel(f, text=t, font=("Roboto", 10), text_color=CYBER_THEME["text_dim"]).pack(side="left", padx=5)
            l = ctk.CTkLabel(f, text=str(cfg.get(config_key, 10)), width=25, text_color=CYBER_THEME["primary"], font=("Consolas", 11, "bold")); l.pack(side="right", padx=5)
            def on_change(v):
                val = int(v)
                self.mem.write_byte(b, val)
                l.configure(text=str(val))
                cfg[config_key] = val; save_config() # Save on slide
            sl = ctk.CTkSlider(f, from_=10, to=100, number_of_steps=90, width=130, progress_color=CYBER_THEME["primary"], command=on_change)
            sl.set(cfg.get(config_key, 10)) # Load from config or default 10
            sl.pack(side="right"); return sl

        self.sl_farm = add_sl(tab_dll, "FARM SPEED", 7, "speed_farm")
        self.sl_cook = add_sl(tab_dll, "COOK SPEED", 6, "speed_cook")
        self.sl_time = add_sl(tab_dll, "GLOBAL SPEED", 5, "speed_time")

        def add_bot(p, t, vk, nk, sw_cmd):
            f = CyberFrame(p); f.pack(fill="x", pady=4)
            r1 = ctk.CTkFrame(f, fg_color="transparent"); r1.pack(fill="x", pady=2)
            ctk.CTkLabel(r1, text=t, font=("Roboto", 11, "bold"), text_color="white").pack(side="left", padx=10)
            s = ctk.CTkSwitch(r1, text="", width=40, command=sw_cmd, progress_color=CYBER_THEME["primary"]); s.pack(side="right", padx=10)
            r2 = ctk.CTkFrame(f, fg_color="transparent"); r2.pack(fill="x", pady=2)
            ctk.CTkLabel(r2, text="TRIGGER:", font=("Roboto", 10), text_color=CYBER_THEME["text_dim"]).pack(side="left", padx=10)
            BindBtn(r2, vk, nk, self.save_bind, logger=self.logger).pack(side="right", padx=10)
            return s
        self.sw_walk = add_bot(tab_bot, "AUTO WALK", "walk_trig", "walk_trig_name", self.upd_state)
        self.sw_cam = add_bot(tab_bot, "CAM LOCK", "cam_trig", "cam_trig_name", self.upd_state)
        
        f_loot = CyberFrame(tab_bot); f_loot.pack(fill="x", pady=4)
        ctk.CTkLabel(f_loot, text="HARVESTER", font=("Roboto", 11, "bold"), text_color=CYBER_THEME["primary"]).pack(pady=4)
        r1 = ctk.CTkFrame(f_loot, fg_color="transparent"); r1.pack(fill="x")
        self.om_preset = ctk.CTkOptionMenu(r1, values=list(cfg["presets"].keys()), width=130, fg_color=CYBER_THEME["bg_input"], command=self.load_preset); self.om_preset.set(cfg["current_preset"]); self.om_preset.pack(side="left", padx=10)
        self.ent_time = ctk.CTkEntry(r1, width=50, fg_color=CYBER_THEME["bg_input"], border_color=CYBER_THEME["border"], text_color=CYBER_THEME["primary"]); self.ent_time.insert(0, str(cfg["presets"].get(cfg["current_preset"], 155.0))); self.ent_time.pack(side="right", padx=10)
        r2 = ctk.CTkFrame(f_loot, fg_color="transparent"); r2.pack(fill="x", pady=4)
        BindBtn(r2, "loot_trig", "loot_trig_name", self.save_bind, logger=self.logger).pack(side="left", padx=10)
        self.sw_loot = ctk.CTkSwitch(r2, text="", width=40, command=self.upd_state, progress_color=CYBER_THEME["primary"]); self.sw_loot.pack(side="right", padx=10)

        # Key & Mode selectors
        r3 = ctk.CTkFrame(f_loot, fg_color="transparent"); r3.pack(fill="x", pady=4)
        ctk.CTkLabel(r3, text="KEY:", font=("Roboto", 10), text_color=CYBER_THEME["text_dim"]).pack(side="left", padx=10)
        self.om_loot_key = ctk.CTkOptionMenu(r3, values=["F", "E", "Space"], width=80, fg_color=CYBER_THEME["bg_input"], command=self.change_loot_key)
        vk_to_name = {0x46: "F", 0x45: "E", 0x20: "Space"}
        self.om_loot_key.set(vk_to_name.get(cfg.get("loot_vk", 0x20), "Space"))
        self.om_loot_key.pack(side="left")
        
        ctk.CTkLabel(r3, text="MODE:", font=("Roboto", 10), text_color=CYBER_THEME["text_dim"]).pack(side="left", padx=10)
        self.om_loot_mode = ctk.CTkOptionMenu(r3, values=["Hold", "Spam"], width=80, fg_color=CYBER_THEME["bg_input"], command=self.change_loot_mode)
        self.om_loot_mode.set("Spam" if cfg.get("loot_mode", "spam") == "spam" else "Hold")
        self.om_loot_mode.pack(side="left")

        f_i = CyberFrame(tab_cook); f_i.pack(fill="x", pady=5)
        for l, k in [("1. HEAT", "img_heat"), ("2. SERVE", "img_serve"), ("3. START", "img_start"), ("4. RECIPE", "img_recipe"), ("5. STOVE", "img_stove")]:
            ImgSelect(f_i, l, k).pack(fill="x", padx=5, pady=2)
        r_c = CyberFrame(tab_cook, fg_color=CYBER_THEME["bg_input"], border_color=CYBER_THEME["primary"]); r_c.pack(fill="x", pady=10)
        ctk.CTkLabel(r_c, text="AI COOKING", font=("Roboto", 11, "bold"), text_color="white").pack(side="left", padx=15, pady=10)
        self.sw_cook = ctk.CTkSwitch(r_c, text="", command=self.upd_state, progress_color=CYBER_THEME["primary"]); self.sw_cook.pack(side="right", padx=15)
        BindBtn(r_c, "cook_trig", "cook_trig_name", self.save_bind, logger=self.logger).pack(side="right", padx=5)

        # --- SNOW TAB ---
        f_s = CyberFrame(tab_snow); f_s.pack(fill="x", pady=5)
        ImgSelect(f_s, "PUZZLE IMG", "img_snow").pack(fill="x", padx=5, pady=5)
        
        r_s = CyberFrame(tab_snow, fg_color=CYBER_THEME["bg_input"], border_color=CYBER_THEME["primary"]); r_s.pack(fill="x", pady=10)
        ctk.CTkLabel(r_s, text="SNOW PUZZLE", font=("Roboto", 11, "bold"), text_color="white").pack(side="left", padx=15, pady=10)
        self.sw_snow = ctk.CTkSwitch(r_s, text="", command=self.upd_state, progress_color=CYBER_THEME["primary"]); self.sw_snow.pack(side="right", padx=15)
        BindBtn(r_s, "snow_trig", "snow_trig_name", self.save_bind, logger=self.logger).pack(side="right", padx=5)

        # --- BUILD TAB (GLITCH) ---
        f_b = CyberFrame(tab_build); f_b.pack(fill="x", pady=5)
        ImgSelect(f_b, "EYE ICON", "img_build_eye").pack(fill="x", padx=5, pady=5)
        ImgSelect(f_b, "CHECK ICON", "img_build_check").pack(fill="x", padx=5, pady=5)
        r_b = CyberFrame(tab_build, fg_color=CYBER_THEME["bg_input"], border_color=CYBER_THEME["primary"])
        r_b.pack(fill="x", pady=10)
        ctk.CTkLabel(r_b, text="TRIGGER KEY:", font=("Roboto", 11, "bold"), text_color="white").pack(side="left", padx=15, pady=10)
        BindBtn(r_b, "build_trig", "build_trig_name", self.save_bind, logger=self.logger).pack(side="right", padx=15, pady=8)
        ctk.CTkLabel(tab_build, text="NOTE: Trigger performs INSTANT BATCH CLICK\non both images if found.", font=("Roboto", 9), text_color=CYBER_THEME["text_dim"]).pack(pady=5)

        # --- ICE TAB (GLITCH) ---
        f_ice = CyberFrame(tab_ice); f_ice.pack(fill="x", pady=5)
        ImgSelect(f_ice, "1. CHALLENGE", "img_ice_1").pack(fill="x", padx=5, pady=2)
        ImgSelect(f_ice, "2. START", "img_ice_2").pack(fill="x", padx=5, pady=2)
        ImgSelect(f_ice, "3. END", "img_ice_3").pack(fill="x", padx=5, pady=2)
        ImgSelect(f_ice, "4. CONFIRM", "img_ice_4").pack(fill="x", padx=5, pady=2)
        
        r_ice = CyberFrame(tab_ice, fg_color=CYBER_THEME["bg_input"], border_color=CYBER_THEME["primary"]); r_ice.pack(fill="x", pady=10)
        ctk.CTkLabel(r_ice, text="ICE LOOP", font=("Roboto", 11, "bold"), text_color="white").pack(side="left", padx=15, pady=10)
        self.sw_ice = ctk.CTkSwitch(r_ice, text="", command=self.upd_state, progress_color=CYBER_THEME["primary"]); self.sw_ice.pack(side="right", padx=15)
        BindBtn(r_ice, "ice_trig", "ice_trig_name", self.save_bind, logger=self.logger).pack(side="right", padx=5)


        f_log = ctk.CTkFrame(self, fg_color="transparent"); f_log.pack(side="bottom", fill="both", expand=True, padx=15, pady=10)
        self.logger = LogConsole(f_log, height=100); self.logger.pack(fill="both", expand=True)

    def refresh(self): self.wins = get_windows(); self.om_win.configure(values=self.wins); (self.om_win.set(self.wins[0]) if self.wins else None)
    def save_bind(self, ck, cv, nk, nv): cfg[ck] = cv; cfg[nk] = nv; save_config(); self.logger.log(f"BIND: {nk} -> {nv}")
    def load_preset(self, val): t = cfg["presets"].get(val, 155.0); self.ent_time.delete(0, "end"); self.ent_time.insert(0, str(t)); cfg["current_preset"] = val; save_config()
    def change_loot_key(self, val):
        name_to_vk = {"F": 0x46, "E": 0x45, "Space": 0x20}
        cfg["loot_vk"] = name_to_vk.get(val, 0x20)
        cfg["loot_name"] = val
        save_config()
        self.logger.log(f"HARVESTER KEY: {val}")
    def change_loot_mode(self, val):
        cfg["loot_mode"] = val.lower()
        save_config()
        self.logger.log(f"HARVESTER MODE: {val}")

    def update_overlay_state(self):
        enabled = self.sw_overlay.get() == 1
        cfg["overlay_enabled"] = enabled; save_config()
        self.manage_overlay()
    
    def update_overlay_pos(self, pos):
        cfg["overlay_pos"] = pos; save_config()
        self.upd_state()

    def manage_overlay(self):
        enabled = self.sw_overlay.get() == 1
        if enabled and self.connected and self.hwnd:
            if self.overlay is None:
                self.overlay = DynamicGhost(self, self.hwnd)
                self.upd_state()
        else:
            if self.overlay: self.overlay.kill(); self.overlay = None

    def toggle_conn(self):
        if not self.connected:
            name = self.om_win.get(); h = user32.FindWindowW(None, name)
            if h: 
                self.hwnd = h; self.connected = True
                self.btn_conn.configure(text="STOP", fg_color=CYBER_THEME["secondary"])
                cfg["window"] = name; save_config(); self.om_win.configure(state="disabled")
                self.logger.log(f"LINKED >> {name}")
                self.manage_overlay()
        else:
            self.connected = False; self.state_walk_sent = False; self.state_cam_sent = False
            send_input_vk(cfg["walk_vk"], False); send_input_vk(0x02 if cfg["mouse_btn"] == "Right" else 0x01, False)
            self.sw_walk.deselect(); self.sw_cam.deselect(); self.sw_loot.deselect(); self.sw_cook.deselect(); self.sw_snow.deselect(); self.sw_ice.deselect();
            self.sw_mem_farm.deselect(); self.sw_mem_cook.deselect(); self.sw_mem_ui.deselect(); self.sw_mem_time.deselect();
            self.upd_state()
            self.btn_conn.configure(text="LINK", fg_color=CYBER_THEME["primary"]); self.om_win.configure(state="normal")
            self.logger.log("UNLINKED")
            self.manage_overlay()

    def upd_state(self): 
        # THREAD SAFETY
        if threading.current_thread() is not threading.main_thread():
            self.after(0, self.upd_state)
            return

        self.s_walk = self.sw_walk.get() == 1; self.s_cam = self.sw_cam.get() == 1
        self.s_loot = self.sw_loot.get() == 1; self.s_cook = self.sw_cook.get() == 1; 
        self.s_snow = self.sw_snow.get() == 1; self.s_ice = self.sw_ice.get() == 1
        self.s_mfarm = self.sw_mem_farm.get() == 1; self.s_mcook = self.sw_mem_cook.get() == 1
        self.s_ui = self.sw_mem_ui.get() == 1; self.s_time = self.sw_mem_time.get() == 1
        
        if self.overlay: 
            states = {
                "walk": self.s_walk, "cam": self.s_cam, "loot": self.s_loot, 
                "cook": self.s_cook, "snow": self.s_snow, "ice": self.s_ice,
                "mfarm": self.s_mfarm, "mcook": self.s_mcook, "ui": self.s_ui, "time": self.s_time
            }
            self.overlay.update_status(states)

    def perform_build_glitch(self):
        # 1. Check paths
        p_eye = cfg.get("img_build_eye", "")
        p_chk = cfg.get("img_build_check", "")
        if not (os.path.exists(p_eye) and os.path.exists(p_chk)):
            self.logger.log("ERR: Build images missing")
            return
        
        # 2. Locate BOTH first
        try:
            loc_eye = pyautogui.locateCenterOnScreen(p_eye, confidence=0.85, grayscale=False)
            loc_chk = pyautogui.locateCenterOnScreen(p_chk, confidence=0.85, grayscale=False)
            
            if loc_eye and loc_chk:
                # 3. USE BATCH CLICK (Optimized for simultaneity)
                hardware_dual_click(loc_eye.x, loc_eye.y, loc_chk.x, loc_chk.y)
                self.logger.log("BUILD GLITCH FIRED")
            else:
                self.logger.log("ERR: Build imgs not found")
        except Exception as e:
            self.logger.log(f"ERR: {e}")

    def input_loop(self):
        lt = {"w":0, "c":0, "l":0, "ck":0, "sn":0, "ice":0, "bg": 0, "d_farm":0, "d_cook":0, "d_ui":0, "d_time":0}
        while self.running:
            time.sleep(0.01); curr = time.time()
            is_active_window = (user32.GetForegroundWindow() == self.hwnd)
            try:
                if self.connected:
                    def chk(tk, key, sw):
                        if is_pressed(cfg[tk]) and curr - lt[key] > 0.4:
                            self.after(0, sw.toggle) 
                            lt[key] = curr
                    chk("walk_trig", "w", self.sw_walk); chk("cam_trig", "c", self.sw_cam)
                    chk("loot_trig", "l", self.sw_loot); chk("cook_trig", "ck", self.sw_cook)
                    chk("snow_trig", "sn", self.sw_snow); chk("ice_trig", "ice", self.sw_ice)
                    
                    # BUILD GLITCH TRIGGER (One Shot, not a toggle)
                    if is_pressed(cfg["build_trig"]) and curr - lt["bg"] > 0.5:
                        threading.Thread(target=self.perform_build_glitch).start()
                        lt["bg"] = curr

                    def dll(tk, key, sw, b, n):
                        if is_pressed(cfg[tk]) and curr - lt[key] > 0.4:
                            self.after(0, lambda: self._toggle_mem(sw, b, n))
                            lt[key] = curr
                    dll("dll_farm_trig", "d_farm", self.sw_mem_farm, 1, "Farm")
                    dll("dll_cook_trig", "d_cook", self.sw_mem_cook, 2, "Cook")
                    dll("dll_ui_trig", "d_ui", self.sw_mem_ui, 3, "UI")
                    dll("dll_time_trig", "d_time", self.sw_mem_time, 4, "Time")
            except: pass

            if self.connected and is_active_window:
                if curr - self.last_pulse > 1.5:
                    if self.s_walk: send_input_vk(cfg["walk_vk"], True)
                    if self.s_cam: send_input_vk(0x02 if cfg["mouse_btn"] == "Right" else 0x01, True)
                    self.last_pulse = curr
                if self.s_walk:
                    if not self.state_walk_sent: send_input_vk(cfg["walk_vk"], True); self.state_walk_sent = True
                else:
                    if self.state_walk_sent: send_input_vk(cfg["walk_vk"], False); self.state_walk_sent = False
                m_btn = 0x02 if cfg["mouse_btn"] == "Right" else 0x01
                if self.s_cam:
                    if not self.state_cam_sent: send_input_vk(m_btn, True); self.state_cam_sent = True
                else:
                    if self.state_cam_sent: send_input_vk(m_btn, False); self.state_cam_sent = False
            elif self.connected:
                if self.state_walk_sent: send_input_vk(cfg["walk_vk"], False); self.state_walk_sent = False
                if self.state_cam_sent: send_input_vk(0x02 if cfg["mouse_btn"] == "Right" else 0x01, False); self.state_cam_sent = False

    def _toggle_mem(self, sw, b, n):
        sw.toggle()

    def loot_loop(self):
        while self.running:
            time.sleep(0.1)
            if (user32.GetForegroundWindow() == self.hwnd) and self.connected and self.s_loot:
                if cfg.get("loot_mode", "spam") == "hold":
                    try: d = float(self.ent_time.get())
                    except: d = 155.0
                    send_input_vk(cfg["loot_vk"], True); s = time.time()
                    while time.time() - s < d:
                        if not self.s_loot or not self.connected: break
                        time.sleep(0.1)
                    send_input_vk(cfg["loot_vk"], False); time.sleep(0.2)
                else:
                    # Spam Mode
                    send_input_vk(cfg["loot_vk"], True)
                    time.sleep(0.05)
                    send_input_vk(cfg["loot_vk"], False)
                    # Sleep for the configured interval
                    start_time = time.time()
                    interval = cfg.get("loot_spam_interval", 0.1)
                    while time.time() - start_time < interval:
                        if not self.s_loot or not self.connected: break
                        time.sleep(0.02)

    def cook_loop(self):
        while self.running:
            if not (self.s_cook and self.connected and (user32.GetForegroundWindow() == self.hwnd)): time.sleep(0.5); continue
            try: cc = float(cfg.get("cook_confidence", 0.8))
            except: cc = 0.8
            def fc(k):
                p = cfg.get(k, ""); 
                if p and os.path.exists(p):
                    try: 
                        pos = pyautogui.locateCenterOnScreen(p, confidence=cc, grayscale=False)
                        if pos: hardware_click_at(pos.x, pos.y); return True
                    except: return False
                return False
            if fc("img_heat") or fc("img_serve") or fc("img_start") or fc("img_recipe") or fc("img_stove"): continue
            time.sleep(0.01)

    def snow_loop(self):
        while self.running:
            if not (self.s_snow and self.connected and (user32.GetForegroundWindow() == self.hwnd)): 
                time.sleep(0.5); continue
            try: 
                p = cfg.get("img_snow", "")
                if p and os.path.exists(p):
                    matches = list(pyautogui.locateAllOnScreen(p, confidence=0.90, grayscale=False))
                    if not matches:
                        time.sleep(0.01); continue
                    count = 0
                    for box in matches:
                        cx = box.left + (box.width // 2); cy = box.top + (box.height // 2)
                        hardware_click_at(cx, cy); count += 1
                        if count >= 3: break
                else: time.sleep(0.5)
            except: time.sleep(0.01)

    # --- ICE LOOP (REVERTED TO COLOR MATCH FOR ACCURACY) ---
    def ice_loop(self):
        while self.running:
            if not (self.s_ice and self.connected and (user32.GetForegroundWindow() == self.hwnd)):
                time.sleep(0.5); continue
            
            # 4 -> 3 -> 2 -> 1
            priority_keys = ["img_ice_4", "img_ice_3", "img_ice_2", "img_ice_1"]
            
            clicked = False
            for k in priority_keys:
                p = cfg.get(k, "")
                if p and os.path.exists(p):
                    try:
                        # Reverted grayscale=False because True was clicking wrong items
                        pos = pyautogui.locateCenterOnScreen(p, confidence=0.85, grayscale=False)
                        if pos:
                            hardware_click_at(pos.x, pos.y)
                            clicked = True
                            # Short sleep to prevent double clicking but keep it snappy
                            time.sleep(0.15) 
                            break 
                    except: pass
            
            if not clicked:
                time.sleep(0.01)

if __name__ == "__main__":
    app = App()
    app.mainloop()