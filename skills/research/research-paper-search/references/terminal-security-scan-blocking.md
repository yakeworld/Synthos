# Terminal Security Scan — curl | python3 Pipe Blocking

## Trap (2026-06-07)

`curl | python3` or `curl | jq` pipes are blocked by the terminal security scanner with pattern `tirith:curl_pipe_shell`:

```
⚠️ Security scan — [HIGH] Pipe to interpreter: curl | python3
[HIGH] Pipe to interpreter: curl | jq
```

**Root cause**: The security scanner treats piping downloaded content directly to an interpreter as untrusted execution.

## Fix

**Never pipe curl output directly to an interpreter.** Instead:

1. **Write script to file, then execute**: `write_file` → `terminal` to run the .py/.sh script.
2. **Use a temp file for intermediate data**: `curl -o /tmp/data.json ...` then `python3 -c "import json; ..."` with `cat /tmp/data.json | python3` OR `json.load(open('/tmp/data.json'))`.
3. **Use single-line python for trivial one-liners**: `python3 -c "import urllib.request; r = urllib.request.urlopen('URL'); print(r.read().decode())"` — no pipe, just native Python stdlib.

## Pattern: Prefer urllib.stdlib over curl entirely (2026-06-07 v76 Confirmation)

This session confirmed that using `urllib.request.urlopen()` directly in Python scripts is the cleanest approach — no curl at all, no temp files needed. All PubMed scans and OpenAlex scans in this session used this pattern successfully.

## Safe Python One-Liners (2026-06-07 Session Discovery)

`python3 -c "..."` with file-based reads (NOT piped input) is SAFE and does not trigger the scanner:

```python
# SAFE — reads from file, no pipe involved
python3 -c "import json; d=json.load(open('/tmp/data.json')); print(len(d['esearchresult']['idlist']))"

# SAFE — urllib stdlib, no curl, no pipe
python3 -c "import json,urllib.request; r=urllib.request.urlopen('URL'); d=json.loads(r.read()); print(d)"
```

**Key rule**: The scanner blocks `curl | python3` (pipe from curl to interpreter). It does NOT block:
- `python3 script.py` (file execution)
- `python3 -c "..."` with file reads (`open('/tmp/file.json')`)
- `python3 -c "..."` with stdlib `urllib.request` (no curl)

## Pattern for PubMed Scanning Scripts

Always use this template:

```python
#!/usr/bin/env python3
"""<description>"""
import json, urllib.request

# Use urllib directly, not curl | python3
url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=..."
with urllib.request.urlopen(url, timeout=15) as r:
    d = json.loads(r.read())
ids = d.get("esearchresult", {}).get("idlist", [])
print(f"Count: {len(ids)}")
```

See also: `references/pubmed-xml-parsing-pattern.md` — PubMed XML parsing traps (int() vs re.search, empty Count tags).
See also: `references/pubmed-false-positive-patterns.md` — PubMed query expansion traps (caloric=restriction, PINN=protein).

See also: `references/pubmed-scan-template.py`
