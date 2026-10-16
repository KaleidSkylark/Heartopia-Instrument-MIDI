// ═══════════════════════════════════════════════════════════════════
// Module: Online Community Supabase Search & Sync
// ═══════════════════════════════════════════════════════════════════

function handleSearchInput() {
  clearTimeout(window.searchTimeout);
  window.searchTimeout = setTimeout(() => {
    window.currentPage = 1;
    searchOnline();
  }, 400);
}

function refreshOnline() {
  const sInput = document.getElementById('search-online');
  if (sInput) sInput.value = '';
  window.currentPage = 1;
  setOnlineFilter('All');
}

function setOnlineFilter(t) {
  window.currentOnlineFilter = t;
  document.querySelectorAll('#online .filter-btn').forEach(b => b.classList.remove('active'));
  const btn = document.getElementById(`on-${t.toLowerCase()}`);
  if (btn) btn.classList.add('active');
  window.currentPage = 1;
  searchOnline();
}

function changePage(delta) {
  const maxPage = Math.ceil(window.totalItems / window.itemsPerPage) || 1;
  const newPage = window.currentPage + delta;
  if (newPage >= 1 && newPage <= maxPage) {
    window.currentPage = newPage;
    searchOnline();
  }
}

function changePerPage() {
  window.itemsPerPage = parseInt(document.getElementById('online-per-page')?.value) || 50;
  window.currentPage = 1;
  searchOnline();
}

async function searchOnline() {
  const query = document.getElementById('search-online')?.value || '';
  const listEl = document.getElementById('online-list');
  if (!listEl) return;

  listEl.innerHTML = `<div style="padding: 40px; text-align: center; color: var(--text-muted);">Connecting to community library (Page ${window.currentPage})...</div>`;

  window.itemsPerPage = parseInt(document.getElementById('online-per-page')?.value) || 50;

  try {
    const res = await ipcRenderer.invoke('online:search', query, window.currentOnlineFilter, window.currentPage, window.itemsPerPage);

    window.onlineLoaded = true;
    window.totalItems = res.total || 0;
    const maxPage = Math.ceil(window.totalItems / window.itemsPerPage) || 1;

    const pageInfo = document.getElementById('page-info');
    if (pageInfo) pageInfo.innerText = `Page ${window.currentPage} of ${maxPage} (${window.totalItems} songs)`;

    const pagination = document.getElementById('online-pagination');
    if (pagination) pagination.style.display = window.totalItems > 0 ? 'flex' : 'none';

    if (!res.songs || res.songs.length === 0) {
      listEl.innerHTML = '<div style="padding: 40px; text-align: center; color: var(--text-muted);">No community songs found.</div>';
      return;
    }

    listEl.innerHTML = '';
    const fragment = document.createDocumentFragment();

    res.songs.forEach(s => {
      const is15k = (s.instrument_type || '').includes('15');
      const row = document.createElement('div');
      row.className = 'song-row';
      row.innerHTML = `
        <div style="flex: 1; display: flex; align-items: center; overflow: hidden; pointer-events: none;">
          <input type="checkbox" class="chk-select" value="${escapeHtml(s.song_name)}" style="margin-right: 14px; flex-shrink: 0; width: 16px; height: 16px; accent-color: var(--primary); pointer-events: auto;">
          <div style="flex: 1; overflow: hidden;">
            <span class="song-tag ${is15k ? 'tag-15k' : 'tag-22k'}">${s.instrument_type || '22-Keys'}</span>
            <span class="song-name-text" title="${escapeHtml(s.song_name)}">${escapeHtml(s.song_name)}</span>
          </div>
        </div>
        <button class="btn-neu accent btn-download" style="padding: 6px 14px; font-size: 0.82em; pointer-events: auto;">⬇ Download</button>
      `;

      row.addEventListener('click', (e) => {
        if (e.target.closest('button') || e.target.closest('input[type="checkbox"]')) return;
        selectSong(s.song_name, 'online');
      });

      const chk = row.querySelector('.chk-select');
      if (chk) chk.addEventListener('change', updateSelectCount);

      const dlBtn = row.querySelector('.btn-download');
      if (dlBtn) {
        dlBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          downloadSingle(s.song_name, dlBtn);
        });
      }

      fragment.appendChild(row);
    });

    listEl.appendChild(fragment);

    const selectAll = document.getElementById('chk-select-all');
    if (selectAll) selectAll.checked = false;
    updateSelectCount();
    appLog(`Online search loaded ${res.songs.length} community tracks.`, 'success');
  } catch (err) {
    listEl.innerHTML = '<div style="padding: 40px; text-align: center; color: var(--danger);">Failed to connect to Supabase: ' + err.message + '</div>';
    appLog('Online connection error: ' + err.message, 'error');
  }
}

function toggleSelectAll() {
  const isChecked = document.getElementById('chk-select-all')?.checked || false;
  document.querySelectorAll('#online-list .chk-select').forEach(cb => (cb.checked = isChecked));
  updateSelectCount();
}

function updateSelectCount() {
  const count = document.querySelectorAll('#online-list .chk-select:checked').length;
  const countEl = document.getElementById('selected-count');
  if (countEl) countEl.innerText = `${count} selected`;
}

async function downloadSingle(name, btn) {
  const og = btn ? btn.innerText : '⬇ Download';
  if (btn) btn.innerText = '...';
  appLog(`Downloading community song: ${name}...`, 'info');

  try {
    const res = await ipcRenderer.invoke('online:download', name);
    if (res.ok) {
      if (btn) {
        btn.innerText = '✔';
        setTimeout(() => (btn.innerText = og), 2000);
      }
      showModal('Downloaded', `Saved "${name}" to your local library!`);
      if (typeof loadPlaylistData === 'function') loadPlaylistData();
    } else {
      if (btn) {
        btn.innerText = '❌';
        setTimeout(() => (btn.innerText = og), 2000);
      }
      showModal('Error', 'Download failed.');
    }
  } catch (e) {
    if (btn) {
      btn.innerText = '❌';
      setTimeout(() => (btn.innerText = og), 2000);
    }
    showModal('Error', 'Download failed: ' + e.message);
  }
}

async function downloadSelected() {
  const names = Array.from(document.querySelectorAll('#online-list .chk-select:checked')).map(cb => cb.value);
  if (names.length === 0) {
    showModal('Info', 'Select songs first.');
    return;
  }

  showModal('Downloading', `Downloading ${names.length} songs...`);
  appLog(`Batch downloading ${names.length} songs...`, 'info');

  try {
    const res = await ipcRenderer.invoke('online:downloadBatch', names);
    showModal('Batch Download Complete', `✅ Success: ${res.success}\n❌ Failed: ${res.failed}`);
    if (typeof loadPlaylistData === 'function') loadPlaylistData();
    refreshOnline();
  } catch (e) {
    showModal('Error', 'Batch download failed: ' + e.message);
  }
}

async function uploadOnlineFiles(input) {
  if (!input.files || input.files.length === 0) return;

  const fileData = [];
  for (const f of input.files) {
    if (f.size > 512000) continue;
    const text = await f.text();
    fileData.push({ name: f.name, size: f.size, content: text });
  }

  if (fileData.length === 0) {
    showModal('Info', 'Selected files were larger than 500KB or empty.');
    return;
  }

  showModal('Uploading', 'Uploading songs to community Supabase...');
  appLog(`Uploading ${fileData.length} files...`, 'info');

  try {
    const res = await ipcRenderer.invoke('online:upload', fileData);
    showModal('Upload Report', `✅ Uploaded: ${res.uploaded}\n⚠ Duplicates: ${res.duplicates}\n❌ Errors: ${res.errors}`);
    searchOnline();
  } catch (e) {
    showModal('Error', 'Upload failed: ' + e.message);
  }
  input.value = '';
}

// Expose globally on window
window.handleSearchInput = handleSearchInput;
window.refreshOnline = refreshOnline;
window.setOnlineFilter = setOnlineFilter;
window.changePage = changePage;
window.changePerPage = changePerPage;
window.searchOnline = searchOnline;
window.toggleSelectAll = toggleSelectAll;
window.updateSelectCount = updateSelectCount;
window.downloadSingle = downloadSingle;
window.downloadSelected = downloadSelected;
window.uploadOnlineFiles = uploadOnlineFiles;
