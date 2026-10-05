@echo off
title PianiPia V6 Final Stability Build
color 0B
set "ENV_NAME=pianipia_stable_env"
set "PY_PATH=C:\Users\Skylark\AppData\Local\Programs\Python\Python310\python.exe"

echo ==================================================
echo   PIANIPIA STABILITY BUILD (CLEANED)
echo ==================================================

:: 1. Create clean environment
if exist %ENV_NAME% rmdir /s /q %ENV_NAME%
"%PY_PATH%" -m venv %ENV_NAME%
call %ENV_NAME%\Scripts\activate

:: 2. Install slim dependencies
echo Installing dependencies...
pip install --upgrade pip
:: Removed: pyautogui, pillow, pyscreeze, requests, opencv
pip install flask mido pyinstaller supabase flask-socketio simple-websocket pydirectinput

:: 3. Build with MINIMAL exclusions
echo Building...
pyinstaller --noconsole --onefile --clean ^
 --name "PianiPia V6" ^
 --icon "logo.ico" ^
 --exclude-module pydoc ^
 --copy-metadata=flask ^
 --copy-metadata=flask_socketio ^
 --copy-metadata=supabase ^
 --hidden-import=engineio.async_drivers.threading ^
 --hidden-import=tkinter.filedialog ^
 --hidden-import=supabase ^
 PianiPiaV6.py || pause

:: 4. Cleanup
deactivate
rmdir /s /q %ENV_NAME%

echo.
echo ==================================================
echo   DONE!
echo   This build will actually run.
echo ==================================================
pause