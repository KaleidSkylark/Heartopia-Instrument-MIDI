// ═══════════════════════════════════════════════════════════════════
// Module: Common State, Maps & Modal Utilities
// ═══════════════════════════════════════════════════════════════════

var electron = (window.nodeRequire || window.require)('electron');
var ipcRenderer = electron.ipcRenderer;
window.ipcRenderer = ipcRenderer;

// ─── Global State ───
window.allSongs = [];
window.favorites = [];
window.queue = [];
window.currentSong = null;
window.currentSongSource = 'local';
window.onlineLoaded = false;
window.searchTimeout = null;
window.currentPlaylistFilter = 'All';
window.currentOnlineFilter = 'All';
window.tempHotkeys = { play: 'F4', stop: 'F5' };
window.isListening = null;
window.confirmCallback = null;

window.cachedSongData = null;
window.monacoEditor = null;
window.decorations = [];

window.currentPage = 1;
window.totalItems = 0;
window.itemsPerPage = 50;

// Conversion files
window.selectedMidiFiles = [];

// Key Maps
window.MAP_22 = {};
window.MAP_15 = {};
window.MAP_22_REV = {};
window.MAP_15_REV = {};

async function initMaps() {
  try {
    const maps = await ipcRenderer.invoke('maps:get');
    if (maps) {
      window.MAP_22 = maps.MAP_22 || {};
      window.MAP_15 = maps.MAP_15 || {};
      window.MAP_22_REV = maps.REVERSE_MAP_22 || {};
      window.MAP_15_REV = maps.REVERSE_MAP_15 || {};
    }
  } catch (e) {
    console.error('Failed to get maps:', e);
  }
}

// ─── Modals ───
function showModal(title, message) {
  const t = document.getElementById('modal-title');
  const b = document.getElementById('modal-body');
  if (t) t.innerText = title;
  if (b) b.innerText = message;
  const m = document.getElementById('custom-modal');
  if (m) {
    m.classList.add('active');
    m.style.display = 'flex';
  }
}

function closeModal() {
  const m = document.getElementById('custom-modal');
  if (m) {
    m.classList.remove('active');
    m.style.display = 'none';
  }
}

function showConfirm(title, message, callback) {
  const t = document.getElementById('confirm-title');
  const b = document.getElementById('confirm-body');
  if (t) t.innerText = title;
  if (b) b.innerText = message;
  window.confirmCallback = callback;
  const m = document.getElementById('custom-confirm');
  if (m) {
    m.classList.add('active');
    m.style.display = 'flex';
  }
}

function confirmYes() {
  const m = document.getElementById('custom-confirm');
  if (m) {
    m.classList.remove('active');
    m.style.display = 'none';
  }
  if (window.confirmCallback) {
    window.confirmCallback();
    window.confirmCallback = null;
  }
}

function confirmNo() {
  const m = document.getElementById('custom-confirm');
  if (m) {
    m.classList.remove('active');
    m.style.display = 'none';
  }
  window.confirmCallback = null;
}

function showExitModal() {
  const m = document.getElementById('exit-modal');
  if (m) {
    m.classList.add('active');
    m.style.display = 'flex';
  }
}

function finalizeExit() {
  ipcRenderer.invoke('window:close');
}

// ─── App Logger & Console ───
function appLog(msg, type = 'info') {
  console.log(`[PianiPia V8] [${type.toUpperCase()}] ${msg}`);
  const consoleEl = document.getElementById('app-console');
  if (consoleEl) {
    const m = String(msg).toLowerCase();
    if (m.includes('error') || m.includes('fail') || m.includes('❌')) type = 'error';
    else if (m.includes('success') || m.includes('complete') || m.includes('loaded') || m.includes('saved') || m.includes('✅')) type = 'success';

    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;

    let icon = 'ℹ';
    if (type === 'success') icon = '✔';
    if (type === 'error') icon = '✖';
    if (m.includes('play')) icon = '▶';
    if (m.includes('stop')) icon = '⏹';
    if (m.includes('downl')) icon = '⬇';
    if (m.includes('upload')) icon = '⬆';

    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    entry.innerHTML = `
      <div class="log-header">
        <span>${icon} ${type.toUpperCase()}</span>
        <span>${timeStr}</span>
      </div>
      <div class="log-body">${escapeHtml(msg)}</div>
    `;

    consoleEl.appendChild(entry);
    consoleEl.scrollTop = consoleEl.scrollHeight;

    while (consoleEl.children.length > 50) {
      consoleEl.removeChild(consoleEl.firstChild);
    }
  }
}

function clearConsole() {
  const consoleEl = document.getElementById('app-console');
  if (consoleEl) consoleEl.innerHTML = '';
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function escapeJs(str) {
  if (!str) return '';
  return String(str)
    .replace(/\\/g, '\\\\')
    .replace(/'/g, "\\'")
    .replace(/"/g, '\\"');
}

function formatTime(seconds) {
  if (isNaN(seconds) || seconds < 0) return '0:00';
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s < 10 ? '0' : ''}${s}`;
}

// Auto-blur clicked buttons so key presses never re-trigger them
window.addEventListener('mouseup', (e) => {
  const btn = e.target && e.target.closest ? e.target.closest('button, .nav-btn, .btn-neu') : null;
  if (btn && typeof btn.blur === 'function') {
    btn.blur();
  }
});

// Expose globally on window
window.ipcRenderer = ipcRenderer;
window.initMaps = initMaps;
window.showModal = showModal;
window.closeModal = closeModal;
window.showConfirm = showConfirm;
window.confirmYes = confirmYes;
window.confirmNo = confirmNo;
window.showExitModal = showExitModal;
window.finalizeExit = finalizeExit;
window.appLog = appLog;
window.clearConsole = clearConsole;
window.escapeHtml = escapeHtml;
window.escapeJs = escapeJs;
window.formatTime = formatTime;

