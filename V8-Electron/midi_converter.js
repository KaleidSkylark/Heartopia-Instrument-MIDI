const fs = require('fs');
const path = require('path');
const MidiParser = require('midi-parser-js');

const MAP_22 = {
  48: ',', 49: 'l', 50: '.', 51: ';', 52: '/', 53: 'o', 54: '0', 55: 'p',
  56: '-', 57: '[', 58: '=', 59: ']', 60: 'z', 61: 's', 62: 'x', 63: 'd',
  64: 'c', 65: 'v', 66: 'g', 67: 'b', 68: 'h', 69: 'n', 70: 'j', 71: 'm',
  72: 'q', 73: '2', 74: 'w', 75: '3', 76: 'e', 77: 'r', 78: '5', 79: 't',
  80: '6', 81: 'y', 82: '7', 83: 'u', 84: 'i'
};

const MAP_15 = {
  60: 'a', 62: 's', 64: 'd', 65: 'f', 67: 'g', 69: 'h', 71: 'j',
  72: 'q', 74: 'w', 76: 'e', 77: 'r', 79: 't', 81: 'y', 83: 'u', 84: 'i'
};

const VALID_15K_NOTES = Object.keys(MAP_15).map(Number).sort((a, b) => a - b);
const VALID_22K_NOTES = Object.keys(MAP_22).map(Number).sort((a, b) => a - b);

function parseMidiFile(filePath) {
  const buf = fs.readFileSync(filePath);
  const midi = MidiParser.parse(new Uint8Array(buf));
  if (!midi || !midi.track) {
    throw new Error('Failed to parse MIDI structure.');
  }

  const ticksPerBeat = midi.timeDivision || 480;
  const events = [];

  const tracks = Array.isArray(midi.track) ? midi.track : [midi.track];
  for (const tr of tracks) {
    let absTime = 0;
    const trEvents = tr.event || [];
    for (const ev of trEvents) {
      absTime += (ev.deltaTime || 0);

      // note_on: type === 9, note_off: type === 8
      if (ev.type === 9) {
        const note = Math.max(0, Math.min(127, ev.data[0]));
        const vel = ev.data[1] || 0;
        events.push({
          tm: absTime,
          type: vel > 0 ? 'note_on' : 'note_off',
          note,
          vel
        });
      } else if (ev.type === 8) {
        const note = Math.max(0, Math.min(127, ev.data[0]));
        events.push({
          tm: absTime,
          type: 'note_off',
          note,
          vel: 0
        });
      } else if (ev.type === 255 && ev.metaType === 81 && Array.isArray(ev.data)) {
        // set_tempo event (3 bytes)
        const tempo = (ev.data[0] << 16) | (ev.data[1] << 8) | ev.data[2];
        events.push({
          tm: absTime,
          type: 'set_tempo',
          tempo
        });
      }
    }
  }

  events.sort((a, b) => a.tm - b.tm);
  return { events, ticksPerBeat };
}

function convertMidiFilesNode(files, target = 'Both', pitch = 0, noteFolder) {
  if (!noteFolder) {
    throw new Error('Notes folder directory is required.');
  }
  if (!fs.existsSync(noteFolder)) {
    fs.mkdirSync(noteFolder, { recursive: true });
  }

  const pitchVal = parseInt(pitch) || 0;
  const logs = [];

  let modes = [];
  if (target === 'Both') {
    modes = [{ is15: false, isViolin: false }, { is15: true, isViolin: false }];
  } else if (target === '15K') {
    modes = [{ is15: true, isViolin: false }];
  } else if (target === 'Violin') {
    modes = [{ is15: false, isViolin: true }];
  } else {
    modes = [{ is15: false, isViolin: false }];
  }

  const validFiles = (files || []).filter(f => f && fs.existsSync(f));
  if (validFiles.length === 0) {
    return { ok: false, message: 'No valid or accessible MIDI files found.' };
  }

  for (const filePath of validFiles) {
    const fileName = path.basename(filePath);
    try {
      const { events, ticksPerBeat } = parseMidiFile(filePath);
      const raw = events.filter(e => e.type === 'note_on').map(e => e.note);

      if (raw.length === 0) {
        logs.push(`⚠️ Skipped ${fileName}: No notes found`);
        continue;
      }

      // Calculate median
      const sortedRaw = [...raw].sort((a, b) => a - b);
      const med = sortedRaw[Math.floor(sortedRaw.length / 2)];

      for (const { is15, isViolin } of modes) {
        let trans = 0;
        if (is15) {
          const tc = 72 + (pitchVal * 12);
          const cMaj = new Set([0, 2, 4, 5, 7, 9, 11]);
          let bestShift = -6;
          let maxCount = -1;
          for (let s = -6; s <= 5; s++) {
            let count = 0;
            for (const n of raw) {
              if (cMaj.has(((n + s) % 12 + 12) % 12)) count++;
            }
            if (count > maxCount) {
              maxCount = count;
              bestShift = s;
            }
          }
          trans = bestShift + Math.round((tc - (med + bestShift)) / 12.0) * 12;
        } else {
          trans = Math.round((66 + (pitchVal * 12) - med) / 12.0) * 12;
        }

        const out = [];
        let last = 0;
        const act = new Set();
        let tempo = 500000;
        let pendingChordKeys = [];
        const keymap = is15 ? MAP_15 : MAP_22;

        for (const m of events) {
          if (m.tm > last) {
            if (is15 && pendingChordKeys.length > 0) {
              for (const k of pendingChordKeys) out.push(`Keyboard : ${k} : KeyDown`);
              for (const k of pendingChordKeys) out.push(`Keyboard : ${k} : KeyUp`);
              pendingChordKeys = [];
            }

            const ms = Math.floor(((m.tm - last) * tempo) / (ticksPerBeat * 1000));
            out.push(`DELAY : ${ms}`);
          }

          last = m.tm;

          if (m.type === 'set_tempo') {
            tempo = m.tempo;
            continue;
          }
          if (m.type !== 'note_on' && m.type !== 'note_off') {
            continue;
          }

          const targetNote = m.note + trans;

          if (is15) {
            let kVal = null;
            if (keymap[targetNote]) {
              kVal = keymap[targetNote];
            } else {
              let closest = VALID_15K_NOTES[0];
              let minDist = Math.abs(closest - targetNote);
              for (const n of VALID_15K_NOTES) {
                const dist = Math.abs(n - targetNote);
                if (dist < minDist) {
                  minDist = dist;
                  closest = n;
                }
              }
              kVal = keymap[closest];
            }

            if (m.type === 'note_on' && m.vel > 0) {
              if (!pendingChordKeys.includes(kVal)) {
                pendingChordKeys.push(kVal);
              }
            }
          } else {
            if (isViolin) {
              let closest = VALID_22K_NOTES[0];
              let minDist = Math.abs(closest - targetNote);
              for (const n of VALID_22K_NOTES) {
                const dist = Math.abs(n - targetNote);
                if (dist < minDist) {
                  minDist = dist;
                  closest = n;
                }
              }
              const k = keymap[closest];
              const isOn = (m.type === 'note_on' && m.vel > 0);
              if (isOn && !act.has(k)) {
                out.push(`Keyboard : ${k} : KeyDown`);
                act.add(k);
              } else if (!isOn && act.has(k)) {
                out.push(`Keyboard : ${k} : KeyUp`);
                act.delete(k);
              }
            } else {
              if (keymap[targetNote]) {
                const k = keymap[targetNote];
                const isOn = (m.type === 'note_on' && m.vel > 0);
                if (isOn && !act.has(k)) {
                  out.push(`Keyboard : ${k} : KeyDown`);
                  act.add(k);
                } else if (!isOn && act.has(k)) {
                  out.push(`Keyboard : ${k} : KeyUp`);
                  act.delete(k);
                }
              }
            }
          }
        }

        if (is15 && pendingChordKeys.length > 0) {
          for (const k of pendingChordKeys) out.push(`Keyboard : ${k} : KeyDown`);
          for (const k of pendingChordKeys) out.push(`Keyboard : ${k} : KeyUp`);
        }

        for (const k of act) {
          out.push(`Keyboard : ${k} : KeyUp`);
        }

        const suffix = is15 ? '_15K' : (isViolin ? '_Violin' : '_22K');
        const baseName = path.basename(fileName, path.extname(fileName));
        const cleanName = baseName.replace(/[^a-zA-Z0-9 ._-]/g, '').trim() || 'Song';
        const saveName = `${cleanName}${suffix}.txt`;
        const savePath = path.join(noteFolder, saveName);

        fs.writeFileSync(savePath, out.join('\n'), 'utf-8');
        logs.push(`✅ Converted: ${saveName}`);
      }
    } catch (err) {
      logs.push(`❌ Failed ${fileName}: ${err.message}`);
    }
  }

  return {
    ok: true,
    message: logs.join('\n') || 'No files converted.'
  };
}

module.exports = {
  convertMidiFilesNode
};
