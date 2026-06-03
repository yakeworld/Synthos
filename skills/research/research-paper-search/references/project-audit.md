# Multi-file project audit and cleanup workflow

## Overview
A systematic approach for auditing and cleaning up a multi-file project repository — detecting duplicates, fixing code quality issues, cleaning README, adding license, and pushing to GitHub.

## Phase 1: Clone and Inventory

```bash
# Clone the repo
git clone https://github.com/USER/REPO.git /tmp/REPO_audit
cd /tmp/REPO_audit

# Inventory all files by size and type
find . -type f | sort
# Focus on: .html, .py, .json, .md, config files
```

## Phase 2: Structural Checks

### Duplicate detection (HTML files)
```python
# Check for triplicated/multiplied content in HTML files
with open(fpath, 'r') as f:
    content = f.read()
body_count = content.count('<body')
html_close = content.count('</html>')
# If body_count > 1 or html_close > 1 → content is duplicated
```

### Duplicate files
```python
# Check for near-duplicate files (e.g., journal.json vs journals.json)
# Also check for compressed copies (journals.zip alongside journals.json)
```

### ID uniqueness
```python
import re
ids = re.findall(r'id="([^"]+)"', content)
dup = {i: ids.count(i) for i in set(ids) if ids.count(i) > 1}
```

## Phase 3: Code Quality Fixes

### Security
- Find and replace all hardcoded credentials (tokens, API keys, passwords)
- Replace with `os.environ.get('VAR', '')` pattern
- Use byte-level replacement if the code execution pipeline masks sensitive strings

### Code quality
- Fix unclosed tags (`</script>`, `</html>`, etc.)
- Remove `eval()` calls — replace with safe function calls
- Remove inline `onclick` handlers — move to `<script>` blocks
- Fix duplicate IDs in HTML

### Documentation
- Clean up README.md: remove excessive blank lines, fix numbering
- Add LICENSE file if missing
- Add .gitignore for generated/compressed files

## Phase 4: Commit and Push

### Push to GitHub (may fail due to credential issues)
```bash
# Common failure: "没有那个设备或地址" or "Bad credentials"

# Workaround 1: Use gh CLI for auth
echo "TOKEN" | gh auth login --with-token
git push origin main

# Workaround 2: Embed token in URL
git remote set-url origin https://x-access-token:TOKEN@github.com/USER/REPO.git
git push origin main

# Workaround 3: Use credential store
git config credential.helper "store --file=/tmp/.git-creds"
# Then push — it will read from the stored file
```

## Phase 5: Verify
```python
# Final validation checklist
all_ok = True
for each file:
    - body == 1, html_close == 1 (no duplication)
    - no duplicate IDs (except JS-generated like `${checkboxId}`)
    - no eval() calls
    - no hardcoded credentials
    - </html>, </body>, </script> all present and balanced
```

## Common Pitfalls
- **Non-interactive .bashrc**: Env vars set in `.bashrc` after the `case $- in *i*) ;; *) return;; esac` guard are not visible to subprocesses.
- **Pipeline masking**: Sensitive strings are replaced with `***` in tool output. Use byte-level operations to patch files containing them.
- **Sandbox Python mismatch**: The code execution sandbox may use a different Python binary than the shell. Always verify imports with the actual sandbox Python.
- **Git credentials committed**: `.git-credentials` may already be in git history. `git rm --cached` is necessary even after adding to `.gitignore`.
- **Large HTML files**: Files >50KB may contain structural issues. Check `</html>` count first before deep analysis.
- **JS-generated IDs**: Patterns like `${checkboxId}` in `id=` attributes are generated at runtime by JavaScript. They are NOT real duplicates — the regex will match them but they won't cause DOM issues.
