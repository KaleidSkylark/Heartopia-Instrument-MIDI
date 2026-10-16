// ═══════════════════════════════════════════════════════════════════
// PianiPia V8 Electron — Main Application Orchestrator
// ═══════════════════════════════════════════════════════════════════

async function initApp() {
  console.log('[App] Starting PianiPia V8 Modular Suite...');
  try {
    if (typeof initWindowControls === 'function') initWindowControls();
    if (typeof initMaps === 'function') await initMaps();
    if (typeof loadSettings === 'function') await loadSettings();
    if (typeof loadPlaylistData === 'function') await loadPlaylistData();
    if (typeof loadAssistStatus === 'function') await loadAssistStatus();

    // Check Dynamic Island overlay status
    if (typeof ipcRenderer !== 'undefined') {
      const overlayActive = await ipcRenderer.invoke('overlay:status');
      if (typeof updateOverlayButtonState === 'function') {
        updateOverlayButtonState(overlayActive);
      }
    }

    if (typeof appLog === 'function') {
      appLog('PianiPia V8 Modular Suite Initialized & Ready', 'success');
    }
  } catch (err) {
    console.error('[App] Init Error:', err);
    if (typeof appLog === 'function') {
      appLog('Initialization error: ' + err.message, 'error');
    }
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initApp);
} else {
  initApp();
}
