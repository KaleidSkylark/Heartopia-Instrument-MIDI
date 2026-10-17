@echo off
setlocal enabledelayedexpansion
title PianiPia V8 - Windows Executable Builder
color 0B

echo =======================================================
echo   PIANIPIA V8 - WINDOWS EXECUTABLE BUILDER (ELECTRON)
echo =======================================================
echo.

cd /d "%~dp0"

:: 1. Verify Node.js and npm
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js was not found in your system PATH!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

where npm >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] npm was not found in your system PATH!
    pause
    exit /b 1
)

:: 2. Ensure standalone Python engine is compiled
if not exist "%~dp0engine\engine.exe" (
    echo [1/3] Compiling Standalone Python Engine (PyInstaller)...
    where pyinstaller >nul 2>&1
    if !ERRORLEVEL! equ 0 (
        call pyinstaller --noconfirm --onedir --console --distpath ./engine-dist --name engine python_bridge.py
        if exist engine-dist\engine (
            if exist engine rmdir /s /q engine
            move engine-dist\engine .\engine
            if exist engine-dist rmdir /s /q engine-dist
            if exist build rmdir /s /q build
            if exist engine.spec del /f /q engine.spec
        )
    ) else (
        echo [INFO] PyInstaller not in PATH, will package with current engine directory.
    )
)

:: 3. Ensure all dependencies are installed
echo [2/3] Checking and installing dependencies...
call npm install
if %ERRORLEVEL% neq 0 (
    echo [ERROR] npm install encountered an error.
    pause
    exit /b 1
)

:: 4. Build standalone Windows executables (Portable + Fast Installer)
echo.
echo [3/3] Packaging PianiPia V8 into standalone executables...
call npx electron-builder --win
if %ERRORLEVEL% equ 0 (
    echo.
    echo =======================================================
    echo   BUILD SUCCESSFUL!
    echo   Executables are ready in:
    echo     - Portable:  %~dp0dist\PianiPia_V8_Portable.exe
    echo     - Installer: %~dp0dist\PianiPia_V8_Setup.exe (Instant launch)
    echo     - Unpacked:  %~dp0dist\win-unpacked\
    echo =======================================================
) else (
    echo.
    echo =======================================================
    echo   [ERROR] Packaging failed. Please see log above.
    echo =======================================================
)

pause
