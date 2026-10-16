// ═══════════════════════════════════════════════════════════════════
// Module: MIDI File Converter
// ═══════════════════════════════════════════════════════════════════

function handleFileSelect(input) {
  if (input.files && input.files.length > 0) {
    window.selectedMidiFiles = Array.from(input.files).map(f => f.path);
    const display = document.getElementById('file-name-display');
    if (display) {
      display.innerText = `${window.selectedMidiFiles.length} file(s) selected:\n` +
        window.selectedMidiFiles.map(p => p.split(/[\\/]/).pop()).join(', ');
    }
  }
}

async function browseMidiFiles() {
  const filePaths = await ipcRenderer.invoke('dialog:browseMidi');
  if (filePaths && filePaths.length > 0) {
    window.selectedMidiFiles = filePaths;
    const display = document.getElementById('file-name-display');
    if (display) {
      display.innerText = `${window.selectedMidiFiles.length} file(s) selected:\n` +
        filePaths.map(p => p.split(/[\\/]/).pop()).join(', ');
    }
  }
}

// Setup drag and drop
document.addEventListener('DOMContentLoaded', () => {
  const dropZone = document.getElementById('drop-zone');
  if (dropZone) {
    dropZone.addEventListener('dragover', e => {
      e.preventDefault();
      dropZone.classList.add('dragover');
    });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    dropZone.addEventListener('drop', e => {
      e.preventDefault();
      dropZone.classList.remove('dragover');
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        window.selectedMidiFiles = Array.from(e.dataTransfer.files)
          .filter(f => f.name.toLowerCase().endsWith('.mid') || f.name.toLowerCase().endsWith('.midi'))
          .map(f => f.path);
        const display = document.getElementById('file-name-display');
        if (display) {
          display.innerText = `${window.selectedMidiFiles.length} MIDI file(s) dropped:\n` +
            window.selectedMidiFiles.map(p => p.split(/[\\/]/).pop()).join(', ');
        }
      }
    });
  }
});

async function convertMidi() {
  if (!window.selectedMidiFiles || window.selectedMidiFiles.length === 0) {
    showModal('Info', 'Please select or drag-and-drop MIDI files first!');
    return;
  }

  const target = document.getElementById('convert-target')?.value || 'Both';
  const pitch = parseInt(document.getElementById('slider-pitch')?.value || 0);

  const logEl = document.getElementById('convert-log');
  if (logEl) logEl.innerText = 'Processing conversion with Python engine...';
  appLog(`Starting conversion of ${window.selectedMidiFiles.length} files...`, 'info');

  try {
    const res = await ipcRenderer.invoke('converter:run', {
      files: window.selectedMidiFiles,
      target,
      pitch
    });

    if (logEl) {
      logEl.innerText = res.log || (res.ok ? 'Conversion finished successfully!' : 'Conversion error occurred.');
    }

    if (res.ok) {
      appLog('Conversion successful! Reloading playlist library...', 'success');
      showModal('Conversion Complete', 'Your MIDI files were successfully converted and saved to your notes library!');
      if (typeof loadPlaylistData === 'function') loadPlaylistData();
    } else {
      appLog('Conversion failed: ' + (res.error || 'Unknown error'), 'error');
      showModal('Conversion Failed', res.error || 'An error occurred during Python MIDI conversion.');
    }
  } catch (err) {
    if (logEl) logEl.innerText = 'Conversion failed: ' + err.message;
    appLog('Conversion error: ' + err.message, 'error');
    showModal('Error', err.message);
  }
}

// Expose globally on window
window.handleFileSelect = handleFileSelect;
window.browseMidiFiles = browseMidiFiles;
window.convertMidi = convertMidi;
