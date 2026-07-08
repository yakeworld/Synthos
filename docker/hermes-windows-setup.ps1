# ============================================================
# hermes-windows-setup.ps1 — Hermes Agent + OpenCode 一键安装
# 适用于 Windows 10/11 (PowerShell 5.1+)
#
# 用法:
#   方法1: 双击此文件
#   方法2: 右键 → "使用 PowerShell 运行"
#   方法3: powershell -ExecutionPolicy Bypass -File .\hermes-windows-setup.ps1
#
# 功能:
#   1. 检测并安装 Python 3.12+
#   2. 安装 pipx, uv
#   3. 安装 Hermes Agent
#   4. 安装 Node.js + OpenCode CLI
#   5. 创建桌面快捷方式
#   6. 验证安装
# ============================================================

#Requires -Version 5.1
[CmdletBinding()]
Param()

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# ── 颜色定义 ──
$GREEN = "#3B82F6"
$YELLOW = "#F59E0B"
$RED = "#EF4444"
$BG = "#0F172A"

function Write-Step { Write-Host "`n==> $args" -ForegroundColor Cyan }
function Write-OK { Write-Host "   ✅ $args" -ForegroundColor Green }
function Write-Err { Write-Host "   ❌ $args" -ForegroundColor Red }
function Write-Info { Write-Host "   ℹ️  $args" -ForegroundColor Yellow }

# ── 安装目录 ──
$INSTALL_DIR = "$HOME\AppData\Local\hermes"
$SHORTCUT_PATH = "$HOME\Desktop\Hermes Agent.lnk"

Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          Hermes Agent + OpenCode — Windows 一键安装       ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

# ── Step 1: 检测 Python ──
Write-Step "Step 1: Python"

$pythonFound = $false
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pyVer = python --version 2>&1
    Write-Info "已找到: $pyVer"
    $pythonFound = $true
}
if (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pyVer = python3 --version 2>&1
    Write-Info "已找到: $pyVer"
    $pythonFound = $true
}

if (-not $pythonFound) {
    Write-Info "未找到 Python，正在下载..."
    
    # 下载 Python 3.12 Windows installer (64-bit)
    $pythonUrl = "https://python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe"
    $pythonExe = "$env:TEMP\python-installer.exe"
    
    try {
        Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonExe -UseBasicParsing
        Write-Info "安装 Python 3.12.7 (添加 PATH)..."
        Start-Process -FilePath $pythonExe -ArgumentList "/PrependPath=1 /quiet InstallAllUsers=0" -Wait -NoNewWindow
        Remove-Item $pythonExe -Force
        
        # 刷新 PATH
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")
        
        # 验证
        if (Get-Command python -ErrorAction SilentlyContinue) {
            Write-OK "Python 安装成功: $(python --version)"
        } else {
            Write-Err "Python 安装后仍无法找到，请手动安装 Python 3.12+"
            Write-Info "下载地址: https://www.python.org/downloads/windows/"
            Write-Info "⚠️  安装时请勾选 'Add Python to PATH'"
            Read-Host "按 Enter 继续"
        }
    }
    catch {
        Write-Err "Python 下载失败: $_"
        Write-Info "请手动安装 Python 3.12+，安装时勾选 'Add Python to PATH'"
        Read-Host "按 Enter 继续"
    }
} else {
    Write-OK "Python 已安装: $(python --version)"
}

# ── Step 2: 安装 uv (Python 包管理) ──
Write-Step "Step 2: uv"

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Info "安装 uv (Python 包管理器)..."
    try {
        Invoke-WebRequest -Uri "https://astral.sh/uv/install.ps1" -OutFile "$env:TEMP\uv-install.ps1" -UseBasicParsing
        # uv 安装脚本需要执行权限，临时放宽
        $origPolicy = [ScriptBlock]::Create("").ExecutionPolicy
        powershell -ExecutionPolicy Bypass -File "$env:TEMP\uv-install.ps1"
        Remove-Item "$env:TEMP\uv-install.ps1" -Force
        Write-OK "uv 安装成功: $(uv --version)"
    }
    catch {
        Write-Err "uv 安装失败，尝试 pip 备用方案..."
        python -m pip install uv
    }
} else {
    Write-OK "uv 已安装: $(uv --version)"
}

# ── Step 3: 安装 Hermes Agent ──
Write-Step "Step 3: Hermes Agent"

if (-not (Get-Command hermes -ErrorAction SilentlyContinue)) {
    Write-Info "通过 pipx 安装 Hermes Agent..."
    python -m pip install --user pipx
    python -m pipx ensurepath
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")
    pipx install hermes-agent
    Write-OK "Hermes Agent 安装成功: $(hermes --version)"
} else {
    Write-OK "Hermes Agent 已安装: $(hermes --version)"
}

# ── Step 4: 安装 Node.js + OpenCode ──
Write-Step "Step 4: Node.js + OpenCode CLI"

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Info "未找到 Node.js，正在安装..."
    
    $nodeUrl = "https://nodejs.org/dist/v22.11.0/node-v22.11.0-x64.msi"
    $nodeInstaller = "$env:TEMP\node-installer.msi"
    
    try {
        Invoke-WebRequest -Uri $nodeUrl -OutFile $nodeInstaller -UseBasicParsing
        Write-Info "安装 Node.js 22 LTS..."
        Start-Process -FilePath "msiexec.exe" -ArgumentList "/i `"$nodeInstaller`" /quiet ADDLOCAL=All" -Wait -NoNewWindow
        Remove-Item $nodeInstaller -Force
        
        # 刷新 PATH
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")
        
        if (Get-Command node -ErrorAction SilentlyContinue) {
            Write-OK "Node.js 安装成功: $(node --version)"
        }
    }
    catch {
        Write-Err "Node.js 安装失败: $_"
        Write-Info "请手动安装 Node.js 22 LTS"
    }
} else {
    Write-OK "Node.js 已安装: $(node --version)"
}

if (Get-Command opencode -ErrorAction SilentlyContinue) {
    Write-Info "OpenCode CLI 已安装: $(opencode --version)"
} else {
    Write-Info "安装 OpenCode CLI..."
    npm install -g @ai-sdk/opencode
    Write-OK "OpenCode CLI 安装成功: $(opencode --version)"
}

# ── Step 5: 创建配置文件 ──
Write-Step "Step 5: 配置文件"

# 创建 Hermes 配置目录
if (-not (Test-Path "$HOME\.hermes")) {
    New-Item -ItemType Directory -Path "$HOME\.hermes" -Force | Out-Null
}

if (-not (Test-Path "$HOME\.hermes\config.yaml")) {
    @"
# Hermes Agent — Windows 默认配置
model:
  default: qwen3.6-35b-nvfp4
  provider: custom:local

custom_providers:
  - name: local
    base_url: http://localhost:8000/v1
    api_key: "\${API_KEY:-EMPTY}"
    model: qwen3.6-35b-nvfp4

agent:
  max_turns: 150
  gateway_timeout: 1800
"@ | Out-File -FilePath "$HOME\.hermes\config.yaml" -Encoding UTF8 -Force
    Write-OK "Hermes 配置已创建"
}

# ── Step 6: 创建启动脚本 ──
Write-Step "Step 6: 启动脚本"

$hermesBatPath = "$INSTALL_DIR\run-hermes.bat"
New-Item -ItemType Directory -Path (Split-Path $hermesBatPath) -Force | Out-Null

@"
@echo off
REM Hermes Agent — Windows 快捷启动
REM 使用方法: 双击运行，或拖入问题文本
hermes chat -q "%*" -Q
pause
"@ | Out-File -FilePath $hermesBatPath -Encoding ASCII -Force

# OpenCode 启动脚本
$opencodeBatPath = "$INSTALL_DIR\run-opencode.bat"
@"
@echo off
REM OpenCode CLI — Windows 快捷启动
@echo off
REM OpenCode CLI — Windows 快捷启动
opencode %*
pause
"@ | Out-File -FilePath $opencodeBatPath -Encoding ASCII -Force

Write-OK "启动脚本已创建: $INSTALL_DIR"

# ── Step 7: 创建桌面快捷方式 ──
Write-Step "Step 7: 桌面快捷方式"

$wshShell = New-Object -ComObject WScript.Shell
if (Test-Path $SHORTCUT_PATH) { Remove-Item $SHORTCUT_PATH -Force }

$shortcut = $wshShell.CreateShortcut($SHORTCUT_PATH)
$shortcut.TargetPath = "cmd.exe"
$shortcut.Arguments = "/k cd /d `"$INSTALL_DIR`" && echo 欢迎使用 Hermes Agent! & echo 输入 'hermes chat -q 你的问题' 开始 & echo 输入 'exit' 退出"
$shortcut.WorkingDirectory = $INSTALL_DIR
$shortcut.Description = "Hermes Agent — AI 研究助手"
$shortcut.IconLocation = "powershell.exe,0"
$shortcut.Save()

Write-OK "桌面快捷方式已创建"

# ── Step 8: 验证 ──
Write-Step "Step 8: 验证安装"

$passCount = 0
$failCount = 0

function Test-Item {
    param($name, $cmd)
    try {
        $result = Invoke-Expression $cmd 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-OK "$name : $result"
            $script:passCount++
        } else {
            Write-Err "$name : $result"
            $script:failCount++
        }
    } catch {
        Write-Err "$name : $_"
        $script:failCount++
    }
}

Test-Item "Python" "python --version"
Test-Item "uv" "uv --version"
Test-Item "Hermes" "hermes --version"
Test-Item "Node.js" "node --version"
Test-Item "OpenCode" "opencode --version"
Test-Item "Git" "git --version"

Write-Host ""
Write-Host "══════════════════════════════════════════════════════════" -ForegroundColor Cyan
if ($failCount -eq 0) {
    Write-Host "  ✅ 全部通过 — 安装成功！" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  $failCount 项未通过，请检查上方" -ForegroundColor Yellow
}
Write-Host "══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步:" -ForegroundColor White
Write-Host "  1. 桌面双击 'Hermes Agent' 快捷方式" -ForegroundColor White
Write-Host "  2. 或直接运行: $hermesBatPath 你的问题" -ForegroundColor White
Write-Host ""
Write-Host "配置 API Key:" -ForegroundColor White
Write-Host "  编辑: $HOME\.hermes\config.yaml" -ForegroundColor White
Write-Host ""
Write-Host "更新:" -ForegroundColor White
Write-Host "  python -m pip install --user --upgrade hermes-agent" -ForegroundColor White
Write-Host ""

Read-Host "按 Enter 退出"