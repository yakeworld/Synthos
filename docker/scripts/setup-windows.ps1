# ============================================================================
# Hermes + OpenCode — Portable Setup (Windows)
# ============================================================================
# Downloads portable Python, Node.js, uv, git, clones Hermes, creates venv.
# All files go into .cache/runtimes/windows-x64/ - zero host pollution.
# ============================================================================

param(
    [Parameter(Mandatory = $true)]
    [string]$Root
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "Continue"

# Paths
$CacheDir     = Join-Path $Root ".cache"
$RuntimeDir   = Join-Path $CacheDir "runtimes\windows-x64"
$SrcDir       = Join-Path $Root "src"
$BinDir       = Join-Path $RuntimeDir "bin"
$TempDir      = Join-Path $Root ".tmp"
$DataDir      = Join-Path $Root "data"

foreach ($d in @($RuntimeDir, $SrcDir, $BinDir, $TempDir, $DataDir)) {
    New-Item -ItemType Directory -Force -Path $d | Out-Null
}

# Clean macOS metadata from exFAT drives
Get-ChildItem -Path $Root -Filter "._*" -Recurse -Force -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue

# Download URLs
$PythonUrl = "https://github.com/astral-sh/python-build-standalone/releases/download/20260623/cpython-3.11.15+202****0623-x86_64-pc-windows-msvc-install_only.tar.gz"
$NodeUrl   = "https://nodejs.org/dist/v22.22.3/node-v22.22.3-win-x64.zip"
$UvUrl     = "https://github.com/astral-sh/uv/releases/download/0.11.19/uv-x86_64-pc-windows-msvc.zip"
$GitUrl    = "https://github.com/git-for-windows/git/releases/download/v2.54.0.windows.1/MinGit-2.54.0-64-bit.zip"
$SourceUrl = "https://github.com/NousResearch/hermes-agent/archive/refs/heads/main.zip"

# Helpers
function Write-Step($msg) { Write-Host ""; Write-Host "[SETUP] $msg" -ForegroundColor Cyan }
function Write-Done($msg) { Write-Host "[OK]    $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "[WARN]  $msg" -ForegroundColor Yellow }

function Download-File($Url, $OutFile, $Desc) {
    $name = Split-Path $Url -Leaf
    if (Test-Path $OutFile) {
        $size = (Get-Item $OutFile).Length
        if ($size -gt 0) {
            $sizeMB = [math]::Round($size / 1MB, 2)
            Write-Host "        $name already cached ($sizeMB MB). Skipped." -ForegroundColor Yellow
            return
        } else {
            Write-Warn "$name exists but is 0 bytes - re-downloading..."
            Remove-Item $OutFile -Force
        }
    }
    Write-Step "Downloading $Desc ($name)..."
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 -bor [Net.SecurityProtocolType]::Tls13
        Invoke-WebRequest -Uri $Url -OutFile $OutFile -UseBasicParsing -TimeoutSec 900
    } catch {
        throw "Failed to download $Desc: $_"
    }
    $sizeMB = [math]::Round((Get-Item $OutFile).Length / 1MB, 2)
    Write-Done "Downloaded $name ($sizeMB MB)"
}

# ── Step 1: Python ───────────────────────────────────────────
Write-Step "Step 1/5: Python runtime"
$pythonTar = Join-Path $TempDir "python.tar.gz"
try {
    Download-File $PythonUrl $pythonTar "Python 3.11 (standalone)"
    tar -xzf $pythonTar -C $RuntimeDir 2>&1 | Out-Null
    # Flatten: cpython-xxx/ -> root
    $sub = Get-ChildItem $RuntimeDir -Directory -Name | Select-Object -First 1
    if ($sub -and (Test-Path (Join-Path $RuntimeDir $sub))) {
        Copy-Item (Join-Path $RuntimeDir $sub "\*") $RuntimeDir -Recurse -Force
        Remove-Item (Join-Path $RuntimeDir $sub) -Recurse -Force
    }
    Write-Done "Python 3.11.15 ready"
} catch {
    throw "Python download failed: $_"
}

# ── Step 2: Node.js ──────────────────────────────────────────
Write-Step "Step 2/5: Node.js runtime"
$nodeZip = Join-Path $TempDir "node.zip"
try {
    Download-File $NodeUrl $nodeZip "Node.js 22 LTS"
    Expand-Archive -Path $nodeZip -DestinationPath (Join-Path $RuntimeDir "node") -Force
    # Flatten
    $nodeRoot = Join-Path $RuntimeDir "node"
    $flattened = Get-ChildItem $nodeRoot -Directory | Select-Object -First 1
    if ($flattened) {
        Copy-Item (Join-Path $flattened.FullName "\*") $nodeRoot -Recurse -Force
        Remove-Item $flattened.FullName -Recurse -Force
    }
    Write-Done "Node.js 22 ready"
} catch {
    throw "Node.js download failed: $_"
}

# ── Step 3: uv ───────────────────────────────────────────────
Write-Step "Step 3/5: uv (package manager)"
$uvZip = Join-Path $TempDir "uv.zip"
try {
    Download-File $UvUrl $uvZip "uv"
    Expand-Archive -Path $uvZip -DestinationPath $RuntimeDir -Force
    if (Test-Path (Join-Path $RuntimeDir "uv.exe")) {
        Copy-Item (Join-Path $RuntimeDir "uv.exe") (Join-Path $BinDir "uv.exe") -Force
    }
    Write-Done "uv ready"
} catch {
    Write-Warn "uv download failed - will use pip instead"
}

# ── Step 4: Create virtual environment ───────────────────────
Write-Step "Step 4/5: Setting up environment"
$venvPath = Join-Path $RuntimeDir "venv"
if (Test-Path $venvPath) { Remove-Item $venvPath -Recurse -Force }

$pythonExe = Join-Path $RuntimeDir "python" "python.exe"
& $pythonExe -m venv $venvPath 2>&1 | Out-Null

if (Test-Path $venvPath) {
    Write-Done "Virtual environment created"
} else {
    throw "Failed to create venv"
}

# ── Step 5: Install Hermes + source code ─────────────────────
Write-Step "Step 5/5: Installing Hermes Agent"

# pip install from PyPI
$pipExe = Join-Path $venvPath "Scripts\pip.exe"
& $pipExe install hermes-agent 2>&1 | Out-Null

if (Test-Path (Join-Path $venvPath "Scripts\hermes.exe")) {
    Write-Done "Hermes Agent installed via pip"
} else {
    Write-Warn "pip install had issues, trying direct..."
    & $pythonExe -m pip install hermes-agent 2>&1 | Out-Null
    Write-Done "Hermes Agent installed (direct)"
}

# Clone source for hot-update capability
Write-Step "Cloning Hermes Agent source..."
if (-not (Test-Path (Join-Path $SrcDir "hermes-agent"))) {
    # Try git first, fallback to zip download
    $gitExe = Join-Path $BinDir "git.exe"
    if (Test-Path $gitExe) {
        git clone --depth 1 https://github.com/NousResearch/hermes-agent.git $SrcDir\hermes-agent 2>&1 | Out-Null
    } else {
        Download-File $SourceUrl (Join-Path $TempDir "hermes-src.zip") "Hermes Agent source"
        Expand-Archive -Path (Join-Path $TempDir "hermes-src.zip") -DestinationPath $SrcDir -Force
        $sf = Get-ChildItem $SrcDir -Directory -Name "hermes-agent*" | Select-Object -First 1
        if ($sf) {
            Rename-Item (Join-Path $SrcDir $sf) "hermes-agent" -ErrorAction SilentlyContinue
        }
    }
    Write-Done "Source cloned"
} else {
    Write-Done "Source already present"
}

# ── Config ───────────────────────────────────────────────────
Write-Step "Creating default configuration..."

if (-not (Test-Path (Join-Path $DataDir ".env"))) {
    @"
# Add your API keys below
OPENROUTER_API_KEY=sk-or-v1-xxx
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
"@ | Out-File -FilePath (Join-Path $DataDir ".env") -Encoding UTF8 -Force
}

if (-not (Test-Path (Join-Path $DataDir "config.yaml"))) {
    @"
# Hermes Agent configuration
model:
  default: qwen3.6-35b-nvfp4
  provider: custom:local

custom_providers:
  - name: local
    base_url: http://localhost:8000/v1
    api_key: EMPTY
    model: qwen3.6-35b-nvfp4

agent:
  max_turns: 150
  gateway_timeout: 1800
"@ | Out-File -FilePath (Join-Path $DataDir "config.yaml") -Encoding UTF8 -Force
}

# ── Done ─────────────────────────────────────────────────────
"ready" | Out-File (Join-Path $RuntimeDir "ready.flag") -Encoding ASCII -Force

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  Setup complete! Double-click launch.bat to start." -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Next steps:" -ForegroundColor Cyan
Write-Host "    1. Edit data/.env — add your API keys" -ForegroundColor White
Write-Host "    2. Double-click launch.bat" -ForegroundColor White
Write-Host ""
$totalMB = [math]::Round((Get-ChildItem $Root -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum / 1MB, 0)
Write-Host "  Total size: ${totalMB} MB" -ForegroundColor Yellow
Write-Host ""