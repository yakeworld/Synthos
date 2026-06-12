# Large Text Upload to NotebookLM — Reliable Pattern

**Session**: 2026-06-12, hcs3wt-breast-cancer Layer B re-evaluation  
**Problem**: 25KB manuscript text could not be uploaded via any CLI method  
**Root Cause**: 3 distinct CLI modes behave differently with large content

## The Three Modes and Their Traps

### Mode 1: `notebooklm source add --type text file_path`
**Trap**: The CLI does NOT read the file. It uses `file_path` as literal text content.
- Gemini received the string "/tmp/hcs3wt-manuscript-v3.txt" instead of the paper text
- Output: "sources only contain text strings of local file paths"
- This affects ANY file path passed with `--type text`

### Mode 2: `notebooklm source add --type text "$(cat file)"`  
**Trap**: Shell argument length limit. For files >80KB, `$(cat ...)` fails entirely.
- For 25KB files it *might* work on some systems, but is unreliable
- The content gets shell-escaped, which may corrupt special characters

### Mode 3: `notebooklm source add --type text CONTENT` (positional arg)
**Trap**: Same as Mode 2 — positional arg IS inline text. For 25KB+ content, the shell/CLI argument handling breaks.
- `subprocess.run(['notebooklm', 'source', 'add', '--type', 'text', large_text])` 
  → Python's `argv` handling truncates or corrupts large strings

## Working Pattern (2026-06-12 Verified — Partial)

### For PDFs:
```bash
# PDF upload → always returns "error" status (known encoding issue)
# SKIP PDF uploads entirely. They are unreliable.
```

### For BibTeX (small files, <10KB):
```bash
# Use Python subprocess with stdin to avoid shell truncation
python3 -c "
import subprocess
with open('references.bib') as f: content = f.read()
result = subprocess.run(
    ['notebooklm', 'source', 'add', '--type', 'text', '--title', 'Refs', '-n', 'NOTEBOOK_ID'],
    input=content, capture_output=True, text=True
)
"
```
⚠️ BUT: This may still cause the "path-as-content" trap if the CLI treats the content differently in different versions.

### For Large Text (>10KB):
```bash
# No reliable method via notebooklm CLI for files >10KB
# Workaround: Split content into chunks uploaded separately
# OR: Use the notebooklm-py library directly (not CLI)
# OR: Accept that Layer B for large papers requires manual intervention
```

## API-Level Workaround (not CLI)

The notebooklm-py library has an API that may handle large files better:
```python
from notebooklm._sources import SourcesAPI
# Direct API calls bypass CLI argument parsing limits
```
But this requires understanding the internal API structure which changes between versions.

## Key Takeaway

For papers with >10KB text body (most SCI papers), the NotebookLM CLI cannot reliably upload the manuscript text. The only reliable method is file upload (`--type file`) which itself has network instability issues. **Consider splitting large manuscripts into sections or accepting that Layer B requires interactive/human-assisted upload for large papers.**

## Network Instability Notes

- DNS resolution failures can occur mid-session: `[Errno -3] Temporary failure in name resolution`
- `source list` and `source delete` commands can timeout (15-20s+) unpredictably
- Creating a new notebook (as opposed to reusing/deleting sources in an existing one) is more reliable than trying to clean up a corrupted notebook
- When NotebookLM becomes unstable (timeouts, API errors), **start a fresh notebook** rather than trying to fix the existing one
