// ═══════════════════════════════════════════════════════════════════
// Module: MIDI File Converter
// ═══════════════════════════════════════════════════════════════════

function getElectronModule() {
  try {
    if (window.electron) return window.electron;
    if (typeof window.nodeRequire === 'function') return window.nodeRequire('electron');
    if (typeof require === 'function') return require('electron');
  } catch (e) {
    console.warn('[Converter] Could not access Electron module:', e);
  }
  return null;
}

function getFilePath(file) {
  if (!file) return null;
  if (typeof file === 'string') return file;

  try {
    const el = getElectronModule();
    if (el && el.webUtils && typeof el.webUtils.getPathForFile === 'function') {
      const p = el.webUtils.getPathForFile(file);
      if (p) return p;
    }
  } catch (e) {
    console.warn('[Converter] webUtils.getPathForFile error:', e);
  }

  return file.path || null;
}

function updateFileDisplay(files) {
  const display = document.getElementById('file-name-display');
  if (!display) return;
  if (!files || files.length === 0) {
    display.innerText = '';
    return;
  }
  display.innerText = `${files.length} file(s) selected:\n` +
    files.map(p => (typeof p === 'string' ? p.split(/[\\/]/).pop() : 'MIDI File')).join(', ');
}

function handleFileSelect(input) {
  if (input && input.files && input.files.length > 0) {
    const paths = Array.from(input.files)
      .map(getFilePath)
      .filter(p => p && (p.toLowerCase().endsWith('.mid') || p.toLowerCase().endsWith('.midi')));

    if (paths.length > 0) {
      window.selectedMidiFiles = paths;
      updateFileDisplay(window.selectedMidiFiles);
    }
  }
}

async function browseMidiFiles(event) {
  if (event) {
    event.stopPropagation();
  }
  try {
    const filePaths = await ipcRenderer.invoke('dialog:browseMidi');
    if (filePaths && filePaths.length > 0) {
      window.selectedMidiFiles = filePaths;
      updateFileDisplay(window.selectedMidiFiles);
    }
  } catch (err) {
    console.error('[Converter] Error browsing MIDI files:', err);
    appLog('Error selecting MIDI files: ' + err.message, 'error');
  }
}

// Setup drag and drop
document.addEventListener('DOMContentLoaded', () => {
  const dropZone = document.getElementById('drop-zone');
  if (dropZone) {
    dropZone.addEventListener('dragover', e => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.add('dragover');
    });
    dropZone.addEventListener('dragleave', e => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.remove('dragover');
    });
    dropZone.addEventListener('drop', e => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.remove('dragover');
      if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        const paths = Array.from(e.dataTransfer.files)
          .map(getFilePath)
          .filter(p => p && (p.toLowerCase().endsWith('.mid') || p.toLowerCase().endsWith('.midi')));

        if (paths.length > 0) {
          window.selectedMidiFiles = paths;
          updateFileDisplay(window.selectedMidiFiles);
        } else {
          showModal('Invalid Files', 'Please drop valid .mid or .midi files!');
        }
      }
    });
  }

  // Listen for convert_result events from python bridge
  if (typeof ipcRenderer !== 'undefined' && ipcRenderer.on) {
    ipcRenderer.on('convert_result', (_, msg) => {
      const logEl = document.getElementById('convert-log');
      if (logEl && msg && msg.message) {
        logEl.innerText = msg.message;
      }
    });
  }
});

async function convertMidi() {
  if (!window.selectedMidiFiles || window.selectedMidiFiles.length === 0) {
    showModal('Info', 'Please select or drag-and-drop MIDI files first!');
    return;
  }

  const convertBtn = document.querySelector('#add button.btn-neu.accent');
  const target = document.getElementById('convert-target')?.value || 'Both';
  const pitch = parseInt(document.getElementById('slider-pitch')?.value || 0);

  const logEl = document.getElementById('convert-log');
  if (logEl) logEl.innerText = 'Processing conversion with Python engine...';
  appLog(`Starting conversion of ${window.selectedMidiFiles.length} file(s)...`, 'info');

  if (convertBtn) {
    convertBtn.disabled = true;
    convertBtn.innerText = 'CONVERTING...';
  }

  try {
    const res = await ipcRenderer.invoke('converter:run', {
      files: window.selectedMidiFiles,
      target,
      pitch
    });

    if (logEl) {
      logEl.innerText = res.log || (res.ok ? 'Conversion finished successfully!' : (res.error || 'Conversion error occurred.'));
    }

    if (res && res.ok) {
      appLog('Conversion successful! Reloading playlist library...', 'success');
      showModal('Conversion Complete', 'Your MIDI files were successfully converted and saved to your notes library!\n\n' + (res.log || ''));
      if (typeof loadPlaylistData === 'function') {
        loadPlaylistData();
      }
    } else {
      const errMsg = (res && res.error) || (res && res.log) || 'An error occurred during Python MIDI conversion.';
      appLog('Conversion failed: ' + errMsg, 'error');
      showModal('Conversion Failed', errMsg);
    }
  } catch (err) {
    if (logEl) logEl.innerText = 'Conversion failed: ' + err.message;
    appLog('Conversion error: ' + err.message, 'error');
    showModal('Error', err.message);
  } finally {
    if (convertBtn) {
      convertBtn.disabled = false;
      convertBtn.innerText = 'CONVERT ALL FILES';
    }
  }
}

// Expose globally on window
window.handleFileSelect = handleFileSelect;
window.browseMidiFiles = browseMidiFiles;
window.convertMidi = convertMidi;
