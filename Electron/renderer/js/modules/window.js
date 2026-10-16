// ═══════════════════════════════════════════════════════════════════
// Module: Frameless Window Controls, Win11 Snap Layouts & Island
// ═══════════════════════════════════════════════════════════════════

function initWindowControls() {
  const btnMin = document.getElementById('btn-win-min');
  const btnMax = document.getElementById('btn-win-max');
  const btnClose = document.getElementById('btn-win-close');
  const snapWrapper = document.getElementById('snap-btn-wrapper');
  const snapMenu = document.getElementById('win11-snap-menu');
  let snapCloseTimer = null;

  function showSnapMenu() {
    clearTimeout(snapCloseTimer);
    if (snapMenu) {
      snapMenu.style.opacity = '';
      snapMenu.style.visibility = '';
      snapMenu.classList.add('snap-menu-open');
    }
  }

  function hideSnapMenu(delay = 350) {
    clearTimeout(snapCloseTimer);
    if (delay === 0) {
      snapMenu?.classList.remove('snap-menu-open');
    } else {
      snapCloseTimer = setTimeout(() => {
        snapMenu?.classList.remove('snap-menu-open');
      }, delay);
    }
  }

  if (snapWrapper && snapMenu) {
    snapWrapper.addEventListener('mouseenter', showSnapMenu);
    snapWrapper.addEventListener('mouseleave', () => hideSnapMenu(350));
    snapMenu.addEventListener('mouseenter', showSnapMenu);
    snapMenu.addEventListener('mouseleave', () => hideSnapMenu(300));
  }

  if (btnMin) {
    btnMin.onclick = () => ipcRenderer.invoke('window:minimize');
  }

  if (btnMax) {
    btnMax.addEventListener('click', async (e) => {
      e.stopPropagation();
      e.preventDefault();
      hideSnapMenu(0);
      try {
        const isMax = await ipcRenderer.invoke('window:maximize');
        btnMax.textContent = isMax ? '🗗' : '🗖';
        btnMax.title = isMax ? 'Restore' : 'Maximize';
      } catch (err) {
        console.error('Window maximize error:', err);
      }
    });
  }

  // Double click titlebar to toggle maximize/unmaximize
  const titlebar = document.querySelector('.titlebar');
  if (titlebar) {
    titlebar.addEventListener('dblclick', async (e) => {
      if (e.target.closest('.titlebar-controls') || e.target.closest('.titlebar-center') || e.target.closest('button')) {
        return;
      }
      try {
        const isMax = await ipcRenderer.invoke('window:maximize');
        if (btnMax) {
          btnMax.textContent = isMax ? '🗗' : '🗖';
          btnMax.title = isMax ? 'Restore' : 'Maximize';
        }
      } catch (err) {}
    });
  }

  ipcRenderer.invoke('window:isMaximized').then(isMax => {
    if (btnMax && isMax !== undefined) {
      btnMax.textContent = isMax ? '🗗' : '🗖';
      btnMax.title = isMax ? 'Restore' : 'Maximize';
    }
  }).catch(() => {});

  ipcRenderer.on('window:state_changed', (_, { isMaximized }) => {
    if (btnMax) {
      btnMax.textContent = isMaximized ? '🗗' : '🗖';
      btnMax.title = isMaximized ? 'Restore' : 'Maximize';
    }
  });

  if (btnClose) {
    btnClose.onclick = () => {
      const exitModal = document.getElementById('exit-modal');
      if (exitModal) {
        exitModal.classList.add('active');
      } else {
        ipcRenderer.invoke('window:close');
      }
    };
  }

  // Windows 11 Snap Layout Zone clicks
  const snapZones = document.querySelectorAll('.snap-zone');
  snapZones.forEach(zone => {
    zone.addEventListener('click', async (e) => {
      e.stopPropagation();
      e.preventDefault();
      hideSnapMenu(0);
      const snapType = zone.getAttribute('data-snap');
      if (snapType) {
        await ipcRenderer.invoke('window:snap', { zone: snapType });
      }
    });
  });
}

function finalizeExit() {
  ipcRenderer.invoke('window:close');
}

// ─── Dynamic Island Overlay Controller ───
async function toggleOverlay() {
  try {
    const res = await ipcRenderer.invoke('overlay:toggle');
    const active = typeof res === 'boolean' ? res : !!res?.active;
    updateOverlayButtonState(active);
  } catch (err) {
    console.error('Failed to toggle Dynamic Island overlay:', err);
  }
}

function updateOverlayButtonState(isActive) {
  const btn = document.getElementById('btn-toggle-island');
  const text = document.getElementById('island-btn-text');
  if (btn) {
    btn.classList.toggle('active', !!isActive);
  }
  if (text) {
    text.textContent = isActive ? 'Island Overlay: On' : 'Island Overlay: Off';
  }
}

ipcRenderer.on('overlay_status_changed', (_, active) => {
  updateOverlayButtonState(active);
});

window.initWindowControls = initWindowControls;
window.finalizeExit = finalizeExit;
window.toggleOverlay = toggleOverlay;
window.updateOverlayButtonState = updateOverlayButtonState;
