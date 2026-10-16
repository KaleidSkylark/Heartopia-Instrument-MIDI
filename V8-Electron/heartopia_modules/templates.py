# --- 1. MINIFIED STYLES (CSS) ---
_CSS = r"""
:root { --bg:#f0f2f5; --sidebar-bg:#ffffff; --surface:#ffffff; --primary:#00b4d8; --primary-hover:#0077b6; --text:#1a1a24; --text-light:#6c757d; --border:#dee2e6; --tag-22k:#ff477e; --tag-15k:#9d4edd; --shadow:0 4px 15px rgba(0,0,0,0.05); --neon-glow:0 4px 12px rgba(0, 180, 216, 0.3); --sidebar-width:260px; --modal-bg:rgba(255,255,255,0.9); --card-hover:#f8f9fa; --console-bg:rgba(0,0,0,0.03); }
body.dark-theme { --bg:#000000; --sidebar-bg:#050505; --surface:#080808; --primary:#ff007f; --primary-hover:#ff3399; --text:#ffffff; --text-light:#b3b3cc; --border:#2d0a1b; --tag-22k:#00e5ff; --tag-15k:#b026ff; --shadow:0 8px 30px rgba(0,0,0,0.9); --neon-glow:0 0 12px rgba(255,0,127,0.5), inset 0 0 5px rgba(255,0,127,0.2); --modal-bg:rgba(0,0,0,0.9); --card-hover:#0f0f0f; --console-bg:rgba(0,0,0,0.6); }
*, *::before, *::after { box-sizing: border-box; }
body { background-color:var(--bg); color:var(--text); font-family:'Nunito',sans-serif; margin:0; display:flex; height:100vh; overflow:hidden; letter-spacing:0.5px; -webkit-font-smoothing:antialiased; }
body, .sidebar, .content, .player-panel, .modern-card, .info-card, .editor-pane, .editor-header, .editor-toolbar, .editor-footer, .console-log, .song-list, .queue-list, .upload-zone { transition: background-color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease; }
.sidebar { width:var(--sidebar-width); background:var(--sidebar-bg); padding:20px; display:flex; flex-direction:column; border-right:1px solid var(--border); box-shadow:2px 0 20px rgba(0,0,0,0.05); z-index:100; height:100vh; flex-shrink:0; }
.dark-theme .sidebar { box-shadow:2px 0 20px rgba(0,0,0,0.8); }
.sidebar-header { flex-shrink:0; margin-bottom:20px; text-align:center; }
.sidebar-nav { flex:1; overflow-y:auto; display:flex; flex-direction:column; gap:8px; padding-right:5px; min-height:0; }
.sidebar-footer { flex-shrink:0; margin-top:10px; display:flex; flex-direction:column; gap:10px; }
.content { flex:1; padding:25px; overflow-y:auto; display:flex; flex-direction:column; position:relative; scroll-behavior:smooth; min-width:0; }
h2 { color:var(--primary); margin:0; font-size:1.8em; font-weight:800; letter-spacing:1px; line-height:1.2; text-shadow:0 0 10px rgba(0,180,216,0.2); text-transform:uppercase; }
.dark-theme h2 { text-shadow:0 0 10px var(--primary); }
h3 { color:var(--text); font-weight:800; margin:0 0 15px 0; font-size:1.1em; text-transform:uppercase; letter-spacing:1.5px; text-shadow:0 0 5px rgba(255,255,255,0.3); }
button, .btn { background:var(--surface); color:var(--text); border:1px solid var(--border); padding:10px 18px; border-radius:6px; cursor:pointer; font-weight:800; font-family:inherit; font-size:0.85em; text-transform:uppercase; letter-spacing:1px; transition:all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1); will-change:transform, box-shadow, border-color; transform:translateZ(0); user-select:none; }
button:active { transform:scale(0.95) translateZ(0); }
button:hover { border-color:var(--primary); color:var(--primary); box-shadow:var(--neon-glow); transform:translateY(-2px) translateZ(0); text-shadow:0 0 5px rgba(0,180,216,0.3); }
.dark-theme button:hover { text-shadow:0 0 5px var(--primary); }
button.primary { background:var(--primary); color:#fff; border:1px solid var(--primary); box-shadow:var(--neon-glow); }
button.primary:hover { background:var(--primary-hover); border-color:var(--primary-hover); color:#fff; box-shadow:0 0 20px rgba(0,180,216,0.5); text-shadow:none; }
.dark-theme button.primary { background:transparent; color:var(--primary); border:2px solid var(--primary); }
.dark-theme button.primary:hover { background:var(--primary); border-color:var(--primary-hover); color:#000; box-shadow:0 0 20px var(--primary); }
button.danger { background:transparent; color:#ff3333; border:1px solid #ffcccc; }
.dark-theme button.danger { border-color:#660000; }
button.danger:hover { background:#ff3333; color:#fff; box-shadow:0 0 15px #ff3333; border-color:#ff3333; text-shadow:none; }
.dark-theme button.danger:hover { color:#000; }
button.audio-btn { background:rgba(0,180,216,0.05); color:var(--primary); border-color:var(--primary); width:100%; margin-top:10px; padding:12px; font-size:1em; border-width:2px; box-shadow:var(--neon-glow); }
.dark-theme button.audio-btn { background:rgba(255,0,127,0.05); }
button.audio-btn.playing { background:var(--primary); color:#fff; animation:neon-pulse 1.5s infinite; font-weight:800; text-shadow:none; }
.dark-theme button.audio-btn.playing { color:#000; }
@keyframes neon-pulse { 0% { box-shadow:0 0 10px var(--primary); } 50% { box-shadow:0 0 30px var(--primary), inset 0 0 10px rgba(255,255,255,0.3); } 100% { box-shadow:0 0 10px var(--primary); } }
input[type="text"], input[type="number"], select { background:var(--surface); border:1px solid var(--border); color:var(--text); padding:12px; border-radius:6px; width:100%; outline:none; font-weight:600; font-family:inherit; transition:all 0.2s ease; }
input[type="text"]:focus { border-color:var(--primary); box-shadow:var(--neon-glow); }
.tab-btn { text-align:left; padding:12px 16px; background:transparent; border:none; border-radius:6px; color:var(--text-light); font-size:0.95em; display:flex; align-items:center; gap:12px; font-weight:700; width:100%; }
.tab-btn:hover { background:var(--card-hover); color:var(--primary); transform:translateX(5px) translateZ(0); text-shadow:0 0 5px rgba(0,180,216,0.2); box-shadow:none; border-color:transparent;}
.dark-theme .tab-btn:hover { text-shadow:0 0 5px var(--primary); }
.tab-btn.active { background:var(--card-hover); color:var(--primary); box-shadow:inset 4px 0 0 var(--primary); text-shadow:0 0 5px rgba(0,180,216,0.2); border-color:transparent;}
.dark-theme .tab-btn.active { text-shadow:0 0 5px var(--primary); }
.tab-content { display:none; height:100%; flex-direction:column; }
.tab-content.active { display:flex; animation:fadeUp 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); height:100%; }
@keyframes fadeUp { from { opacity:0; transform:translateY(15px) translateZ(0); } to { opacity:1; transform:translateY(0) translateZ(0); } }
.playlist-grid { display:grid; grid-template-columns:1.5fr 1fr; gap:25px; height:100%; overflow:hidden; }
.playlist-column { display:flex; flex-direction:column; height:100%; overflow:hidden; min-width:0; }
.song-list { flex:1; overflow-y:auto; border:1px solid var(--border); border-radius:8px; margin-top:10px; background:var(--console-bg); padding:8px; -webkit-overflow-scrolling:touch; box-shadow:inset 0 0 10px rgba(0,0,0,0.05); }
.dark-theme .song-list { box-shadow:inset 0 0 20px rgba(0,0,0,0.5); }
.song-row { display:flex; justify-content:space-between; padding:10px 12px; margin:4px 0; border-radius:6px; align-items:center; border:1px solid transparent; cursor:pointer; background:var(--surface); transition:all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1); will-change:transform; transform:translateZ(0); box-shadow:0 2px 5px rgba(0,0,0,0.02); }
.song-row:hover { background:var(--card-hover); border-color:var(--border); transform:translateX(4px) translateZ(0); }
.song-row.active { background:var(--card-hover); border-color:var(--primary); box-shadow:var(--neon-glow); transform:translateX(4px) translateZ(0); }
.song-tag { font-size:0.65em; padding:4px 8px; border-radius:4px; margin-right:12px; font-weight:800; text-transform:uppercase; letter-spacing:1px; flex-shrink:0; border:1px solid transparent; }
.tag-22k { background:rgba(0,180,216,0.1); color:var(--tag-22k); border-color:var(--tag-22k); text-shadow:0 0 5px rgba(255,71,126,0.3); box-shadow:0 0 5px rgba(0,180,216,0.1); }
.tag-15k { background:rgba(157,78,221,0.1); color:var(--tag-15k); border-color:var(--tag-15k); text-shadow:0 0 5px rgba(157,78,221,0.3); box-shadow:0 0 5px rgba(157,78,221,0.1); }
.dark-theme .tag-22k { background:rgba(0,229,255,0.1); color:var(--tag-22k); text-shadow:0 0 5px var(--tag-22k); box-shadow:0 0 5px rgba(0,229,255,0.2); }
.dark-theme .tag-15k { background:rgba(176,38,255,0.1); color:var(--tag-15k); text-shadow:0 0 5px var(--tag-15k); box-shadow:0 0 5px rgba(176,38,255,0.2); }
.song-name-text { font-weight:700; color:var(--text); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; display:block; max-width:100%; }
.queue-list { flex:1; overflow-y:auto; border:1px solid var(--border); border-radius:8px; background:var(--console-bg); padding:8px; margin-top:15px; -webkit-overflow-scrolling:touch; box-shadow:inset 0 0 10px rgba(0,0,0,0.05); }
.dark-theme .queue-list { box-shadow:inset 0 0 20px rgba(0,0,0,0.5); }
.queue-item { display:flex; justify-content:space-between; align-items:center; padding:10px 12px; margin:4px 0; background:var(--surface); border-radius:6px; font-size:0.9em; font-weight:700; border:1px solid transparent; transition:all 0.2s ease; box-shadow:0 2px 5px rgba(0,0,0,0.02); }
.queue-item:hover { border-color:var(--border); transform:translateX(4px) translateZ(0); }
.player-panel { background:var(--surface); padding:25px; border-radius:12px; border:1px solid var(--border); box-shadow:var(--shadow); flex-shrink:0; position:relative; overflow:hidden; }
.player-panel::before { content:''; position:absolute; top:0; left:0; right:0; height:2px; background:var(--primary); box-shadow:0 0 15px rgba(0,180,216,0.5); }
.dark-theme .player-panel::before { box-shadow:0 0 15px var(--primary); }
.now-playing { font-size:1.1em; font-weight:800; color:var(--primary); margin-bottom:15px; display:flex; align-items:center; gap:10px; flex-wrap:wrap; text-shadow:0 0 5px rgba(0,180,216,0.2); }
.dark-theme .now-playing { text-shadow:0 0 5px var(--primary); }
.now-playing-icon { font-size:1.5em; animation:pulse-icon 2s infinite; }
@keyframes pulse-icon { 0% { transform:scale(1); text-shadow:0 0 10px var(--primary); } 50% { transform:scale(1.2); text-shadow:0 0 20px var(--primary); } 100% { transform:scale(1); text-shadow:0 0 10px var(--primary); } }
.controls-grid { display:grid; grid-template-columns:repeat(3, 1fr); gap:15px; margin-bottom:0; }
.control-group label { display:block; font-size:0.75em; color:var(--text-light); font-weight:800; text-transform:uppercase; margin-bottom:8px; letter-spacing:1px; }
.progress-container { height:6px; background:var(--border); margin-bottom:15px; border-radius:3px; overflow:hidden; box-shadow:inset 0 0 5px rgba(0,0,0,0.1); }
.dark-theme .progress-container { box-shadow:inset 0 0 5px rgba(0,0,0,0.8); }
.progress-bar { height:100%; background:var(--primary); width:0%; transition:width 0.1s linear; border-radius:3px; box-shadow:0 0 10px rgba(0,180,216,0.5); }
.dark-theme .progress-bar { box-shadow:0 0 10px var(--primary); }
.custom-checkbox { position:relative; display:inline-block; width:36px; height:20px; }
.custom-checkbox input { opacity:0; width:0; height:0; }
.slider { position:absolute; cursor:pointer; top:0; left:0; right:0; bottom:0; background-color:var(--border); transition:.3s; border-radius:20px; border:1px solid rgba(0,0,0,0.1); }
.slider:before { position:absolute; content:""; height:12px; width:12px; left:3px; bottom:3px; background-color:#fff; transition:.3s cubic-bezier(0.25, 0.8, 0.25, 1); border-radius:50%; box-shadow:0 1px 3px rgba(0,0,0,0.2); }
input:checked + .slider { background-color:rgba(0,180,216,0.2); border-color:var(--primary); box-shadow:var(--neon-glow); }
.dark-theme input:checked + .slider { background-color:rgba(255,0,127,0.2); border-color:var(--primary); }
input:checked + .slider:before { transform:translateX(16px); background-color:var(--primary); box-shadow:0 0 10px rgba(0,180,216,0.5); }
.dark-theme input:checked + .slider:before { box-shadow:0 0 10px var(--primary); }
input[type=range] { -webkit-appearance:none; background:transparent; width:100%; }
input[type=range]::-webkit-slider-thumb { -webkit-appearance:none; height:16px; width:16px; border-radius:50%; background:var(--primary); cursor:pointer; margin-top:-6px; box-shadow:0 0 10px rgba(0,180,216,0.3); border:2px solid #fff; transition:transform 0.1s cubic-bezier(0.25, 0.8, 0.25, 1); }
.dark-theme input[type=range]::-webkit-slider-thumb { box-shadow:0 0 10px var(--primary); border:2px solid #000; }
input[type=range]::-webkit-slider-thumb:hover { transform:scale(1.3); box-shadow:0 0 15px var(--primary); }
input[type=range]::-webkit-slider-runnable-track { width:100%; height:4px; cursor:pointer; background:var(--border); border-radius:2px; box-shadow:inset 0 0 2px rgba(0,0,0,0.1); }
.modern-card { background:var(--surface); border-radius:12px; padding:30px; box-shadow:var(--shadow); border:1px solid var(--border); height:100%; display:flex; flex-direction:column; overflow:hidden; position:relative; }
.modern-card::before { content:''; position:absolute; top:0; left:0; right:0; height:2px; background:var(--border); transition:background 0.3s, box-shadow 0.3s; }
.modern-card:hover::before { background:var(--primary); box-shadow:0 0 15px rgba(0,180,216,0.5); }
.dark-theme .modern-card:hover::before { box-shadow:0 0 15px var(--primary); }
.upload-zone { border:2px dashed var(--border); border-radius:12px; padding:30px; text-align:center; background:var(--console-bg); cursor:pointer; color:var(--text-light); display:flex; flex-direction:column; justify-content:center; align-items:center; height:100%; width:100%; }
.upload-zone:hover { border-color:var(--primary); background:rgba(0,180,216,0.05); color:var(--primary); box-shadow:inset 0 0 20px rgba(0,180,216,0.1); transform:scale(1.02) translateZ(0); text-shadow:0 0 5px rgba(0,180,216,0.2); }
.dark-theme .upload-zone:hover { background:rgba(255,0,127,0.05); box-shadow:inset 0 0 20px rgba(255,0,127,0.1); text-shadow:0 0 10px var(--primary); }
.filter-group { display:flex; gap:5px; background:var(--console-bg); padding:4px; border-radius:8px; border:1px solid var(--border); width:fit-content; overflow-x:auto; }
.filter-btn { border:none; background:transparent; color:var(--text-light); padding:6px 14px; border-radius:6px; font-size:0.8em; font-weight:800; white-space:nowrap; box-shadow:none; border:1px solid transparent; }
.filter-btn:hover { background:var(--card-hover); color:var(--text); border-color:var(--border); transform:none; }
.filter-btn.active { background:rgba(0,180,216,0.1); color:var(--primary); border-color:var(--primary); box-shadow:var(--neon-glow); text-shadow:0 0 5px rgba(0,180,216,0.2); }
.dark-theme .filter-btn.active { background:rgba(255,0,127,0.1); text-shadow:0 0 5px var(--primary); }
.info-grid { display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:25px; margin-top:20px; }
.info-card { background:var(--surface); padding:30px; border-radius:12px; border:1px solid var(--border); box-shadow:var(--shadow); }
.info-card:hover { transform:translateY(-5px) translateZ(0); border-color:var(--primary); box-shadow:0 15px 30px rgba(0,0,0,0.1), var(--neon-glow); }
.dark-theme .info-card:hover { box-shadow:0 15px 30px rgba(0,0,0,0.9), var(--neon-glow); }
::-webkit-scrollbar { width:6px; height:6px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:#a0aec0; border-radius:3px; }
.dark-theme ::-webkit-scrollbar-thumb { background:#2a2a35; }
::-webkit-scrollbar-thumb:hover { background:var(--primary); box-shadow:var(--neon-glow); }
.flex-row { display:flex; gap:10px; align-items:center; flex-wrap:wrap; }
.section-header { border-bottom:1px solid var(--border); padding-bottom:10px; margin-bottom:20px; font-size:1.1em; color:var(--primary); font-weight:800; display:flex; align-items:center; gap:10px; text-transform:uppercase; letter-spacing:2px; text-shadow:0 0 5px rgba(0,180,216,0.2); }
.dark-theme .section-header { text-shadow:0 0 5px var(--primary); }
.badge-count { background:transparent; color:var(--primary); border:1px solid var(--primary); padding:2px 8px; border-radius:4px; font-size:0.75em; box-shadow:var(--neon-glow); text-shadow:0 0 5px rgba(0,180,216,0.3); }
.dark-theme .badge-count { text-shadow:0 0 5px var(--primary); }
.full-height-grid { display:grid; grid-template-columns:1fr 1.2fr; gap:30px; height:100%; overflow:hidden; }
.console-log { background:var(--console-bg); border:1px solid var(--border); padding:10px; font-family:'Consolas', monospace; font-size:0.75em; flex: 1; min-height: 100px; overflow-y:auto; display:flex; flex-direction:column; gap:6px; border-radius:8px; margin-bottom:5px; box-shadow:inset 0 0 10px rgba(0,0,0,0.05); }
.dark-theme .console-log { box-shadow:inset 0 0 15px rgba(0,0,0,0.8); }
.log-entry { background:var(--surface); border:1px solid var(--border); border-left-width:3px; border-radius:4px; padding:8px; animation:slideIn 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); display:flex; flex-direction:column; box-shadow:0 2px 4px rgba(0,0,0,0.02); }
.log-entry.info { border-left-color:var(--primary); }
.log-entry.success { border-left-color:#00e676; }
.log-entry.error { border-left-color:#ff1744; }
.log-header { display:flex; justify-content:space-between; font-size:0.85em; font-weight:800; opacity:0.8; margin-bottom:4px; text-transform:uppercase; letter-spacing:1px; }
.log-body { font-weight:600; color:var(--text); line-height:1.4; }
.pagination-container { display:flex; justify-content:center; align-items:center; gap:15px; margin-top:10px; padding:15px; background:var(--surface); border:1px solid var(--border); border-radius:8px; flex-wrap:wrap; box-shadow:var(--shadow); }
.page-btn { background:transparent; border:1px solid var(--border); color:var(--text-light); padding:8px 16px; border-radius:6px; font-weight:800; font-family:inherit; text-transform:uppercase; letter-spacing:1px; }
.page-btn:hover { border-color:var(--primary); color:var(--primary); box-shadow:var(--neon-glow); text-shadow:0 0 5px rgba(0,180,216,0.3); }
.dark-theme .page-btn:hover { text-shadow:0 0 5px var(--primary); }
.per-page-select { background:var(--console-bg); border:1px solid var(--border); padding:8px 12px; border-radius:6px; color:var(--text); font-weight:700; font-size:0.85em; cursor:pointer; }
.per-page-select:hover { border-color:var(--primary); box-shadow:var(--neon-glow); }
.piano-canvas { width:100%; height:220px; background:#fafafa; border-radius:8px; margin-bottom:10px; box-shadow:inset 0 0 10px rgba(0,0,0,0.1); display:block; border:1px solid var(--border); border-bottom:2px solid var(--primary); }
.dark-theme .piano-canvas { background:#000; box-shadow:inset 0 0 20px rgba(0,0,0,0.8); }
.editor-container { display:grid; grid-template-columns:1.2fr 1fr; gap:20px; height:100%; overflow:hidden; }
.editor-pane { display:flex; flex-direction:column; height:100%; overflow:hidden; background:var(--surface); border:1px solid var(--border); border-radius:12px; box-shadow:var(--shadow); position:relative; }
.editor-header { padding:10px 15px; background:var(--console-bg); border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center; font-weight:800; color:var(--primary); height:50px; text-shadow:0 0 5px rgba(0,180,216,0.2); text-transform:uppercase; letter-spacing:1px; }
.dark-theme .editor-header { text-shadow:0 0 5px var(--primary); }
.editor-main { flex:1; position:relative; overflow:hidden; width:100%; height:100%; background:#fff; }
.dark-theme .editor-main { background:#000; }
#monaco-container { position:absolute; top:0; left:0; width:100%; height:100%; }
.monaco-highlight-line { background-color:rgba(0,180,216,0.15) !important; box-shadow:inset 4px 0 0 0 var(--primary) !important; }
.dark-theme .monaco-highlight-line { background-color:rgba(255,0,127,0.15) !important; }
.editor-toolbar { display:flex; gap:8px; padding:8px 15px; background:var(--console-bg); border-bottom:1px solid var(--border); align-items:center; overflow-x:auto; }
.tool-btn { padding:6px 10px; font-size:0.75em; border-radius:4px; background:transparent; border:1px solid var(--border); color:var(--text-light); font-weight:800; cursor:pointer; white-space:nowrap; text-transform:uppercase; letter-spacing:1px; }
.tool-btn:hover { background:rgba(0,180,216,0.1); color:var(--primary); border-color:var(--primary); box-shadow:var(--neon-glow); text-shadow:0 0 5px rgba(0,180,216,0.3); }
.dark-theme .tool-btn:hover { background:rgba(255,0,127,0.1); text-shadow:0 0 5px var(--primary); }
.editor-footer { padding:15px; background:var(--console-bg); border-top:1px solid var(--border); display:flex; flex-direction:column; gap:10px; z-index:3; }
.editor-seek-container { display:flex; align-items:center; gap:10px; font-size:0.8em; font-weight:800; color:var(--text-light); font-family:'Consolas', monospace; }
.editor-slider-track { flex:1; height:4px; background:var(--border); border-radius:2px; position:relative; cursor:pointer; box-shadow:inset 0 0 2px rgba(0,0,0,0.1); }
.editor-slider-fill { height:100%; background:var(--primary); border-radius:2px; width:0%; pointer-events:none; box-shadow:0 0 10px rgba(0,180,216,0.4); }
.dark-theme .editor-slider-fill { box-shadow:0 0 10px var(--primary); }
.editor-slider-input { position:absolute; top:-6px; left:0; width:100%; height:16px; opacity:0; cursor:pointer; margin:0; }
.editor-controls { display:flex; gap:10px; align-items:center; }
@keyframes slideIn { from { opacity:0; transform:translateY(10px) translateZ(0); } to { opacity:1; transform:translateY(0) translateZ(0); } }
@media (max-width: 1024px) {
    .playlist-grid { grid-template-columns:1fr; grid-template-rows:auto 1fr; }
    .playlist-column:nth-child(2) { order:-1; height:auto; flex-shrink:0; margin-bottom:20px; }
    .playlist-column:nth-child(1) { overflow-y:auto; }
    .full-height-grid { grid-template-columns:1fr; grid-template-rows:1fr auto; overflow-y:auto; display:flex; flex-direction:column; }
    .modern-card { height:auto; min-height:250px; }
    .controls-grid { gap:10px; }
    .editor-container { grid-template-columns: 1fr; grid-template-rows: 1fr auto; }
}
"""

# --- 2. LOGIC (JS) ---
_JS = r"""
window.addEventListener('mouseup', (e) => { if (e.button === 3 || e.button === 4) e.preventDefault(); });
window.addEventListener('mousedown', (e) => { if (e.button === 3 || e.button === 4) e.preventDefault(); });
window.addEventListener('keydown', (e) => { if(/^F(?:[1-9]|1[0-2])$/.test(e.key)) { if(!isListening) { e.preventDefault(); } } });

let allSongs=[], favorites=[], queue=[], currentSong=null, currentSongSource='local', onlineLoaded=false, searchTimeout=null, currentPlaylistFilter='All', currentOnlineFilter='All', tempHotkeys={play:'F4',stop:'F5'}, isListening=null, confirmCallback=null;
let cachedSongData = null;
let monacoEditor = null;
let decorations = [];

const socket = io();
socket.on('status_update', (data) => {
    const st = document.getElementById('player-status');
    const btn = document.getElementById('btn-play');
    const bar = document.getElementById('progress-bar');
    if(data.is_playing && !data.is_paused) { st.innerText="(Playing)"; st.style.color="#00c853"; btn.innerText="PAUSE"; btn.className="primary"; btn.style.background="#c2185b"; btn.style.borderColor="#c2185b"; } 
    else if(data.is_paused) { st.innerText="(Paused)"; st.style.color="#ffa000"; btn.innerText="RESUME"; btn.className="primary"; btn.style.background=""; btn.style.borderColor="";} 
    else { st.innerText="(Stopped)"; st.style.color="var(--text-light)"; btn.innerText="START"; btn.className="primary"; btn.style.background=""; btn.style.borderColor=""; }
    if(bar) bar.style.width = (data.progress * 100) + '%';
    if(data.current_song && data.current_song !== "None" && data.current_song !== currentSong && currentSongSource === 'local') { currentSong = data.current_song; updatePlayerUI(currentSong); renderPlaylist(); }
});

function onMainSpeedChange(val) { updateParam('speed', val); if(isPreviewing && cachedSongData) { stopAudioPreview(); startAudioEngine(cachedSongData, currentSong.includes('_15K'), 'canvas-player', 'slider-speed', false); } }
let currentPage = 1, totalItems = 0, itemsPerPage = 50;
let audioCtx=null, isPreviewing=false, schedulerInterval=null, visualizerFrame=null;
let masterGain=null, compressorNode=null;
let audioEvents=[]; let nextEventIndex=0; let nextEventTime=0;
let isEditorPreviewing = false, currentEditorFile = null, isPaused = false, editorTotalDuration = 0, editorStartTime = 0, isSeeking = false, selectedNote = null, gridCanvas = null; 
const MAP_22_REV = {{ REVERSE_MAP_22 | tojson }};
const MAP_15_REV = {{ REVERSE_MAP_15 | tojson }};

function safeArgs(str) { return str ? "'" + str.replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/"/g, '\\"') + "'" : "''"; }
function showModal(title, message) { document.getElementById('modal-title').innerText = title; document.getElementById('modal-body').innerText = message; document.getElementById('custom-modal').style.display = 'flex'; }
function showConfirm(title, message, callback) { document.getElementById('confirm-title').innerText = title; document.getElementById('confirm-body').innerText = message; document.getElementById('custom-confirm').style.display = 'flex'; confirmCallback = callback; }
function confirmYes() { document.getElementById('custom-confirm').style.display = 'none'; if(confirmCallback) confirmCallback(); }
function confirmNo() { document.getElementById('custom-confirm').style.display = 'none'; confirmCallback = null; }
function showExitModal() { document.getElementById('exit-modal').style.display = 'flex'; }
async function finalizeExit() { try { window.close(); } catch(e) {} document.body.innerHTML = "<div style='display:flex;justify-content:center;align-items:center;height:100vh;flex-direction:column;font-family:sans-serif;color:#880e4f;background:#fff0f6;'><h1>Application Closed</h1><p>You can close this tab now.</p></div>"; fetch('/api/terminate', { method:'POST' }); }

function initMonaco() {
    if(monacoEditor) return;
    require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.44.0/min/vs' }});
    require(['vs/editor/editor.main'], function() {
        monacoEditor = monaco.editor.create(document.getElementById('monaco-container'), { value: "", language: 'plaintext', theme: document.body.classList.contains('dark-theme') ? 'vs-dark' : 'vs-light', automaticLayout: true, minimap: { enabled: false }, scrollBeyondLastLine: false, fontSize: 14, fontFamily: "'Consolas', 'Monaco', monospace" });
        monacoEditor.onDidChangeModelContent(() => { document.getElementById('editor-status-line').innerText = `Total Lines: ${monacoEditor.getModel().getLineCount()}`; });
    });
}
async function toggleTheme() {
    document.body.classList.toggle('dark-theme');
    const isDark = document.body.classList.contains('dark-theme');
    updateThemeBtn(isDark); redrawCanvas('canvas-player'); redrawCanvas('canvas-editor'); gridCanvas = null; 
    if (monacoEditor) { monaco.editor.setTheme(isDark ? 'vs-dark' : 'vs-light'); }
    try { await fetch('/api/settings/save_theme', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ theme: isDark ? 'dark' : 'light' }) }); } catch(e) {}
}
function redrawCanvas(id) { const c = document.getElementById(id); if(c) { const ctx = c.getContext('2d'); ctx.fillStyle = document.body.classList.contains('dark-theme') ? '#000' : '#fafafa'; ctx.fillRect(0,0,c.width,c.height); } }
function updateThemeBtn(isDark) { document.getElementById('btn-theme').innerHTML = isDark ? '<span>☀</span> Light Mode' : '<span>🌙</span> Dark Mode'; }

function appLog(msg, type='info') {
    const c = document.getElementById('app-console'); if(!c) return;
    const m = msg.toLowerCase();
    if(m.includes('error')||m.includes('fail')) type='error'; else if(m.includes('success')||m.includes('complete')||m.includes('loaded')||m.includes('saved')) type='success';
    const div = document.createElement('div'); div.className = `log-entry ${type}`;
    let icon='ℹ'; if(type==='success') icon='✔'; if(type==='error') icon='✖'; if(m.includes('play')) icon='▶'; if(m.includes('stop')) icon='⏹'; if(m.includes('downl')) icon='⬇'; if(m.includes('upload')) icon='⬆';
    div.innerHTML = `<div class="log-header"><span style="color:inherit;">${icon} ${type}</span><span style="font-weight:400;">${new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit',second:'2-digit'})}</span></div><div class="log-body">${msg}</div>`;
    c.appendChild(div); c.scrollTop = c.scrollHeight; if(c.children.length > 50) c.removeChild(c.firstChild);
}
async function updateParam(key, value) { if(key==='speed') document.getElementById('val-speed').innerText = value; if(key==='snap') document.getElementById('val-snap').innerText = value; try { await fetch('/api/play_params', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({[key]:value})}); } catch(e){} }
function switchTab(id) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
    document.getElementById(id).classList.add('active'); document.getElementById('btn-'+id).classList.add('active');
    if(id==='online' && !onlineLoaded) searchOnline(); if(id==='settings') loadSettings();
    if(id !== 'editor' && isEditorPreviewing) stopEditorPreview();
    if(id !== 'playlist' && isPreviewing) stopAudioPreview();
    if(id === 'playlist') redrawCanvas('canvas-player');
    if(id === 'editor') { redrawCanvas('canvas-editor'); initMonaco(); }
}

async function openEditor(filename) {
    currentEditorFile = filename; document.getElementById('editor-filename').innerText = filename; switchTab('editor');
    try {
        const res = await fetch('/api/preview_content', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({filename:filename, source:'local'}) });
        const d = await res.json();
        if(d.ok) { if(monacoEditor) { monacoEditor.setValue(d.data); } else { setTimeout(() => { if(monacoEditor) monacoEditor.setValue(d.data); }, 1000); } } 
        else { if(monacoEditor) monacoEditor.setValue("Error loading file."); }
    } catch(e) { if(monacoEditor) monacoEditor.setValue("Error loading file."); }
}
function insertTemplate(type) {
    if (!monacoEditor) return;
    let txt = "";
    if(type === 'note') txt = "Keyboard : ? : KeyDown\n"; else if(type === 'release') txt = "Keyboard : ? : KeyUp\n"; else if(type === 'delay') txt = "DELAY : 200\n"; else if(type === 'chord') txt = "Keyboard : ? : KeyDown\nDELAY : 200\nKeyboard : ? : KeyUp\n";
    const position = monacoEditor.getPosition(); const op = { range: new monaco.Range(position.lineNumber, position.column, position.lineNumber, position.column), text: txt, forceMoveMarkers: true }; monacoEditor.executeEdits("my-source", [op]);
}
async function saveEditorContent() {
    if(!currentEditorFile) return showModal("Error", "No file open.");
    if(!monacoEditor) return;
    const content = monacoEditor.getValue();
    try { const res = await fetch('/api/save_content', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({filename: currentEditorFile, data: content}) });
        const d = await res.json(); if(d.ok) { appLog(`Saved ${currentEditorFile}`, 'success'); showModal("Success", "File saved successfully!"); loadPlaylistData(); } else { showModal("Error", "Could not save file."); }
    } catch(e) { showModal("Error", "Save failed."); }
}

function handleCanvasClick(e) {
    if(!audioEvents || audioEvents.length === 0) return;
    const cvs = document.getElementById('canvas-editor'); const rect = cvs.getBoundingClientRect();
    const scaleX = cvs.width / rect.width; const scaleY = cvs.height / rect.height;
    const x = (e.clientX - rect.left) * scaleX; const y = (e.clientY - rect.top) * scaleY;
    const w = cvs.width; const h = cvs.height;
    const laneCount = (visualNoteRange.max - visualNoteRange.min) + 1; const laneWidth = w / laneCount;
    const clickedLane = Math.floor(x / laneWidth); const clickedNote = visualNoteRange.min + clickedLane;
    const pixelsPerSecond = h / 2.5; const hitLineY = h - 10; 
    let currentTime = 0;
    if(audioCtx && !isPaused && isEditorPreviewing) { currentTime = (audioCtx.currentTime - visualStartTime) - 0.05; } else { currentTime = parseFloat(document.getElementById('editor-seek-slider').value) || 0; }
    selectedNote = null; 
    for(let i=0; i<audioEvents.length; i++) {
        const ev = audioEvents[i];
        if(ev.note !== clickedNote) continue;
        if (ev.time + ev.duration < currentTime - 0.5) continue; 
        if (ev.time > currentTime + 3.0) break; 
        const timeDiff = ev.time - currentTime; const drawY = hitLineY - (timeDiff * pixelsPerSecond); const height = ev.duration * pixelsPerSecond;
        if(y >= drawY - height - 5 && y <= drawY + 5) { selectedNote = ev; highlightEditorLine(ev.lineNum); if (monacoEditor) { monacoEditor.revealLineInCenter(ev.lineNum + 1); monacoEditor.setPosition({lineNumber: ev.lineNum + 1, column: 1}); } redrawCanvas('canvas-editor'); return; }
    }
}

function playEditor(offset = 0) {
    if(isEditorPreviewing && isPaused && offset === 0) { resumeEditor(); return; }
    if(isEditorPreviewing && offset === 0) return; 
    if(offset > 0 && isEditorPreviewing) stopEditorPreview();
    if (!monacoEditor) return;
    const content = monacoEditor.getValue(); const is15k = currentEditorFile ? currentEditorFile.includes('15K') : false; 
    startAudioEngine(content, is15k, 'canvas-editor', 'editor-speed', true, offset);
    document.getElementById('btn-editor-play').disabled = true; document.getElementById('btn-editor-pause').disabled = false; document.getElementById('btn-editor-stop').disabled = false; document.getElementById('btn-editor-play').classList.add('active');
    selectedNote = null; isPaused = false;
}
function pauseEditor() {
    if(!isEditorPreviewing || isPaused) return;
    if(audioCtx && audioCtx.state === 'running') { audioCtx.suspend(); isPaused = true; if(schedulerInterval) clearInterval(schedulerInterval); document.getElementById('btn-editor-play').disabled = false; document.getElementById('btn-editor-play').innerText = "▶"; document.getElementById('btn-editor-pause').disabled = true; document.getElementById('btn-editor-play').classList.remove('active'); }
}
function resumeEditor() {
    if(!isEditorPreviewing || !isPaused) return;
    if(audioCtx && audioCtx.state === 'suspended') { audioCtx.resume(); isPaused = false; selectedNote = null; if(window.schedulerInterval) clearInterval(window.schedulerInterval); window.schedulerInterval = setInterval(scheduler, 30); schedulerInterval = window.schedulerInterval; document.getElementById('btn-editor-play').disabled = true; document.getElementById('btn-editor-pause').disabled = false; document.getElementById('btn-editor-play').classList.add('active'); }
}
function stopEditorPreview() {
     stopAudioEngine(); isEditorPreviewing = false; isPaused = false; selectedNote = null; 
     document.getElementById('btn-editor-play').disabled = false; document.getElementById('btn-editor-play').innerText = "▶"; document.getElementById('btn-editor-play').classList.remove('active'); document.getElementById('btn-editor-pause').disabled = true; document.getElementById('btn-editor-stop').disabled = true;
     document.getElementById('editor-seek-slider').value = 0; document.getElementById('editor-seek-fill').style.width = '0%'; document.getElementById('editor-time-current').innerText = "0:00";
     if (monacoEditor) { decorations = monacoEditor.deltaDecorations(decorations, []); }
     redrawCanvas('canvas-editor');
}
function onEditorSeekInput() { isSeeking = true; pauseEditor(); const val = document.getElementById('editor-seek-slider').value; document.getElementById('editor-seek-fill').style.width = (val / editorTotalDuration * 100) + '%'; document.getElementById('editor-time-current').innerText = formatTime(val); }
function onEditorSeekChange() { const val = parseFloat(document.getElementById('editor-seek-slider').value); isSeeking = false; playEditor(val); }
function formatTime(s) { const min = Math.floor(s / 60); const sec = Math.floor(s % 60); return `${min}:${sec.toString().padStart(2, '0')}`; }

function startAudioEngine(text, is15k, canvasId, speedInputId, isEditor, startTimeOffset = 0) {
    if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if(audioCtx.state === 'suspended') audioCtx.resume();
    if(!masterGain) { compressorNode = audioCtx.createDynamicsCompressor(); compressorNode.threshold.setValueAtTime(-24, audioCtx.currentTime); compressorNode.knee.setValueAtTime(30, audioCtx.currentTime); compressorNode.ratio.setValueAtTime(12, audioCtx.currentTime); compressorNode.attack.setValueAtTime(0.003, audioCtx.currentTime); compressorNode.release.setValueAtTime(0.25, audioCtx.currentTime); masterGain = audioCtx.createGain(); masterGain.gain.value = 0.3; masterGain.connect(compressorNode); compressorNode.connect(audioCtx.destination); }
    if (isEditor) { isEditorPreviewing = true; } else { isPreviewing = true; const btn = document.getElementById('btn-audio-preview'); btn.innerText = "⏹ STOP PREVIEW"; btn.classList.add("playing"); }
    prepareAndStartAudio(text, is15k, canvasId, speedInputId, startTimeOffset); appLog(isEditor ? "Editor Preview Started" : "Audio Preview Started");
}
function stopAudioEngine() { if(schedulerInterval) clearInterval(schedulerInterval); if(visualizerFrame) cancelAnimationFrame(visualizerFrame); }

let visualStartTime = 0; let visualNoteRange = {min: 48, max: 84}; let currentCanvasId = 'canvas-player'; 
function parseEvents(text, is15k, speed) {
    const lines = text.split('\n'); const map = is15k ? MAP_15_REV : MAP_22_REV; let cursor = 0; let activeKeys = {}; let events = [];
    lines.forEach((l, idx) => {
        l = l.trim(); if(!l) return;
        if(l.includes('DELAY')) { const ms = parseInt(l.replace(/\D/g, '')); if(ms) cursor += (ms / 1000) / speed; } 
        else if(l.includes('Keyboard')) {
            const parts = l.split(':');
            if(parts.length >= 3) { const keyChar = parts[1].trim().toUpperCase(); const action = parts[2].trim(); const midi = map[keyChar];
                if(midi) { if(action === 'KeyDown') activeKeys[keyChar] = {start: cursor, lineNum: idx}; else if(action === 'KeyUp') { const startObj = activeKeys[keyChar]; if(startObj !== undefined) { let dur = cursor - startObj.start; if(dur < 0.1) dur = 0.1; events.push({ time: startObj.start, note: midi, duration: dur, is15k: is15k, lineNum: startObj.lineNum }); delete activeKeys[keyChar]; } } }
            }
        }
    });
    for(let k in activeKeys) { const startObj = activeKeys[k]; events.push({time: startObj.start, note: map[k] || 60, duration: 0.2, is15k: is15k, lineNum: startObj.lineNum}); }
    events.sort((a,b) => a.time - b.time); return {events: events, duration: cursor};
}
function prepareAndStartAudio(text, is15k, canvasId, speedInputId, startTimeOffset = 0) {
    currentCanvasId = canvasId; const speed = parseFloat(document.getElementById(speedInputId).value) || 1.0;
    const parsed = parseEvents(text, is15k, speed); audioEvents = parsed.events;
    if(canvasId === 'canvas-editor') { editorTotalDuration = parsed.duration; document.getElementById('editor-time-total').innerText = formatTime(editorTotalDuration); const slider = document.getElementById('editor-seek-slider'); slider.max = editorTotalDuration; slider.value = startTimeOffset; }
    if(is15k) visualNoteRange = {min: 60, max: 84}; else visualNoteRange = {min: 48, max: 84};
    nextEventIndex = 0; while(nextEventIndex < audioEvents.length && audioEvents[nextEventIndex].time < startTimeOffset) { nextEventIndex++; }
    nextEventTime = audioCtx.currentTime - startTimeOffset + 0.2; visualStartTime = nextEventTime; gridCanvas = null; 
    if(window.schedulerInterval) clearInterval(window.schedulerInterval); window.schedulerInterval = setInterval(scheduler, 30); schedulerInterval = window.schedulerInterval;
    if(visualizerFrame) cancelAnimationFrame(visualizerFrame); renderPianoRoll();
}
function scheduler() {
    if(!audioCtx) return; if(isPaused) return; 
    const lookAhead = 0.1; const now = audioCtx.currentTime; const startTime = nextEventTime; 
    while(nextEventIndex < audioEvents.length && (startTime + audioEvents[nextEventIndex].time) < now + lookAhead) { const ev = audioEvents[nextEventIndex]; if (startTime + ev.time > now - 0.05) { scheduleNote(ev.note, startTime + ev.time, ev.duration); } nextEventIndex++; }
    if(nextEventIndex >= audioEvents.length && now > startTime + audioEvents[audioEvents.length-1].time + 1.0) { if(isEditorPreviewing) stopEditorPreview(); if(isPreviewing) stopAudioPreview(); }
}
function highlightEditorLine(lineNum) {
    if (isSeeking || !monacoEditor) return;
    const targetLine = lineNum + 1;
    decorations = monacoEditor.deltaDecorations(decorations, [ { range: new monaco.Range(targetLine, 1, targetLine, 1), options: { isWholeLine: true, className: 'monaco-highlight-line', overviewRuler: { position: monaco.editor.OverviewRulerLane.Full } } } ]);
    if (document.getElementById('editor-smooth-scroll').checked) { monacoEditor.revealLineInCenterIfOutsideViewport(targetLine); }
}
function scheduleNote(midi, start, dur) {
    const osc = audioCtx.createOscillator(); osc.type = 'triangle'; const freq = 440 * Math.pow(2, (midi - 69) / 12); osc.frequency.value = freq;
    const filter = audioCtx.createBiquadFilter(); filter.type = 'lowpass'; filter.Q.value = 0.5; filter.frequency.setValueAtTime(freq * 8, start); filter.frequency.exponentialRampToValueAtTime(freq, start + 0.5); 
    const panner = audioCtx.createStereoPanner(); let pan = (midi - 66) / 24; if(pan < -0.9) pan = -0.9; if(pan > 0.9) pan = 0.9; panner.pan.value = pan;
    const gain = audioCtx.createGain(); const vol = 0.15; gain.gain.setValueAtTime(0, start); gain.gain.linearRampToValueAtTime(vol, start + 0.01); gain.gain.exponentialRampToValueAtTime(vol * 0.6, start + 0.3); gain.gain.setValueAtTime(vol * 0.6, start + dur); gain.gain.exponentialRampToValueAtTime(0.001, start + dur + 0.5); 
    osc.connect(filter); filter.connect(gain); gain.connect(panner); panner.connect(masterGain);
    osc.start(start); osc.stop(start + dur + 0.6); 
    setTimeout(() => { try { osc.disconnect(); gain.disconnect(); filter.disconnect(); panner.disconnect(); } catch(e){} }, (dur + 1.0) * 1000);
}
function renderPianoRoll() {
    if((!isPreviewing && !isEditorPreviewing) || !audioCtx) return;
    if(isPaused && isEditorPreviewing && !selectedNote) { visualizerFrame = requestAnimationFrame(renderPianoRoll); return; }
    const cvs = document.getElementById(currentCanvasId); if(!cvs) return; const ctx = cvs.getContext('2d'); const w = cvs.width; const h = cvs.height; const isDark = document.body.classList.contains('dark-theme');
    if (!gridCanvas || gridCanvas.width !== w || gridCanvas.height !== h) {
        gridCanvas = document.createElement('canvas'); gridCanvas.width = w; gridCanvas.height = h; const gCtx = gridCanvas.getContext('2d'); gCtx.fillStyle = isDark ? '#000' : '#fafafa'; gCtx.fillRect(0, 0, w, h);
        const noteRange = visualNoteRange.max - visualNoteRange.min; const laneCount = noteRange + 1; const laneWidth = w / laneCount;
        for(let i=0; i<laneCount; i++) { const lx = i * laneWidth; gCtx.fillStyle = (i % 2 === 0) ? 'rgba(128,128,128,0.05)' : 'rgba(128,128,128,0.02)'; gCtx.fillRect(lx, 0, laneWidth, h); gCtx.fillStyle = 'rgba(128,128,128,0.1)'; gCtx.fillRect(lx, 0, 1, h); }
    }
    ctx.drawImage(gridCanvas, 0, 0);
    const lookAheadSeconds = 2.5; const pixelsPerSecond = h / lookAheadSeconds; const hitLineY = h - 10; const currentTime = (audioCtx.currentTime - visualStartTime) - 0.05;
    if(isEditorPreviewing && !isSeeking) {
        const slider = document.getElementById('editor-seek-slider');
        if(slider && currentTime >= 0 && currentTime <= editorTotalDuration) { slider.value = currentTime; document.getElementById('editor-time-current').innerText = formatTime(currentTime); document.getElementById('editor-seek-fill').style.width = (currentTime / editorTotalDuration * 100) + '%'; document.getElementById('editor-status-time').innerText = `${formatTime(currentTime)} / ${formatTime(editorTotalDuration)}`; }
    }
    ctx.shadowBlur = 10; ctx.shadowColor = 'rgba(0, 180, 216, 0.8)'; ctx.strokeStyle = 'rgba(0, 180, 216, 0.8)'; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(0, hitLineY); ctx.lineTo(w, hitLineY); ctx.stroke(); ctx.shadowBlur = 0;
    let currentEventForHighlight = null;
    let startIndex = 0; let left = 0, right = audioEvents.length - 1;
    while (left <= right) { let mid = Math.floor((left + right) / 2); if (audioEvents[mid].time + audioEvents[mid].duration < currentTime - 0.5) { left = mid + 1; } else { right = mid - 1; startIndex = mid; } }
    const noteRange = visualNoteRange.max - visualNoteRange.min; const laneCount = noteRange + 1; const laneWidth = w / laneCount;
    for(let i=startIndex; i<audioEvents.length; i++) {
        const ev = audioEvents[i];
        if(isEditorPreviewing && !selectedNote) { if(currentTime >= ev.time && currentTime < ev.time + ev.duration) { currentEventForHighlight = ev; } }
        if (ev.time > currentTime + lookAheadSeconds) break;
        const timeDiff = ev.time - currentTime; const y = hitLineY - (timeDiff * pixelsPerSecond); const height = ev.duration * pixelsPerSecond; const x = (ev.note - visualNoteRange.min) * laneWidth; const hue = 180 + ((ev.note - visualNoteRange.min) / noteRange) * 160; 
        if (currentTime >= ev.time && currentTime < ev.time + ev.duration) { ctx.fillStyle = `hsla(${hue}, 100%, 70%, 0.8)`; ctx.shadowBlur = 20; ctx.shadowColor = `hsla(${hue}, 100%, 50%, 0.8)`; ctx.fillRect(x + 1, hitLineY, laneWidth - 2, 5); const grad = ctx.createLinearGradient(0, hitLineY, 0, hitLineY - 100); grad.addColorStop(0, `hsla(${hue}, 100%, 50%, 0.4)`); grad.addColorStop(1, "transparent"); ctx.fillStyle = grad; ctx.fillRect(x, hitLineY - 100, laneWidth, 100); ctx.shadowBlur = 0; }
        if (y - height < h) { ctx.fillStyle = `hsl(${hue}, 70%, 60%)`; const r = 4; const rx = x + 1; const ry = y - height; const rw = laneWidth - 2; const rh = height; if (rh > 5) { ctx.beginPath(); ctx.roundRect(rx, ry, rw, rh, [r, r, r, r]); ctx.fill(); } else { ctx.fillRect(rx, ry, rw, rh); } const tailGrad = ctx.createLinearGradient(0, ry, 0, ry + rh); tailGrad.addColorStop(0, `hsla(${hue}, 70%, 80%, 0.9)`); tailGrad.addColorStop(1, `hsla(${hue}, 70%, 40%, 0.9)`); ctx.fillStyle = tailGrad; ctx.fill(); if(selectedNote && ev === selectedNote) { ctx.strokeStyle = "white"; ctx.lineWidth = 3; ctx.shadowBlur = 15; ctx.shadowColor = "white"; ctx.strokeRect(rx - 1, ry - 1, rw + 2, rh + 2); ctx.shadowBlur = 0; } }
    }
    if(currentEventForHighlight && isEditorPreviewing && !selectedNote) { highlightEditorLine(currentEventForHighlight.lineNum); }
    visualizerFrame = requestAnimationFrame(renderPianoRoll);
}

async function loadPlaylistData() { try { const res = await fetch('/api/songs'); const data = await res.json(); allSongs = data.songs || []; favorites = data.favorites || []; allSongs = allSongs.map(s => ({name: s.name, date: s.mtime || 0})); renderPlaylist(); appLog(`Library loaded: ${allSongs.length} songs.`); } catch(e) { allSongs=[]; appLog("Failed to load library."); } }
function setPlaylistFilter(type) { currentPlaylistFilter = type; document.querySelectorAll('#playlist .filter-btn').forEach(b => b.classList.remove('active')); if(type=='All') document.getElementById('pl-all').classList.add('active'); if(type=='22K') document.getElementById('pl-22k').classList.add('active'); if(type=='15K') document.getElementById('pl-15k').classList.add('active'); renderPlaylist(); }
function toggleQueue(fn) { queue.includes(fn) ? queue=queue.filter(i=>i!==fn) : queue.push(fn); updateQueueBackend(); }
function clearQueue() { queue = []; updateQueueBackend(); }
async function updateQueueBackend() { try{ await fetch('/api/queue/update', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({queue})}); }catch(e){} renderQueueList(); renderPlaylist(); }
function renderQueueList() { const c = document.getElementById('queue-list-container'); document.getElementById('queue-count-badge').innerText = queue.length; if(queue.length===0) { c.innerHTML='<div style="padding:20px; text-align:center; color:var(--text-light); font-size:0.9em;">Queue is empty.<br>Click <b>+</b> on songs to add.</div>'; return; } c.innerHTML = queue.map((s,i) => `<div class="queue-item"><div style="display:flex; align-items:center; overflow:hidden;"><span style="color:var(--primary); margin-right:5px; font-weight:800;">#${i+1}</span><span class="song-tag ${s.includes('15K')?'tag-15k':'tag-22k'}" style="margin-right:5px; font-size:0.6em;">${s.includes('15K')?'15K':'22K'}</span><span class="song-name-text">${s.replace('.txt','').replace('_15K','').replace('_22K','')}</span></div><button class="btn" style="padding:2px 6px; font-size:0.8em; border:none; color:#ef5350;" onclick="toggleQueue(${safeArgs(s)})">✕</button></div>`).join(''); }
function renderPlaylist() {
    const el = document.getElementById('local-list'); el.innerHTML = ''; const q = document.getElementById('search-local').value.toLowerCase(), favOnly = document.getElementById('chk-fav').checked; const sortMode = document.getElementById('sort-select').value;
    let displayList = [...allSongs];
    displayList.sort((a, b) => { if (sortMode === 'name_asc') return a.name.localeCompare(b.name); if (sortMode === 'name_desc') return b.name.localeCompare(a.name); if (sortMode === 'date_desc') return b.date - a.date; if (sortMode === 'date_asc') return a.date - b.date; return 0; });
    if(displayList.length===0) { el.innerHTML='<div style="padding:20px; text-align:center; color:var(--text-light);">No songs found.</div>'; return; }
    let foundAny = false;
    displayList.forEach(obj => { const s = obj.name; const is15k = s.includes('_15K'); if((currentPlaylistFilter==='22K' && is15k) || (currentPlaylistFilter==='15K' && !is15k) || (favOnly && !favorites.includes(s)) || (q && !s.toLowerCase().includes(q))) return; foundAny = true;
        const div = document.createElement('div'); div.className = `song-row ${currentSong===s?'active':''}`;
        div.innerHTML = `<div style="flex:1; cursor:pointer; display:flex; align-items:center; overflow:hidden;"><input type="checkbox" class="chk-playlist-select" value="${s.replace(/"/g, '&quot;')}" onchange="updatePlaylistSelectCount()" style="margin-right:12px; width:18px; height:18px; accent-color:var(--primary); flex-shrink:0;"><div style="flex:1; display:flex; align-items:center; overflow:hidden;" onclick="selectSong(${safeArgs(s)}, 'local')"><span class="song-tag ${is15k?'tag-15k':'tag-22k'}">${is15k?'15K':'22K'}</span><span class="song-name-text">${s.replace('.txt','').replace('_15K','').replace('_22K','')}</span></div></div><div class="flex-row"><button class="btn" onclick="openEditor(${safeArgs(s)})" title="Edit in Studio" style="padding:6px 10px; color:var(--primary); border-color:var(--border);">✏️</button><button class="btn" onclick="toggleQueue(${safeArgs(s)})" style="padding:6px 10px; ${queue.includes(s)?'color:white; background:var(--primary); border-color:var(--primary);':'color:#aaa;'}">${queue.includes(s)?'✓':'+'}</button><button style="padding:6px 10px; background:transparent; font-size:1.2em; border:none;" onclick="toggleFav(${safeArgs(s)})"><span style="color:${favorites.includes(s)?'var(--primary)':'#a0aec0'}">★</span></button><button style="padding:6px 10px; color:#ff3333; background:transparent; border:none;" onclick="deleteSong(${safeArgs(s)})">🗑</button></div>`; el.appendChild(div); });
    if(!foundAny) el.innerHTML='<div style="padding:20px; text-align:center; color:var(--text-light);">No songs match filters.</div>'; document.getElementById('chk-playlist-select-all').checked=false; updatePlaylistSelectCount(); renderQueueList();
}
function togglePlaylistSelectAll() { const c = document.getElementById('chk-playlist-select-all'); document.querySelectorAll('#local-list .chk-playlist-select').forEach(cb => cb.checked = c.checked); updatePlaylistSelectCount(); }
function updatePlaylistSelectCount() { const c = document.querySelectorAll('#local-list .chk-playlist-select:checked').length; document.getElementById('playlist-selected-count').innerText = c + " selected"; }
async function deleteSelectedPlaylist() { const items = Array.from(document.querySelectorAll('#local-list .chk-playlist-select:checked')).map(cb => cb.value); if(items.length === 0) return showModal("Info", "No songs selected for deletion."); showConfirm("Delete Multiple", `Are you sure you want to delete ${items.length} songs?`, async () => { try { const res = await fetch('/api/delete_batch', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({filenames: items})}); const d = await res.json(); if(d.ok) { appLog(`Deleted ${d.count} songs.`, 'success'); loadPlaylistData(); } else { showModal("Error", "Batch delete failed."); } } catch(e) { showModal("Error", "Batch delete failed."); } }); }
async function selectSong(fn, source) { currentSong=fn; currentSongSource=source; if(isPreviewing) stopAudioPreview(); try{await fetch('/api/select',{method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({filename:fn})});}catch(e){} updatePlayerUI(fn); if (source === 'local') renderPlaylist(); else { document.querySelectorAll('#online-list .song-row').forEach(row => { if(row.innerText.includes(fn)) row.classList.add('active'); else row.classList.remove('active'); }); } }
function updatePlayerUI(fn) { if(!fn || fn==="None") { document.getElementById('player-song-name').innerText="No song selected"; document.getElementById('player-song-tag').style.display='none'; return; } document.getElementById('player-song-name').innerText = fn.replace('.txt','').replace('_15K','').replace('_22K',''); const tag = document.getElementById('player-song-tag'); tag.style.display='inline-block'; tag.className = fn.includes('15K')?'song-tag tag-15k':'song-tag tag-22k'; tag.innerText = fn.includes('15K')?"15K":"22K Half"; redrawCanvas('canvas-player'); }
async function toggleFav(fn) { try{await fetch('/api/fav',{method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({filename:fn})}); loadPlaylistData();}catch(e){showModal("Error","Could not save favorite.");} }
async function deleteSong(fn) { showConfirm("Delete File", "Are you sure?", async () => { try{const res=await fetch('/api/delete',{method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({filename:fn})}); if((await res.json()).ok) loadPlaylistData();}catch(e){showModal("Error","Delete failed.");} }); }
async function togglePlayback() { if(isPreviewing) stopAudioPreview(); const d = {seek:document.getElementById('slider-seek').value, speed:document.getElementById('slider-speed').value, snap:document.getElementById('slider-snap').value, loop:document.getElementById('chk-loop').checked}; appLog("Starting playback..."); try{await fetch('/api/play',{method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(d)});}catch(e){showModal("Error","Playback failed.");} }
async function stopPlayback() { appLog("Stopping playback..."); try{await fetch('/api/stop',{method:'POST'});}catch(e){} }
async function toggleAudioPreview() {
    if(isPreviewing) { stopAudioPreview(); return; } if(!currentSong || currentSong === "None") return showModal("Info", "Select a song first!");
    const btn = document.getElementById('btn-audio-preview'); btn.innerText = "⏳ Loading...";
    try { const res = await fetch('/api/preview_content', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({filename:currentSong, source:currentSongSource}) }); const d = await res.json(); if(!d.ok) throw new Error("Load failed"); startAudioEngine(d.data, currentSong.includes('_15K'), 'canvas-player', 'slider-speed', false); } 
    catch(e) { console.error(e); btn.innerText = "🔊 Preview Audio + Visuals"; showModal("Error", "Could not load song preview.\nTry downloading it first."); }
}
function stopAudioPreview() { stopAudioEngine(); isPreviewing = false; const btn = document.getElementById('btn-audio-preview'); btn.innerText = "🔊 Preview Audio + Visuals"; btn.classList.remove("playing"); appLog("Audio Preview Stopped."); redrawCanvas('canvas-player'); }

setInterval(async () => {
    try { const res = await fetch('/api/status'); const d = await res.json();
        if(d.current_song && d.current_song!=="None" && d.current_song!==currentSong && currentSongSource==='local') { currentSong=d.current_song; updatePlayerUI(currentSong); renderPlaylist(); }
        const st=document.getElementById('player-status'), btn=document.getElementById('btn-play');
        if(d.is_playing && !d.is_paused) { st.innerText="(Playing)"; st.style.color="#00e676"; btn.innerText="PAUSE"; btn.className="primary"; btn.style.background="#ff3399"; btn.style.borderColor="#ff3399"; } else if(d.is_paused) { st.innerText="(Paused)"; st.style.color="#ffb300"; btn.innerText="RESUME"; btn.className="primary"; } else { st.innerText="(Stopped)"; st.style.color="var(--text-light)"; btn.innerText="START"; btn.className="primary"; btn.style.background=""; btn.style.borderColor=""; }
        document.getElementById('progress-bar').style.width = (d.progress * 100) + '%';
    } catch(e){}
}, 500);

function handleFileSelect(i) { document.getElementById('file-name-display').innerText = i.files && i.files.length > 0 ? `${i.files.length} file(s) selected` : 'No file selected'; }
async function convertMidi() {
    const inp = document.getElementById('midi-upload'), pitch = document.getElementById('slider-pitch').value, target = document.getElementById('convert-target').value;
    if(!inp.files || inp.files.length===0) return showModal("Error", "Select files!");
    const fd = new FormData(); for(let i=0; i<inp.files.length; i++) fd.append('files[]', inp.files[i]);
    fd.append('target', target); fd.append('pitch', pitch); document.getElementById('convert-log').innerText = "Processing..."; appLog("Starting conversion...", "info");
    try { const res = await fetch('/api/convert', {method:'POST', body:fd}); const d = await res.json(); document.getElementById('convert-log').innerText = d.message; if(d.message) d.message.split('\n').forEach(l => { if(l.trim()) appLog(l, l.includes('❌')?'error':(l.includes('✅')?'success':'info')); }); loadPlaylistData(); showModal("Success", "Conversion complete!"); } catch(e) { document.getElementById('convert-log').innerText="Error."; showModal("Error","Conversion failed."); appLog("Conversion failed.", "error"); }
}
function handleSearchInput() { clearTimeout(searchTimeout); searchTimeout = setTimeout(() => { currentPage=1; searchOnline(); }, 400); }
function refreshOnline() { document.getElementById('search-online').value=""; currentPage=1; setOnlineFilter('All'); }
function setOnlineFilter(t) { currentOnlineFilter=t; document.querySelectorAll('#online .filter-btn').forEach(b => b.classList.remove('active')); if(t=='All') document.getElementById('on-all').classList.add('active'); if(t=='22K') document.getElementById('on-22k').classList.add('active'); if(t=='15K') document.getElementById('on-15k').classList.add('active'); currentPage=1; searchOnline(); }
function changePage(delta) { const maxPage = Math.ceil(totalItems / itemsPerPage); const newPage = currentPage + delta; if (newPage >= 1 && newPage <= maxPage) { currentPage = newPage; searchOnline(); } }
async function changePerPage() {
    itemsPerPage = parseInt(document.getElementById('online-per-page').value);
    currentPage = 1;
    searchOnline();
    try { await fetch('/api/settings/save', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({online_per_page: itemsPerPage}) }); } catch(e) {}
}
async function searchOnline() {
    const q = document.getElementById('search-online').value; document.getElementById('online-list').innerHTML='<div style="padding:40px; text-align:center; color:var(--text-light);">Loading Page '+currentPage+'...</div>';
    itemsPerPage = parseInt(document.getElementById('online-per-page').value) || 50;
    try {
        const res = await fetch(`/api/online/search?q=${encodeURIComponent(q)}&type=${currentOnlineFilter}&page=${currentPage}&per_page=${itemsPerPage}`); const d = await res.json(); onlineLoaded=true; totalItems = d.total || 0;
        const el = document.getElementById('online-list'); el.innerHTML=''; const maxPage = Math.ceil(totalItems / itemsPerPage) || 1; document.getElementById('page-info').innerText = `Page ${currentPage} of ${maxPage} (${totalItems} songs)`; document.getElementById('online-pagination').style.display = totalItems > 0 ? 'flex' : 'none';
        if(d.songs.length===0) { el.innerHTML='<div style="padding:40px; text-align:center; color:var(--text-light);">No songs found.</div>'; return; }
        d.songs.forEach(s => { const is15k = (s.instrument_type || "").includes("15"); const div = document.createElement('div'); div.className='song-row'; div.innerHTML = `<div style="flex:1; display:flex; align-items:center; overflow:hidden;"><input type="checkbox" class="chk-select" value="${s.song_name.replace(/"/g, '&quot;')}" onchange="updateSelectCount()" style="margin-right:15px; width:18px; height:18px; accent-color:var(--primary); flex-shrink:0;"><div style="flex:1; cursor:pointer;" onclick="selectSong(${safeArgs(s.song_name)}, 'online')"><span class="song-tag ${is15k?'tag-15k':'tag-22k'}">${s.instrument_type || "Unknown"}</span><span class="song-name-text">${s.song_name}</span></div></div><button class="primary" style="padding:6px 14px; font-size:0.85em; margin-left:10px;" onclick="downloadSingle(${safeArgs(s.song_name)}, this)">⬇</button>`; el.appendChild(div); }); document.getElementById('chk-select-all').checked=false; updateSelectCount();
    } catch(e) { document.getElementById('online-list').innerHTML='<div style="padding:40px; text-align:center; color:#ff1744;">Failed to connect or bad data.</div>'; console.error(e); }
}
function toggleSelectAll() { const c = document.getElementById('chk-select-all'); document.querySelectorAll('#online-list .chk-select').forEach(cb => cb.checked = c.checked); updateSelectCount(); }
function updateSelectCount() { document.getElementById('selected-count').innerText = document.querySelectorAll('#online-list .chk-select:checked').length + " selected"; }
async function downloadSingle(n, btn) { const og = btn.innerText; btn.innerText="..."; appLog(`Downloading: ${n}...`); try { await fetch('/api/online/download',{method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({name:n})}); btn.innerText="✔"; setTimeout(()=>btn.innerText=og,2000); showModal("Success", `Downloaded: ${n}`); loadPlaylistData(); appLog("Download complete."); } catch(e) { btn.innerText="❌"; setTimeout(()=>btn.innerText=og,2000); showModal("Error", "Download failed."); appLog("Download failed.", "error"); } }
async function downloadSelected() { const ns = Array.from(document.querySelectorAll('#online-list .chk-select:checked')).map(cb => cb.value); if(ns.length===0) return showModal("Info", "No songs selected."); showModal("Downloading", `Downloading ${ns.length} songs...`); appLog(`Batch downloading ${ns.length} songs...`); try { const res=await fetch('/api/online/download_batch',{method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({names:ns})}); const d=await res.json(); showModal("Complete", `✅ Success: ${d.success}\n❌ Failed: ${d.failed}`); loadPlaylistData(); refreshOnline(); appLog(`Batch done. Success: ${d.success}`); } catch(e) { showModal("Error","Batch failed."); appLog("Batch failed.", "error"); } }
async function uploadOnlineFiles(i) { if(!i.files || i.files.length===0) return; const fd = new FormData(); for(let f of i.files) fd.append('files[]', f); showModal("Uploading", "Please wait..."); appLog("Uploading files..."); try { const res=await fetch('/api/online/upload_browser',{method:'POST', body:fd}); const d=await res.json(); showModal("Report", `✅ Uploaded: ${d.uploaded}\n⚠ Duplicates: ${d.duplicates}\n❌ Errors: ${d.errors}\n(Invalid format or >500KB)`); searchOnline(); appLog(`Upload done. New: ${d.uploaded}`); } catch(e) { showModal("Error","Upload failed."); appLog("Upload failed.", "error"); } i.value=''; }
function listenForKey(t) { isListening=t; const b=document.getElementById('btn-bind-'+t); b.innerText="Press key..."; b.classList.add('listening'); document.addEventListener('keydown', handleKeyBind); }
function handleKeyBind(e) { if(!isListening) return; e.preventDefault(); let k = e.key.toUpperCase(); if(e.location===3) k=e.code.toUpperCase(); if(k===" ") k="SPACE"; if(isListening==='play') tempHotkeys.play=k; else tempHotkeys.stop=k; const b=document.getElementById('btn-bind-'+isListening); b.innerText=k; b.classList.remove('listening'); isListening=null; document.removeEventListener('keydown', handleKeyBind); }
async function browseFolderSafe() { try{const res=await fetch('/api/settings/browse_safe'); const d=await res.json(); if(d.path) document.getElementById('set-folder').value=d.path;}catch(e){} }
async function saveSettings() { const folder = document.getElementById('set-folder').value; const h_play = document.getElementById('btn-bind-play').innerText; const h_stop = document.getElementById('btn-bind-stop').innerText; try { const res = await fetch('/api/settings/save', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ note_folder: folder, hotkey_play: h_play, hotkey_stop: h_stop }) }); const d = await res.json(); if(d.ok) { showModal("Success", "Settings saved successfully!"); appLog("Library settings saved."); } else { showModal("Error", "Failed to save settings."); } } catch(e) { showModal("Error", "Failed to save settings."); } }
async function saveSettings() { const folder = document.getElementById('set-folder').value; const h_play = document.getElementById('btn-bind-play').innerText; const h_stop = document.getElementById('btn-bind-stop').innerText; try { const res = await fetch('/api/settings/save', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ note_folder: folder, hotkey_play: h_play, hotkey_stop: h_stop }) }); const d = await res.json(); if(d.ok) { showModal("Success", "Settings saved successfully!"); appLog("Library settings saved."); } else { showModal("Error", "Failed to save settings."); } } catch(e) { showModal("Error", "Failed to save settings."); } }
async function loadSettings() { try { const res=await fetch('/api/settings/get'); const d=await res.json(); if(d.note_folder && d.note_folder !== "None") { document.getElementById('set-folder').value = d.note_folder; } else { document.getElementById('set-folder').value = ""; } tempHotkeys={play:d.hotkey_play || 'F4',stop:d.hotkey_stop || 'F5'}; document.getElementById('btn-bind-play').innerText=tempHotkeys.play; document.getElementById('btn-bind-stop').innerText=tempHotkeys.stop; if(d.online_per_page) { document.getElementById('online-per-page').value = d.online_per_page; itemsPerPage = parseInt(d.online_per_page); } } catch(e){} }

loadPlaylistData(); loadSettings(); appLog("System Ready");
"""

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en"> <head> <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"> <title>PianiPia V6</title> <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet"> <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script> <script src="https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.44.0/min/vs/loader.min.js"></script>
<style>""" + _CSS + r"""</style>
</head> <body class="{{ 'dark-theme' if THEME == 'dark' else '' }}"> <div id="custom-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:var(--modal-bg); backdrop-filter:blur(5px); z-index:1000; justify-content:center; align-items:center;"> <div style="background:var(--surface); padding:30px; border-radius:20px; width:400px; max-width:90%; border:1px solid var(--border); box-shadow:var(--shadow); text-align:center;"> <div id="modal-title" style="font-size:1.5em; font-weight:800; color:var(--primary); margin-bottom:10px;">Alert</div> <div id="modal-body" style="color:var(--text); margin-bottom:20px; white-space:pre-wrap;">Message...</div> <button class="primary" style="min-width:120px;" onclick="document.getElementById('custom-modal').style.display='none'">Got it!</button> </div> </div> <div id="custom-confirm" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:var(--modal-bg); backdrop-filter:blur(5px); z-index:101; justify-content:center; align-items:center;"> <div style="background:var(--surface); padding:30px; border-radius:20px; width:400px; max-width:90%; border:1px solid var(--border); box-shadow:var(--shadow); text-align:center;"> <div id="confirm-title" style="font-size:1.5em; font-weight:800; color:var(--primary); margin-bottom:10px;">Confirm</div> <div id="confirm-body" style="color:var(--text); margin-bottom:20px; white-space:pre-wrap;">Are you sure?</div> <div class="flex-row" style="justify-content:center;"> <button class="btn" style="min-width:100px;" onclick="confirmNo()">Cancel</button> <button class="primary" style="min-width:100px;" onclick="confirmYes()">Yes</button> </div> </div> </div> <div id="exit-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:var(--modal-bg); backdrop-filter:blur(5px); z-index:2000; justify-content:center; align-items:center;"> <div style="background:var(--surface); padding:30px; border-radius:20px; width:400px; max-width:90%; border:1px solid #ff3333; box-shadow:0 0 30px rgba(255,51,51,0.2); text-align:center;"> <div style="font-size:1.5em; font-weight:800; color:#ff3333; margin-bottom:10px;">EXIT APPLICATION</div> <div style="color:var(--text); margin-bottom:20px; font-weight:600;">Are you sure you want to quit PianiPia?</div> <div class="flex-row" style="justify-content:center;"> <button class="btn" style="min-width:100px;" onclick="document.getElementById('exit-modal').style.display='none'">Cancel</button> <button class="danger" style="min-width:100px;" onclick="finalizeExit()">EXIT NOW</button> </div> </div> </div>
<div class="sidebar"> <div class="sidebar-header"> <h2>PIANIPIA</h2> <span style="font-size:0.8em; color:var(--primary); font-weight:800; letter-spacing:1px; text-transform:uppercase;">V6</span> </div>
<div class="sidebar-nav"> <button id="btn-playlist" class="tab-btn active" onclick="switchTab('playlist')"><span>🎵</span> Playlist</button> <button id="btn-editor" class="tab-btn" onclick="switchTab('editor')"><span>📝</span> Studio Editor</button> <button id="btn-online" class="tab-btn" onclick="switchTab('online')"><span>☁</span> Online</button> <button id="btn-add" class="tab-btn" onclick="switchTab('add')"><span>🎹</span> Add / Convert</button> <button id="btn-settings" class="tab-btn" onclick="switchTab('settings')"><span>⚙</span> Settings</button> <button id="btn-guide" class="tab-btn" onclick="switchTab('guide')"><span>❓</span> Information</button> <button id="btn-theme" class="tab-btn" onclick="toggleTheme()"><span>🌙</span> Dark Mode</button> <div id="app-console" class="console-log"></div> </div>
<div class="sidebar-footer"> <button class="danger" style="width:100%; display:flex; justify-content:center; align-items:center; gap:10px;" onclick="showExitModal()"><span style="font-size:1.2em;">✕</span> EXIT APP</button> </div> </div>
<div class="content"> <div id="playlist" class="tab-content active"> <div class="playlist-grid"> <div class="playlist-column"> <div class="flex-row" style="justify-content:space-between; margin-bottom:10px;"> <div class="flex-row" style="flex:1"><input type="text" id="search-local" placeholder="Search song..." onkeyup="renderPlaylist()"></div> </div> <div class="flex-row" style="margin-bottom:10px; justify-content:space-between; flex-wrap:wrap; gap:8px;"> <div class="filter-group"> <button class="filter-btn active" id="pl-all" onclick="setPlaylistFilter('All')">All</button> <button class="filter-btn" id="pl-22k" onclick="setPlaylistFilter('22K')">22K Half</button> <button class="filter-btn" id="pl-15k" onclick="setPlaylistFilter('15K')">15K</button> <button onclick="loadPlaylistData()" class="filter-btn" style="border-left:1px solid var(--border); border-radius:0; padding-left:15px; margin-left:5px;">↻ Refresh</button> </div> <div class="flex-row"> <select id="sort-select" onchange="renderPlaylist()" style="padding:8px; border-radius:8px; width:auto; font-size:0.85em;"> <option value="name_asc">Name (A-Z)</option> <option value="name_desc">Name (Z-A)</option> <option value="date_desc" selected>Newest First</option> <option value="date_asc">Oldest First</option> </select> <label class="custom-checkbox"><input type="checkbox" id="chk-fav" onchange="renderPlaylist()"><span class="slider"></span></label><span style="font-size:0.8em; font-weight:700; color:var(--text-light);">Favorites</span> </div> </div>
            <div class="flex-row" style="margin-bottom:10px; padding:0 2px; justify-content:space-between; align-items:center;"> <div class="flex-row"> <label style="display:flex; align-items:center; cursor:pointer; color:var(--text); font-weight:bold; font-size:0.9em; white-space:nowrap;"> <input type="checkbox" id="chk-playlist-select-all" style="width:16px; height:16px; accent-color:var(--primary);" onchange="togglePlaylistSelectAll()"> <span style="margin-left:6px;">Select All</span> </label> <span id="playlist-selected-count" style="color:var(--primary); font-size:0.85em; font-weight:bold; margin-left:10px;">0 selected</span> </div> <button class="danger" style="padding:6px 12px; font-size:0.85em;" onclick="deleteSelectedPlaylist()">Delete Selected</button> </div> <div class="song-list" id="local-list"></div> </div>
        <div class="playlist-column"> <div class="player-panel"> <div class="now-playing"> <span class="now-playing-icon">🎵</span> <div style="flex:1; overflow:hidden;"> <div id="player-song-name" style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">No song selected</div> <div class="flex-row" style="margin-top:5px;"><span id="player-song-tag" class="song-tag tag-22k" style="display:none;">22K Half</span><span id="player-status" style="font-size:0.7em; color:var(--text-light); font-weight:600;">(Stopped)</span></div> </div> </div>
                <canvas id="canvas-player" class="piano-canvas" width="800" height="220"></canvas>
                <div class="progress-container"><div class="progress-bar" id="progress-bar"></div></div> <div class="controls-grid"> <div class="control-group"><label>Speed: <span id="val-speed">1.0</span></label><input type="range" id="slider-speed" min="0.1" max="5.0" step="0.1" value="1.0" oninput="document.getElementById('val-speed').innerText=this.value" onchange="onMainSpeedChange(this.value)"></div> <div class="flex-row" style="justify-content:center; gap:10px;"><button id="btn-play" class="primary" style="width:90px;" onclick="togglePlayback()">START</button><button id="btn-stop" class="danger" style="width:80px;" onclick="stopPlayback()">STOP</button></div> <div class="control-group"><label>Start %: <span id="val-seek">0</span></label><input type="range" id="slider-seek" min="0" max="100" step="1" value="0" oninput="document.getElementById('val-seek').innerText=this.value"></div> </div>
                <button id="btn-audio-preview" class="audio-btn btn" onclick="toggleAudioPreview()">🔊 Preview Audio + Visuals</button>
                <div style="margin-top:15px; display:flex; justify-content:space-between; align-items:center;"> <div class="control-group" style="flex:1; margin-right:15px;"><label>Chord Timing (ms): <span id="val-snap">0</span></label><input type="range" id="slider-snap" min="0" max="200" step="10" value="0" oninput="updateParam('snap', this.value)"></div> <div class="flex-row"><label class="custom-checkbox"><input type="checkbox" id="chk-loop" onchange="updateParam('loop', this.checked)"><span class="slider"></span></label><span style="font-size:0.8em; font-weight:700; color:var(--text-light);">Loop</span></div> </div> </div> <div style="display:flex; justify-content:space-between; align-items:center; margin-top:20px;"><h3 style="margin:0; font-size:1em; display:flex; align-items:center; gap:10px;">UP NEXT <span id="queue-count-badge" class="badge-count">0</span></h3><button class="btn" style="padding:4px 8px; font-size:0.8em;" onclick="clearQueue()">Clear Queue</button></div> <div class="queue-list" id="queue-list-container"><div style="padding:20px; text-align:center; color:var(--text-light); font-size:0.9em;">Queue is empty.<br>Click <b>+</b> on songs to add.</div></div> </div> </div> </div>
<div id="editor" class="tab-content"> <div class="editor-container"> <div class="editor-pane"> <div class="editor-header"> <span id="editor-filename">Untitled.txt</span> <div class="flex-row"> <label style="font-size:0.8em; display:flex; align-items:center; cursor:pointer;"><input type="checkbox" id="editor-smooth-scroll" checked style="margin-right:5px;"> Auto Scroll</label> <button class="primary" onclick="saveEditorContent()" style="padding:4px 12px; font-size:0.8em;">💾 Save</button> </div> </div> <div class="editor-toolbar"> <span style="font-size:0.7em; font-weight:800; color:var(--primary); margin-right:5px;">INSERT:</span> <button class="tool-btn" onclick="insertTemplate('note')"><span>⬇</span> + Press Key</button> <button class="tool-btn" onclick="insertTemplate('release')"><span>⬆</span> + Release Key</button> <button class="tool-btn" onclick="insertTemplate('delay')"><span>⏳</span> + Wait (Delay)</button> <button class="tool-btn" onclick="insertTemplate('chord')"><span>🎹</span> + Full Click</button> </div> <div class="editor-main"> <div id="monaco-container"></div> </div> <div class="editor-footer"> <div class="flex-row" style="justify-content: space-between; font-size: 0.8em; color: var(--text-light);"> <span id="editor-status-line">Line: 1</span> <span id="editor-status-time">00:00 / 00:00</span> </div> </div> </div>
        <div class="editor-pane"> <div class="editor-header"> <span>LIVE PREVIEW</span> <div class="editor-controls"> <button class="btn" id="btn-editor-play" onclick="playEditor()" title="Play">▶</button> <button class="btn" id="btn-editor-pause" onclick="pauseEditor()" title="Pause" disabled>⏸</button> <button class="btn danger" id="btn-editor-stop" onclick="stopEditorPreview()" title="Stop" disabled>⏹</button> </div> </div> <div style="padding:20px; display:flex; flex-direction:column; height:100%; box-sizing:border-box;"> <canvas id="canvas-editor" class="piano-canvas" width="600" height="300" style="flex:1; height:auto; cursor: pointer;" onclick="handleCanvasClick(event)"></canvas> <div style="margin-top: 15px;"> <div class="control-group"> <label>Seek Progression</label> <div class="editor-seek-container"> <span id="editor-time-current">0:00</span> <div class="editor-slider-track"> <div id="editor-seek-fill" class="editor-slider-fill"></div> <input type="range" id="editor-seek-slider" class="editor-slider-input" min="0" max="100" step="0.1" value="0" oninput="onEditorSeekInput()" onchange="onEditorSeekChange()"> </div> <span id="editor-time-total">0:00</span> </div> </div> </div>
                <div class="controls-grid" style="margin-top:15px;"> <div class="control-group"><label>Preview Speed</label><input type="range" id="editor-speed" min="0.1" max="5.0" step="0.1" value="1.0" oninput="if(isEditorPreviewing) { stopEditorPreview(); playEditor(document.getElementById('editor-seek-slider').value); }"></div> <div style="text-align:center; font-size:0.8em; color:var(--text-light); margin-top:10px;"> Modify text -> Click <b>▶</b>. <br>Click any note in the visualizer to jump to code. </div> </div> </div> </div> </div> </div>
<div id="online" class="tab-content"> <div style="margin-bottom:10px;"><input type="text" id="search-online" placeholder="Search community songs..." oninput="handleSearchInput()"></div> <div class="flex-row" style="margin-bottom:10px; justify-content:space-between; padding:0 2px; flex-wrap:wrap; gap:10px;"> <div class="flex-row" style="gap:10px;"> <label style="display:flex; align-items:center; cursor:pointer; color:var(--text); font-weight:bold; font-size:0.9em; white-space:nowrap;"><input type="checkbox" id="chk-select-all" style="width:16px; height:16px; accent-color:var(--primary);" onchange="toggleSelectAll()"> <span style="margin-left:6px;">Select All</span></label> <span id="selected-count" style="color:var(--primary); font-size:0.85em; font-weight:bold; min-width:60px;">0 selected</span> <div class="filter-group" style="margin-left:5px;"> <button class="filter-btn active" id="on-all" onclick="setOnlineFilter('All')">All</button> <button class="filter-btn" id="on-22k" onclick="setOnlineFilter('22K')">22K Half</button> <button class="filter-btn" id="on-15k" onclick="setOnlineFilter('15K')">15K</button> </div> <button onclick="refreshOnline()" class="btn" style="padding:6px 10px; font-size:0.9em;" title="Refresh List">↻</button> </div> <div class="flex-row" style="gap:8px;"> <button class="primary" onclick="downloadSelected()" style="font-size:0.85em; padding:8px 16px;">Download Selected</button> <label class="btn" style="color:var(--primary); border-color:var(--primary); font-size:0.85em; padding:8px 16px;">Upload File<span style="font-size:0.7em; opacity:0.8; font-weight:400; margin-left:5px;">(Limit: 500KB .txt)</span><input type="file" id="upload-online-file" multiple accept=".txt" style="display:none;" onchange="uploadOnlineFiles(this)"></label> </div> </div> <div class="song-list" id="online-list"><div style="padding:40px; text-align:center; color:var(--text-light);">Start typing to search...</div></div> <div id="online-pagination" class="pagination-container" style="display:none;"> <button class="page-btn" onclick="changePage(-1)">← Prev</button> <span id="page-info" style="font-weight:700; color:var(--text); margin:0 10px;">Page 1</span> <button class="page-btn" onclick="changePage(1)">Next →</button> <div style="border-left:1px solid var(--border); padding-left:15px; margin-left:5px;"> <select id="online-per-page" class="per-page-select" onchange="changePerPage()"> <option value="50">50 / page</option> <option value="100">100 / page</option> <option value="200">200 / page</option> <option value="300">300 / page</option> </select> </div> </div> </div>

<div id="add" class="tab-content"> <div class="full-height-grid"> <label class="upload-zone modern-card" style="margin:0;"> <span style="font-size:5em; margin-bottom:20px;">📂</span><span style="font-weight:800; font-size:2em; color:var(--text);">Drag & Drop MIDI Files</span> <small style="font-size:1.2em; margin-top:10px; color:var(--text-light);">Supports multiple selection (.mid / .midi)</small> <div id="file-name-display" style="text-align:center; color:var(--primary); font-weight:bold; margin-top:20px; font-size:1.1em; min-height:30px;"></div> <input type="file" id="midi-upload" accept=".mid,.midi" multiple style="display:none;" onchange="handleFileSelect(this)"> </label> <div class="modern-card" style="margin:0; justify-content:center;"> <div class="section-header"><span>⚙</span> CONVERSION SETTINGS</div> <div style="display:flex; flex-direction:column; gap:30px;"> <div class="control-group"> <label style="font-size:0.9em;">TARGET INSTRUMENT</label> 
                        <select id="convert-target" class="custom-select" style="width:100%; font-size:1.1em; padding:15px;">
                            <option value="Both">Both (22K Half & 15K)</option>
                            <option value="22K">22-Keys (Half Note)</option>
                            <option value="15K">15-Keys (Simple)</option>
                            <option value="Violin">Violin (Sustain Mode)</option>
                        </select> 
 </div> <div class="control-group"><label style="font-size:0.9em;">PITCH SHIFT: <span id="val-pitch" style="color:var(--text);">0</span></label><input type="range" id="slider-pitch" min="-2" max="2" step="1" value="0" oninput="document.getElementById('val-pitch').innerText=this.value" style="margin-top:10px;"></div> <button class="primary" onclick="convertMidi()" style="height:70px; font-size:1.4em; border-radius:16px; margin-top:10px;">CONVERT ALL FILES</button> <div id="convert-log" style="background:var(--console-bg); border:1px solid var(--border); border-radius:12px; padding:15px; height:150px; overflow-y:auto; color:var(--text); font-family:monospace; font-size:0.9em; box-shadow:inset 0 0 10px rgba(0,0,0,0.05);">Ready to convert...</div> </div> </div> </div> </div>
<div id="settings" class="tab-content"> <div class="full-height-grid"> <div class="modern-card" style="margin:0;"> <div class="section-header"><span>📂</span> LIBRARY SETTINGS</div> <div style="display:flex; flex-direction:column; justify-content:center; height:100%;"> <p style="color:var(--text-light); margin-bottom:20px; font-size:1.1em;">Manage where your songs are stored.</p> <label style="display:block; color:var(--primary); font-weight:800; font-size:0.9em; margin-bottom:15px;">SONG FOLDER PATH</label> <div style="display:flex; gap:15px; margin-bottom:30px;"><input type="text" id="set-folder" placeholder="Downloads/Notes" readonly style="background:var(--console-bg); color:var(--text); font-size:1.1em; padding:20px;"><button class="btn" style="padding:0 30px; font-size:1.1em;" onclick="browseFolderSafe()">Change</button></div> <button class="primary" style="padding:20px; font-size:1.2em; width:100%;" onclick="saveSettings()">SAVE ALL SETTINGS</button> </div> </div> <div class="modern-card" style="margin:0;"> <div class="section-header"><span>⌨</span> CONTROLS</div> <div style="display:flex; flex-direction:column; justify-content:center; height:100%; gap:40px;"> <div><label style="display:block; color:var(--primary); font-weight:800; font-size:0.9em; margin-bottom:15px;">PLAY / PAUSE KEY</label><button id="btn-bind-play" class="btn" style="width:100%; padding:30px; border-style:dashed; font-size:1.5em; border-width:2px;" onclick="listenForKey('play')">F4</button></div> <div><label style="display:block; color:var(--primary); font-weight:800; font-size:0.9em; margin-bottom:15px;">STOP KEY</label><button id="btn-bind-stop" class="btn" style="width:100%; padding:30px; border-style:dashed; font-size:1.5em; border-width:2px;" onclick="listenForKey('stop')">F5</button></div> </div> </div> </div> </div>
<div id="guide" class="tab-content"> <div style="text-align:center; margin-bottom:30px;"> <h2 style="font-size:3em; color:var(--primary); margin-bottom:10px;">PIANIPIA V6</h2> <p style="color:var(--text-light); font-size:1.2em; max-width:600px; margin:0 auto;">The Ultimate Automated Instrument Player for Heartopia.</p> <div style="margin-top: 20px; display: flex; gap: 10px; justify-content: center;"> <a href="https://github.com/KaleidSkylark/Heartopia-Instrument-MIDI" target="_blank" style="color:var(--primary); font-weight:800; text-decoration:none; font-size:1.1em; border: 2px solid var(--primary); padding: 5px 15px; border-radius: 20px; box-shadow:var(--neon-glow);"> <svg height="20" width="20" viewBox="0 0 16 16" fill="currentColor" style="vertical-align: text-bottom; margin-right: 5px;"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path></svg> View on GitHub </a> </div> </div> <div class="info-grid">  <div class="info-card"> <h3>📝 Studio Editor</h3> <p>Powered by the Monaco Engine (VS Code).</p> <ul style="padding-left:20px; line-height:1.6; font-size:0.9em; color:var(--text-light);"> <li><b>Hyper-Performance:</b> Smoothly handles 1,000,000+ lines of MIDI script.</li> <li><b>Live Visual Sync:</b> Canvas visualizer tracks your current code line in real-time.</li> <li><b>Click-to-Find:</b> Click any note in the visualizer to jump straight to its code.</li> </ul> </div> <div class="info-card"> <h3>🎹 MIDI Converter</h3> <p>Drag, drop, and convert instantly.</p> <ul style="padding-left:20px; line-height:1.6; font-size:0.9em; color:var(--text-light);"> <li><b>Dual Generation:</b> Automatically creates both 22-Key and 15-Key versions.</li> <li><b>Pitch Shifting:</b> Adjust note octaves during conversion for the perfect sound.</li> <li><b>Batch Processing:</b> Convert dozens of files in seconds.</li> </ul> <div style="margin-top: 15px; padding: 10px; border-left: 4px solid #4CAF50; background: rgba(0,0,0,0.03);"> <strong>Audio to MIDI Converter:</strong><br> <a href="https://eldoraudio.com/products/piano-audio-to-midi" target="_blank" style="text-decoration: none; color: #4CAF50; font-weight: bold;"> eldoraudio Piano Audio to MIDI Converter </a><br> <span style="font-size: 0.85em; font-style: italic; opacity: 0.8;"> * Note: Converts better if the audio is Piano Cover or Synthesia. </span> </div> </div> <div class="info-card"> <h3>☁ Library & Cloud</h3> <p>Discover and manage your music.</p> <ul style="padding-left:20px; line-height:1.6; font-size:0.9em; color:var(--text-light);"> <li><b>Playlist Queue:</b> Stack up songs, set them on loop, and let them play.</li> <li><b>Community Cloud:</b> Search, download, and upload thousands of community scripts instantly.</li> </ul> </div> <div class="info-card"> <h3>⚠ Important Notes</h3> <p style="font-size:0.9em; line-height:1.6; color:var(--text-light);"> <b>For the best experience:</b> </p> <ul style="padding-left:20px; line-height:1.6; font-size:0.9em; color:var(--text-light);"> <li><b>Permissions:</b> Always run the application as Administrator if keystrokes or mouse clicks are being blocked by the game.</li> </ul> </div> <div class="info-card"> <h3>🎮 External Game Mods</h3> <p>Since the Assist Tab was removed, check out these free community tools:</p> <ul style="padding-left:20px; line-height:1.6; font-size:0.9em; color:var(--text-light);"> <li><a href="https://www.unknowncheats.me/forum/other-games/747079-heartopia-helper.html" target="_blank" style="color:var(--primary); text-decoration:none; font-weight:bold;">Heartopia Helper</a></li> <li><a href="https://www.unknowncheats.me/forum/other-games/736498-heartopia-buddy-teleport-auto-farm.html" target="_blank" style="color:var(--primary); text-decoration:none; font-weight:bold;">Heartopia Buddy (Teleport & Auto Farm)</a></li> </ul> <div style="margin-top:10px; padding:10px; border-radius:8px; background:rgba(255,51,51,0.1); border:1px solid #ff3333;"> <span style="color:#ff3333; font-weight:800; font-size:0.9em;">⚠️ WARNING: AVOID EXCESSIVE CHEATING</span> <p style="color:var(--text-light); font-size:0.85em; margin-top:5px; margin-bottom:0;">Using these mods has led to other players receiving warnings and bans (3 days, 7 days, 1 month). Use at your own risk!</p> </div> </div> </div> <div style="text-align:center; margin-top:40px; color:var(--text-light); font-size:0.9em;"><p>Created by KaleidSkylark</p></div> </div> </div>
<script>""" + _JS + r"""</script>
</body> </html>"""