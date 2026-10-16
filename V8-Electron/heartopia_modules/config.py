import os, json, threading

CONFIG_FILE = "config.json"
FAV_FILE = "favorites.json"
SUPABASE_URL = "https://uiclrnderaagzbgezolt.supabase.co"
SUPABASE_KEY = "sb_publishable_1nuHwPjz75BpU7EICEYDng_9rdsEFvH"

MAP_22 = {48:',',49:'l',50:'.',51:';',52:'/',53:'o',54:'0',55:'p',56:'-',57:'[',58:'=',59:']',60:'z',61:'s',62:'x',63:'d',64:'c',65:'v',66:'g',67:'b',68:'h',69:'n',70:'j',71:'m',72:'q',73:'2',74:'w',75:'3',76:'e',77:'r',78:'5',79:'t',80:'6',81:'y',82:'7',83:'u',84:'i'}
MAP_15 = {60:'a',62:'s',64:'d',65:'f',67:'g',69:'h',71:'j',72:'q',74:'w',76:'e',77:'r',79:'t',81:'y',83:'u',84:'i'}
TRANS = {c: c.lower() for c in "QWERTYUIOPASDFGHJKLZXCVBNM"}
TRANS.update({c: c for c in "1234567890-=/[];',./\\"})

REVERSE_MAP_22 = {str(v).upper(): k for k, v in MAP_22.items()}
REVERSE_MAP_15 = {str(v).upper(): k for k, v in MAP_15.items()}

VK = {'LBUTTON':1,'RBUTTON':2,'MBUTTON':4,'BACKSPACE':8,'TAB':9,'ENTER':13,'SHIFT':16,'CTRL':17,'ALT':18,'PAUSE':19,'CAPSLOCK':20,'ESC':27,'SPACE':32,'PAGEUP':33,'PAGEDOWN':34,'END':35,'HOME':36,'LEFT':37,'UP':38,'RIGHT':39,'DOWN':40,'PRINTSCREEN':44,'INSERT':45,'DELETE':46,'LWIN':91,'RWIN':92,'APPS':93,'NUMLOCK':144,'SCROLL':145,';':186,'=':187,',':188,'-':189,'.':190,'/':191,'`':192,'[':219,'\\':220,']':221,"'":222}
VK.update({str(i): 0x30+i for i in range(10)})
VK.update({chr(i): i for i in range(65, 91)})
VK.update({f'F{i}': 0x70+(i-1) for i in range(1, 25)})
VK.update({f'NUMPAD{i}': 0x60+i for i in range(10)})
VK.update({'MULTIPLY':106,'ADD':107,'SEPARATOR':108,'SUBTRACT':109,'DECIMAL':110,'DIVIDE':111,'NUMPADENTER':13})

def get_vk(k): return VK.get(str(k).upper(), 0)

class AppState:
    def __init__(self):
        # Thread Synchronization Lock
        self.lock = threading.Lock()
        
        self.conf = {
            "note_folder": "", 
            "hotkey_play": "F4", 
            "hotkey_stop": "F5",
            "theme": "light",
            "queue": [],
            "online_per_page": 50 
        }
        
        if not os.path.exists(CONFIG_FILE):
            self.save()
        else:
            self.load_config()
            
        self.favs = []
        if os.path.exists(FAV_FILE):
            try:
                with open(FAV_FILE, 'r', encoding='utf-8', errors='ignore') as f: 
                    self.favs = json.load(f)
            except: pass
        
        self.playing = self.paused = self.stop_req = False
        self.song = "None"; self.prog = 0; self.status = "Ready" 
        self.queue = self.conf.get("queue", [])
        self.spd = 1.0; self.snap = 0; self.loop = False
        
        self.vk_play = get_vk(self.conf.get("hotkey_play", "F4"))
        self.vk_stop = get_vk(self.conf.get("hotkey_stop", "F5"))
        
        if self.conf.get("note_folder", "") and not os.path.exists(self.conf["note_folder"]): 
            try: os.makedirs(self.conf["note_folder"])
            except: pass

    def load_config(self):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    for k in self.conf:
                        if k in data: self.conf[k] = data[k]
        except Exception as e: 
            print(f"Error loading config.json: {e}")

    def save(self):
        self.vk_play = get_vk(self.conf.get("hotkey_play", "F4"))
        self.vk_stop = get_vk(self.conf.get("hotkey_stop", "F5"))
        
        nf = self.conf.get("note_folder", "")
        if nf:
            try: os.makedirs(nf, exist_ok=True)
            except: pass
        
        existing_data = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8', errors='ignore') as f: 
                    d = json.load(f)
                    if isinstance(d, dict): existing_data = d
            except: pass
        
        existing_data.update(self.conf)
        
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f: 
                json.dump(existing_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config.json: {e}")

    def save_fav(self): 
        try:
            with open(FAV_FILE, 'w', encoding='utf-8') as f: 
                json.dump(self.favs, f, ensure_ascii=False)
        except: pass

state = AppState()