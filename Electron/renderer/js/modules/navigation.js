// ═══════════════════════════════════════════════════════════════════
// Module: Navigation & Theme Controller
// ═══════════════════════════════════════════════════════════════════

function switchTab(id) {
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));

  const targetTab = document.getElementById(id);
  if (targetTab) targetTab.classList.add('active');

  const navBtn = document.getElementById(`btn-${id}`);
  if (navBtn) navBtn.classList.add('active');

  if (id === 'online' && !window.onlineLoaded) {
    if (typeof refreshOnline === 'function') refreshOnline();
    window.onlineLoaded = true;
  }

  if (id !== 'editor' && window.isEditorPreviewing) {
    if (typeof stopEditorPreview === 'function') stopEditorPreview();
  }
  if (id !== 'playlist' && window.isPreviewing) {
    if (typeof stopAudioPreview === 'function') stopAudioPreview();
  }

  if (id === 'playlist' && typeof redrawCanvas === 'function') {
    redrawCanvas('canvas-player');
  }
  if (id === 'editor') {
    if (typeof redrawCanvas === 'function') redrawCanvas('canvas-editor');
    if (typeof initMonaco === 'function') initMonaco();
    if (!window.currentEditorFile && window.currentSong && window.currentSong !== 'None' && typeof openInEditor === 'function') {
      openInEditor(window.currentSong);
    }
    setTimeout(() => {
      if (window.monacoEditor) window.monacoEditor.layout();
    }, 120);
  }
}

let lastThemeToggle = 0;

async function toggleTheme() {
  const now = Date.now();
  if (now - lastThemeToggle < 300) return;
  lastThemeToggle = now;

  const btn = document.getElementById('btn-theme');
  if (btn) btn.blur();

  const isLight = document.body.classList.toggle('light-theme');
  document.body.classList.toggle('dark-theme', !isLight);
  updateThemeBtn(isLight);

  // Update Monaco theme
  if (window.monaco && window.monaco.editor) {
    window.monaco.editor.setTheme(isLight ? 'vs' : 'heartopia-dark');
  }

  // Redraw canvases
  if (typeof redrawCanvas === 'function') {
    window.gridCanvas = null;
    redrawCanvas('canvas-player');
    redrawCanvas('canvas-editor');
  }

  try {
    await ipcRenderer.invoke('config:saveTheme', isLight ? 'light' : 'dark');
  } catch (e) {}
}

function updateThemeBtn(isLight) {
  const btn = document.getElementById('btn-theme');
  if (btn) {
    btn.innerHTML = isLight
      ? '<span class="nav-icon">🌙</span><span>Dark Mode</span>'
      : '<span class="nav-icon">☀</span><span>Light Mode</span>';
  }
}

window.switchTab = switchTab;
window.toggleTheme = toggleTheme;
window.updateThemeBtn = updateThemeBtn;
