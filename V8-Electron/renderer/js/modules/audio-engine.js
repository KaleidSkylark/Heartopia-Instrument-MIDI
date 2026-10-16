// ═══════════════════════════════════════════════════════════════════
// Module: Web Audio Synthesis & Piano Roll Visualizer
// ═══════════════════════════════════════════════════════════════════

window.audioCtx = null;
window.isPreviewing = false;
window.masterGain = null;
window.schedulerInterval = null;
window.visualizerFrame = null;
window.audioEvents = [];
window.nextEventIndex = 0;
window.nextEventTime = 0;
window.visualStartTime = 0;
window.visualNoteRange = { min: 48, max: 84 };
window.currentCanvasId = 'canvas-player';

window.isEditorPreviewing = false;
window.currentEditorFile = null;
window.isPaused = false;
window.editorTotalDuration = 0;
window.isSeeking = false;
window.selectedNote = null;
window.gridCanvas = null;

function initAudio() {
  if (!window.audioCtx) {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    window.audioCtx = new AudioContextClass();

    window.masterGain = window.audioCtx.createGain();
    window.masterGain.gain.value = 0.85;

    const compressor = window.audioCtx.createDynamicsCompressor();
    compressor.threshold.value = -12;
    compressor.knee.value = 24;
    compressor.ratio.value = 6;
    compressor.attack.value = 0.003;
    compressor.release.value = 0.25;

    window.masterGain.connect(compressor);
    compressor.connect(window.audioCtx.destination);
  }
  if (window.audioCtx.state === 'suspended') {
    window.audioCtx.resume();
  }
}

function parseSongToEvents(rawText, is15k) {
  if (!rawText) return [];
  const lines = rawText.split(/\r?\n/);
  
  // Resilient fallback maps in case IPC init is delayed
  const fallback22 = {
    ',':48, 'L':49, '.':50, ';':51, '/':52, 'O':53, '0':54, 'P':55,
    '-':56, '[':57, '=':58, ']':59, 'Z':60, 'S':61, 'X':62, 'D':63,
    'C':64, 'V':65, 'G':66, 'B':67, 'H':68, 'N':69, 'J':70, 'M':71,
    'Q':72, '2':73, 'W':74, '3':75, 'E':76, 'R':77, '5':78, 'T':79,
    '6':80, 'Y':81, '7':82, 'U':83, 'I':84
  };
  const fallback15 = {
    'A':60, 'S':62, 'D':64, 'F':65, 'G':67, 'H':69, 'J':71,
    'Q':72, 'W':74, 'E':76, 'R':77, 'T':79, 'Y':81, 'U':83, 'I':84
  };

  const keyMap = is15k
    ? (window.MAP_15_REV && Object.keys(window.MAP_15_REV).length ? window.MAP_15_REV : fallback15)
    : (window.MAP_22_REV && Object.keys(window.MAP_22_REV).length ? window.MAP_22_REV : fallback22);

  const events = [];
  let currentTime = 0;
  const activeNotes = {};

  for (let idx = 0; idx < lines.length; idx++) {
    const line = lines[idx].trim();
    if (!line) continue;
    const upper = line.toUpperCase();

    if (upper.includes('DELAY')) {
      const ms = parseInt(line.replace(/\D/g, '')) || 0;
      currentTime += ms / 1000.0;
    } else if (upper.includes('KEYBOARD')) {
      const parts = line.split(':');
      if (parts.length >= 3) {
        const rawKey = parts[1].trim().toUpperCase();
        const action = parts[2].trim().toLowerCase();
        const midiNote = keyMap[rawKey];

        if (midiNote !== undefined) {
          if (action === 'keydown') {
            activeNotes[rawKey] = { start: currentTime, note: midiNote, line: idx };
          } else if (action === 'keyup') {
            if (activeNotes[rawKey]) {
              const start = activeNotes[rawKey].start;
              const dur = Math.max(0.12, currentTime - start);
              events.push({
                time: start,
                duration: dur,
                note: midiNote,
                lineNum: activeNotes[rawKey].line
              });
              delete activeNotes[rawKey];
            }
          }
        }
      }
    }
  }

  for (const k in activeNotes) {
    events.push({
      time: activeNotes[k].start,
      duration: 0.25,
      note: activeNotes[k].note,
      lineNum: activeNotes[k].line
    });
  }

  events.sort((a, b) => a.time - b.time);
  return events;
}

function startAudioEngine(songData, is15k, canvasId, speedControlId, isEditor = false) {
  initAudio();
  window.audioEvents = parseSongToEvents(songData, is15k);
  if (window.audioEvents.length === 0) {
    showModal('Info', 'No playable notes found in this file.');
    return;
  }

  window.currentCanvasId = canvasId;
  window.visualNoteRange = is15k ? { min: 60, max: 84 } : { min: 48, max: 84 };
  window.gridCanvas = null;
  const speed = parseFloat(document.getElementById(speedControlId)?.value || 1.0);

  for (const ev of window.audioEvents) {
    ev.time = ev.time / speed;
    ev.duration = ev.duration / speed;
  }

  window.editorTotalDuration = window.audioEvents[window.audioEvents.length - 1].time + 1.2;
  window.nextEventIndex = 0;
  window.nextEventTime = window.audioCtx.currentTime + 0.1;
  window.visualStartTime = window.nextEventTime;

  if (isEditor) {
    window.isEditorPreviewing = true;
    window.isPaused = false;
    document.getElementById('editor-time-total').innerText = formatTime(window.editorTotalDuration);
    document.getElementById('editor-seek-slider').max = window.editorTotalDuration;
    document.getElementById('btn-editor-play').disabled = true;
    document.getElementById('btn-editor-pause').disabled = false;
    document.getElementById('btn-editor-stop').disabled = false;
  } else {
    window.isPreviewing = true;
    const btn = document.getElementById('btn-audio-preview');
    if (btn) {
      btn.innerText = '⏹ Stop Audio Preview';
      btn.classList.add('playing');
    }
  }

  if (window.schedulerInterval) clearInterval(window.schedulerInterval);
  window.schedulerInterval = setInterval(scheduler, 25);

  if (window.visualizerFrame) cancelAnimationFrame(window.visualizerFrame);
  renderPianoRoll();

  appLog(`Synthesizing ${window.audioEvents.length} notes...`, 'info');
}

function stopAudioEngine() {
  if (window.schedulerInterval) clearInterval(window.schedulerInterval);
  window.schedulerInterval = null;
  if (window.visualizerFrame) cancelAnimationFrame(window.visualizerFrame);
  window.visualizerFrame = null;
  window.nextEventIndex = 0;
}

function scheduler() {
  if (!window.audioCtx || window.isPaused) return;

  const lookAhead = 0.1;
  const now = window.audioCtx.currentTime;
  const startTime = window.nextEventTime;

  while (
    window.nextEventIndex < window.audioEvents.length &&
    startTime + window.audioEvents[window.nextEventIndex].time < now + lookAhead
  ) {
    const ev = window.audioEvents[window.nextEventIndex];
    if (startTime + ev.time > now - 0.05) {
      scheduleNote(ev.note, startTime + ev.time, ev.duration);
    }
    window.nextEventIndex++;
  }

  if (window.nextEventIndex >= window.audioEvents.length && now > startTime + window.audioEvents[window.audioEvents.length - 1].time + 1.0) {
    if (window.isEditorPreviewing && typeof stopEditorPreview === 'function') stopEditorPreview();
    if (window.isPreviewing && typeof stopAudioPreview === 'function') stopAudioPreview();
  }
}

function scheduleNote(midi, start, dur) {
  try {
    const osc = window.audioCtx.createOscillator();
    osc.type = 'triangle';
    const freq = 440 * Math.pow(2, (midi - 69) / 12);
    osc.frequency.setValueAtTime(freq, start);

    const filter = window.audioCtx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.Q.value = 0.5;
    filter.frequency.setValueAtTime(freq * 8, start);
    filter.frequency.exponentialRampToValueAtTime(freq, start + 0.45);

    const panner = window.audioCtx.createStereoPanner();
    let pan = (midi - 66) / 24;
    pan = Math.max(-0.8, Math.min(0.8, pan));
    panner.pan.setValueAtTime(pan, start);

    const gain = window.audioCtx.createGain();
    const vol = 0.36;
    gain.gain.setValueAtTime(0, start);
    gain.gain.linearRampToValueAtTime(vol, start + 0.012);
    gain.gain.exponentialRampToValueAtTime(vol * 0.7, start + 0.25);
    gain.gain.setValueAtTime(vol * 0.7, start + dur);
    gain.gain.exponentialRampToValueAtTime(0.001, start + dur + 0.4);

    osc.connect(filter);
    filter.connect(gain);
    gain.connect(panner);
    panner.connect(window.masterGain);

    osc.start(start);
    osc.stop(start + dur + 0.5);

    setTimeout(() => {
      try {
        osc.disconnect();
        gain.disconnect();
        filter.disconnect();
        panner.disconnect();
      } catch (e) {}
    }, (dur + 0.8) * 1000);
  } catch (err) {}
}

let lastHighlightedLine = -1;
function highlightEditorLine(lineNum) {
  if (window.isSeeking || !window.monacoEditor) return;
  const targetLine = lineNum + 1;
  if (targetLine === lastHighlightedLine) return;
  lastHighlightedLine = targetLine;

  window.decorations = window.monacoEditor.deltaDecorations(window.decorations, [
    {
      range: new window.monaco.Range(targetLine, 1, targetLine, 1),
      options: {
        isWholeLine: true,
        className: 'monaco-highlight-line',
        overviewRuler: { position: window.monaco.editor.OverviewRulerLane.Full }
      }
    }
  ]);

  const smoothScroll = document.getElementById('editor-smooth-scroll');
  if (smoothScroll && smoothScroll.checked) {
    window.monacoEditor.revealLineInCenterIfOutsideViewport(targetLine);
  }

  const statusLine = document.getElementById('editor-status-line');
  if (statusLine) {
    statusLine.innerText = `Line: ${targetLine}`;
  }
}

function renderPianoRoll() {
  if ((!window.isPreviewing && !window.isEditorPreviewing) || !window.audioCtx) return;

  const cvs = document.getElementById(window.currentCanvasId);
  if (!cvs) return;

  // Auto-resize canvas buffer to client dimensions for crisp rendering
  if (cvs.clientWidth > 0 && (cvs.width !== cvs.clientWidth || cvs.height !== cvs.clientHeight)) {
    cvs.width = cvs.clientWidth;
    cvs.height = cvs.clientHeight;
    window.gridCanvas = null;
  }

  const ctx = cvs.getContext('2d');
  const w = cvs.width;
  const h = cvs.height;
  const isLight = document.body.classList.contains('light-theme');

  const noteRange = window.visualNoteRange.max - window.visualNoteRange.min;
  const laneCount = noteRange + 1;
  const laneWidth = w / laneCount;
  const keyboardHeight = 36;
  const hitLineY = h - keyboardHeight;

  if (!window.gridCanvas || window.gridCanvas.width !== w || window.gridCanvas.height !== h) {
    window.gridCanvas = document.createElement('canvas');
    window.gridCanvas.width = w;
    window.gridCanvas.height = h;
    const gCtx = window.gridCanvas.getContext('2d');
    gCtx.fillStyle = isLight ? '#e4eaf4' : '#080a12';
    gCtx.fillRect(0, 0, w, h);

    for (let i = 0; i < laneCount; i++) {
      const lx = i * laneWidth;
      gCtx.fillStyle = i % 2 === 0 ? 'rgba(255,255,255,0.02)' : 'rgba(0,0,0,0.1)';
      gCtx.fillRect(lx, 0, laneWidth, hitLineY);
      gCtx.fillStyle = 'rgba(255,255,255,0.05)';
      gCtx.fillRect(lx, 0, 1, hitLineY);
    }
  }

  ctx.drawImage(window.gridCanvas, 0, 0);

  const lookAheadSeconds = 2.5;
  const now = window.audioCtx.currentTime;
  const elapsed = Math.max(0, now - window.visualStartTime);

  if (window.isEditorPreviewing && !window.isSeeking) {
    const seekSlider = document.getElementById('editor-seek-slider');
    const seekFill = document.getElementById('editor-seek-fill');
    const timeCur = document.getElementById('editor-time-current');
    const statusTime = document.getElementById('editor-status-time');
    if (seekSlider && seekFill && timeCur) {
      seekSlider.value = elapsed;
      const pct = Math.min(100, (elapsed / (window.editorTotalDuration || 1)) * 100);
      seekFill.style.width = `${pct}%`;
      timeCur.innerText = formatTime(elapsed);
      if (statusTime) statusTime.innerText = `${formatTime(elapsed)} / ${formatTime(window.editorTotalDuration || 0)}`;
    }
  }

  // Hit line
  ctx.strokeStyle = '#9d5df6';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(0, hitLineY);
  ctx.lineTo(w, hitLineY);
  ctx.stroke();

  // Active key tracker for piano keyboard rendering
  const activeKeys = {};
  let currentEventForHighlight = null;

  for (let i = 0; i < window.audioEvents.length; i++) {
    const ev = window.audioEvents[i];
    const timeToHit = ev.time - elapsed;

    if (timeToHit < lookAheadSeconds && timeToHit + ev.duration > -0.2) {
      const lane = Math.max(0, Math.min(noteRange, ev.note - window.visualNoteRange.min));
      const x = lane * laneWidth + 1;
      const barW = Math.max(2, laneWidth - 2);

      const pixelsPerSecond = hitLineY / lookAheadSeconds;
      const yBottom = hitLineY - timeToHit * pixelsPerSecond;
      const barH = Math.max(8, ev.duration * pixelsPerSecond);
      const yTop = yBottom - barH;

      ev.lastRenderBounds = { x, y: yTop, w: barW, h: barH };

      const isSelected = window.selectedNote && window.selectedNote.lineNum === ev.lineNum;
      const isCurrentlyPlaying = timeToHit <= 0 && timeToHit + ev.duration >= 0;

      if (isCurrentlyPlaying) {
        activeKeys[ev.note] = true;
        if (!currentEventForHighlight) currentEventForHighlight = ev;
      }

      if (isSelected) {
        ctx.fillStyle = '#f59e0b';
        ctx.shadowColor = '#f59e0b';
        ctx.shadowBlur = 10;
      } else if (isCurrentlyPlaying) {
        ctx.fillStyle = '#06b6d4';
        ctx.shadowColor = '#06b6d4';
        ctx.shadowBlur = 8;
      } else {
        const hue = 260 + (lane / laneCount) * 60;
        ctx.fillStyle = `hsl(${hue}, 85%, 65%)`;
        ctx.shadowBlur = 0;
      }

      ctx.beginPath();
      ctx.roundRect(x, yTop, barW, barH, 4);
      ctx.fill();
      ctx.shadowBlur = 0;

      // Glow beam when hitting
      if (isCurrentlyPlaying) {
        ctx.fillStyle = 'rgba(6, 182, 212, 0.4)';
        ctx.fillRect(x - 1, yTop, barW + 2, barH);
        ctx.fillStyle = 'rgba(6, 182, 212, 0.2)';
        ctx.fillRect(x - 2, 0, barW + 4, hitLineY);
      }
    }
  }

  // ─── Draw Interactive Piano Keyboard Keys at the Bottom ───
  const is15k = window.visualNoteRange.min === 60;
  const keyLabels15 = {
    60:'A', 62:'S', 64:'D', 65:'F', 67:'G', 69:'H', 71:'J',
    72:'Q', 74:'W', 76:'E', 77:'R', 79:'T', 81:'Y', 83:'U', 84:'I'
  };
  const keyLabels22 = {
    48:',', 49:'L', 50:'.', 51:';', 52:'/', 53:'O', 54:'0', 55:'P',
    56:'-', 57:'[', 58:'=', 59:']', 60:'Z', 61:'S', 62:'X', 63:'D',
    64:'C', 65:'V', 66:'G', 67:'B', 68:'H', 69:'N', 70:'J', 71:'M',
    72:'Q', 73:'2', 74:'W', 75:'3', 76:'E', 77:'R', 78:'5', 79:'T',
    80:'6', 81:'Y', 82:'7', 83:'U', 84:'I'
  };
  const keyLabels = is15k ? keyLabels15 : keyLabels22;

  for (let i = 0; i < laneCount; i++) {
    const midi = window.visualNoteRange.min + i;
    const label = keyLabels[midi] || '';
    const isActive = Boolean(activeKeys[midi]);
    const kx = i * laneWidth + 1;
    const kw = Math.max(3, laneWidth - 2);
    const ky = hitLineY + 2 + (isActive ? 3 : 0); // Visibly presses down when playing!
    const kh = keyboardHeight - 4 - (isActive ? 3 : 0);

    if (isActive) {
      // Lit-up active moving key
      ctx.fillStyle = '#06b6d4';
      ctx.shadowColor = '#06b6d4';
      ctx.shadowBlur = 12;
      ctx.beginPath();
      ctx.roundRect(kx, ky, kw, kh, 3);
      ctx.fill();
      ctx.shadowBlur = 0;

      // Key character label
      if (label && kw >= 10) {
        ctx.fillStyle = '#0c0e18';
        ctx.font = `bold ${Math.min(12, Math.max(9, kw - 2))}px sans-serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(label, kx + kw / 2, ky + kh / 2);
      }
    } else {
      // Inactive key cap
      ctx.fillStyle = isLight ? '#dbe4f0' : '#141828';
      ctx.beginPath();
      ctx.roundRect(kx, ky, kw, kh, 3);
      ctx.fill();

      ctx.strokeStyle = isLight ? 'rgba(0,0,0,0.1)' : 'rgba(255,255,255,0.08)';
      ctx.lineWidth = 1;
      ctx.stroke();

      if (label && kw >= 10) {
        ctx.fillStyle = isLight ? '#64748b' : '#94a3b8';
        ctx.font = `${Math.min(11, Math.max(8, kw - 2))}px sans-serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(label, kx + kw / 2, ky + kh / 2);
      }
    }
  }

  // Monaco live line highlight & smooth-scroll
  if (window.isEditorPreviewing && currentEventForHighlight && !window.selectedNote) {
    highlightEditorLine(currentEventForHighlight.lineNum);
  }

  if (!window.isPaused) {
    window.visualizerFrame = requestAnimationFrame(renderPianoRoll);
  }
}

function redrawCanvas(canvasId) {
  const cvs = document.getElementById(canvasId);
  if (!cvs) return;
  const ctx = cvs.getContext('2d');
  const isLight = document.body.classList.contains('light-theme');
  ctx.fillStyle = isLight ? '#e4eaf4' : '#080a12';
  ctx.fillRect(0, 0, cvs.width, cvs.height);
}

function handleCanvasClick(event) {
  if (!window.audioEvents || window.audioEvents.length === 0) return;
  const cvs = document.getElementById('canvas-editor');
  if (!cvs) return;

  const rect = cvs.getBoundingClientRect();
  const scaleX = cvs.width / rect.width;
  const scaleY = cvs.height / rect.height;
  const clickX = (event.clientX - rect.left) * scaleX;
  const clickY = (event.clientY - rect.top) * scaleY;

  for (let i = 0; i < window.audioEvents.length; i++) {
    const ev = window.audioEvents[i];
    if (ev.lastRenderBounds) {
      const b = ev.lastRenderBounds;
      if (
        clickX >= b.x - 2 &&
        clickX <= b.x + b.w + 2 &&
        clickY >= b.y - 2 &&
        clickY <= b.y + b.h + 2
      ) {
        selectNoteAndJumpToCode(ev);
        break;
      }
    }
  }
}

function selectNoteAndJumpToCode(ev) {
  window.selectedNote = ev;
  const line = ev.lineNum + 1;

  if (window.monacoEditor) {
    window.monacoEditor.revealLineInCenter(line);
    window.monacoEditor.setPosition({ lineNumber: line, column: 1 });
    window.decorations = window.monacoEditor.deltaDecorations(window.decorations, [
      {
        range: new window.monaco.Range(line, 1, line, 1),
        options: {
          isWholeLine: true,
          className: 'line-highlight-note'
        }
      }
    ]);
  }

  appLog(`Jumped to line ${line} (Note MIDI: ${ev.note})`, 'info');
  if (!window.isEditorPreviewing) {
    initAudio();
    scheduleNote(ev.note, window.audioCtx.currentTime, 0.2);
  }
}

window.initAudio = initAudio;
window.parseSongToEvents = parseSongToEvents;
window.startAudioEngine = startAudioEngine;
window.stopAudioEngine = stopAudioEngine;
window.scheduler = scheduler;
window.scheduleNote = scheduleNote;
window.renderPianoRoll = renderPianoRoll;
window.redrawCanvas = redrawCanvas;
window.handleCanvasClick = handleCanvasClick;
window.selectNoteAndJumpToCode = selectNoteAndJumpToCode;
