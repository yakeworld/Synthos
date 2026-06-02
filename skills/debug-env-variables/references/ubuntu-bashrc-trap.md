# Ubuntu .bashrc Non-Interactive Trap — Case Study

## Problem
Semantic Scholar API key set in `~/.bashrc` works in interactive terminal but is empty when `main.py` runs via `subprocess.run(shell=True)` or `bash -c "..."`.

## Root Cause Chain
1. `.bashrc` has `case $- in *) return;; esac` at line 6–9
2. `bash -c` creates a non-interactive shell (no `i` flag)
3. The `return` at line 8 exits `.bashrc` BEFORE reaching `export SEMANTIC_SCHOLAR_API_KEY=...` (originally at lines 134–138)
4. Python subprocess never receives the variable
5. `Config.__init__` reads empty string → API calls fail with 403/500

## Fix Applied
- Moved `export GITHUB_TOKEN` and `export SEMANTIC_SCHOLAR_API_KEY` to **before** the `case $-` guard (lines 1–5)
- Added `.api_key` fallback file in `src/core/.api_key` — Config reads this when env var is empty
- Verified with: `bash -c "source ~/.bashrc; echo $SEMANTIC_SCHOLAR_API_KEY"` → now outputs the key

## Key Lesson
In Ubuntu/Debian `.bashrc`, the interactive guard is at the **top** of the file. Any exports after `esac` are ONLY visible to interactive shells. For automated scripts, CI, or subprocess-based execution, either:
- Put exports before the guard
- Set `BASH_ENV=~/.bashrc` before running the script
- Use a file-based fallback in the application code

## Files Involved
- `~/.bashrc` — interactive guard + exports
- `src/core/config.py` — Config.__init__ with `.api_key` fallback
- `src/core/.api_key` — plaintext API key (gitignored, mode 600)
