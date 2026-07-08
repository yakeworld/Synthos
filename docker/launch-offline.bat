@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

REM ============================================================================
REM Hermes + OpenCode — Offline Portable Launcher (Windows)
REM ============================================================================
REM Pre-downloaded offline version. NO internet connection needed.
REM Just unzip and run. All runtimes are bundled inside .cache/runtimes/.
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
for %%d in ("%DATA_DIR%" "%SRC_DIR%" "%BIN_DIR%") do (
    if not exist "%%d" mkdir "%%d" 2>nul
)

REM ── Environment isolation ──────────────────────────────────────
set "VIRTUAL_ENV=%RUNTIME_DIR%\venv"
set "PATH=%VIRTUAL_ENV%\Scripts;%RUNTIME_DIR%\python;%RUNTIME_DIR%\python\Scripts;%RUNTIME_DIR%\node;%RUNTIME_DIR%\node\bin;%RUNTIME_DIR%\bin;%PATH%"
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

REM Fix pyvenv.cfg
if exist "%VIRTUAL_ENV%\pyvenv.cfg" (
    echo home = %RUNTIME_DIR%\python > "%VIRTUAL_ENV%\pyvenv.cfg"
    echo include-system-site-packages = false >> "%VIRTUAL_ENV%\pyvenv.cfg"
    for /f "tokens=2" %%v in ('"%RUNTIME_DIR%\python\python.exe" --version 2^>nul') do echo version = %%v >> "%VIRTUAL_ENV%\pyvenv.cfg"
)

REM ── Verify runtimes exist ──────────────────────────────────────
if not exist "%RUNTIME_DIR%\python\python.exe" (
    echo [ERROR] Python runtime not found.
    echo Please extract the offline package correctly.
    pause
    exit /b 1
)
if not exist "%RUNTIME_DIR%\node\node.exe" (
    echo [ERROR] Node.js runtime not found.
    echo Please extract the offline package correctly.
    pause
    exit /b 1
)
if not exist "%SRC_DIR%\hermes-agent" (
    echo [ERROR] Hermes source not found.
    echo Please extract the offline package correctly.
    pause
    exit /b 1
)

REM ── Run Hermes or show menu ───────────────────────────────────
if not "%~1"=="" (
    if /I "%~1"=="hermes" shift
    cd /d "%SRC_DIR%\hermes-agent"
    python -c "from hermes_cli.main import main; main()" %*
    exit /b
)

cls
echo.
echo  ╔═══════════════════════════════════════════════════╗
echo  ║   Hermes + OpenCode — Offline Portable Edition    ║
echo  ╚═══════════════════════════════════════════════════╝
echo.
echo   [1] Start Chat (Hermes Agent)
echo   [2] Start OpenCode CLI
echo   [3] System Info
echo   [0] Exit
echo.

set /p "choice=Choose [0-3]: "

if "%choice%"=="1" (
    echo.
    echo Starting Hermes Chat...
    echo Press Ctrl+C to exit.
    echo.
    cd /d "%SRC_DIR%\hermes-agent"
    python -c "from hermes_cli.main import main; main()"
) else if "%choice%"=="2" (
    echo.
    echo Starting OpenCode CLI...
    cd /d "%PORTABLE_ROOT%"
    opencode
) else if "%choice%"=="3" (
    echo.
    echo === System Info ===
    echo Portable Root: %PORTABLE_ROOT%
    echo Data Dir:      %DATA_DIR%
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
    echo Disk usage:
    dir /s /b "%PORTABLE_ROOT%\*" 2>nul | findstr /c:"." > nul && for /f "delims=" %%A in ('dir /s /b "%PORTABLE_ROOT%\*" 2^>nul') do if exist "%%A" (if not "%%~dA"=="" echo  %%~fA)
    pause
)

exit /b 0