// ═══════════════════════════════════════════════════════════════════
// Module: Assist Automation & Configuration Modals
// ═══════════════════════════════════════════════════════════════════

window.assistState = {
  connected: false,
  window_name: 'Heartopia',
  walk_active: false,
  cam_active: false,
  harvest_active: false,
  tree_rock_active: false,
  cook_active: false,
  snow_active: false,
  jump_active: false,
  confidence: 0.8,
  use_grayscale: false,
  harvest_method: 'spam', // 'spam' or 'vision'
  harvest_mode: 'spam',
  harvest_vk: 70,
  harvest_duration: 5.0,
  harvest_spam_interval: 0.1,
  mouse_btn: 2,
  harvest_images: [],
  images: {}
};

window.assistHotkeys = {
  walk: 112,
  cam: 113,
  harvest: 114,
  tree_rock: 120,
  cook: 117,
  snow: 118,
  jump: 119
};

async function loadAssistStatus() {
  try {
    const conf = await ipcRenderer.invoke('config:get');
    if (conf) {
      if (conf.walk_hotkey) window.assistHotkeys.walk = conf.walk_hotkey;
      if (conf.cam_hotkey) window.assistHotkeys.cam = conf.cam_hotkey;
      if (conf.harvest_hotkey) window.assistHotkeys.harvest = conf.harvest_hotkey;
      if (conf.tree_rock_hotkey) window.assistHotkeys.tree_rock = conf.tree_rock_hotkey;
      if (conf.cook_hotkey) window.assistHotkeys.cook = conf.cook_hotkey;
      if (conf.snow_hotkey) window.assistHotkeys.snow = conf.snow_hotkey;
      if (conf.jump_hotkey) window.assistHotkeys.jump = conf.jump_hotkey;
      updateAssistHotkeyBadges();
    }
    const status = await ipcRenderer.invoke('assist:status');
    if (status) {
      Object.assign(window.assistState, status);
    }
    // If no harvest images cached, fetch defaults from Tree&Rock&BushReference
    if (!window.assistState.harvest_images || window.assistState.harvest_images.length === 0) {
      const defaults = await ipcRenderer.invoke('assist:getDefaultHarvestImages');
      if (defaults && defaults.length > 0) {
        window.assistState.harvest_images = defaults;
      }
    }
    updateAssistUI();
    await refreshAssistWindows();
  } catch (e) {
    console.error('Error fetching assist status:', e);
  }
}

function updateAssistUI() {
  const badge = document.getElementById('assist-status-badge');
  const btnConnect = document.getElementById('btn-assist-connect');
  if (badge) {
    if (window.assistState.connected) {
      badge.innerText = `Connected (${window.assistState.window_name || 'Heartopia'})`;
      badge.style.color = 'var(--success)';
      badge.style.borderColor = 'rgba(16, 185, 129, 0.4)';
    } else {
      badge.innerText = 'Disconnected';
      badge.style.color = 'var(--danger)';
      badge.style.borderColor = 'rgba(239, 68, 68, 0.4)';
    }
  }
  if (btnConnect) {
    btnConnect.innerText = window.assistState.connected ? 'Disconnect' : 'Connect Game';
    btnConnect.className = window.assistState.connected ? 'btn-neu danger' : 'btn-neu accent';
  }

  const features = ['walk', 'cam', 'harvest', 'cook', 'snow', 'jump'];
  features.forEach(feat => {
    const btn = document.getElementById(`btn-assist-${feat}`);
    const card = document.getElementById(`card-assist-${feat}`) || (btn ? btn.closest('.assist-card') : null);
    const active = !!window.assistState[`${feat}_active`];
    if (btn) {
      const name = feat.charAt(0).toUpperCase() + feat.slice(1);
      if (active) {
        btn.innerText = `✓ Active — Disable ${name}`;
        btn.className = 'btn-neu assist-active';
      } else {
        btn.innerText = `Enable ${name}`;
        btn.className = 'btn-neu';
      }
    }
    if (card) {
      card.classList.toggle('active', active);
    }
  });

  const slider = document.getElementById('slider-assist-conf');
  const valSpan = document.getElementById('val-assist-conf');
  if (slider && valSpan) {
    slider.value = window.assistState.confidence || 0.8;
    valSpan.innerText = parseFloat(slider.value).toFixed(2);
  }
  window.assistState.use_grayscale = false;

  // Harvest summary on card
  const isVision = window.assistState.harvest_method === 'vision';
  const summaryHarvestMode = document.getElementById('summary-harvest-mode');
  if (summaryHarvestMode) {
    if (isVision) {
      summaryHarvestMode.innerText = `👁️ Vision Detection (Screen Match)`;
    } else {
      const keyName = getAssistVKName(window.assistState.harvest_vk || 70);
      const modeText = window.assistState.harvest_mode === 'hold'
        ? `Hold ${(window.assistState.harvest_duration || 5.0).toFixed(1)}s`
        : `Spam ${(window.assistState.harvest_spam_interval || 0.1).toFixed(2)}s`;
      summaryHarvestMode.innerText = `⚡ ${keyName} Key (${modeText})`;
    }
  }

  const btnCardSpam = document.getElementById('card-harvest-method-spam');
  const btnCardVision = document.getElementById('card-harvest-method-vision');
  if (btnCardSpam && btnCardVision) {
    btnCardSpam.classList.toggle('active', !isVision);
    btnCardVision.classList.toggle('active', isVision);
  }

  const harvestCount = window.assistState.harvest_images ? window.assistState.harvest_images.length : 0;
  const summaryHarvestCount = document.getElementById('summary-harvest-count');
  if (summaryHarvestCount) {
    summaryHarvestCount.innerText = `${harvestCount} Targets Cached`;
  }

  // Mouse button segmented control
  const camLeft = document.getElementById('cam-left');
  const camRight = document.getElementById('cam-right');
  if (camLeft && camRight) {
    const isLeft = window.assistState.mouse_btn === 1;
    camLeft.classList.toggle('active', isLeft);
    camRight.classList.toggle('active', !isLeft);
  }

  // Populate reference images
  if (window.assistState.images) {
    for (const [key, pathStr] of Object.entries(window.assistState.images)) {
      const input = document.getElementById(`img-${key}`);
      if (input && pathStr) {
        input.value = pathStr.split(/[/\\]/).pop();
        input.title = pathStr;
      }
    }
  }
}

function setCamMouseButton(btnName) {
  const isLeft = btnName.toLowerCase() === 'left';
  window.assistState.mouse_btn = isLeft ? 1 : 2;
  document.getElementById('cam-left')?.classList.toggle('active', isLeft);
  document.getElementById('cam-right')?.classList.toggle('active', !isLeft);
  saveAssistSettings();
}

async function browseAssistImage(key) {
  const filePath = await ipcRenderer.invoke('dialog:browseImage');
  if (filePath) {
    const input = document.getElementById(`img-${key}`);
    if (input) {
      input.value = filePath.split(/[/\\]/).pop();
      input.title = filePath;
    }
    if (!window.assistState.images) window.assistState.images = {};
    window.assistState.images[key] = filePath;
    await ipcRenderer.invoke('assist:setImages', { [key]: filePath });
    appLog(`Updated reference image for ${key}: ${filePath.split(/[/\\]/).pop()}`, 'success');
  }
}

// ─── Modal Management ───
function openHarvestModal() {
  const selVk = document.getElementById('modal-harvest-vk');
  if (selVk && window.assistState.harvest_vk) selVk.value = String(window.assistState.harvest_vk);

  const selMode = document.getElementById('modal-harvest-mode');
  if (selMode && window.assistState.harvest_mode) selMode.value = window.assistState.harvest_mode;

  const inSpam = document.getElementById('modal-harvest-spam');
  if (inSpam && window.assistState.harvest_spam_interval) inSpam.value = window.assistState.harvest_spam_interval;

  const inDur = document.getElementById('modal-harvest-duration');
  if (inDur && window.assistState.harvest_duration) inDur.value = window.assistState.harvest_duration;

  syncHarvestModalToState();
  renderHarvestChips();
  document.getElementById('modal-harvest-config')?.classList.add('active');
}

function closeHarvestModal() {
  document.getElementById('modal-harvest-config')?.classList.remove('active');
}

async function setHarvestMethod(method) {
  window.assistState.harvest_method = method;

  // Update card buttons
  const btnSpam = document.getElementById('card-harvest-method-spam');
  const btnVision = document.getElementById('card-harvest-method-vision');
  if (btnSpam) btnSpam.classList.toggle('active', method === 'spam');
  if (btnVision) btnVision.classList.toggle('active', method === 'vision');

  // Update modal buttons & description
  const mSpam = document.getElementById('modal-method-spam');
  const mVision = document.getElementById('modal-method-vision');
  if (mSpam) mSpam.classList.toggle('active', method === 'spam');
  if (mVision) mVision.classList.toggle('active', method === 'vision');

  const mDesc = document.getElementById('modal-method-desc');
  if (mDesc) {
    mDesc.innerText = method === 'spam'
      ? '⚡ Spam Method: Continuous rapid keystroke interaction for crops and farm plots.'
      : '👁️ Vision Method: Screen template matching targeting Trees, Rocks, Bushes, and Crops directly in RAM.';
  }

  // Update card summary
  updateAssistUI();

  try {
    await ipcRenderer.invoke('assist:updateConfig', {
      harvest_method: method
    });
    appLog(`Auto Harvest Method changed to: ${method === 'spam' ? '⚡ Keystroke Spam' : '👁️ Screen Vision'}`, 'info');
  } catch (err) {
    console.error('Failed to update harvest method:', err);
  }
}

function syncHarvestModalToState() {
  const method = window.assistState.harvest_method || 'spam';
  const mSpam = document.getElementById('modal-method-spam');
  const mVision = document.getElementById('modal-method-vision');
  if (mSpam) mSpam.classList.toggle('active', method === 'spam');
  if (mVision) mVision.classList.toggle('active', method === 'vision');

  const mDesc = document.getElementById('modal-method-desc');
  if (mDesc) {
    mDesc.innerText = method === 'spam'
      ? '⚡ Spam Method: Continuous rapid keystroke interaction for crops and farm plots.'
      : '👁️ Vision Method: Screen template matching targeting Trees, Rocks, Bushes, and Crops directly in RAM.';
  }

  const selMode = document.getElementById('modal-harvest-mode');
  const isHold = selMode ? selMode.value === 'hold' : false;
  const wrapSpam = document.getElementById('modal-harvest-spam-wrap');
  const wrapDur = document.getElementById('modal-harvest-dur-wrap');
  if (wrapSpam) wrapSpam.style.display = isHold ? 'none' : 'block';
  if (wrapDur) wrapDur.style.display = isHold ? 'block' : 'none';
}

function renderHarvestChips() {
  const container = document.getElementById('harvest-chips-container');
  const badge = document.getElementById('modal-harvest-count-badge');
  const cardSummary = document.getElementById('summary-harvest-count');
  const images = window.assistState.harvest_images || [];

  if (badge) badge.innerText = `${images.length} Targets`;
  if (cardSummary) cardSummary.innerText = `${images.length} Targets Cached`;

  if (!container) return;

  if (images.length === 0) {
    container.innerHTML = '<span style="color: var(--text-muted); font-size: 0.82em; margin: auto;">No targets loaded. Click "Select All from Tree&Rock&Bush" to load presets.</span>';
    return;
  }

  container.innerHTML = '';
  images.forEach((pathStr, idx) => {
    const filename = pathStr.split(/[/\\]/).pop();
    let icon = '🎯';
    const lower = filename.toLowerCase();
    if (lower.includes('tree')) icon = '🌲';
    else if (lower.includes('rock')) icon = '🪨';
    else if (lower.includes('bush')) icon = '🌿';

    const chip = document.createElement('div');
    chip.className = 'target-chip';
    chip.title = pathStr;
    chip.innerHTML = `
      <span>${icon}</span>
      <span>${escapeHtml(filename)}</span>
      <span class="target-chip-remove" onclick="removeHarvestImage(${idx})" title="Remove Target">✕</span>
    `;
    container.appendChild(chip);
  });
}

function removeHarvestImage(idx) {
  if (window.assistState.harvest_images && window.assistState.harvest_images[idx] !== undefined) {
    const removed = window.assistState.harvest_images.splice(idx, 1);
    renderHarvestChips();
    appLog(`Removed harvest target: ${removed[0]?.split(/[/\\]/).pop()}`, 'info');
  }
}
window.removeHarvestChip = removeHarvestImage;

async function addBulkHarvestImages() {
  const filePaths = await ipcRenderer.invoke('dialog:browseImages');
  if (filePaths && filePaths.length > 0) {
    if (!window.assistState.harvest_images) window.assistState.harvest_images = [];
    let addedCount = 0;
    filePaths.forEach(fp => {
      if (!window.assistState.harvest_images.includes(fp)) {
        window.assistState.harvest_images.push(fp);
        addedCount++;
      }
    });
    renderHarvestChips();
    appLog(`Added ${addedCount} reference image(s) to Auto Harvest cache.`, 'success');
  }
}

async function loadDefaultHarvestImages() {
  const defaults = await ipcRenderer.invoke('assist:getDefaultHarvestImages');
  if (defaults && defaults.length > 0) {
    window.assistState.harvest_images = defaults;
    renderHarvestChips();
    appLog(`Loaded ${defaults.length} default reference images from Tree&Rock&BushReference!`, 'success');
  } else {
    showModal('Not Found', 'Could not locate the Tree&Rock&BushReference folder.');
  }
}

function clearAllHarvestImages() {
  window.assistState.harvest_images = [];
  renderHarvestChips();
  appLog('Cleared all Auto Harvest target images.', 'info');
}

async function saveHarvestModalConfig() {
  const selVk = document.getElementById('modal-harvest-vk');
  const selMode = document.getElementById('modal-harvest-mode');
  const inSpam = document.getElementById('modal-harvest-spam');
  const inDur = document.getElementById('modal-harvest-duration');

  if (selVk) window.assistState.harvest_vk = parseInt(selVk.value) || 70;
  if (selMode) window.assistState.harvest_mode = selMode.value;
  if (inSpam) window.assistState.harvest_spam_interval = parseFloat(inSpam.value) || 0.1;
  if (inDur) window.assistState.harvest_duration = parseFloat(inDur.value) || 5.0;

  await ipcRenderer.invoke('assist:updateConfig', {
    harvest_method: window.assistState.harvest_method || 'spam',
    harvest_vk: window.assistState.harvest_vk,
    harvest_mode: window.assistState.harvest_mode,
    harvest_spam_interval: window.assistState.harvest_spam_interval,
    harvest_duration: window.assistState.harvest_duration,
    harvest_images: window.assistState.harvest_images || []
  });

  await ipcRenderer.invoke('assist:setHarvestImages', window.assistState.harvest_images || []);

  closeHarvestModal();
  updateAssistUI();
  appLog(`Saved Auto Harvest configuration (${window.assistState.harvest_images?.length || 0} vision targets cached in RAM).`, 'success');
}

function openCookModal() {
  document.getElementById('modal-cook-config')?.classList.add('active');
}

function closeCookModal() {
  document.getElementById('modal-cook-config')?.classList.remove('active');
}

async function loadDefaultCookImages() {
  const defaults = await ipcRenderer.invoke('assist:getDefaultCookImages');
  if (defaults) {
    if (!window.assistState.images) window.assistState.images = {};
    Object.assign(window.assistState.images, defaults);
    for (const [key, p] of Object.entries(defaults)) {
      const input = document.getElementById(`img-${key}`);
      if (input) {
        input.value = p.split(/[/\\]/).pop();
        input.title = p;
      }
    }
    await ipcRenderer.invoke('assist:setImages', defaults);
    appLog('Loaded default CookingReference images.', 'success');
  }
}

function openSnowModal() {
  document.getElementById('modal-snow-config')?.classList.add('active');
}

function closeSnowModal() {
  document.getElementById('modal-snow-config')?.classList.remove('active');
}

async function loadDefaultSnowImages() {
  const defaults = await ipcRenderer.invoke('assist:getDefaultSnowImages');
  if (defaults) {
    if (!window.assistState.images) window.assistState.images = {};
    Object.assign(window.assistState.images, defaults);
    for (const [key, p] of Object.entries(defaults)) {
      const input = document.getElementById(`img-${key}`);
      if (input) {
        input.value = p.split(/[/\\]/).pop();
        input.title = p;
      }
    }
    await ipcRenderer.invoke('assist:setImages', defaults);
    appLog('Loaded default SnowReference images.', 'success');
  }
}

async function refreshAssistWindows() {
  appLog('Scanning for open game windows...');
  const res = await ipcRenderer.invoke('assist:getWindows');
  const select = document.getElementById('sel-assist-window');
  if (select && res && res.windows) {
    select.innerHTML = '';
    res.windows.forEach(w => {
      const opt = document.createElement('option');
      opt.value = w;
      opt.innerText = w;
      select.appendChild(opt);
    });
    if (select.options.length > 0) {
      select.selectedIndex = 0;
    }
    appLog(`Window filter: strictly connected to ${select.value}`);
  }
}

async function toggleAssistConnection() {
  if (window.assistState.connected) {
    await ipcRenderer.invoke('assist:disconnect');
    window.assistState.connected = false;
    appLog('Disconnected from game window.');
  } else {
    const sel = document.getElementById('sel-assist-window');
    const winName = sel ? sel.value : 'Heartopia';
    const res = await ipcRenderer.invoke('assist:connect', winName);
    if (res && res.connected) {
      window.assistState.connected = true;
      window.assistState.window_name = winName;
      appLog(`Connected to window: ${winName}`, 'success');
      showModal('Connected', `Successfully attached to ${winName}!`);
    } else {
      showModal('Connection Failed', `Could not find window "${winName}". Ensure Heartopia (xdt.exe) is running!`);
      appLog(`Failed to connect to ${winName}`, 'error');
    }
  }
  updateAssistUI();
}

const toggleInFlight = {};
const lastToggleTimes = {};

async function toggleAssistFeature(feat, event) {
  if (event) {
    if (typeof event.preventDefault === 'function') event.preventDefault();
  }

  const now = Date.now();
  if (lastToggleTimes[feat] && (now - lastToggleTimes[feat] < 150)) {
    return; // Light debounce against hardware switch bounce
  }
  if (toggleInFlight[feat]) {
    return; // Already pending IPC response
  }
  lastToggleTimes[feat] = now;
  toggleInFlight[feat] = true;

  if (!window.assistState.connected) {
    toggleInFlight[feat] = false;
    showModal('Not Connected', 'Please connect to the Heartopia game window first!');
    return;
  }

  // Optimistic UI update for 0ms visual latency
  window.assistState[`${feat}_active`] = !window.assistState[`${feat}_active`];
  updateAssistUI();

  try {
    const res = await ipcRenderer.invoke('assist:toggle', feat);
    if (res && res.state) {
      Object.assign(window.assistState, res.state);
      updateAssistUI();
      const nowActive = window.assistState[`${feat}_active`];
      appLog(`Assist ${feat.toUpperCase()}: ${nowActive ? 'ON' : 'OFF'}`, nowActive ? 'success' : 'info');
    }
  } catch (err) {
    console.error(`Failed to toggle assist ${feat}:`, err);
    // Revert optimistic update on failure
    window.assistState[`${feat}_active`] = !window.assistState[`${feat}_active`];
    updateAssistUI();
  } finally {
    toggleInFlight[feat] = false;
  }
}

async function updateAssistSettings() {
  await saveAssistSettings(false);
}

async function saveAssistSettings(showNotice = false) {
  const conf = parseFloat(document.getElementById('slider-assist-conf')?.value || 0.8);
  const gray = false;
  const mouseBtn = document.getElementById('cam-left')?.classList.contains('active') ? 1 : 2;

  window.assistState.confidence = conf;
  window.assistState.use_grayscale = gray;
  window.assistState.mouse_btn = mouseBtn;

  await ipcRenderer.invoke('assist:updateConfig', {
    confidence: conf,
    use_grayscale: gray,
    mouse_btn: mouseBtn,
    harvest_method: window.assistState.harvest_method || 'spam',
    harvest_vk: window.assistState.harvest_vk,
    harvest_mode: window.assistState.harvest_mode,
    harvest_duration: window.assistState.harvest_duration,
    harvest_spam_interval: window.assistState.harvest_spam_interval,
    harvest_images: window.assistState.harvest_images || []
  });

  if (showNotice) {
    showModal('Settings Saved', 'Assist vision, harvest, and control settings successfully saved!');
  }
}

// ─── Assist Hotkey Binding with Single-Listener Guard ───
let activeHotkeyCleanup = null;

function listenForAssistHotkey(feat, event) {
  if (event) {
    if (typeof event.preventDefault === 'function') event.preventDefault();
    if (typeof event.stopPropagation === 'function') event.stopPropagation();
  }
  if (document.activeElement && typeof document.activeElement.blur === 'function') {
    document.activeElement.blur();
  }

  // Cancel any existing listener cleanly
  if (activeHotkeyCleanup) {
    activeHotkeyCleanup();
    activeHotkeyCleanup = null;
  }

  const btn = document.getElementById(`hotkey-${feat}`);
  if (!btn) return;

  const originalText = btn.innerText;
  btn.innerText = 'Press key...';
  btn.classList.add('listening');

  // Pause hotkeys during rebinding
  ipcRenderer.invoke('hotkeys:pause', true);

  const cleanup = () => {
    window.removeEventListener('keydown', onKeyDown, true);
    window.removeEventListener('mousedown', onMouseDown, true);
    activeHotkeyCleanup = null;
    btn.classList.remove('listening');
    ipcRenderer.invoke('hotkeys:pause', false);
  };

  const onKeyDown = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    e.stopImmediatePropagation();

    let key = e.key.toUpperCase();
    if (key === 'ESCAPE' || key === 'ESC') {
      btn.innerText = originalText;
      cleanup();
      return;
    }

    if (key.startsWith('ARROW')) key = key.replace('ARROW', '');
    if (key === ' ') key = 'SPACE';

    let vk = e.keyCode || e.which;
    if (e.code && e.code.startsWith('Numpad')) {
      const numpadCodeToVK = {
        'Numpad0': 96, 'Numpad1': 97, 'Numpad2': 98, 'Numpad3': 99, 'Numpad4': 100,
        'Numpad5': 101, 'Numpad6': 102, 'Numpad7': 103, 'Numpad8': 104, 'Numpad9': 105,
        'NumpadMultiply': 106, 'NumpadAdd': 107, 'NumpadSubtract': 109,
        'NumpadDecimal': 110, 'NumpadDivide': 111
      };
      if (numpadCodeToVK[e.code]) {
        vk = numpadCodeToVK[e.code];
      }
    }

    window.assistHotkeys[feat] = vk;
    btn.innerText = getAssistVKName(vk);
    cleanup();

    try {
      await ipcRenderer.invoke('assist:setHotkey', { feature: feat, key, vk });
      appLog(`Assist ${feat.toUpperCase()} bound to ${getAssistVKName(vk)}`, 'success');
    } catch (err) {
      console.error('Failed to bind assist hotkey:', err);
    }
  };

  const onMouseDown = (e) => {
    // If clicked outside the button, cancel listening
    if (e.target !== btn) {
      btn.innerText = originalText;
      cleanup();
    }
  };

  activeHotkeyCleanup = () => {
    btn.innerText = originalText;
    cleanup();
  };

  window.addEventListener('keydown', onKeyDown, { capture: true });
  window.addEventListener('mousedown', onMouseDown, { capture: true });
}

window.addEventListener('blur', () => {
  if (activeHotkeyCleanup) {
    activeHotkeyCleanup();
  }
});

function updateAssistHotkeyBadges() {
  for (const [feat, vk] of Object.entries(window.assistHotkeys)) {
    const btn = document.getElementById(`hotkey-${feat}`);
    if (btn) btn.innerText = getAssistVKName(vk);
  }
}

function getAssistVKName(vk) {
  if (!vk) return 'None';
  if (vk >= 112 && vk <= 123) return `F${vk - 111}`;
  if (vk >= 65 && vk <= 90) return String.fromCharCode(vk);
  if (vk >= 48 && vk <= 57) return String.fromCharCode(vk);
  if (vk >= 96 && vk <= 105) return `NUM ${vk - 96}`;
  if (vk === 106) return 'NUM *';
  if (vk === 107) return 'NUM +';
  if (vk === 109) return 'NUM -';
  if (vk === 110) return 'NUM .';
  if (vk === 111) return 'NUM /';
  if (vk === 32) return 'SPACE';
  if (vk === 9) return 'TAB';
  if (vk === 13) return 'ENTER';
  if (vk === 27) return 'ESC';
  if (vk === 5) return 'M4';
  if (vk === 6) return 'M5';
  return `VK_${vk}`;
}

// Background assist updates from main process
ipcRenderer.on('assist_update', (_, data) => {
  if (data) {
    Object.assign(window.assistState, data);
    updateAssistUI();
  }
});

window.loadAssistStatus = loadAssistStatus;
window.updateAssistUI = updateAssistUI;
window.setCamMouseButton = setCamMouseButton;
window.setHarvestMethod = setHarvestMethod;
window.browseAssistImage = browseAssistImage;
window.openHarvestModal = openHarvestModal;
window.closeHarvestModal = closeHarvestModal;
window.syncHarvestModalToState = syncHarvestModalToState;
window.renderHarvestChips = renderHarvestChips;
window.removeHarvestImage = removeHarvestImage;
window.addBulkHarvestImages = addBulkHarvestImages;
window.loadDefaultHarvestImages = loadDefaultHarvestImages;
window.clearAllHarvestImages = clearAllHarvestImages;
window.saveHarvestModalConfig = saveHarvestModalConfig;
window.openCookModal = openCookModal;
window.closeCookModal = closeCookModal;
window.loadDefaultCookImages = loadDefaultCookImages;
window.openSnowModal = openSnowModal;
window.closeSnowModal = closeSnowModal;
window.loadDefaultSnowImages = loadDefaultSnowImages;
window.refreshAssistWindows = refreshAssistWindows;
window.toggleAssistConnection = toggleAssistConnection;
window.toggleAssistFeature = toggleAssistFeature;
window.updateAssistSettings = updateAssistSettings;
window.saveAssistSettings = saveAssistSettings;
window.listenForAssistHotkey = listenForAssistHotkey;
window.updateAssistHotkeyBadges = updateAssistHotkeyBadges;
window.getAssistVKName = getAssistVKName;
