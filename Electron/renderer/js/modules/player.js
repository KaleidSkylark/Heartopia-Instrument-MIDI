// ═══════════════════════════════════════════════════════════════════
// Module: Native Game Playback & Status Sync
// ═══════════════════════════════════════════════════════════════════

let lastPlaybackToggleTime = 0;
let playbackToggleInFlight = false;

async function togglePlayback() {
  const now = Date.now();
  if (now - lastPlaybackToggleTime < 150 || playbackToggleInFlight) return;
  lastPlaybackToggleTime = now;
  playbackToggleInFlight = true;

  const btnPlay = document.getElementById('btn-play');

  try {
    if (window.isPreviewing && typeof stopAudioPreview === 'function') {
      stopAudioPreview();
    }

    if (!window.currentSong || window.currentSong === 'None') {
      showModal('Info', 'Please select a song from your playlist first.');
      return;
    }

    const d = {
      song: window.currentSong,
      seek: parseFloat(document.getElementById('slider-seek')?.value || 0),
      speed: parseFloat(document.getElementById('slider-speed')?.value || 1.0),
      snap: parseInt(document.getElementById('slider-snap')?.value || 0),
      loop: document.getElementById('chk-loop')?.checked || false
    };

    const res = await ipcRenderer.invoke('player:play', d);
    if (res && res.error) {
      showModal('Error', res.error);
      if (btnPlay) {
        btnPlay.innerText = 'START';
        btnPlay.className = 'btn-neu accent';
      }
      return;
    }

    if (btnPlay) {
      if (btnPlay.innerText.includes('START') || btnPlay.innerText.includes('RESUME')) {
        btnPlay.innerText = 'PAUSE';
        btnPlay.className = 'btn-neu danger';
      } else {
        btnPlay.innerText = 'RESUME';
        btnPlay.className = 'btn-neu accent';
      }
    }
  } finally {
    playbackToggleInFlight = false;
  }
}

let lastStopToggleTime = 0;
async function stopPlayback() {
  const now = Date.now();
  if (now - lastStopToggleTime < 150) return;
  lastStopToggleTime = now;

  const btnPlay = document.getElementById('btn-play');
  if (btnPlay) {
    btnPlay.innerText = 'START';
    btnPlay.className = 'btn-neu accent';
  }
  const statusEl = document.getElementById('player-status');
  if (statusEl) {
    statusEl.innerText = '(Stopped)';
    statusEl.style.color = 'var(--text-muted)';
  }

  await ipcRenderer.invoke('player:stop');
}

async function updateParam(key, val) {
  if (key === 'speed') {
    const el = document.getElementById('val-speed');
    if (el) el.innerText = val;
  }
  if (key === 'snap') {
    const el = document.getElementById('val-snap');
    if (el) el.innerText = val;
  }
  await ipcRenderer.invoke('player:setParams', { [key]: val });
}

function onMainSpeedChange(val) {
  updateParam('speed', val);
  if (window.isPreviewing && window.cachedSongData && typeof startAudioEngine === 'function') {
    stopAudioPreview();
    startAudioEngine(window.cachedSongData, (window.currentSong || '').includes('_15K'), 'canvas-player', 'slider-speed', false);
  }
}

// Audio preview button
async function toggleAudioPreview() {
  if (window.isPreviewing) {
    stopAudioPreview();
    return;
  }
  if (!window.currentSong || window.currentSong === 'None') {
    showModal('Info', 'Please select a song from the library first!');
    return;
  }

  const btn = document.getElementById('btn-audio-preview');
  if (btn) btn.innerText = '⏳ Loading note preview...';

  try {
    const res = await ipcRenderer.invoke('songs:previewContent', window.currentSong, window.currentSongSource);
    if (!res.ok) throw new Error(res.error || 'Failed to load content');

    window.cachedSongData = res.data;
    if (btn) {
      btn.innerText = '⏹ Stop Audio Preview';
      btn.classList.add('playing');
    }
    if (typeof startAudioEngine === 'function') {
      startAudioEngine(window.cachedSongData, (window.currentSong || '').includes('_15K'), 'canvas-player', 'slider-speed', false);
    }
  } catch (err) {
    if (btn) btn.innerText = '🔊 Preview Audio + Visualizer';
    showModal('Error', 'Failed to preview song: ' + err.message);
  }
}

function stopAudioPreview() {
  if (typeof stopAudioEngine === 'function') {
    stopAudioEngine();
  }
  window.isPreviewing = false;
  const btn = document.getElementById('btn-audio-preview');
  if (btn) {
    btn.innerText = '🔊 Preview Audio + Visualizer';
    btn.classList.remove('playing');
  }
  if (typeof redrawCanvas === 'function') {
    redrawCanvas('canvas-player');
  }
}

// Listen for status updates from Python bridge via IPC
ipcRenderer.on('status_update', (_, data) => {
  const statusEl = document.getElementById('player-status');
  const btnPlay = document.getElementById('btn-play');
  const progressBar = document.getElementById('progress-bar');

  if (data.is_playing && !data.is_paused) {
    if (statusEl) {
      statusEl.innerText = '(Playing)';
      statusEl.style.color = 'var(--success)';
    }
    if (btnPlay) {
      btnPlay.innerText = 'PAUSE';
      btnPlay.className = 'btn-neu danger';
    }
  } else if (data.is_paused) {
    if (statusEl) {
      statusEl.innerText = '(Paused)';
      statusEl.style.color = 'var(--warning)';
    }
    if (btnPlay) {
      btnPlay.innerText = 'RESUME';
      btnPlay.className = 'btn-neu accent';
    }
  } else {
    if (statusEl) {
      statusEl.innerText = `(${data.status || 'Stopped'})`;
      statusEl.style.color = 'var(--text-muted)';
    }
    if (btnPlay) {
      btnPlay.innerText = 'START';
      btnPlay.className = 'btn-neu accent';
    }
  }

  if (progressBar && typeof data.progress === 'number') {
    progressBar.style.width = (data.progress * 100).toFixed(1) + '%';
  }

  if (data.current_song && data.current_song !== 'None' && data.current_song !== window.currentSong) {
    window.currentSong = data.current_song;
    if (typeof updatePlayerUI === 'function') updatePlayerUI(window.currentSong);
    if (typeof updatePlaylistActiveSong === 'function') {
      updatePlaylistActiveSong(window.currentSong);
    }
  }
});

// Expose globally on window
window.togglePlayback = togglePlayback;
window.stopPlayback = stopPlayback;
window.updateParam = updateParam;
window.onMainSpeedChange = onMainSpeedChange;
window.toggleAudioPreview = toggleAudioPreview;
window.stopAudioPreview = stopAudioPreview;
