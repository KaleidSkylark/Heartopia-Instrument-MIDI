const { app, BrowserWindow, ipcMain, dialog, globalShortcut, screen } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const { createClient } = require('@supabase/supabase-js');

// ─── Process & Cache Configuration ───
try {
  app.commandLine.appendSwitch('disable-gpu-shader-disk-cache');
  app.commandLine.appendSwitch('disable-http-cache');
  app.commandLine.appendSwitch('js-flags', '--max-old-space-size=256');
  app.commandLine.appendSwitch('disable-renderer-backgrounding');
  app.setPath('userData', path.join(app.getPath('appData'), 'PianiPiaV8'));
} catch (e) {}

// ─── Process Error Protection ───
process.on('uncaughtException', (err) => {
  if (err && (err.code === 'EPIPE' || err.code === 'ERR_STREAM_DESTROYED' || String(err.message).includes('EPIPE'))) return;
  console.warn('[Main Uncaught Exception]:', err?.message || err);
});
process.on('unhandledRejection', (reason) => {
  console.warn('[Main Unhandled Rejection]:', reason);
});


// ─── Config & Constants ───
const USER_DATA_DIR = path.join(app.getPath('appData'), 'PianiPiaV8');
try { if (!fs.existsSync(USER_DATA_DIR)) fs.mkdirSync(USER_DATA_DIR, { recursive: true }); } catch (e) {}

const CONFIG_FILE = path.join(USER_DATA_DIR, 'config.json');
const FAV_FILE = path.join(USER_DATA_DIR, 'favorites.json');
const SUPABASE_URL = 'https://uiclrnderaagzbgezolt.supabase.co';
const SUPABASE_KEY = 'sb_publishable_1nuHwPjz75BpU7EICEYDng_9rdsEFvH';

function resolveAppPath(filename) {
  if (app.isPackaged) {
    const unpacked = path.join(process.resourcesPath, 'app.asar.unpacked', filename);
    if (fs.existsSync(unpacked)) return unpacked;
    const directApp = path.join(process.resourcesPath, 'app', filename);
    if (fs.existsSync(directApp)) return directApp;
  }
  return path.join(__dirname, filename);
}

function findReferenceDir(name) {
  const candidates = [
    path.join(__dirname, name),
    path.join(__dirname, '..', name),
    path.join(process.resourcesPath, name),
    path.join(process.resourcesPath, '..', name),
    path.join(process.cwd(), name)
  ];
  for (const c of candidates) {
    try { if (fs.existsSync(c)) return c; } catch(e) {}
  }
  return path.join(process.cwd(), name);
}

let mainWindow = null;
let supabase = null;
let config = {};
let favorites = [];
let pythonProcess = null;
let hotkeysPaused = false;
let hotkeysPauseTimer = null;

let playerState = {
  is_playing: false,
  is_paused: false,
  progress: 0,
  status: 'Ready',
  current_song: 'None',
  speed: 1.0,
  snap: 0,
  loop: false,
  queue: []
};

// ─── Key Maps ───
const MAP_22 = {
  48:',', 49:'l', 50:'.', 51:';', 52:'/', 53:'o', 54:'0', 55:'p',
  56:'-', 57:'[', 58:'=', 59:']', 60:'z', 61:'s', 62:'x', 63:'d',
  64:'c', 65:'v', 66:'g', 67:'b', 68:'h', 69:'n', 70:'j', 71:'m',
  72:'q', 73:'2', 74:'w', 75:'3', 76:'e', 77:'r', 78:'5', 79:'t',
  80:'6', 81:'y', 82:'7', 83:'u', 84:'i'
};

const MAP_15 = {
  60:'a', 62:'s', 64:'d', 65:'f', 67:'g', 69:'h', 71:'j',
  72:'q', 74:'w', 76:'e', 77:'r', 79:'t', 81:'y', 83:'u', 84:'i'
};

const REVERSE_MAP_22 = {};
const REVERSE_MAP_15 = {};
for (const [k, v] of Object.entries(MAP_22)) REVERSE_MAP_22[v.toUpperCase()] = parseInt(k);
for (const [k, v] of Object.entries(MAP_15)) REVERSE_MAP_15[v.toUpperCase()] = parseInt(k);

// ─── Load / Save Config & Favorites ───
function loadConfig() {
  const defaults = {
    note_folder: 'C:/Users/Skylark/Downloads/Notes',
    hotkey_play: 'F4',
    hotkey_stop: 'F5',
    theme: 'dark',
    queue: [],
    online_per_page: 50
  };
  try {
    if (fs.existsSync(CONFIG_FILE)) {
      const data = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf-8'));
      config = { ...defaults, ...data };
      if (!config.note_folder || !fs.existsSync(config.note_folder)) {
        if (fs.existsSync(defaults.note_folder)) {
          config.note_folder = defaults.note_folder;
        }
      }
    } else {
      config = defaults;
      saveConfig();
    }
  } catch (e) {
    console.error('Config load error:', e);
    config = defaults;
  }
  playerState.queue = config.queue || [];
  console.log('[Config] Loaded. Note folder:', config.note_folder);
}

function saveConfig() {
  try {
    let existing = {};
    if (fs.existsSync(CONFIG_FILE)) {
      try { existing = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf-8')); } catch(e) {}
    }
    Object.assign(existing, config);
    fs.writeFileSync(CONFIG_FILE, JSON.stringify(existing, null, 4), 'utf-8');
  } catch (e) {
    console.error('Config save error:', e);
  }
}

function loadFavorites() {
  try {
    if (fs.existsSync(FAV_FILE)) {
      favorites = JSON.parse(fs.readFileSync(FAV_FILE, 'utf-8'));
    }
  } catch (e) { favorites = []; }
}

function saveFavorites() {
  try {
    fs.writeFileSync(FAV_FILE, JSON.stringify(favorites, null, 2), 'utf-8');
  } catch (e) {}
}

function initSupabase() {
  try {
    supabase = createClient(SUPABASE_URL, SUPABASE_KEY);
    console.log('[Supabase] Initialized with client URL:', SUPABASE_URL);
  } catch (e) {
    console.error('Supabase init error:', e);
  }
}

// ─── Python Process Bridge ───
function startPythonBridge() {
  if (pythonProcess) return;

  const scriptPath = resolveAppPath('python_bridge.py');
  const workingDir = path.dirname(scriptPath);

  pythonProcess = spawn('python', [scriptPath], {
    cwd: workingDir,
    stdio: ['pipe', 'pipe', 'pipe'],
    env: { ...process.env, PYTHONIOENCODING: 'utf-8', PYTHONLEGACYWINDOWSSTDIO: 'utf-8' }
  });

  pythonProcess.stdin.on('error', (err) => {
    if (err.code !== 'EPIPE' && err.code !== 'EOF') {
      console.warn('[Python Bridge stdin]:', err.message);
    }
  });

  pythonProcess.on('error', (err) => {
    console.warn('[Python Bridge error]:', err.message);
  });

  pythonProcess.stdout.on('data', (chunk) => {
    const lines = chunk.toString().split('\n');
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed) continue;
      try {
        const msg = JSON.parse(trimmed);
        handlePythonMessage(msg);
      } catch (err) {
        console.log('[Python Log]:', trimmed);
      }
    }
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error('[Python Error]:', data.toString());
  });

  pythonProcess.on('close', (code) => {
    console.log(`Python bridge exited with code ${code}`);
    pythonProcess = null;
  });
}

function sendPythonCommand(cmdObj) {
  if (!pythonProcess || !pythonProcess.stdin) return;
  try {
    if (!pythonProcess.stdin.destroyed && pythonProcess.stdin.writable) {
      pythonProcess.stdin.write(JSON.stringify(cmdObj) + '\n', (err) => {
        // Suppress pipe errors if process is terminating
      });
    }
  } catch (err) {
    // Ignore EPIPE or broken pipes safely
  }
}

function stopPythonBridge() {
  if (!pythonProcess) return;
  const proc = pythonProcess;
  pythonProcess = null;
  try {
    if (proc.stdin && !proc.stdin.destroyed && proc.stdin.writable) {
      proc.stdin.write(JSON.stringify({ cmd: 'exit' }) + '\n', () => {});
      proc.stdin.end();
    }
  } catch (e) {}

  setTimeout(() => {
    try {
      if (!proc.killed) proc.kill();
    } catch (e) {}
  }, 100);
}

let assistState = {
  connected: false,
  window_name: 'Heartopia',
  walk_active: false,
  cam_active: false,
  harvest_active: false,
  cook_active: false,
  snow_active: false,
  jump_active: false,
  confidence: 0.8,
  use_grayscale: false
};
const assistResolvers = {};

function handlePythonMessage(msg) {
  if (msg.type === 'ready') {
    sendPythonCommand({
      cmd: 'set_hotkeys',
      play: config.hotkey_play || 'F4',
      stop: config.hotkey_stop || 'F5'
    });
  } else if (msg.type === 'status') {
    playerState.is_playing = msg.is_playing;
    playerState.is_paused = msg.is_paused;
    playerState.progress = msg.progress;
    playerState.status = msg.status;
    if (msg.current_song) {
      playerState.current_song = msg.current_song;
    }
    mainWindow?.webContents.send('status_update', playerState);
    overlayWindow?.webContents.send('player_status', playerState);
  } else if (msg.type === 'convert_result') {
    mainWindow?.webContents.send('convert_result', msg);
  } else if (msg.type === 'hotkey_pressed') {
    if (hotkeysPaused) {
      console.log(`[Main] Hotkey ignored during rebinding (${msg.action})`);
      return;
    }
    console.log(`[Main] Hotkey received from Python: ${msg.action}`);
    if (msg.action === 'play') {
      triggerPlayPause();
    } else if (msg.action === 'stop') {
      triggerStop();
    }
  } else if (msg.type === 'assist_windows') {
    if (assistResolvers['getWindows']) {
      assistResolvers['getWindows'](msg);
      delete assistResolvers['getWindows'];
    }
  } else if (msg.type === 'assist_connect_result') {
    assistState.connected = !!msg.ok;
    assistState.window_name = msg.window || 'Heartopia';
    if (assistResolvers['connect']) {
      assistResolvers['connect']({ connected: assistState.connected, window: assistState.window_name });
      delete assistResolvers['connect'];
    }
    mainWindow?.webContents.send('assist_update', assistState);
    overlayWindow?.webContents.send('assist_update', assistState);
  } else if (msg.type === 'assist_disconnect_result') {
    assistState.connected = false;
    if (assistResolvers['disconnect']) {
      assistResolvers['disconnect']({ ok: true });
      delete assistResolvers['disconnect'];
    }
    mainWindow?.webContents.send('assist_update', assistState);
    overlayWindow?.webContents.send('assist_update', assistState);
  } else if (msg.type === 'assist_state_update' || msg.type === 'assist_status_result') {
    if (msg.state) Object.assign(assistState, msg.state);
    if (assistResolvers['toggle'] && Array.isArray(assistResolvers['toggle'])) {
      const resolvers = assistResolvers['toggle'].splice(0);
      resolvers.forEach(r => { try { r({ ok: true, state: assistState }); } catch(e){} });
    } else if (typeof assistResolvers['toggle'] === 'function') {
      assistResolvers['toggle']({ ok: true, state: assistState });
      delete assistResolvers['toggle'];
    }
    if (assistResolvers['status']) {
      assistResolvers['status'](assistState);
      delete assistResolvers['status'];
    }
    mainWindow?.webContents.send('assist_update', assistState);
    overlayWindow?.webContents.send('assist_update', assistState);
  } else if (msg.type === 'assist_build_result') {
    if (assistResolvers['build']) {
      assistResolvers['build'](msg);
      delete assistResolvers['build'];
    }
  }
}

// ─── Global Hotkeys ───
function toAccelerator(key) {
  if (!key) return null;
  let str = String(key).trim();
  const upper = str.toUpperCase();
  if (upper.startsWith('NUMPAD')) {
    return 'num' + upper.replace('NUMPAD', '');
  }
  if (upper === 'SPACE') return 'Space';
  return str;
}

function registerGlobalHotkeys() {
  globalShortcut.unregisterAll();
  if (hotkeysPauseTimer) {
    clearTimeout(hotkeysPauseTimer);
    hotkeysPauseTimer = null;
  }
  hotkeysPaused = false;
  sendPythonCommand({ cmd: 'pause_hotkeys', paused: false });

  // Sync hotkeys with Python bridge's native GetAsyncKeyState listener
  // to avoid key intercept conflicts and duplicate triggers with game input
  sendPythonCommand({
    cmd: 'set_hotkeys',
    play: config.hotkey_play || 'F4',
    stop: config.hotkey_stop || 'F5'
  });
  console.log(`[PianiPia V8 Hotkeys] Synchronized Play/Stop hotkeys to native background engine: ${config.hotkey_play || 'F4'} / ${config.hotkey_stop || 'F5'}`);
}

let lastPlayTriggerTime = 0;
function triggerPlayPause() {
  const now = Date.now();
  if (now - lastPlayTriggerTime < 500) {
    console.log('[PianiPia V8] Debounce: ignored duplicate play trigger');
    return;
  }
  lastPlayTriggerTime = now;

  if (playerState.is_playing) {
    sendPythonCommand({ cmd: 'pause_resume' });
  } else {
    let songToPlay = playerState.current_song;
    if (!songToPlay || songToPlay === 'None') {
      if (playerState.queue && playerState.queue.length > 0) {
        songToPlay = playerState.queue[0];
      }
    }


    if (songToPlay && songToPlay !== 'None') {
      const fullPath = path.join(config.note_folder, songToPlay);
      if (!fs.existsSync(fullPath)) {
        mainWindow?.webContents.send('app_log', {
          text: `Song file not found on disk: ${songToPlay}`,
          type: 'error'
        });
        console.warn(`[PianiPia V8] Playback aborted: file not found (${fullPath})`);
        return;
      }
      sendPythonCommand({
        cmd: 'play',
        path: fullPath,
        speed: playerState.speed,
        snap: playerState.snap,
        seek: 0,
        loop: playerState.loop
      });
      console.log(`[PianiPia V8] Playback started: ${songToPlay}`);
    } else {
      mainWindow?.webContents.send('app_log', {
        text: 'Play hotkey pressed, but no song is selected.',
        type: 'warning'
      });
      console.warn('[PianiPia V8] Play hotkey pressed, but no song is selected.');
    }
  }
}

let lastStopTriggerTime = 0;
function triggerStop() {
  const now = Date.now();
  if (now - lastStopTriggerTime < 500) {
    console.log('[PianiPia V8] Debounce: ignored duplicate stop trigger');
    return;
  }
  lastStopTriggerTime = now;
  sendPythonCommand({ cmd: 'stop' });
}

let overlayWindow = null;
let overlayCenter = null;

function getOverlayBounds(mode = 'compact') {
  const primaryDisplay = screen.getPrimaryDisplay();
  const workArea = primaryDisplay.workArea;

  if (!overlayCenter) {
    if (config.overlay_center && typeof config.overlay_center.cx === 'number' && typeof config.overlay_center.cy === 'number') {
      overlayCenter = config.overlay_center;
    } else {
      overlayCenter = {
        cx: Math.floor(workArea.x + workArea.width / 2),
        cy: workArea.y + 35
      };
    }
  }

  let islandWidth = 330;
  let islandHeight = 46;

  if (mode === 'dot') {
    islandWidth = 44;
    islandHeight = 44;
  } else if (mode === 'expanded' || mode === true) {
    islandWidth = 450;
    islandHeight = 172;
  }

  let x = Math.round(overlayCenter.cx - islandWidth / 2);
  let y = Math.round(overlayCenter.cy - islandHeight / 2);

  x = Math.max(workArea.x, Math.min(workArea.x + workArea.width - islandWidth, x));
  y = Math.max(workArea.y, Math.min(workArea.y + workArea.height - islandHeight, y));

  return { x, y, width: islandWidth, height: islandHeight };
}

function createOverlayWindow() {
  if (overlayWindow && !overlayWindow.isDestroyed()) {
    overlayWindow.show();
    return overlayWindow;
  }

  const bounds = getOverlayBounds('dot');

  overlayWindow = new BrowserWindow({
    width: bounds.width,
    height: bounds.height,
    x: bounds.x,
    y: bounds.y,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    skipTaskbar: true,
    resizable: false,
    hasShadow: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      webSecurity: false
    },
    show: false
  });

  overlayWindow.setAlwaysOnTop(true, 'screen-saver', 1);
  overlayWindow.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true });
  overlayWindow.loadFile(path.join(__dirname, 'renderer', 'overlay.html'));

  overlayWindow.on('moved', () => {
    if (!overlayWindow || overlayWindow.isDestroyed()) return;
    const b = overlayWindow.getBounds();
    overlayCenter = {
      cx: Math.round(b.x + b.width / 2),
      cy: Math.round(b.y + b.height / 2)
    };
    config.overlay_center = overlayCenter;
    saveConfig();
  });

  overlayWindow.once('ready-to-show', () => {
    overlayWindow.show();
    overlayWindow.webContents.send('sync_state', {
      player: playerState,
      assist: assistState
    });
    overlayWindow.webContents.send('sync_theme', config.theme || 'dark');
    mainWindow?.webContents.send('overlay_status_changed', true);
  });

  overlayWindow.on('closed', () => {
    overlayWindow = null;
    mainWindow?.webContents.send('overlay_status_changed', false);
  });

  return overlayWindow;
}

function toggleOverlayWindow() {
  if (!overlayWindow || overlayWindow.isDestroyed()) {
    createOverlayWindow();
    mainWindow?.webContents.send('overlay_status_changed', true);
    return { active: true };
  }

  if (overlayWindow.isVisible()) {
    overlayWindow.hide();
    mainWindow?.webContents.send('overlay_status_changed', false);
    return { active: false };
  } else {
    overlayWindow.show();
    overlayWindow.webContents.send('sync_state', {
      player: playerState,
      assist: assistState
    });
    overlayWindow.webContents.send('sync_theme', config.theme || 'dark');
    mainWindow?.webContents.send('overlay_status_changed', true);
    return { active: true };
  }
}

// ─── Window Creation ───
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 480,
    minHeight: 360,
    frame: false,
    transparent: false,
    backgroundColor: '#0a0c14',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true,
      webSecurity: false
    },
    icon: path.join(__dirname, 'logo.ico'),
    show: false
  });

  mainWindow.loadFile('renderer/index.html');

  mainWindow.webContents.on('console-message', (event) => {
    console.log(`[Renderer]: ${event.message || event}`);
  });

  mainWindow.on('maximize', () => {
    mainWindow?.webContents.send('window:state_changed', { isMaximized: true });
  });

  mainWindow.on('unmaximize', () => {
    mainWindow?.webContents.send('window:state_changed', { isMaximized: false });
  });

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  mainWindow.on('closed', () => {
    if (overlayWindow && !overlayWindow.isDestroyed()) {
      overlayWindow.close();
    }
    mainWindow = null;
    stopPythonBridge();
  });
}

// ─── IPC Handlers ───
function setupIPC() {
  // Window controls
  ipcMain.handle('window:minimize', () => mainWindow?.minimize());
  ipcMain.handle('window:maximize', () => {
    if (!mainWindow) return false;
    if (mainWindow.isMaximized()) {
      mainWindow.unmaximize();
      return false;
    } else {
      mainWindow.maximize();
      return true;
    }
  });
  ipcMain.handle('window:close', () => {
    app.quit();
  });
  ipcMain.handle('window:isMaximized', () => mainWindow?.isMaximized());
  ipcMain.handle('hotkeys:pause', (_, paused) => {
    if (hotkeysPauseTimer) {
      clearTimeout(hotkeysPauseTimer);
      hotkeysPauseTimer = null;
    }
    hotkeysPaused = !!paused;
    if (hotkeysPaused) {
      hotkeysPauseTimer = setTimeout(() => {
        hotkeysPaused = false;
        sendPythonCommand({ cmd: 'pause_hotkeys', paused: false });
      }, 5000);
    }
    sendPythonCommand({ cmd: 'pause_hotkeys', paused: hotkeysPaused });
    return { ok: true, paused: hotkeysPaused };
  });

  // Windows 11 Snap Layouts
  ipcMain.handle('window:snap', (_, { zone }) => {
    if (!mainWindow) return { ok: false };
    if (mainWindow.isMaximized()) mainWindow.unmaximize();
    const currentBounds = mainWindow.getBounds();
    const currentDisplay = screen.getDisplayMatching(currentBounds);
    const { x, y, width, height } = currentDisplay.workArea;

    let targetBounds = null;
    switch (zone) {
      case 'left-half':
        targetBounds = { x, y, width: Math.floor(width / 2), height };
        break;
      case 'right-half':
        targetBounds = { x: x + Math.floor(width / 2), y, width: Math.ceil(width / 2), height };
        break;
      case 'left-two-thirds':
        targetBounds = { x, y, width: Math.floor(width * 0.67), height };
        break;
      case 'right-one-third':
        targetBounds = { x: x + Math.floor(width * 0.67), y, width: Math.ceil(width * 0.33), height };
        break;
      case 'col-left':
        targetBounds = { x, y, width: Math.floor(width * 0.25), height };
        break;
      case 'col-center':
        targetBounds = { x: x + Math.floor(width * 0.25), y, width: Math.floor(width * 0.5), height };
        break;
      case 'col-right':
        targetBounds = { x: x + Math.floor(width * 0.75), y, width: Math.ceil(width * 0.25), height };
        break;
      case 'quad-tl':
        targetBounds = { x, y, width: Math.floor(width / 2), height: Math.floor(height / 2) };
        break;
      case 'quad-tr':
        targetBounds = { x: x + Math.floor(width / 2), y, width: Math.ceil(width / 2), height: Math.floor(height / 2) };
        break;
      case 'quad-bl':
        targetBounds = { x, y: y + Math.floor(height / 2), width: Math.floor(width / 2), height: Math.ceil(height / 2) };
        break;
      case 'quad-br':
        targetBounds = { x: x + Math.floor(width / 2), y: y + Math.floor(height / 2), width: Math.ceil(width / 2), height: Math.ceil(height / 2) };
        break;
      default:
        return { ok: false };
    }
    if (targetBounds) {
      mainWindow.setBounds(targetBounds, true);
      return { ok: true };
    }
    return { ok: false };
  });

  // Dynamic Island Overlay Controls
  ipcMain.handle('overlay:toggle', () => toggleOverlayWindow());
  ipcMain.handle('overlay:status', () => !!(overlayWindow && !overlayWindow.isDestroyed() && overlayWindow.isVisible()));
  ipcMain.handle('overlay:playPause', () => triggerPlayPause());
  ipcMain.handle('overlay:stop', () => triggerStop());
  ipcMain.handle('overlay:toggleFeature', (_, feat) => {
    sendPythonCommand({ cmd: 'assist_toggle', feature: feat });
  });
  ipcMain.handle('overlay:focusMain', () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.show();
      mainWindow.focus();
    }
  });
  ipcMain.handle('overlay:close', () => {
    if (overlayWindow && !overlayWindow.isDestroyed()) {
      overlayWindow.hide();
      mainWindow?.webContents.send('overlay_status_changed', false);
    }
    return { active: false };
  });

  ipcMain.on('overlay:setMode', (_, mode) => {
    if (overlayWindow && !overlayWindow.isDestroyed()) {
      overlayWindow.setBounds(getOverlayBounds(mode));
    }
  });

  ipcMain.on('overlay:setExpanded', (_, expanded) => {
    if (overlayWindow && !overlayWindow.isDestroyed()) {
      overlayWindow.setBounds(getOverlayBounds(expanded ? 'expanded' : 'compact'));
    }
  });

  ipcMain.on('overlay:ignoreMouse', (_, ignore) => {
    if (overlayWindow && !overlayWindow.isDestroyed()) {
      overlayWindow.setIgnoreMouseEvents(ignore, { forward: true });
    }
  });

  // Config
  const handleSaveConfig = (_, data) => {
    Object.assign(config, data);
    saveConfig();
    registerGlobalHotkeys();
    return { ok: true };
  };
  ipcMain.handle('config:get', () => config);
  ipcMain.handle('config:save', handleSaveConfig);
  ipcMain.handle('config:set', handleSaveConfig);
  ipcMain.handle('config:saveTheme', (_, theme) => {
    config.theme = theme;
    saveConfig();
    if (overlayWindow && !overlayWindow.isDestroyed()) {
      overlayWindow.webContents.send('sync_theme', theme);
    }
    return { ok: true };
  });

  // Songs
  ipcMain.handle('songs:list', () => {
    let folder = config.note_folder;
    if (!folder || !fs.existsSync(folder)) {
      const fallback = 'C:/Users/Skylark/Downloads/Notes';
      if (fs.existsSync(fallback)) {
        folder = fallback;
        config.note_folder = fallback;
        saveConfig();
      }
    }

    const songs = [];
    if (folder && fs.existsSync(folder)) {
      try {
        const files = fs.readdirSync(folder);
        for (const f of files) {
          if (f.endsWith('.txt')) {
            try {
              const fp = path.join(folder, f);
              const stat = fs.statSync(fp);
              songs.push({ name: f, mtime: stat.mtimeMs / 1000 });
            } catch (err) {
              songs.push({ name: f, mtime: 0 });
            }
          }
        }
      } catch (e) {
        console.error('Error reading songs folder:', e);
      }
    }
    console.log(`[IPC songs:list] Returning ${songs.length} songs from folder: ${folder}`);
    return { songs, favorites, queue: config.queue || [] };
  });

  ipcMain.handle('songs:select', (_, filename) => {
    playerState.current_song = filename;
    return { ok: true };
  });

  ipcMain.handle('songs:previewContent', async (_, filename, source) => {
    try {
      let fn = filename.endsWith('.txt') ? filename : filename + '.txt';
      const filePath = path.join(config.note_folder, fn);
      if (fs.existsSync(filePath)) {
        return { ok: true, data: fs.readFileSync(filePath, 'utf-8') };
      }
      // Try online from Supabase if requested
      if (supabase) {
        const cleanName = filename.replace(/\.txt$/, '').trim();
        const { data } = await supabase
          .from('HeartopiaMIDI_CommunitySongs')
          .select('song_data')
          .eq('song_name', cleanName)
          .limit(1);
        if (data && data.length > 0) {
          return { ok: true, data: data[0].song_data };
        }
      }
    } catch (e) {
      console.error(e);
    }
    return { ok: false, error: 'Could not load song' };
  });

  ipcMain.handle('songs:get', async (_, filename) => {
    try {
      let fn = filename.endsWith('.txt') ? filename : filename + '.txt';
      const filePath = path.join(config.note_folder, fn);
      if (fs.existsSync(filePath)) {
        return { ok: true, content: fs.readFileSync(filePath, 'utf-8'), data: fs.readFileSync(filePath, 'utf-8') };
      }
      if (supabase) {
        const cleanName = filename.replace(/\.txt$/, '').trim();
        const { data } = await supabase
          .from('HeartopiaMIDI_CommunitySongs')
          .select('song_data')
          .eq('song_name', cleanName)
          .limit(1);
        if (data && data.length > 0) {
          return { ok: true, content: data[0].song_data, data: data[0].song_data };
        }
      }
    } catch (e) {
      console.error('songs:get error:', e);
    }
    return { ok: false, content: '', error: 'Could not load song' };
  });

  ipcMain.handle('songs:save', (_, { filename, content }) => {
    try {
      let fn = filename.endsWith('.txt') ? filename : filename + '.txt';
      const fp = path.join(config.note_folder, fn);
      fs.writeFileSync(fp, content, 'utf-8');
      return { ok: true };
    } catch (e) {
      return { ok: false, error: e.message };
    }
  });

  ipcMain.handle('songs:saveContent', (_, filename, data) => {
    try {
      let fn = filename.endsWith('.txt') ? filename : filename + '.txt';
      const fp = path.join(config.note_folder, fn);
      fs.writeFileSync(fp, data, 'utf-8');
      return { ok: true };
    } catch (e) {
      return { ok: false, error: e.message };
    }
  });

  ipcMain.handle('songs:delete', (_, filename) => {
    try {
      const p = path.join(config.note_folder, filename);
      if (fs.existsSync(p)) fs.unlinkSync(p);
      return { ok: true };
    } catch (e) {
      return { ok: false };
    }
  });

  ipcMain.handle('songs:deleteBatch', (_, filenames) => {
    let count = 0;
    for (let n of filenames) {
      n = n.replace(/^['"]|['"]$/g, '');
      let p = path.join(config.note_folder, n);
      if (fs.existsSync(p)) {
        fs.unlinkSync(p);
        count++;
      } else if (!p.endsWith('.txt')) {
        p += '.txt';
        if (fs.existsSync(p)) {
          fs.unlinkSync(p);
          count++;
        }
      }
    }
    return { ok: true, count };
  });

  // Favorites
  ipcMain.handle('songs:toggleFav', (_, filename) => {
    const idx = favorites.indexOf(filename);
    if (idx >= 0) favorites.splice(idx, 1);
    else favorites.push(filename);
    saveFavorites();
    return { ok: true };
  });

  // Queue
  ipcMain.handle('queue:update', (_, newQueue) => {
    playerState.queue = newQueue;
    config.queue = newQueue;
    saveConfig();
    return { ok: true };
  });

  // Player controls
  ipcMain.handle('player:getStatus', () => playerState);

  ipcMain.handle('player:setParams', (_, data) => {
    if (data.speed !== undefined) playerState.speed = parseFloat(data.speed);
    if (data.snap !== undefined) playerState.snap = parseInt(data.snap);
    if (data.loop !== undefined) playerState.loop = Boolean(data.loop);
    sendPythonCommand({
      cmd: 'update_params',
      speed: playerState.speed,
      snap: playerState.snap,
      loop: playerState.loop
    });
    return { ok: true };
  });

  ipcMain.handle('player:play', (_, data) => {
    if (playerState.is_playing) {
      sendPythonCommand({ cmd: 'pause_resume' });
      return { ok: true };
    }

    let song = data?.song || playerState.current_song;
    if (!song || song === 'None') {
      if (playerState.queue && playerState.queue.length > 0) {
        song = playerState.queue[0];
      }
    }

    if (!song || song === 'None') return { ok: false, error: 'No song selected' };

    playerState.current_song = song;
    if (data?.speed) playerState.speed = parseFloat(data.speed);
    if (data?.snap) playerState.snap = parseInt(data.snap);
    if (data?.loop !== undefined) playerState.loop = Boolean(data.loop);

    const fullPath = path.join(config.note_folder, song);
    if (!fs.existsSync(fullPath)) {
      console.warn(`[PianiPia V8] Playback aborted: file not found (${fullPath})`);
      return { ok: false, error: `File not found on disk: ${song}` };
    }
    sendPythonCommand({
      cmd: 'play',
      path: fullPath,
      speed: playerState.speed,
      snap: playerState.snap,
      seek: data?.seek || 0,
      loop: playerState.loop
    });
    return { ok: true };
  });

  ipcMain.handle('player:stop', () => {
    sendPythonCommand({ cmd: 'stop' });
    return { ok: true };
  });

  // Browse folder
  ipcMain.handle('dialog:browseFolder', async () => {
    const result = await dialog.showOpenDialog(mainWindow, {
      properties: ['openDirectory']
    });
    if (result.canceled) return null;
    const selected = result.filePaths[0];
    config.note_folder = selected;
    saveConfig();
    return selected;
  });

  // Browse MIDI files
  ipcMain.handle('dialog:browseMidi', async () => {
    const result = await dialog.showOpenDialog(mainWindow, {
      properties: ['openFile', 'multiSelections'],
      filters: [{ name: 'MIDI Files', extensions: ['mid', 'midi'] }]
    });
    if (result.canceled) return [];
    return result.filePaths;
  });

  // Convert MIDI files
  ipcMain.handle('converter:run', (_, data) => {
    sendPythonCommand({
      cmd: 'convert',
      files: data.files,
      target: data.target,
      pitch: data.pitch,
      folder: config.note_folder
    });
    return { ok: true };
  });

  // Online (Supabase)
  ipcMain.handle('online:search', async (_, query, type, page, perPage) => {
    try {
      if (!supabase) initSupabase();
      if (!supabase) return { songs: [], total: 0, page };

      const curPage = Math.max(1, parseInt(page) || 1);
      const limit = Math.max(10, parseInt(perPage) || 50);
      const start = (curPage - 1) * limit;
      const end = start + limit - 1;

      let q = supabase
        .from('HeartopiaMIDI_CommunitySongs')
        .select('song_name, instrument_type, created_at', { count: 'exact' });

      if (query && query.trim()) {
        q = q.ilike('song_name', `%${query.trim()}%`);
      }
      if (type && type !== 'All') {
        q = q.ilike('instrument_type', type === '15K' ? '%15%' : '%22%');
      }

      const { data, count, error } = await q.order('created_at', { ascending: false }).range(start, end);
      if (error) {
        console.error('Supabase query error:', error);
        throw error;
      }
      console.log(`[IPC online:search] Query "${query}" returned ${data?.length || 0} songs (Total: ${count})`);
      return { songs: data || [], total: count || 0, page: curPage };
    } catch (e) {
      console.error('Online search error:', e);
      return { songs: [], total: 0, page: 1, error: e.message };
    }
  });

  ipcMain.handle('online:download', async (_, name) => {
    try {
      if (!supabase) return { ok: false };
      const { data } = await supabase.from('HeartopiaMIDI_CommunitySongs')
        .select('*').eq('song_name', name).limit(1);
      if (data && data.length > 0) {
        const safeName = name.replace(/[\\/*?:"<>|]/g, '').trim();
        const fileName = safeName.toLowerCase().endsWith('.txt') ? safeName : `${safeName}.txt`;
        const fp = path.join(config.note_folder, fileName);
        fs.writeFileSync(fp, data[0].song_data, 'utf-8');
        return { ok: true };
      }
    } catch (e) { console.error('Download single error:', e); }
    return { ok: false };
  });

  ipcMain.handle('online:downloadBatch', async (_, names) => {
    let success = 0, failed = 0;
    try {
      if (!supabase) return { success: 0, failed: names.length };
      for (const n of names) {
        try {
          const { data } = await supabase.from('HeartopiaMIDI_CommunitySongs')
            .select('*').eq('song_name', n).limit(1);
          if (data && data.length > 0) {
            const safeName = n.replace(/[\\/*?:"<>|]/g, '').trim();
            const fileName = safeName.toLowerCase().endsWith('.txt') ? safeName : `${safeName}.txt`;
            fs.writeFileSync(path.join(config.note_folder, fileName), data[0].song_data, 'utf-8');
            success++;
          } else { failed++; }
        } catch (e) { failed++; }
      }
    } catch (e) { failed = names.length; }
    return { success, failed };
  });

  ipcMain.handle('online:upload', async (_, files) => {
    let uploaded = 0, duplicates = 0, errors = 0;
    try {
      if (!supabase) return { uploaded: 0, duplicates: 0, errors: files.length };
      for (const file of files) {
        try {
          if (file.size > 512000 || !file.name.toLowerCase().endsWith('.txt')) { errors++; continue; }
          let nm = file.name.replace(/\.txt$/i, '').replace(/[\\/*?:"<>|]/g, '').trim();
          if (!nm) { errors++; continue; }
          if (nm.length > 150) nm = nm.substring(0, 150);
          const txt = file.content;
          if (!txt.includes('DELAY') && !txt.includes('Keyboard')) { errors++; continue; }
          const { data: existing } = await supabase.from('HeartopiaMIDI_CommunitySongs')
            .select('id').eq('song_name', nm).limit(1);
          if (existing && existing.length > 0) { duplicates++; continue; }
          await supabase.from('HeartopiaMIDI_CommunitySongs').insert({
            song_name: nm,
            song_data: txt,
            instrument_type: nm.includes('15K') ? '15-Keys' : '22-Keys'
          });
          uploaded++;
        } catch (e) { errors++; }
      }
    } catch (e) { errors = files.length; }
    return { uploaded, duplicates, errors };
  });

  // Maps
  ipcMain.handle('maps:get', () => ({
    MAP_22, MAP_15, REVERSE_MAP_22, REVERSE_MAP_15
  }));

  // ─── Assist Automation IPC ───
  ipcMain.handle('assist:status', async () => {
    return new Promise(resolve => {
      assistResolvers['status'] = resolve;
      sendPythonCommand({ cmd: 'assist_status' });
      setTimeout(() => resolve(assistState), 600);
    });
  });

  ipcMain.handle('assist:getWindows', async () => {
    return new Promise(resolve => {
      assistResolvers['getWindows'] = resolve;
      sendPythonCommand({ cmd: 'assist_get_windows' });
      setTimeout(() => resolve({ windows: ['Heartopia'] }), 800);
    });
  });

  ipcMain.handle('assist:connect', async (_, windowName) => {
    return new Promise(resolve => {
      assistResolvers['connect'] = resolve;
      sendPythonCommand({ cmd: 'assist_connect', window: windowName || 'Heartopia' });
      setTimeout(() => resolve({ connected: false }), 1000);
    });
  });

  ipcMain.handle('assist:disconnect', async () => {
    return new Promise(resolve => {
      assistResolvers['disconnect'] = resolve;
      sendPythonCommand({ cmd: 'assist_disconnect' });
      setTimeout(() => resolve({ ok: true }), 500);
    });
  });

  ipcMain.handle('assist:toggle', async (_, feature) => {
    return new Promise(resolve => {
      if (!assistResolvers['toggle']) assistResolvers['toggle'] = [];
      let resolved = false;
      const safeResolve = (res) => {
        if (!resolved) {
          resolved = true;
          resolve(res);
        }
      };
      assistResolvers['toggle'].push(safeResolve);
      sendPythonCommand({ cmd: 'assist_toggle', feature });
      setTimeout(() => safeResolve({ ok: true, state: assistState }), 600);
    });
  });

  ipcMain.handle('assist:buildGlitch', async () => {
    return new Promise(resolve => {
      assistResolvers['build'] = resolve;
      sendPythonCommand({ cmd: 'assist_build_glitch' });
      setTimeout(() => resolve({ ok: true }), 1000);
    });
  });

  ipcMain.handle('assist:updateConfig', (_, cfg) => {
    sendPythonCommand({ cmd: 'assist_update_config', ...cfg });
    return { ok: true };
  });

  ipcMain.handle('assist:setImages', (_, images) => {
    sendPythonCommand({ cmd: 'assist_set_images', images });
    return { ok: true };
  });

  ipcMain.handle('assist:setHarvestImages', (_, images) => {
    sendPythonCommand({ cmd: 'assist_set_harvest_images', images });
    return { ok: true };
  });

  ipcMain.handle('assist:getDefaultHarvestImages', () => {
    const primaryDir = findReferenceDir('Tree&Rock&BushReference');
    let targets = [];
    if (fs.existsSync(primaryDir)) {
      try {
        const files = fs.readdirSync(primaryDir);
        targets = files
          .filter(f => /\.(png|jpg|jpeg|bmp|webp)$/i.test(f))
          .map(f => path.join(primaryDir, f));
      } catch (e) {
        console.error('Error reading Tree&Rock&BushReference:', e);
      }
    }
    if (targets.length === 0) {
      const fallbackDir = findReferenceDir('Tree&RockReference');
      if (fs.existsSync(fallbackDir)) {
        try {
          const files = fs.readdirSync(fallbackDir);
          targets = files
            .filter(f => /\.(png|jpg|jpeg|bmp|webp)$/i.test(f))
            .map(f => path.join(fallbackDir, f));
        } catch (e) {}
      }
    }
    return targets;
  });

  ipcMain.handle('assist:getDefaultCookImages', () => {
    const cookDir = findReferenceDir('CookingReference');
    return {
      stove: path.join(cookDir, 'stove.png'),
      start: path.join(cookDir, 'start_cooking.png'),
      heat: path.join(cookDir, 'heat.png'),
      serve: path.join(cookDir, 'served.png'),
      recipe: path.join(cookDir, 'recipe.png')
    };
  });

  ipcMain.handle('assist:getDefaultSnowImages', () => {
    const snowDir = findReferenceDir('SnowReference');
    return {
      snow_add: path.join(snowDir, 'add_snow.png'),
      snow_start: path.join(snowDir, 'start_snow.png'),
      snow_puzzle: path.join(snowDir, 'snow_puzzle.png'),
      snow_get: path.join(snowDir, 'get_snow.png')
    };
  });

  ipcMain.handle('dialog:browseImages', async () => {
    const result = await dialog.showOpenDialog(mainWindow, {
      properties: ['openFile', 'multiSelections'],
      filters: [{ name: 'Image Files', extensions: ['png', 'jpg', 'jpeg', 'bmp', 'webp'] }]
    });
    if (result.canceled) return [];
    return result.filePaths;
  });

  ipcMain.handle('dialog:browseImage', async () => {
    const result = await dialog.showOpenDialog(mainWindow, {
      properties: ['openFile'],
      filters: [{ name: 'Image Files', extensions: ['png', 'jpg', 'jpeg', 'bmp', 'webp'] }]
    });
    if (result.canceled || !result.filePaths.length) return null;
    return result.filePaths[0];
  });

  ipcMain.handle('assist:setHotkey', (_, { feature, key, vk }) => {
    config[`${feature}_hotkey`] = vk;
    saveConfig();
    sendPythonCommand({
      cmd: 'assist_update_hotkeys',
      hotkeys: { [feature]: vk }
    });
    return { ok: true, feature, key, vk };
  });
}

// ─── App Lifecycle ───
app.whenReady().then(() => {
  loadConfig();
  loadFavorites();
  initSupabase();
  startPythonBridge();

  if (config.note_folder && !fs.existsSync(config.note_folder)) {
    try { fs.mkdirSync(config.note_folder, { recursive: true }); } catch(e) {}
  }

  createWindow();
  setupIPC();
  registerGlobalHotkeys();
});

app.on('will-quit', () => {
  globalShortcut.unregisterAll();
  stopPythonBridge();
});

app.on('window-all-closed', () => {
  app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
