import os, threading, sys, re, subprocess
import tkinter as tk
from tkinter import filedialog
from flask import render_template_string, jsonify, request, send_from_directory
from supabase import create_client # <--- Add this here at the top

from .config import state, SUPABASE_URL, SUPABASE_KEY, REVERSE_MAP_22, REVERSE_MAP_15
from .templates import HTML_TEMPLATE
from .player import toggle_play, stop_play
from .converter import process_conversion

def open_dialog_direct(mode='directory', filetypes=None):
    """
    Opens a dialog directly in the current process.
    This prevents the 'subprocess loop' issue in compiled exes.
    """
    path = None
    try:
        # Create a hidden root window
        root = tk.Tk()
        root.withdraw() 
        root.attributes('-topmost', True) 
        
        if mode == 'directory':
            path = filedialog.askdirectory()
        elif mode == 'file':
            path = filedialog.askopenfilename(filetypes=filetypes)
            
        root.destroy()
    except Exception as e:
        print(f"Dialog Error: {e}")
    return path

def clean_filename(name):
    """
    Sanitize filename to prevent directory traversal and illegal OS characters.
    Allows Unicode (Chinese, etc.) but removes: \ / * ? : " < > |
    """
    # Remove null bytes
    name = name.replace('\0', '')
    # Allow anything EXCEPT illegal Windows/FS chars
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

def register_routes(app, socketio):
    
    def status_broadcaster():
        while True:
            socketio.sleep(0.016)
            try:
                socketio.emit('status_update', {
                    'is_playing': state.playing,
                    'is_paused': state.paused,
                    'progress': state.prog,
                    'text': state.status,
                    'current_song': state.song
                })
            except: pass
    
    threading.Thread(target=status_broadcaster, daemon=True).start()

    @app.route('/')
    def index(): 
        return render_template_string(HTML_TEMPLATE, REVERSE_MAP_22=REVERSE_MAP_22, REVERSE_MAP_15=REVERSE_MAP_15, THEME=state.conf.get('theme', 'light'))

    @app.route('/api/queue/update', methods=['POST'])
    def q_upd(): 
        state.queue = request.json.get('queue', [])
        state.conf['queue'] = state.queue
        state.save()
        return jsonify({'ok': True})

    @app.route('/api/play_params', methods=['POST'])
    def p_prms():
        d = request.json
        if 'speed' in d: state.spd = float(d['speed'])
        if 'snap' in d: state.snap = int(d['snap'])
        if 'loop' in d: state.loop = bool(d['loop'])
        return jsonify({'ok': True})

    @app.route('/api/songs')
    def get_s():
        d = state.conf.get("note_folder", "")
        songs = []
        if d and os.path.exists(d):
            for f in os.listdir(d):
                if f.endswith('.txt'):
                    fp = os.path.join(d, f)
                    songs.append({'name': f, 'mtime': os.path.getmtime(fp)})
        return jsonify({'songs': songs, 'favorites': state.favs, 'queue': state.conf.get('queue', [])})

    @app.route('/api/select', methods=['POST'])
    def sel_s():
        if state.playing: stop_play()
        state.song = request.json.get('filename')
        return jsonify({'ok': True})

    @app.route('/api/preview_content', methods=['POST'])
    def r_prev_c():
        fn = request.json.get('filename')
        try:
            if not fn.endswith('.txt'): fn_txt = fn + ".txt"
            else: fn_txt = fn
            path = os.path.join(state.conf["note_folder"], fn_txt)
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return jsonify({'ok': True, 'data': f.read()})
        except: pass
        try:
            from supabase import create_client
            sb = create_client(SUPABASE_URL, SUPABASE_KEY)
            res = sb.table("HeartopiaMIDI_CommunitySongs").select("song_data").eq("song_name", fn.replace(".txt", "")).execute()
            if res.data:
                 return jsonify({'ok': True, 'data': res.data[0]['song_data']})
        except Exception as e: print(e)
        return jsonify({'ok': False})

    @app.route('/api/save_content', methods=['POST'])
    def save_c():
        fn = request.json.get('filename')
        data = request.json.get('data')
        if not fn or not data: return jsonify({'ok': False})
        try:
            path = os.path.join(state.conf["note_folder"], fn)
            with open(path, 'w', encoding='utf-8') as f: f.write(data)
            return jsonify({'ok': True})
        except Exception as e: return jsonify({'ok': False})

    @app.route('/api/play', methods=['POST'])
    def r_play(): toggle_play(request.json); return jsonify({'ok': True})

    @app.route('/api/stop', methods=['POST'])
    def r_stop(): stop_play(); return jsonify({'ok': True})
    
    @app.route('/api/status')
    def r_stat(): return jsonify({'is_playing': state.playing, 'is_paused': state.paused, 'progress': state.prog, 'text': state.status, 'current_song': state.song})

    @app.route('/api/fav', methods=['POST'])
    def r_fav():
        f = request.json.get('filename')
        state.favs.remove(f) if f in state.favs else state.favs.append(f)
        state.save_fav(); return jsonify({'ok': True})

    @app.route('/api/delete', methods=['POST'])
    def r_del():
        p = os.path.join(state.conf["note_folder"], request.json.get('filename'))
        if os.path.exists(p): os.remove(p)
        return jsonify({'ok': True})

    @app.route('/api/delete_batch', methods=['POST'])
    def r_del_batch():
        names = request.json.get('filenames', [])
        c = 0
        for n in names:
            # Clean possible JS quoting
            clean_n = n
            if clean_n.startswith("'") and clean_n.endswith("'"): clean_n = clean_n[1:-1]
            if clean_n.startswith('"') and clean_n.endswith('"'): clean_n = clean_n[1:-1]
            
            p = os.path.join(state.conf["note_folder"], clean_n)
            if os.path.exists(p):
                try: 
                    os.remove(p)
                    c += 1
                except Exception as e: 
                    print(f"Failed to delete {p}: {e}")
            else:
                if not p.endswith('.txt'):
                     p_txt = p + ".txt"
                     if os.path.exists(p_txt):
                        try:
                            os.remove(p_txt)
                            c += 1
                        except: pass
        return jsonify({'ok': True, 'count': c})

    @app.route('/api/convert', methods=['POST'])
    def r_conv():
        files = request.files.getlist('files[]')
        target = request.form.get('target', 'Both')
        pitch = int(request.form.get('pitch', 0))
        msg = process_conversion(files, target, pitch)
        return jsonify({'message': msg})

    @app.route('/api/settings/browse_safe')
    def browse():
        path = open_dialog_direct(mode='directory')
        if path: return jsonify({'path': path})
        return jsonify({'path': None})

    @app.route('/api/settings/get')
    def get_conf(): 
        return jsonify(state.conf)

    @app.route('/api/settings/save', methods=['POST'])
    def save_conf():
        try:
            d = request.get_json(silent=True) or {}
            # Defaults to current config if not provided in request
            current = state.conf
            state.conf.update({
                "note_folder": d.get('note_folder', current.get('note_folder', '')), 
                "hotkey_play": d.get('hotkey_play', current.get('hotkey_play', 'F4')), 
                "hotkey_stop": d.get('hotkey_stop', current.get('hotkey_stop', 'F5')),
                "online_per_page": int(d.get('online_per_page', current.get('online_per_page', 50)))
            })
            state.save()
            return jsonify({'ok': True})
        except Exception as e:
            print(f"Save Settings Error: {e}")
            return jsonify({'ok': False})

    @app.route('/api/settings/save_theme', methods=['POST'])
    def save_theme():
        try:
            d = request.get_json(silent=True) or {}
            state.conf['theme'] = d.get('theme', 'light')
            state.save()
            return jsonify({'ok': True})
        except Exception as e:
            print(f"Save Theme Error: {e}")
            return jsonify({'ok': False})

    @app.route('/api/terminate', methods=['POST'])
    def kill(): 
        threading.Timer(0.1, lambda: os._exit(0)).start()
        return jsonify({'ok': True})

    # --- SUPABASE WRAPPERS ---
    @app.route('/api/online/search')
    def ol_search():
        try:
            from supabase import create_client
            sb = create_client(SUPABASE_URL, SUPABASE_KEY)
            q = request.args.get('q', '')
            t = request.args.get('type', 'All')
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 50))
            
            if per_page not in [50, 100, 200, 300]: per_page = 50

            start = (page - 1) * per_page
            end = start + per_page - 1

            query = sb.table("HeartopiaMIDI_CommunitySongs").select("song_name, instrument_type, created_at", count='exact')
            if q: query = query.ilike("song_name", f"%{q}%")
            if t != 'All': query = query.ilike("instrument_type", "%15%" if t == '15K' else "%22%")

            res = query.order("created_at", desc=True).range(start, end).execute()
            total_count = res.count if res.count is not None else len(res.data)
            return jsonify({'songs': res.data, 'total': total_count, 'page': page})
        except Exception as e:
            print(f"Online Search Error: {e}")
            return jsonify({'songs': [], 'total': 0})

    @app.route('/api/online/download', methods=['POST'])
    def ol_dl():
        try:
            from supabase import create_client
            r = create_client(SUPABASE_URL, SUPABASE_KEY).table("HeartopiaMIDI_CommunitySongs").select("*").eq("song_name", request.json.get('name')).execute()
            if r.data:
                # Still clean names for downloads to file system
                safe_name = clean_filename(request.json.get('name'))
                with open(os.path.join(state.conf["note_folder"], f"{safe_name}.txt"), 'w', encoding='utf-8') as f: 
                    f.write(r.data[0]['song_data'])
        except Exception as e: 
            print(f"Download Error: {e}")
            return jsonify({'ok': False})
        return jsonify({'ok': True})

    @app.route('/api/online/download_batch', methods=['POST'])
    def ol_dl_batch():
        ns = request.json.get('names', [])
        s, f_count = 0, 0
        try:
            from supabase import create_client
            sb = create_client(SUPABASE_URL, SUPABASE_KEY)
            for n in ns:
                try:
                    r = sb.table("HeartopiaMIDI_CommunitySongs").select("*").eq("song_name", n).execute()
                    if r.data:
                        safe_name = clean_filename(n)
                        with open(os.path.join(state.conf["note_folder"], f"{safe_name}.txt"), 'w', encoding='utf-8') as fh: 
                            fh.write(r.data[0]['song_data'])
                        s += 1
                    else: f_count += 1
                except: f_count += 1
        except: pass
        return jsonify({'success': s, 'failed': f_count})

    @app.route('/api/online/upload_browser', methods=['POST'])
    def ol_ul():
        u, d, e = 0, 0, 0
        files = request.files.getlist('files[]')
        if not files: return jsonify({'uploaded':0,'duplicates':0,'errors':0})
        try:
            from supabase import create_client
            sb = create_client(SUPABASE_URL, SUPABASE_KEY)
            for f in files:
                try:
                    f.seek(0, 2); sz = f.tell(); f.seek(0)
                    # 500KB LIMIT (512,000 bytes)
                    if sz > 512000 or not f.filename.lower().endswith('.txt'): e+=1; continue
                    
                    # USE clean_filename TO ALLOW FOREIGN TEXT BUT STRIP ILLEGAL CHARS
                    # This preserves: Chinese, Japanese, ( ), [ ]
                    nm = clean_filename(f.filename.rsplit('.', 1)[0])
                    if not nm: e+=1; continue
                    
                    if len(nm) > 150: nm = nm[:150] # DB Safety

                    txt = f.read().decode('utf-8')
                    if "DELAY" not in txt and "Keyboard" not in txt: e+=1; continue
                    
                    if sb.table("HeartopiaMIDI_CommunitySongs").select("id").eq("song_name", nm).execute().data: d+=1; continue
                    
                    sb.table("HeartopiaMIDI_CommunitySongs").insert({"song_name": nm, "song_data": txt, "instrument_type": "15-Keys" if "15K" in nm else "22-Keys"}).execute()
                    u += 1
                except: e += 1
        except: e = len(files)
        return jsonify({'uploaded': u, 'duplicates': d, 'errors': e})

    # --- ASSIST MODULE ENDPOINTS ---
    try:
        from .assist import assist_state, connect_to_window, disconnect, get_windows, perform_build_glitch
        assist_available = True
    except Exception as ex:
        print(f"Assist module failed to load: {ex}")
        assist_available = False
        assist_state = None

    # Assist status/log emitter (pushes live logs every 0.1s, status every 0.5s)
    def assist_status_broadcaster():
        tick = 0
        while True:
            socketio.sleep(0.1)
            tick += 1
            try:
                if assist_available and assist_state:
                    while assist_state.logs:
                        log_msg = assist_state.logs.pop(0)
                        socketio.emit('assist_log', {'message': log_msg})
                    if tick >= 5:
                        tick = 0
                        socketio.emit('assist_status', {
                            'connected': assist_state.connected,
                            'window': assist_state.window_name,
                            'walk': assist_state.walk_active,
                            'cam': assist_state.cam_active,
                            'cook': assist_state.cook_active,
                            'snow': assist_state.snow_active,
                            'harvest': assist_state.harvest_active,
                            'jump': assist_state.jump_active
                        })
            except:
                pass
    threading.Thread(target=assist_status_broadcaster, daemon=True).start()



    @app.route('/api/assist/windows')
    def assist_windows():
        if not assist_available:
            return jsonify({'windows': []})
        try:
            return jsonify({'windows': get_windows()})
        except:
            return jsonify({'windows': []})

    @app.route('/api/assist/status')
    def assist_status():
        if not assist_available or not assist_state:
            return jsonify({'available': False})
        return jsonify({
            'available': True,
            'connected': assist_state.connected,
            'window': assist_state.window_name,
            'walk': assist_state.walk_active,
            'cam': assist_state.cam_active,
            'cook': assist_state.cook_active,
            'snow': assist_state.snow_active,
            'harvest': assist_state.harvest_active,
            'jump': assist_state.jump_active
        })

    @app.route('/api/assist/connect', methods=['POST'])
    def assist_connect():
        if not assist_available or not assist_state:
            return jsonify({'ok': False, 'error': 'Assist module not available'})
        win = request.json.get('window', 'Heartopia')
        if connect_to_window(win):
            return jsonify({'ok': True})
        return jsonify({'ok': False, 'error': 'Window not found'})

    @app.route('/api/assist/disconnect', methods=['POST'])
    def assist_disconnect():
        if not assist_available or not assist_state:
            return jsonify({'ok': False})
        disconnect()
        return jsonify({'ok': True})

    @app.route('/api/assist/toggle', methods=['POST'])
    def assist_toggle():
        if not assist_available or not assist_state:
            return jsonify({'ok': False})
        f = request.json.get('feature')
        v = request.json.get('value', False)
        if f == 'walk':
            assist_state.walk_active = v
        elif f == 'cam':
            assist_state.cam_active = v
        elif f == 'cook':
            assist_state.cook_active = v
        elif f == 'snow':
            assist_state.snow_active = v
        elif f == 'harvest':
            assist_state.harvest_active = v
        elif f == 'jump':
            assist_state.jump_active = v
        return jsonify({'ok': True})


    @app.route('/api/assist/settings', methods=['GET', 'POST'])
    def assist_settings():
        if not assist_available or not assist_state:
            return jsonify({'ok': False})
            
        if request.method == 'GET':
            mouse_btn_str = 'Right' if assist_state.mouse_btn == 2 else 'Left'
            return jsonify({
                'confidence': assist_state.confidence,
                'use_grayscale': assist_state.use_grayscale,
                'img_stove': assist_state.img_stove,
                'img_start': assist_state.img_start,
                'img_heat': assist_state.img_heat,
                'img_serve': assist_state.img_serve,
                'img_recipe': assist_state.img_recipe,
                'img_snow_add': assist_state.img_snow_add,
                'img_snow_start': assist_state.img_snow_start,
                'img_snow_puzzle': assist_state.img_snow_puzzle,
                'img_snow_get': assist_state.img_snow_get,
                'img_build_eye': assist_state.img_build_eye,
                'img_build_check': assist_state.img_build_check,
                'walk_hotkey': assist_state.walk_hotkey,
                'cam_hotkey': assist_state.cam_hotkey,
                'cook_hotkey': assist_state.cook_hotkey,
                'snow_hotkey': assist_state.snow_hotkey,
                'build_hotkey': assist_state.build_hotkey,
                'harvest_hotkey': assist_state.harvest_hotkey,
                'jump_hotkey': assist_state.jump_hotkey,
                'mouse_btn': mouse_btn_str,
                'harvest_vk': assist_state.harvest_vk,
                'harvest_mode': assist_state.harvest_mode,
                'harvest_duration': assist_state.harvest_duration,
                'harvest_spam_interval': assist_state.harvest_spam_interval
            })
            
        try:
            d = request.get_json(silent=True) or {}
            if 'confidence' in d:
                assist_state.confidence = float(d['confidence'])
            if 'use_grayscale' in d:
                assist_state.use_grayscale = bool(d['use_grayscale'])
            if 'img_stove' in d:
                assist_state.img_stove = d['img_stove']
            if 'img_start' in d:
                assist_state.img_start = d['img_start']
            if 'img_heat' in d:
                assist_state.img_heat = d['img_heat']
            if 'img_serve' in d:
                assist_state.img_serve = d['img_serve']
            if 'img_recipe' in d:
                assist_state.img_recipe = d['img_recipe']
            if 'img_snow_add' in d:
                assist_state.img_snow_add = d['img_snow_add']
            if 'img_snow_start' in d:
                assist_state.img_snow_start = d['img_snow_start']
            if 'img_snow_puzzle' in d:
                assist_state.img_snow_puzzle = d['img_snow_puzzle']
            if 'img_snow_get' in d:
                assist_state.img_snow_get = d['img_snow_get']
            if 'img_build_eye' in d:
                assist_state.img_build_eye = d['img_build_eye']
            if 'img_build_check' in d:
                assist_state.img_build_check = d['img_build_check']
            if 'walk_hotkey' in d:
                assist_state.walk_hotkey = int(d['walk_hotkey'])
            if 'cam_hotkey' in d:
                assist_state.cam_hotkey = int(d['cam_hotkey'])
            if 'cook_hotkey' in d:
                assist_state.cook_hotkey = int(d['cook_hotkey'])
            if 'snow_hotkey' in d:
                assist_state.snow_hotkey = int(d['snow_hotkey'])
            if 'build_hotkey' in d:
                assist_state.build_hotkey = int(d['build_hotkey'])
            if 'harvest_hotkey' in d:
                assist_state.harvest_hotkey = int(d['harvest_hotkey'])
            if 'jump_hotkey' in d:
                assist_state.jump_hotkey = int(d['jump_hotkey'])
            if 'harvest_vk' in d:
                assist_state.harvest_vk = int(d['harvest_vk'])
            if 'harvest_mode' in d:
                assist_state.harvest_mode = d['harvest_mode']
            if 'harvest_duration' in d:
                assist_state.harvest_duration = float(d['harvest_duration'])
            if 'harvest_spam_interval' in d:
                assist_state.harvest_spam_interval = float(d['harvest_spam_interval'])
            if 'mouse_btn' in d:
                assist_state.mouse_btn = 2 if d['mouse_btn'] == 'Right' else 1
                
            assist_state.save_config()
            return jsonify({'ok': True})
        except Exception as e:
            print(f"Assist Settings Error: {e}")
            return jsonify({'ok': False})


    @app.route('/api/assist/browse_image', methods=['POST'])
    def assist_browse_image():
        path = open_dialog_direct(mode='file', filetypes=[('Image Files', '*.png *.jpg *.jpeg')])
        if path:
            return jsonify({'path': path})
        return jsonify({'path': None})

    # ── BUILD GLITCH ROUTES ──────────────────────────────────────────────
    @app.route('/api/assist/build/trigger', methods=['POST'])
    def assist_build_trigger():
        if not assist_available or not assist_state:
            return jsonify({'ok': False, 'error': 'Assist module not available'})
        threading.Thread(target=perform_build_glitch, daemon=True).start()
        return jsonify({'ok': True})
