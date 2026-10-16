// ═══════════════════════════════════════════════════════════════════
// Module: Application Settings & Global Hotkeys
// ═══════════════════════════════════════════════════════════════════

function displayKeyName(key) {
  if (!key) return 'None';
  let str = String(key).trim().toUpperCase();
  if (str.startsWith('NUMPAD')) {
    const num = str.replace('NUMPAD', '').trim();
    return `NUMPAD ${num}`;
  }
  return str;
}

function formatKeyFromEvent(e) {
  // Check e.code first to detect Numpad regardless of NumLock state
  if (e.code && e.code.startsWith('Numpad')) {
    const code = e.code;
    if (code === 'Numpad0') return 'NUMPAD0';
    if (code === 'Numpad1') return 'NUMPAD1';
    if (code === 'Numpad2') return 'NUMPAD2';
    if (code === 'Numpad3') return 'NUMPAD3';
    if (code === 'Numpad4') return 'NUMPAD4';
    if (code === 'Numpad5') return 'NUMPAD5';
    if (code === 'Numpad6') return 'NUMPAD6';
    if (code === 'Numpad7') return 'NUMPAD7';
    if (code === 'Numpad8') return 'NUMPAD8';
    if (code === 'Numpad9') return 'NUMPAD9';
    if (code === 'NumpadAdd') return 'NUMPAD+';
    if (code === 'NumpadSubtract') return 'NUMPAD-';
    if (code === 'NumpadMultiply') return 'NUMPAD*';
    if (code === 'NumpadDivide') return 'NUMPAD/';
    if (code === 'NumpadDecimal') return 'NUMPAD.';
    if (code === 'NumpadEnter') return 'NUMPADENTER';
    return code.toUpperCase();
  }

  let key = (e.key || '').toUpperCase();
  if (key === ' ' || e.code === 'Space') return 'SPACE';
  if (key.startsWith('ARROW')) return key.replace('ARROW', '');
  return key;
}

async function loadSettings() {
  try {
    const conf = await ipcRenderer.invoke('config:get');
    if (conf) {
      document.getElementById('set-folder').value = conf.note_folder || '';
      document.getElementById('btn-bind-play').innerText = displayKeyName(conf.hotkey_play || 'F4');
      document.getElementById('btn-bind-stop').innerText = displayKeyName(conf.hotkey_stop || 'F5');
      window.tempHotkeys.play = conf.hotkey_play || 'F4';
      window.tempHotkeys.stop = conf.hotkey_stop || 'F5';
    }
  } catch (err) {
    console.error('Failed to load settings:', err);
  }
}

async function browseFolderSafe() {
  const selected = await ipcRenderer.invoke('dialog:browseFolder');
  if (selected) {
    document.getElementById('set-folder').value = selected;
    await loadPlaylistData();
    appLog(`Song folder set to: ${selected}`, 'success');
  }
}

let activeSettingsKeyCleanup = null;

function listenForKey(action) {
  const btn = document.getElementById(`btn-bind-${action}`);
  if (!btn) return;

  if (activeSettingsKeyCleanup) {
    activeSettingsKeyCleanup();
    activeSettingsKeyCleanup = null;
  }

  // Blur any active element so keys like Space or numbers don't trigger focused buttons
  if (document.activeElement && typeof document.activeElement.blur === 'function') {
    document.activeElement.blur();
  }

  window.isListening = action;
  const originalText = btn.innerText;
  btn.innerText = 'Press any key...';
  btn.classList.add('listening');

  // Inform main process & python to pause hotkeys while rebinding
  ipcRenderer.invoke('hotkeys:pause', true);

  const cleanup = () => {
    window.removeEventListener('keydown', onKeyDown, true);
    window.removeEventListener('mousedown', onMouseDown, true);
    activeSettingsKeyCleanup = null;
    window.isListening = null;
    btn.classList.remove('listening');
    ipcRenderer.invoke('hotkeys:pause', false);
  };

  const onKeyDown = (e) => {
    e.preventDefault();
    e.stopPropagation();
    e.stopImmediatePropagation();

    const key = formatKeyFromEvent(e);
    if (key === 'ESCAPE' || key === 'ESC') {
      btn.innerText = originalText;
      cleanup();
      return;
    }

    window.tempHotkeys[action] = key;
    btn.innerText = displayKeyName(key);
    cleanup();
    appLog(`Bound ${action.toUpperCase()} hotkey to: ${displayKeyName(key)}`, 'info');
  };

  const onMouseDown = (e) => {
    if (e.target !== btn) {
      btn.innerText = originalText;
      cleanup();
    }
  };

  activeSettingsKeyCleanup = () => {
    btn.innerText = originalText;
    cleanup();
  };

  window.addEventListener('keydown', onKeyDown, { once: true, capture: true });
  window.addEventListener('mousedown', onMouseDown, { capture: true });
}

window.addEventListener('blur', () => {
  if (activeSettingsKeyCleanup) {
    activeSettingsKeyCleanup();
  }
});

async function saveSettings() {
  if (activeSettingsKeyCleanup) {
    activeSettingsKeyCleanup();
  }
  ipcRenderer.invoke('hotkeys:pause', false);

  const folder = document.getElementById('set-folder')?.value.trim();
  const play = window.tempHotkeys.play;
  const stop = window.tempHotkeys.stop;

  try {
    await ipcRenderer.invoke('config:save', {
      note_folder: folder,
      hotkey_play: play,
      hotkey_stop: stop
    });

    showModal('Saved', 'Application settings and global hotkeys saved successfully!');
    appLog(`Settings saved. Global hotkeys: Play/Pause=${displayKeyName(play)}, Stop=${displayKeyName(stop)}`, 'success');
  } catch (err) {
    showModal('Error', 'Failed to save settings: ' + err.message);
  }
}

window.loadSettings = loadSettings;
window.browseFolderSafe = browseFolderSafe;
window.listenForKey = listenForKey;
window.saveSettings = saveSettings;
window.displayKeyName = displayKeyName;
