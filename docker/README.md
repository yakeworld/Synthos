# ╔═══════════════════════════════════════════════════════════╗
# ║  Hermes + OpenCode — Portable Edition                    ║
# ╚═══════════════════════════════════════════════════════════╝

## Two Versions

### Online Version (Recommended)
`launch.bat` / `launch.sh` — Downloads runtimes on first run (~800MB)
- Smaller initial download: just the script
- Always up-to-date runtimes
- Best for: users with good internet, USB distribution

### Offline Version
`launch-offline.bat` / `launch-offline.sh` — Pre-downloaded, NO internet needed
- Larger initial package (~300MB compressed)
- Zero internet connection required
- Best for: USB distribution, air-gapped machines, offline use

## Quick Start

### Windows
```
# Online version
Double-click launch.bat

# Offline version
Double-click launch-offline.bat
```

### macOS / Linux
```bash
# Online version
chmod +x launch.sh
./launch.sh

# Offline version
chmod +x launch-offline.sh
./launch-offline.sh
```

## What you get
- Portable Python (no system Python needed)
- Portable Node.js
- uv + git
- Hermes Agent
- OpenCode CLI
- Isolated data (in `data/`)

## Zero host pollution
```
PYTHONNOUSERSITE=1
PYTHONHOME=
PYTHONPATH=
HERMES_HOME=./data/
```

## Data stays local
All conversations, memory, skills, configs — in `data/` folder only.

## Update
Online: `[5] Update` in menu
Offline: Re-download new version