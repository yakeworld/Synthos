# Session Report: unified scan fix — 2026-06-23

## Context
Cron job `unified-paper-scan.sh` timed out at 120s. Root cause: script called `codex -p hermes exec` which spawns a non-blocking background process, but the shell script had `set -euo pipefail` and no timeout handling, causing the outer process to wait for codex to exit (which it never does for long-running tasks).

## Fix
Replaced `codex` call with direct Python script execution. The Python script (`scan_bib_integrity.py`) was captured as a support file in `scripts/scan_bib_integrity.py` under `bib-integrity-audit`.

## Results
- 125 bib files scanned across 121 papers
- 2,847 total entries, 74.6% DOI coverage (G5 threshold: 90%)
- 162 suspicious entries detected
- 525 cross-file duplicate keys
- 6 papers with empty bib files (0 entries)

## Key Findings
- Most suspicious entries: arXiv preprints without arXiv:ID (136 entries)
- 3d-eyeball-iris-segmentation: 48 suspicious entries across 3 bib files
- 2 cross-file entries with inconsistent metadata (Wang2023, Raissi2019)

## Shell Script Pitfall (CRITICAL)
When a `.sh` script needs to call a long-running tool, NEVER use `codex -p hermes exec` directly in the script. Instead:
1. Create a standalone Python script that does the work directly
2. Have the shell script call `python3 <script.py>`
3. Shell scripts calling codex for long-running tasks will silently timeout
