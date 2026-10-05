import threading, webbrowser, os, sys, logging, multiprocessing

# --- 1. SILENCE LOGS ---
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR) 
logging.getLogger('socketio').setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)

from flask import Flask
from flask_socketio import SocketIO
from heartopia_modules.routes import register_routes
from heartopia_modules.hotkeys import listener
from heartopia_modules.config import state
app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*")

if __name__ == "__main__":
    # 0. PyInstaller Freeze Support (Critical for exe)
    multiprocessing.freeze_support()

    # 1. Ensure Note Folder Exists if set
    if state.conf["note_folder"] and not os.path.exists(state.conf["note_folder"]): 
        try: 
            os.makedirs(state.conf["note_folder"])
            print(f"Created music folder: {state.conf['note_folder']}")
        except: pass

    # 2. Start Hotkey Listener
    threading.Thread(target=listener, daemon=True).start()
    # 4. Register Routes
    register_routes(app, socketio)

    # 5. Open Browser
    url = "http://127.0.0.1:5000"
    threading.Timer(1.5, lambda: webbrowser.open(url)).start()

    print(f"==========================================")
    print(f" PianiPia V6 - STARTED ")
    print(f"==========================================")
    print(f" App running at: {url}")
    print(f" Keep this window open.")

    socketio.run(app, port=5000, allow_unsafe_werkzeug=True)