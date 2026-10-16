@echo off
setlocal
title PianiPia V8 - Windows Standalone Executable Builder
color 0B

echo =======================================================
echo   PIANIPIA V8 - ROOT BUILD LAUNCHER
echo =======================================================
echo.

if not exist "%~dp0V8-Electron\package.json" (
    echo [ERROR] Could not find V8-Electron directory at %~dp0V8-Electron!
    pause
    exit /b 1
)

call "%~dp0V8-Electron\build_exe.bat"
