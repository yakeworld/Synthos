@echo off
REM ============================================================
REM Hermes Agent — Windows 便携启动器
REM 用法: 双击运行，或右键 → 以管理员身份运行
REM 首次运行会执行安装引导
REM ============================================================

@echo off
setlocal enabledelayedexpansion

REM 检查是否已安装
if not exist "%USERPROFILE%\AppData\Local\hermes\run-hermes.bat" (
    echo ========================================
    echo  Hermes Agent — 首次运行
    echo ========================================
    echo.
    echo 正在引导安装...
    echo.
    echo 方法1: 双击 hermes-windows-setup.ps1 一键安装
    echo 方法2: 在 PowerShell 中运行:
    echo   powershell -ExecutionPolicy Bypass -File hermes-windows-setup.ps1
    echo.
    echo 安装完成后，双击本文件即可使用
    echo.
    pause
    exit /b 1
)

REM 已安装，正常启动
if "%~1"=="" (
    echo ========================================
    echo  Hermes Agent — 便携版
    echo  输入 'exit' 退出
    echo ========================================
    echo.
    cmd /k "echo 欢迎使用 Hermes Agent! & echo. & hermes chat -q"
) else (
    "%USERPROFILE%\AppData\Local\hermes\run-hermes.bat" %*
)