// ═══════════════════════════════════════════════════════════════════
// Module: Monaco Editor & Visual Sync
// ═══════════════════════════════════════════════════════════════════

let monacoLoading = false;

function initMonaco() {
  if (window.monacoEditor) return;
  const container = document.getElementById('monaco-container');
  if (!container) return;

  if (window.monaco && window.monaco.editor) {
    setupMonacoInstance(container);
    return;
  }

  if (monacoLoading) return;
  monacoLoading = true;

  const fallback = document.getElementById('editor-fallback');
  if (fallback) {
    fallback.style.display = 'block';
    fallback.placeholder = 'Loading Studio Monaco engine from CDN...';
  }

  // Preserve Node globals while loading Monaco AMD loader
  const origRequire = window.require;
  const origModule = window.module;
  const origExports = window.exports;
  const origProcess = window.process;

  delete window.require;
  delete window.module;
  delete window.exports;
  delete window.process;

  const script = document.createElement('script');
  script.src = 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.44.0/min/vs/loader.min.js';
  script.onload = () => {
    const amdRequire = window.require;

    // Restore Node's globals
    window.require = origRequire;
    window.module = origModule;
    window.exports = origExports;
    window.process = origProcess;

    if (amdRequire && amdRequire.config) {
      amdRequire.config({
        paths: { vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.44.0/min/vs' }
      });
      amdRequire(['vs/editor/editor.main'], function() {
        console.log('[Monaco] Successfully lazy loaded Monaco engine on-demand!');
        monacoLoading = false;
        setupMonacoInstance(container);
      }, function(err) {
        monacoLoading = false;
        console.warn('[Monaco] Load notification:', err?.message || err);
      });
    }
  };
  script.onerror = (err) => {
    monacoLoading = false;
    window.require = origRequire;
    window.module = origModule;
    window.exports = origExports;
    window.process = origProcess;
    console.warn('[Monaco] CDN unavailable, fallback editor active.');
  };
  document.head.appendChild(script);
}

function setupMonacoInstance(container) {
  if (window.monacoEditor) return;
  const fallback = document.getElementById('editor-fallback');
  let initialValue = '// Select a song to inspect or write your own note commands...\n';
  if (fallback && fallback.value && fallback.value.trim() && !fallback.value.startsWith('Loading Studio')) {
    initialValue = fallback.value;
  }
  if (fallback) fallback.style.display = 'none';

  // Custom Heartopia MIDI Script Language
  window.monaco.languages.register({ id: 'heartopia-script' });
  window.monaco.languages.setMonarchTokensProvider('heartopia-script', {
    tokenizer: {
      root: [
        [/DELAY\s+\d+/, 'keyword.delay'],
        [/Keyboard\s*:\s*[A-Za-z0-9]+\s*:\s*KeyDown/, 'custom.keydown'],
        [/Keyboard\s*:\s*[A-Za-z0-9]+\s*:\s*KeyUp/, 'custom.keyup'],
        [/\/\/.*$/, 'comment'],
        [/#.*$/, 'comment']
      ]
    }
  });

  window.monaco.editor.defineTheme('heartopia-dark', {
    base: 'vs-dark',
    inherit: true,
    rules: [
      { token: 'keyword.delay', foreground: '06b6d4', fontStyle: 'bold' },
      { token: 'custom.keydown', foreground: '10b981', fontStyle: 'bold' },
      { token: 'custom.keyup', foreground: 'f43f5e' },
      { token: 'comment', foreground: '64748b', fontStyle: 'italic' }
    ],
    colors: {
      'editor.background': '#0c0f18',
      'editor.foreground': '#f1f5f9',
      'editor.lineHighlightBackground': '#1e2433'
    }
  });

  const isLight = document.body.classList.contains('light-theme');
  window.monacoEditor = window.monaco.editor.create(container, {
    value: initialValue,
    language: 'heartopia-script',
    theme: isLight ? 'vs' : 'heartopia-dark',
    fontSize: 13,
    fontFamily: "'Fira Code', 'Cascadia Code', monospace",
    minimap: { enabled: true },
    scrollBeyondLastLine: false,
    automaticLayout: true
  });

  window.monacoEditor.onDidChangeCursorPosition(e => {
    const statusLine = document.getElementById('editor-status-line');
    if (statusLine) {
      statusLine.innerText = `Line: ${e.position.lineNumber}, Col: ${e.position.column}`;
    }
  });
}

function openInEditor(song) {
  window.currentEditorFile = song;
  window.currentSong = song; // Keep main player synchronized
  switchTab('editor');

  ipcRenderer.invoke('songs:get', song).then(res => {
    if (res && res.content) {
      if (window.monacoEditor) {
        window.monacoEditor.setValue(res.content);
      } else {
        const fallback = document.getElementById('editor-fallback');
        if (fallback) fallback.value = res.content;
      }
      document.getElementById('editor-filename').innerText = song;
      appLog(`Opened ${song} in Studio Editor`, 'info');
    }
  }).catch(err => {
    showModal('Error', 'Failed to open song in editor: ' + err.message);
  });
}

function saveEditorContent() {
  if (!window.currentEditorFile) {
    showModal('Error', 'No song file currently opened to save.');
    return;
  }
  let content = '';
  if (window.monacoEditor) {
    content = window.monacoEditor.getValue();
  } else {
    content = document.getElementById('editor-fallback')?.value || '';
  }

  ipcRenderer.invoke('songs:save', { filename: window.currentEditorFile, content }).then(res => {
    if (res && res.ok) {
      appLog(`Saved changes to ${window.currentEditorFile}`, 'success');
      showModal('Saved', `Successfully saved ${window.currentEditorFile}`);
    } else {
      showModal('Error', 'Failed to save song changes.');
    }
  }).catch(err => {
    showModal('Error', 'Save error: ' + err.message);
  });
}

function insertTemplate(type) {
  if (!window.monacoEditor) return;
  const pos = window.monacoEditor.getPosition();
  let text = '';
  if (type === 'note') text = 'Keyboard: Q : KeyDown\nDELAY 120\nKeyboard: Q : KeyUp\n';
  else if (type === 'release') text = 'Keyboard: Q : KeyUp\n';
  else if (type === 'delay') text = 'DELAY 250\n';
  else if (type === 'chord') text = 'Keyboard: Q : KeyDown\nKeyboard: E : KeyDown\nDELAY 200\nKeyboard: Q : KeyUp\nKeyboard: E : KeyUp\n';

  window.monacoEditor.executeEdits('toolbar-insert', [
    { range: new window.monaco.Range(pos.lineNumber, pos.column, pos.lineNumber, pos.column), text }
  ]);
  window.monacoEditor.focus();
}

function playEditor(seekSeconds = 0) {
  let content = '';
  if (window.monacoEditor) {
    content = window.monacoEditor.getValue();
  } else {
    content = document.getElementById('editor-fallback')?.value || '';
  }

  if (!content.trim()) {
    showModal('Info', 'Editor is empty. Write or load some note scripts first!');
    return;
  }

  const upper = content.toUpperCase();
  const is15k = (window.currentEditorFile || '').includes('15K') ||
    (!upper.includes('KEYBOARD : Z') && !upper.includes('KEYBOARD : X') && !upper.includes('KEYBOARD : C') &&
     (upper.includes('KEYBOARD : A') || upper.includes('KEYBOARD : F')));

  startAudioEngine(content, is15k, 'canvas-editor', 'editor-speed', true);

  if (seekSeconds > 0) {
    seekAudioEngine(seekSeconds);
  }
}

function pauseEditor() {
  if (!window.audioCtx || !window.isEditorPreviewing) return;
  window.isPaused = !window.isPaused;
  const btnPause = document.getElementById('btn-editor-pause');
  if (btnPause) {
    btnPause.innerText = window.isPaused ? '▶ Resume' : '⏸';
  }
  if (!window.isPaused) {
    const currentSeek = parseFloat(document.getElementById('editor-seek-slider')?.value || 0);
    window.nextEventIndex = 0;
    while (window.nextEventIndex < window.audioEvents.length && window.audioEvents[window.nextEventIndex].time < currentSeek) {
      window.nextEventIndex++;
    }
    window.nextEventTime = window.audioCtx.currentTime - currentSeek;
    window.visualStartTime = window.nextEventTime;
    if (typeof renderPianoRoll === 'function') {
      window.visualizerFrame = requestAnimationFrame(renderPianoRoll);
    }
  }
}

function stopEditorPreview() {
  stopAudioEngine();
  window.isEditorPreviewing = false;
  window.isPaused = false;
  document.getElementById('btn-editor-play').disabled = false;
  document.getElementById('btn-editor-pause').disabled = true;
  document.getElementById('btn-editor-stop').disabled = true;
  document.getElementById('btn-editor-pause').innerText = '⏸';
  redrawCanvas('canvas-editor');
}

function onEditorSeekInput() {
  window.isSeeking = true;
  const val = parseFloat(document.getElementById('editor-seek-slider')?.value || 0);
  const timeCur = document.getElementById('editor-time-current');
  const seekFill = document.getElementById('editor-seek-fill');
  if (timeCur) timeCur.innerText = formatTime(val);
  if (seekFill) {
    const pct = Math.min(100, (val / window.editorTotalDuration) * 100);
    seekFill.style.width = `${pct}%`;
  }
}

function onEditorSeekChange() {
  const val = parseFloat(document.getElementById('editor-seek-slider')?.value || 0);
  window.isSeeking = false;
  seekAudioEngine(val);
}

function seekAudioEngine(targetSeconds) {
  if (!window.audioCtx) return;
  const wasPlaying = window.isEditorPreviewing && !window.isPaused;
  if (!window.isEditorPreviewing) {
    playEditor(targetSeconds);
    return;
  }

  window.nextEventIndex = 0;
  while (window.nextEventIndex < window.audioEvents.length && window.audioEvents[window.nextEventIndex].time < targetSeconds) {
    window.nextEventIndex++;
  }

  window.nextEventTime = window.audioCtx.currentTime - targetSeconds;
  window.visualStartTime = window.nextEventTime;

  if (!wasPlaying) {
    window.isPaused = false;
    document.getElementById('btn-editor-pause').innerText = '⏸';
  }
}

window.initMonaco = initMonaco;
window.openInEditor = openInEditor;
window.openEditor = openInEditor;
window.saveEditorContent = saveEditorContent;
window.insertTemplate = insertTemplate;
window.playEditor = playEditor;
window.pauseEditor = pauseEditor;
window.stopEditorPreview = stopEditorPreview;
window.onEditorSeekInput = onEditorSeekInput;
window.onEditorSeekChange = onEditorSeekChange;
window.seekAudioEngine = seekAudioEngine;

