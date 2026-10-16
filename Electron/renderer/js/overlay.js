// ═══════════════════════════════════════════════════════════════════
// Dynamic Island Overlay Controller — iPhone Style Live Island
// ═══════════════════════════════════════════════════════════════════

const { ipcRenderer } = require('electron');

let state = {
  isPlaying: false,
  isPaused: false,
  songName: 'No song loaded',
  progress: 0,
  timeElapsed: '00:00',
  timeTotal: '00:00',
  autoWalk: false,
  camLock: false,
  autoHarvest: false,
  treeRock: false
};

// DOM Elements
const island = document.getElementById('dynamic-island');
const dotView = document.getElementById('dot-view');
const compactSongTitle = document.getElementById('compact-song-title');
const compactTime = document.getElementById('compact-time');
const compactEq = document.getElementById('compact-eq');
const compactDisc = document.getElementById('compact-disc');

const indicatorWalk = document.getElementById('indicator-walk');
const indicatorCam = document.getElementById('indicator-cam');
const indicatorHarvest = document.getElementById('indicator-harvest');
const indicatorTreeRock = document.getElementById('indicator-tree_rock');

const expandedArtDisc = document.getElementById('expanded-art-disc');
const expandedSongTitle = document.getElementById('expanded-song-title');
const expandedStatusBadge = document.getElementById('expanded-status-badge');
const scrubberFill = document.getElementById('scrubber-fill');
const timeElapsedEl = document.getElementById('time-elapsed');
const timeTotalEl = document.getElementById('time-total');
const playIcon = document.getElementById('play-icon');

const btnPillWalk = document.getElementById('btn-pill-walk');
const btnPillCam = document.getElementById('btn-pill-cam');
const btnPillHarvest = document.getElementById('btn-pill-harvest');
const btnPillTreeRock = document.getElementById('btn-pill-tree_rock');

let wasPlaying = false;
let autoCollapseTimer = null;
let isHovered = false;
let currentMode = 'dot';

function isAnyActive() {
  return (
    state.isPlaying ||
    state.isPaused ||
    state.autoWalk ||
    state.camLock ||
    state.autoHarvest ||
    state.treeRock
  );
}

// ─── Mode Switching ───
function setIslandMode(mode, force = false) {
  if (currentMode === mode && !force) return;
  currentMode = mode;
  island.classList.remove('dot', 'compact', 'expanded');
  island.classList.add(mode);
  ipcRenderer.send('overlay:setMode', mode);
}

function syncIslandState() {
  if (isHovered && currentMode === 'expanded') {
    return;
  }
  if (isAnyActive()) {
    setIslandMode('compact');
  } else {
    setIslandMode('dot');
  }
}

// ─── IPC Listeners ───
ipcRenderer.on('sync_state', (_, data) => {
  if (data) {
    if (data.player) handlePlayerStatus(data.player);
    if (data.assist) handleAssistStatus(data.assist);
  }
  syncIslandState();
});

ipcRenderer.on('player_status', (_, status) => {
  handlePlayerStatus(status);
  syncIslandState();
});

ipcRenderer.on('assist_update', (_, assist) => {
  handleAssistStatus(assist);
  syncIslandState();
});

ipcRenderer.on('sync_theme', (_, theme) => {
  applyOverlayTheme(theme);
});

function applyOverlayTheme(theme) {
  if (theme === 'light') {
    document.body.classList.add('light-theme');
  } else {
    document.body.classList.remove('light-theme');
  }
}

ipcRenderer.invoke('config:get').then(conf => {
  if (conf && conf.theme) {
    applyOverlayTheme(conf.theme);
  }
}).catch(() => {});

function handlePlayerStatus(status) {
  if (!status) return;

  const newlyStarted = !wasPlaying && !!status.is_playing;
  const justStopped = wasPlaying && !status.is_playing;
  state.isPlaying = !!status.is_playing;
  state.isPaused = !!status.is_paused;
  state.songName = status.current_song || status.song_name || (state.isPlaying ? 'Playing MIDI' : 'PianiPia V8 Standby');
  state.progress = typeof status.progress === 'number' ? status.progress : 0;

  if (status.current_time_str && status.total_time_str) {
    state.timeElapsed = status.current_time_str;
    state.timeTotal = status.total_time_str;
  } else if (status.time_str && status.time_str.includes('/')) {
    const parts = status.time_str.split('/');
    state.timeElapsed = parts[0].trim();
    state.timeTotal = parts[1].trim();
  } else {
    const pct = Math.round(state.progress * 100);
    state.timeElapsed = `${pct}%`;
    state.timeTotal = state.isPlaying ? 'MIDI' : '00:00';
  }

  updateIslandUI();

  if (newlyStarted) {
    setIslandMode('expanded');
    clearTimeout(autoCollapseTimer);
    autoCollapseTimer = setTimeout(() => {
      if (!isHovered) {
        syncIslandState();
      }
    }, 3800);
  } else if (justStopped) {
    clearTimeout(autoCollapseTimer);
    autoCollapseTimer = setTimeout(() => {
      if (!isHovered) {
        syncIslandState();
      }
    }, 1200);
  }

  wasPlaying = state.isPlaying;
}

function handleAssistStatus(assist) {
  if (!assist) return;
  if (assist.walk_active !== undefined) {
    state.autoWalk = !!assist.walk_active;
    indicatorWalk?.classList.toggle('active', state.autoWalk);
    btnPillWalk?.classList.toggle('active', state.autoWalk);
  }
  if (assist.cam_active !== undefined) {
    state.camLock = !!assist.cam_active;
    indicatorCam?.classList.toggle('active', state.camLock);
    btnPillCam?.classList.toggle('active', state.camLock);
  }
  if (assist.harvest_active !== undefined) {
    state.autoHarvest = !!assist.harvest_active;
    indicatorHarvest?.classList.toggle('active', state.autoHarvest);
    btnPillHarvest?.classList.toggle('active', state.autoHarvest);
  }
  if (assist.tree_rock_active !== undefined) {
    state.treeRock = !!assist.tree_rock_active;
    indicatorTreeRock?.classList.toggle('active', state.treeRock);
    btnPillTreeRock?.classList.toggle('active', state.treeRock);
  }
}

function updateIslandUI() {
  if (compactSongTitle) {
    compactSongTitle.textContent = state.songName;
  }
  if (compactTime) {
    compactTime.textContent = state.timeElapsed;
  }
  if (compactEq) {
    compactEq.classList.toggle('playing', state.isPlaying && !state.isPaused);
  }
  if (compactDisc) {
    compactDisc.classList.toggle('spinning', state.isPlaying && !state.isPaused);
  }

  if (expandedSongTitle) {
    expandedSongTitle.textContent = state.songName;
  }
  if (expandedArtDisc) {
    expandedArtDisc.classList.toggle('playing', state.isPlaying && !state.isPaused);
  }
  if (expandedStatusBadge) {
    if (state.isPlaying) {
      if (state.isPaused) {
        expandedStatusBadge.textContent = 'Paused';
        expandedStatusBadge.className = 'pill-badge paused';
      } else {
        expandedStatusBadge.textContent = 'Playing';
        expandedStatusBadge.className = 'pill-badge playing';
      }
    } else {
      expandedStatusBadge.textContent = 'Standby';
      expandedStatusBadge.className = 'pill-badge';
    }
  }

  if (scrubberFill) {
    const widthPct = Math.min(100, Math.max(0, state.progress * 100));
    scrubberFill.style.width = `${widthPct}%`;
  }
  if (timeElapsedEl) {
    timeElapsedEl.textContent = state.timeElapsed;
  }
  if (timeTotalEl) {
    timeTotalEl.textContent = state.timeTotal;
  }

  if (playIcon) {
    playIcon.textContent = (state.isPlaying && !state.isPaused) ? '⏸' : '▶';
  }
}

// ─── Drag & Hover Interactions ───
let hoverTimeout = null;
let isMouseDown = false;

window.addEventListener('mousedown', () => {
  isMouseDown = true;
  clearTimeout(hoverTimeout);
});

window.addEventListener('mouseup', () => {
  isMouseDown = false;
});

island.addEventListener('mouseenter', () => {
  isHovered = true;
  clearTimeout(autoCollapseTimer);
  clearTimeout(hoverTimeout);
  if (isMouseDown) return;

  if (currentMode === 'compact') {
    hoverTimeout = setTimeout(() => {
      if (isHovered && !isMouseDown) {
        setIslandMode('expanded');
      }
    }, 280);
  }
});

island.addEventListener('mouseleave', () => {
  isHovered = false;
  clearTimeout(hoverTimeout);
  hoverTimeout = setTimeout(() => {
    syncIslandState();
  }, 320);
});

// Click dot view or compact view to expand
dotView?.addEventListener('click', (e) => {
  e.stopPropagation();
  clearTimeout(hoverTimeout);
  setIslandMode('expanded');
});

document.getElementById('compact-view')?.addEventListener('click', (e) => {
  e.stopPropagation();
  clearTimeout(hoverTimeout);
  setIslandMode('expanded');
});

// ─── User Actions ───
function overlayPlayPause() {
  ipcRenderer.invoke('overlay:playPause');
}

function overlayStop() {
  ipcRenderer.invoke('overlay:stop');
}

function overlayToggleFeature(feature) {
  ipcRenderer.invoke('overlay:toggleFeature', feature);
}

function focusMainApp() {
  ipcRenderer.invoke('overlay:focusMain');
}

function collapseOverlay() {
  isHovered = false;
  clearTimeout(hoverTimeout);
  clearTimeout(autoCollapseTimer);
  if (isAnyActive()) {
    setIslandMode('compact', true);
  } else {
    setIslandMode('dot', true);
  }
}

function closeOverlay() {
  ipcRenderer.invoke('overlay:close');
}

// Initial mode sync: force dot mode on start if nothing active
setIslandMode(isAnyActive() ? 'compact' : 'dot', true);
