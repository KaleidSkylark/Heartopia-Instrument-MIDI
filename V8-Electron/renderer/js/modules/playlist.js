// ═══════════════════════════════════════════════════════════════════
// Module: Local Playlist & Queue Manager (Fast Paginated)
// ═══════════════════════════════════════════════════════════════════

window.playlistCurrentPage = 1;
window.playlistPerPage = 50;
window.playlistSearchTimeout = null;

async function loadPlaylistData() {
  console.log('[App] Loading playlist data from backend...');
  try {
    const data = await ipcRenderer.invoke('songs:list');
    window.allSongs = (data.songs || []).map(s => ({ name: s.name, date: s.mtime || 0 }));
    window.favorites = data.favorites || [];
    window.queue = data.queue || [];
    window.playlistCurrentPage = 1;
    renderPlaylist();
    renderQueueList();
    appLog(`Library loaded: ${window.allSongs.length} songs.`, 'success');
  } catch (e) {
    console.error('Failed to load library:', e);
    window.allSongs = [];
    appLog('Failed to load library: ' + e.message, 'error');
  }
}

function setPlaylistFilter(type) {
  window.currentPlaylistFilter = type;
  document.querySelectorAll('#playlist .filter-btn').forEach(b => b.classList.remove('active'));
  const btn = document.getElementById(`pl-${type.toLowerCase()}`);
  if (btn) btn.classList.add('active');
  window.playlistCurrentPage = 1;
  renderPlaylist();
}

function handlePlaylistSearch() {
  clearTimeout(window.playlistSearchTimeout);
  window.playlistSearchTimeout = setTimeout(() => {
    window.playlistCurrentPage = 1;
    renderPlaylist();
  }, 120);
}

function getFilteredPlaylist() {
  const query = (document.getElementById('search-local')?.value || '').toLowerCase().trim();
  const favOnly = document.getElementById('chk-fav')?.checked;
  const sortMode = document.getElementById('sort-select')?.value || 'date_desc';

  let displayList = [...window.allSongs];
  displayList.sort((a, b) => {
    if (sortMode === 'name_asc') return a.name.localeCompare(b.name);
    if (sortMode === 'name_desc') return b.name.localeCompare(a.name);
    if (sortMode === 'date_desc') return b.date - a.date;
    if (sortMode === 'date_asc') return a.date - b.date;
    return 0;
  });

  return displayList.filter(obj => {
    const s = obj.name;
    const is15k = s.includes('_15K') || s.includes('15K');

    if (window.currentPlaylistFilter === '22K' && is15k) return false;
    if (window.currentPlaylistFilter === '15K' && !is15k) return false;
    if (favOnly && !window.favorites.includes(s)) return false;
    if (query && !s.toLowerCase().includes(query)) return false;
    return true;
  });
}

function changePlaylistPage(delta) {
  const filtered = getFilteredPlaylist();
  const perPage = window.playlistPerPage === 'all' ? Math.max(1, filtered.length) : window.playlistPerPage;
  const maxPage = Math.ceil(filtered.length / perPage) || 1;
  const newPage = window.playlistCurrentPage + delta;
  if (newPage >= 1 && newPage <= maxPage) {
    window.playlistCurrentPage = newPage;
    renderPlaylist();
  }
}

function changePlaylistPerPage() {
  const sel = document.getElementById('playlist-per-page');
  const val = sel?.value || '50';
  window.playlistPerPage = val === 'all' ? 'all' : parseInt(val);
  window.playlistCurrentPage = 1;
  renderPlaylist();
}

function renderPlaylist() {
  const listEl = document.getElementById('local-list');
  if (!listEl) return;
  listEl.innerHTML = '';

  const filtered = getFilteredPlaylist();
  const totalCount = filtered.length;

  const perPage = window.playlistPerPage === 'all' ? Math.max(1, totalCount) : window.playlistPerPage;
  const maxPage = Math.ceil(totalCount / perPage) || 1;

  if (window.playlistCurrentPage > maxPage) {
    window.playlistCurrentPage = maxPage;
  }
  if (window.playlistCurrentPage < 1) {
    window.playlistCurrentPage = 1;
  }

  // Update Pagination Controls
  const pageInfo = document.getElementById('playlist-page-info');
  if (pageInfo) {
    pageInfo.innerText = `Page ${window.playlistCurrentPage} of ${maxPage} (${totalCount} songs)`;
  }
  const paginContainer = document.getElementById('playlist-pagination');
  if (paginContainer) {
    paginContainer.style.display = totalCount > 0 ? 'flex' : 'none';
  }

  if (totalCount === 0) {
    listEl.innerHTML = '<div style="padding: 30px; text-align: center; color: var(--text-muted);">No songs match your search or filters. Check Settings to set your folder!</div>';
    return;
  }

  // Slice for instant lag-free rendering
  const startIndex = (window.playlistCurrentPage - 1) * perPage;
  const pageItems = window.playlistPerPage === 'all' ? filtered : filtered.slice(startIndex, startIndex + perPage);

  const fragment = document.createDocumentFragment();

  pageItems.forEach(obj => {
    const s = obj.name;
    const is15k = s.includes('_15K') || s.includes('15K');
    const isFav = window.favorites.includes(s);
    const inQueue = window.queue.includes(s);
    const isActive = window.currentSong === s;

    const row = document.createElement('div');
    row.className = `song-row ${isActive ? 'active' : ''}`;
    row.setAttribute('data-song', s);

    const displayName = s.replace('.txt', '').replace('_15K', '').replace('_22K', '').replace('_Violin', '');

    row.innerHTML = `
      <div style="flex: 1; display: flex; align-items: center; overflow: hidden; pointer-events: none;">
        <input type="checkbox" class="chk-playlist-select" value="${escapeHtml(s)}" style="margin-right: 12px; flex-shrink: 0; width: 16px; height: 16px; accent-color: var(--primary); pointer-events: auto;">
        <div style="flex: 1; display: flex; align-items: center; overflow: hidden;">
          <span class="song-tag ${is15k ? 'tag-15k' : 'tag-22k'}">${is15k ? '15K' : '22K'}</span>
          <span class="song-name-text" title="${escapeHtml(s)}">${escapeHtml(displayName)}</span>
        </div>
      </div>
      <div class="flex-row gap-sm" style="pointer-events: auto;">
        <button class="btn-neu btn-edit" title="Edit in Studio Editor" style="padding: 5px 9px;">✏️</button>
        <button class="btn-neu btn-queue ${inQueue ? 'accent' : ''}" title="${inQueue ? 'In Queue' : 'Add to Queue'}" style="padding: 5px 9px;">
          ${inQueue ? '✓' : '+'}
        </button>
        <button class="btn-neu btn-fav" style="padding: 5px 9px; color: ${isFav ? 'var(--tag-22k)' : 'var(--text-muted)'};" title="Favorite">
          ★
        </button>
        <button class="btn-neu btn-del danger" style="padding: 5px 9px;" title="Delete">
          🗑
        </button>
      </div>
    `;

    // Make the ENTIRE row bar selectable
    row.addEventListener('click', (e) => {
      if (e.target.closest('button') || e.target.closest('input[type="checkbox"]')) {
        return;
      }
      selectSong(s, 'local');
    });

    const chk = row.querySelector('.chk-playlist-select');
    if (chk) chk.addEventListener('change', updatePlaylistSelectCount);

    const btnEdit = row.querySelector('.btn-edit');
    if (btnEdit) btnEdit.addEventListener('click', (e) => { e.stopPropagation(); openEditor(s); });

    const btnQueue = row.querySelector('.btn-queue');
    if (btnQueue) btnQueue.addEventListener('click', (e) => { e.stopPropagation(); toggleQueue(s); });

    const btnFav = row.querySelector('.btn-fav');
    if (btnFav) btnFav.addEventListener('click', (e) => { e.stopPropagation(); toggleFav(s); });

    const btnDel = row.querySelector('.btn-del');
    if (btnDel) btnDel.addEventListener('click', (e) => { e.stopPropagation(); deleteSong(s); });

    fragment.appendChild(row);
  });

  listEl.appendChild(fragment);

  const selectAllCb = document.getElementById('chk-playlist-select-all');
  if (selectAllCb) selectAllCb.checked = false;
  updatePlaylistSelectCount();
}

function togglePlaylistSelectAll() {
  const isChecked = document.getElementById('chk-playlist-select-all')?.checked || false;
  document.querySelectorAll('#local-list .chk-playlist-select').forEach(cb => (cb.checked = isChecked));
  updatePlaylistSelectCount();
}

function updatePlaylistSelectCount() {
  const count = document.querySelectorAll('#local-list .chk-playlist-select:checked').length;
  const countBadge = document.getElementById('playlist-selected-count');
  if (countBadge) countBadge.innerText = `${count} selected`;
}

async function deleteSelectedPlaylist() {
  const selected = Array.from(document.querySelectorAll('#local-list .chk-playlist-select:checked')).map(cb => cb.value);
  if (selected.length === 0) {
    showModal('Info', 'No songs selected for deletion.');
    return;
  }

  showConfirm('Delete Multiple Songs', `Are you sure you want to delete ${selected.length} selected songs?`, async () => {
    const res = await ipcRenderer.invoke('songs:deleteBatch', selected);
    if (res && res.ok) {
      appLog(`Deleted ${res.count} songs.`, 'success');
      loadPlaylistData();
    } else {
      showModal('Error', 'Batch deletion failed.');
    }
  });
}

function updatePlaylistActiveSong(fn) {
  document.querySelectorAll('#local-list .song-row').forEach(row => {
    if (row.getAttribute('data-song') === fn) {
      row.classList.add('active');
    } else {
      row.classList.remove('active');
    }
  });
}

async function selectSong(fn, source = 'local') {
  window.currentSong = fn;
  window.currentSongSource = source;
  if (window.isPreviewing && typeof stopAudioPreview === 'function') {
    stopAudioPreview();
  }

  // Update in-place without re-rendering or wiping the DOM!
  updatePlaylistActiveSong(fn);
  updatePlayerUI(fn);

  ipcRenderer.invoke('songs:select', fn).catch(() => {});
}

function updatePlayerUI(fn) {
  const nameEl = document.getElementById('player-song-name');
  const tagEl = document.getElementById('player-song-tag');

  if (!fn || fn === 'None') {
    if (nameEl) nameEl.innerText = 'No song selected';
    if (tagEl) tagEl.style.display = 'none';
    return;
  }

  const cleanName = fn.replace('.txt', '').replace('_15K', '').replace('_22K', '').replace('_Violin', '');
  if (nameEl) nameEl.innerText = cleanName;

  const is15k = fn.includes('15K');
  if (tagEl) {
    tagEl.style.display = 'inline-block';
    tagEl.className = is15k ? 'song-tag tag-15k' : 'song-tag tag-22k';
    tagEl.innerText = is15k ? '15K' : '22K Half';
  }

  if (typeof redrawCanvas === 'function') {
    redrawCanvas('canvas-player');
  }
}

async function toggleFav(fn) {
  const idx = window.favorites.indexOf(fn);
  const nowFav = idx === -1;
  if (nowFav) {
    window.favorites.push(fn);
  } else {
    window.favorites.splice(idx, 1);
  }

  // In-place DOM update for instant responsiveness
  document.querySelectorAll(`#local-list .song-row[data-song="${CSS.escape(fn)}"] .btn-fav`).forEach(btn => {
    btn.style.color = nowFav ? 'var(--tag-22k)' : 'var(--text-muted)';
  });

  if (window.currentPlaylistFilter === 'Favorites') {
    renderPlaylist();
  }

  ipcRenderer.invoke('songs:toggleFav', fn).catch(() => {});
}

async function deleteSong(fn) {
  showConfirm('Delete Song', `Are you sure you want to delete "${fn}"?`, async () => {
    const res = await ipcRenderer.invoke('songs:delete', fn);
    if (res && res.ok) {
      appLog(`Deleted song: ${fn}`, 'success');
      loadPlaylistData();
    }
  });
}

function toggleQueue(fn) {
  const inQueue = window.queue.includes(fn);
  if (inQueue) {
    window.queue = window.queue.filter(item => item !== fn);
  } else {
    window.queue.push(fn);
  }

  // In-place DOM button update without touching playlist rows
  document.querySelectorAll(`#local-list .song-row[data-song="${CSS.escape(fn)}"] .btn-queue`).forEach(btn => {
    if (!inQueue) {
      btn.classList.add('accent');
      btn.innerText = '✓';
      btn.title = 'In Queue';
    } else {
      btn.classList.remove('accent');
      btn.innerText = '+';
      btn.title = 'Add to Queue';
    }
  });

  updateQueueBackend();
}

function clearQueue() {
  window.queue = [];
  updateQueueBackend();
  // Clear accent on all queue buttons in-place
  document.querySelectorAll('#local-list .btn-queue').forEach(btn => {
    btn.classList.remove('accent');
    btn.innerText = '+';
    btn.title = 'Add to Queue';
  });
}

async function updateQueueBackend() {
  renderQueueList();
  ipcRenderer.invoke('queue:update', window.queue).catch(() => {});
}

function renderQueueList() {
  const container = document.getElementById('queue-list-container');
  const countBadge = document.getElementById('queue-count-badge');
  if (countBadge) countBadge.innerText = window.queue.length;
  if (!container) return;

  if (window.queue.length === 0) {
    container.innerHTML = '<div style="padding: 24px; text-align: center; color: var(--text-muted); font-size: 0.88em;">Queue is empty.<br>Click <b>+</b> on any song to add.</div>';
    return;
  }

  container.innerHTML = '';
  const fragment = document.createDocumentFragment();

  window.queue.forEach((s, idx) => {
    const is15k = s.includes('15K');
    const clean = s.replace('.txt', '').replace('_15K', '').replace('_22K', '');

    const item = document.createElement('div');
    item.className = 'queue-item';

    const info = document.createElement('div');
    info.style.cssText = 'display: flex; align-items: center; overflow: hidden;';

    const num = document.createElement('span');
    num.style.cssText = 'color: var(--primary); margin-right: 8px; font-weight: 800;';
    num.innerText = `#${idx + 1}`;

    const tag = document.createElement('span');
    tag.className = `song-tag ${is15k ? 'tag-15k' : 'tag-22k'}`;
    tag.style.marginRight = '8px';
    tag.innerText = is15k ? '15K' : '22K';

    const name = document.createElement('span');
    name.className = 'song-name-text';
    name.innerText = clean;
    name.title = s;

    info.appendChild(num);
    info.appendChild(tag);
    info.appendChild(name);

    const btnRemove = document.createElement('button');
    btnRemove.className = 'btn-neu danger';
    btnRemove.style.cssText = 'padding: 4px 8px; font-size: 0.75em;';
    btnRemove.innerText = '✕';
    btnRemove.title = 'Remove from Queue';
    btnRemove.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleQueue(s);
    });

    item.appendChild(info);
    item.appendChild(btnRemove);
    fragment.appendChild(item);
  });

  container.appendChild(fragment);
}

// Expose globally on window
window.loadPlaylistData = loadPlaylistData;
window.setPlaylistFilter = setPlaylistFilter;
window.handlePlaylistSearch = handlePlaylistSearch;
window.changePlaylistPage = changePlaylistPage;
window.changePlaylistPerPage = changePlaylistPerPage;
window.renderPlaylist = renderPlaylist;
window.togglePlaylistSelectAll = togglePlaylistSelectAll;
window.updatePlaylistSelectCount = updatePlaylistSelectCount;
window.deleteSelectedPlaylist = deleteSelectedPlaylist;
window.selectSong = selectSong;
window.updatePlayerUI = updatePlayerUI;
window.toggleFav = toggleFav;
window.deleteSong = deleteSong;
window.toggleQueue = toggleQueue;
window.clearQueue = clearQueue;
window.updatePlaylistActiveSong = updatePlaylistActiveSong;
window.renderQueueList = renderQueueList;
