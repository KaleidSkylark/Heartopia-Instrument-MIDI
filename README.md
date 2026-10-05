<div align="center">
  <h3>✨ Visit my personal Wiki ✨</h3>
  <a href="https://heartopia-wikios.vercel.app/"><img src="https://img.shields.io/badge/Heartopia%20Wiki-Visit%20Now-pink?style=for-the-badge" alt="Visit Heartopia Wiki"></a>
</div>
<br>

<h1 align="center">PianiPia (Open Source)</h1>
<p align="center">
  <b>The Ultimate Automated Piano Player & Assist Suite for Heartopia</b><br>
  🔓 Open Source • 🐍 Python Based • 🤖 Made with AI • 🎵 Studio Editor • 🎹 Visual Piano Roll • ✨ Game Assist
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows">
  <img src="https://img.shields.io/badge/License-Open%20Source-brightgreen?style=for-the-badge" alt="Open Source">
</p>

<p align="center">
  <a href="#-versions-overview">Versions (V6 vs V7)</a> •
  <a href="#-running-from-source">Run from Source</a> •
  <a href="#-features">Features</a> •
  <a href="#-how-to-use">How To Use</a> •
  <a href="#-repository-structure">Structure</a>
</p>

---

### 🎥 Watch the Demo
<div align="center">
  <a href="https://youtu.be/tteFOOMR9X4" target="_blank">
    <img src="https://img.youtube.com/vi/tteFOOMR9X4/hqdefault.jpg" alt="Watch the Demo" width="600" style="border-radius: 10px; box-shadow: 0px 0px 20px rgba(0, 0, 0, 0.5);">
  </a>
  <p><i>(Watch PianiPia in action)</i></p>
</div>

---

### 🚀 Now Fully Open Source!

PianiPia is now **100% open source**! You can inspect every line of code, run directly from Python without relying on pre-packaged executables (avoiding antivirus false positives entirely), customize shortcuts, or build your own custom distributions.

---

### 📦 Versions Overview: V6 vs V7

This repository contains both **V6** and **V7** source trees:

| Version | Focus | Included Features |
| :--- | :--- | :--- |
| **[V6](V6/)** | **Ultra-Lightweight & Focused** | • Complete MIDI Player & visual piano roll<br>• Monaco Studio Editor (1M+ lines)<br>• Community Cloud (upload/download)<br>• 22K & 15K MIDI converter<br>• Fully debloated (no OpenCV or bot dependencies) |
| **[V7](V7/)** | **Full Automation & Assist Suite** | • Everything in V6, **plus** the complete in-game **Assist System**:<br>  - 🚶 Auto Walk & 📷 Cam Lock<br>  - 👨‍🍳 Auto Cook (visual heat detection)<br>  - ❄️ Snow Puzzle Mini-Game Solver<br>  - 🚜 Auto Harvest (Hold & Spam modes)<br>  - 🦘 Auto Jump<br>  - 🎣 Fish Automation & 🛠️ Build Glitch trigger |

---

### 💻 Running from Source

You can run PianiPia directly using Python on Windows:

#### 1. Prerequisites
- **Python 3.10 or higher** installed ([python.org](https://www.python.org/downloads/))
- During Python installation, ensure **"Add python.exe to PATH"** is checked.

#### 2. Clone the Repository
```bash
git clone https://github.com/KaleidSkylark/Heartopia-Instrument-MIDI.git
cd Heartopia-Instrument-MIDI
```

#### 3. Create & Activate a Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```

#### 4. Install Dependencies

**For V6 (Lightweight Music Player):**
```bash
pip install flask flask-socketio simple-websocket pydirectinput mido supabase
```

**For V7 (Full Suite with Game Assist):**
```bash
pip install flask flask-socketio simple-websocket pydirectinput pyautogui pynput pillow mido supabase
```

#### 5. Launch the Application

- **To run PianiPia V6:**
  ```bash
  python V6/PianiPiaV6.py
  ```

- **To run PianiPia V7:**
  ```bash
  python V7/PianiPiaV7.py
  ```

Your default web browser will automatically open to `http://127.0.0.1:5000` with the UI ready to go!

---

### 🏗️ Building Executables (.exe)

If you want to package the app into a standalone `.exe`:

```bash
pip install pyinstaller
```

Run the build script provided in `V6/`:
```bash
cd V6
build_bot_modular.bat
```

---

### ✨ Core Features

> ⚠️ **Note:** Heartopia needs to be foreground/active for key simulation to register in-game. Run as Administrator if keystrokes are blocked.

* **🎵 Accurate Auto-Player:** Plays complex multi-track MIDI scripts using direct keyboard emulation.
* **📝 Monaco Studio Editor:** VS Code's Monaco engine built-in. Smoothly edits 1,000,000+ line MIDI scripts with real-time cursor sync.
* **🎹 Visual Piano Roll:** Live interactive canvas visualizer tracking your code lines in real-time. Click any note to jump directly to code.
* **☁️ Community Cloud:** Search, download, and share song scripts directly from within the app.
* **✨ Game Assist (V7):** Comprehensive image-recognition and automation suite for cooking, puzzle solving, farming, and camera navigation.

---

### 📂 Repository Structure

```text
Heartopia-Instrument-MIDI/
├── V6/                         # PianiPia V6 (Dedicated Music Player)
│   ├── PianiPiaV6.py           # V6 Entry point
│   ├── build_bot_modular.bat   # PyInstaller build script
│   ├── config.json             # V6 player configuration
│   └── heartopia_modules/      # Modular backend (routes, player, editor, converter)
├── V7/                         # PianiPia V7 (Music Player + In-Game Assist)
│   ├── PianiPiaV7.py           # V7 Entry point
│   ├── HeartAssist.py          # Standalone assist automation engine
│   ├── config.json             # V7 player & assist settings
│   ├── build glitch/           # Reference assets for build glitch helper
│   └── heartopia_modules/      # Modular backend + assist module & web UI
├── CookingReference/           # Default template images for Auto-Cook recognition
├── SnowReference/              # Default template images for Snow Puzzle solver
├── images/                     # Screenshot previews for README & documentation
├── PianiPiaV6.exe              # Pre-compiled V6 standalone executable
├── Heartopia MIDI V5.2.exe     # Legacy V5.2 executable
└── README.md
```

---

### 🛠️ Patch Notes History

#### V7.0 Major Automation Release
* **✅ Modular Architecture:** Refactored into clean `heartopia_modules` with modular routes, player, config, and hotkey listeners.
* **✅ Full Assist Integration:** Added in-app Assist tab directly into the Web UI.
* **✅ Auto Cook & Snow Puzzle:** Integrated computer vision detection for cooking cycles and snow puzzles.
* **✅ Auto Harvest & Auto Jump:** Added hold/spam modes for harvesting and jumping traversal.
* **✅ Build Glitch Trigger:** Added simultaneous icon manipulation for build glitch shortcuts.
* **✅ Open Source:** Entire codebase opened up for community contribution and direct Python execution.

#### V6.0 Optimization & UI Overhaul
* **✅ Storage & Performance Optimization:** Cleaned up dependencies for a streamlined music experience. Size dropped to 24MB.
* **✅ Amoled Neon UI:** Redesigned interface with vibrant Amoled dark theme and responsive layout.
* **✅ Playlist Filters:** Added multi-select, quick filters, and refreshed search.
* **✅ Monaco Studio Editor:** Ultra-fast editor handling massive song scripts with live visual seek.

#### V5.2 Converter Intelligence Update 
* **✅ 15K Smart Pitch Folding:** Notes outside the 15-key range fold gracefully instead of being discarded.
* **✅ Zero Dropped Notes:** Every note from source MIDI is preserved for full rhythm density.
* **✅ Tap Mode Logic:** Eliminates ghost notes and de-sync issues on fast tempos.

#### V5.1 Hotfix & Improvements
* **✅ 500KB Upload Limit:** Increased upload limit for complex multipart scripts.
* **✅ Smart Pagination:** Custom per-page selection (50/100/200/300) in Online tab.
* **✅ Filename Sanitization:** Fixes illegal OS characters on download.

---

### ⚠️ Important: Antivirus False Positives (For .exe Users)

**Is the `.exe` safe? Yes.**

If you run the pre-compiled `.exe`, antivirus programs (Windows Defender, Avast, etc.) may flag it.

**Why does this happen?**
1. **Input Simulation:** The app uses Windows input APIs (`pydirectinput`, `pyautogui`) to press keys in games. Antivirus heuristics frequently flag keyboard automation as a keylogger or Trojan.
2. **Unsigned Executable:** Independent open-source projects lack expensive code-signing certificates.
3. **PyInstaller Packing:** PyInstaller binaries are commonly flagged by heuristic scanners.

> 💡 **Best Solution:** Since PianiPia is **Open Source**, you can run directly from Python source (`python V6/PianiPiaV6.py` or `python V7/PianiPiaV7.py`). Running raw Python scripts bypasses binary scanner false positives completely!

If you prefer using the `.exe`:
1. Create a dedicated folder (e.g. `C:\Games\PianiPia`).
2. Add that folder as an exclusion in **Windows Security** > **Virus & threat protection settings** > **Exclusions**.
3. Place and run the executable inside that folder.

---

### 📖 How to Use

1. **Launch:** Run `python V6/PianiPiaV6.py` (or `python V7/PianiPiaV7.py`). The browser UI opens at `http://127.0.0.1:5000`.
2. **Get Songs:**
   * **☁️ Online Tab:** Search the cloud library and click download.
   * **🎹 Add / Convert Tab:** Drag and drop `.mid` files to automatically generate 22K or 15K scripts.
3. **Play:**
   * In **Playlist**, add songs to the **Queue**.
   * Focus Heartopia in the foreground.
   * Press **Start Key (Default: NUMPAD7 or F4)** to begin playing.
   * Press **Stop Key (Default: NUMPAD8 or F5)** to halt.
4. **Assist (V7 Only):**
   * Go to the **✨ Assist** tab.
   * Select the game window from the dropdown and click **Connect**.
   * Toggle Auto Walk, Cam Lock, Auto Cook, Auto Harvest, or Snow Puzzle as needed.

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/KaleidSkylark">KaleidSkylark</a>
</p>
