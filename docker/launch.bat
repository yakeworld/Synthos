@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

REM ============================================================================
REM Hermes + OpenCode — Portable Launcher (Windows)
REM ============================================================================
REM 双击运行，零依赖。所有运行时下载到此目录内，不碰系统。
REM ============================================================================

REM Resolve portable root
set "PORTABLE_ROOT=%~dp0"
set "PORTABLE_ROOT=%PORTABLE_ROOT:~0,-1%"

set "DATA_DIR=%PORTABLE_ROOT%\data"
set "CACHE_DIR=%PORTABLE_ROOT%\.cache"
set "RUNTIME_DIR=%CACHE_DIR%\runtimes\windows-x64"
set "SRC_DIR=%PORTABLE_ROOT%\src"
set "BIN_DIR=%RUNTIME_DIR%\bin"

REM Ensure directories exist
for %%d in ("%DATA_DIR%" "%CACHE_DIR%" "%RUNTIME_DIR%" "%SRC_DIR%" "%BIN_DIR%") do (
    if not exist "%%d" mkdir "%%d" 2>nul
)

REM ── First-run setup ─────────────────────────────────────────────
if not exist "%RUNTIME_DIR%\ready.flag" (
    echo.
    echo ============================================================
    echo    Hermes + OpenCode — Portable Setup
    echo ============================================================
    echo  This will download and install portable runtimes locally.
    echo  Python, Node.js, uv, git — all self-contained.
    echo  Total download: ~800MB. Please be patient.
    echo ============================================================
    echo.
    powershell -ExecutionPolicy Bypass -File "%PORTABLE_ROOT%\scripts\setup-windows.ps1" -Root "%PORTABLE_ROOT%"
    if errorlevel 1 (
        echo.
        echo [ERROR] Setup failed. Please check your internet connection and try again.
        pause
        exit /b 1
    )
)

REM ── Environment isolation ──────────────────────────────────────
set "VIRTUAL_ENV=%RUNTIME_DIR%\venv"
set "PATH=%VIRTUAL_ENV%\Scripts;%RUNTIME_DIR%\python;%RUNTIME_DIR%\python\Scripts;%RUNTIME_DIR%\node;%RUNTIME_DIR%\node\bin;%RUNTIME_DIR%\uv;%RUNTIME_DIR%\bin;%PATH%"
set "PYTHONNOUSERSITE=1"
set "PYTHONHOME="
set "PYTHONPATH="
set "UV_NO_CONFIG=1"
set "UV_PYTHON=%RUNTIME_DIR%\python\python.exe"
set "APPDATA=%PORTABLE_ROOT%\.cache\windows-appdata"
set "LOCALAPPDATA=%PORTABLE_ROOT%\.cache\windows-localappdata"
set "HERMES_HOME=%DATA_DIR%"
set "NODE_PATH=%RUNTIME_DIR%\node\node_modules"
set "NPM_CONFIG_PREFIX=%RUNTIME_DIR%\node"

REM Fix pyvenv.cfg for portability
if exist "%VIRTUAL_ENV%\pyvenv.cfg" (
    for /f "tokens=2" %%v in ('"%RUNTIME_DIR%\python\python.exe" --version 2^>nul') do set "PYTHON_VERSION=%%v"
    if not defined PYTHON_VERSION set "PYTHON_VERSION=3.11.15"
    echo home = %RUNTIME_DIR%\python > "%VIRTUAL_ENV%\pyvenv.cfg"
    echo include-system-site-packages = false >> "%VIRTUAL_ENV%\pyvenv.cfg"
    echo version = !PYTHON_VERSION! >> "%VIRTUAL_ENV%\pyvenv.cfg"
)

REM ── Update pyvenv.cfg with current PATH ────────────────────────
REM (re-run this on every launch so portable root changes are picked up)
if exist "%VIRTUAL_ENV%\pyvenv.cfg" (
    python -c "
import os
cfg = os.path.join(os.path.dirname(os.path.abspath('__file__')), 'pyvenv.cfg')
" 2>nul
    echo home = %RUNTIME_DIR%\python > "%VIRTUAL_ENV%\pyvenv.cfg"
    echo include-system-site-packages = false >> "%VIRTUAL_ENV%\pyvenv.cfg"
    for /f "tokens=2" %%v in ('"%RUNTIME_DIR%\python\python.exe" --version 2^>nul') do echo version = %%v >> "%VIRTUAL_ENV%\pyvenv.cfg"
)

REM ── Run Hermes or show menu ───────────────────────────────────
if not "%~1"=="" (
    REM Direct command mode
    if /I "%~1"=="hermes" shift
    if /I "%~1"=="update" (
        cd /d "%SRC_DIR%\hermes-agent"
        python -c "from hermes_cli.main import main; main()" /hermes update
        pause
        exit /b
    )
    cd /d "%SRC_DIR%\hermes-agent"
    python -c "from hermes_cli.main import main; main()" %*
    exit /b
)

REM ── Interactive Terminal Menu ─────────────────────────────────
cd /d "%SRC_DIR%\hermes-agent"

cls
echo.
echo  ╔═══════════════════════════════════════════════════╗
echo  ║   Hermes + OpenCode — Portable Edition            ║
echo  ╚═══════════════════════════════════════════════════╝
echo.
echo   [1] Start Chat (Hermes Agent)
echo   [2] Start OpenCode CLI
echo   [3] Setup / Reconfigure API Keys
echo   [4] System Info
echo   [5] Update Hermes Agent
echo   [6] Clear Conversations
echo   [0] Exit
echo.

set /p "choice=Choose [0-6]: "

if "%choice%"=="1" (
    echo.
    echo Starting Hermes Chat...
    echo Press Ctrl+C to exit.
    echo.
    python -c "from hermes_cli.main import main; main()"
) else if "%choice%"=="2" (
    echo.
    echo Starting OpenCode CLI...
    echo Press Ctrl+C to exit.
    echo.
    cd /d "%PORTABLE_ROOT%"
    opencode
) else if "%choice%"=="3" (
    echo.
    echo Opening config editor...
    echo Edit %DATA_DIR%\.env  for API keys
    echo Edit %DATA_DIR%\config.yaml for model config
    start notepad.exe "%DATA_DIR%\.env"
    start notepad.exe "%DATA_DIR%\config.yaml"
) else if "%choice%"=="4" (
    echo.
    echo === System Info ===
    echo Portable Root: %PORTABLE_ROOT%
    echo Data Dir:      %DATA_DIR%
    echo Cache Dir:     %CACHE_DIR%
    echo Runtime:       %RUNTIME_DIR%
    echo Source:        %SRC_DIR%\hermes-agent
    echo.
    echo Python:
    python --version 2>&1
    echo.
    echo Node.js:
    node --version 2>&1
    echo.
    echo Hermes:
    hermes --version 2>&1
    echo.
    echo OpenCode:
    opencode --version 2>&1
    echo.
    echo Disk usage:
    for /f %%A in ('dir "%PORTABLE_ROOT%" /s /b ^| findstr /v "^"') do echo  %%A
    dir /s /a /b "%PORTABLE_ROOT%" 2>nul | findstr /c:"." | wc -l 2>nul || powershell -Command "(Get-ChildItem -Path '%PORTABLE_ROOT%' -Recurse -File -Force | Measure-Object -Property Length -Sum).Sum / 1MB"
    pause
) else if "%choice%"=="5" (
    echo.
    echo Updating Hermes Agent...
    cd /d "%SRC_DIR%\hermes-agent"
    git pull 2>nul || (
        echo Source not in git, reinstalling...
        if exist "%SRC_DIR%\hermes-agent" rmdir /s /q "%SRC_DIR%\hermes-agent"
        curl -sL -o "%CACHE_DIR%\hermes-main.zip" "https://github.com/NousResearch/hermes-agent/archive/refs/heads/main.zip"
        tar -xzf "%CACHE_DIR%\hermes-main.zip" -C "%SRC_DIR%" 2>nul || (
            powershell -Command "Expand-Archive -Path '%CACHE_DIR%\hermes-main.zip' -DestinationPath '%SRC_DIR%' -Force"
        )
        ren "%SRC_DIR%\hermes-agent-main" "hermes-agent" 2>nul
    )
    pip install -e "%SRC_DIR%\hermes-agent" --upgrade --quiet
    echo Done!
    pause
) else if "%choice%"=="6" (
    if exist "%DATA_DIR%\sessions" (
        rmdir /s /q "%DATA_DIR%\sessions"
        mkdir "%DATA_DIR%\sessions"
        echo Conversations cleared.
    ) else (
        echo No sessions found.
    )
    pause
)

exit /b 0