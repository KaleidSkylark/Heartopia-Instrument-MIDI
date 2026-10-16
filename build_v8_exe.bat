@echo off
setlocal
title PianiPia V8 - Windows Standalone Executable Builder
color 0B

echo =======================================================
echo   PIANIPIA V8 - ROOT BUILD LAUNCHER
echo =======================================================
echo.

if not exist "%~dp0Electron\package.json" (
    echo [ERROR] Could not find Electron directory at %~dp0Electron!
    pause
    exit /b 1
)

call "%~dp0Electron\build_exe.bat"
