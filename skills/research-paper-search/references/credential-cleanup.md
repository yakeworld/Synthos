# Credential leak detection and cleanup procedure

## Overview

Procedures for detecting and fixing hardcoded credentials, tokens, and API keys in project source code, including the special case where the code execution pipeline masks sensitive strings.

## Detection

```python
import os, re, subprocess

root = '/path/to/project'
exclude = {'.git', '__pycache__', 'src.src', '.roo', '.devcontainer'}

patterns = [
    rb'github_pat_[A-Za-z0-9_]{20,}',
    rb'ghp_[A-Za-z0-9_]{20,}',
    rb'gho_[A-Za-z0-9_]{20,}',
    rb'ghs_[A-Za-z0-9_]{20,}',
    rb's2k-[A-Za-z0-9]{20,}',      # Semantic Scholar
    rb'x-api-key',                   # Generic API key headers
    rb'Bearer [A-Za-z0-9_/.+-]{20,}', # Generic bearer tokens
    rb'password[=:]\s*\S+',         # Hardcoded passwords
]

for dirpath, dirnames, filenames in os.walk(root):
    dirnames[:] = [d for d in dirnames if d not in exclude]
    for fn in filenames:
        fpath = os.path.join(dirpath, fn)
        if fn.endswith(('.py', '.js', '.ts', '.sh', '.yaml', '.yml', '.env',
                         '.json', '.toml', '.cfg', '.ini', '.conf')):
            with open(fpath, 'rb') as f:
                data = f.read()
            for pat in patterns:
                if re.search(pat, data):
                    print(f"  {fpath}: contains token/credential")
```

## Fixing Hardcoded Credentials

### Step 1: Replace with env var lookups

```python
# Before (hardcoded):
GITHUB_TOKEN="[REDACTED]"

# After (env var):
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
```

### Step 2: Use byte-level replacement when pipeline masks tokens

When the code execution environment masks sensitive strings (replacing them with `***`), standard `patch` or string replacement will fail. Use byte-level replacement instead:

```python
with open(fpath, 'rb') as f:
    data = f.read()

# Find the exact byte pattern (even if display is masked)
# Replace at byte level
old_bytes = b'#GITHUB_TOKEN="[REDACTED]"\nGITHUB_TOKEN="[REDACTED]"'
new_bytes = b"# GitHub token — set via GITHUB_TOKEN environment variable.\n# DO NOT hardcode tokens in source files.\nGITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')\n"

data = data.replace(old_bytes, new_bytes)
with open(fpath, 'wb') as f:
    f.write(data)
```

### Step 3: Update .gitignore for credential files

```
# Security
*.key
*.pem
*.credentials
.git-credentials
.github/credentials
```

### Step 4: Remove from git tracking

```bash
git rm --cached .git-credentials
git rm --cached .git/credentials  # if tracked
```

### Step 5: Add to shell profile

```bash
# ~/.bashrc or ~/.zshrc — add at the end, outside the interactive-only guard
export GITHUB_TOKEN="[REDACTED]"
export SEMANTIC_SCHOLAR_API_KEY="[REDACTED]"
```

Note: `~/.bashrc` on Ubuntu has `case $- in *i*) ;; *) return;; esac` which exits for non-interactive shells. Credentials set after this guard will NOT be available to subprocesses. If needed, also set in `~/.profile`.

### Step 6: Remove old credential files from disk

```bash
rm -f .git-credentials .git/credentials
```

### Step 7: Verify

```bash
# Check no more hardcoded tokens remain
grep -rn 'github_pat_\|ghp_\|gho_\|ghs_\|s2k-' src/  # should be empty
```

## Special Cases

### Token that works in `curl` but fails in `git push`

A token may authenticate to `/user` (public user info) but fail for authenticated API calls like `/rate_limit`. This usually means:
- Token is expired or revoked (re-generate)
- Token lacks required scopes (need `repo` + `read:user`)
- Token is a fine-grained PAT with limited permissions

### Git push failures with credentials

In this environment, `git push` with HTTPS often fails with "没有那个设备或地址" (No such device or address) even when the token is correct. Workarounds:
1. Use `gh auth login --with-token` to register the token with `gh` CLI, then `git push` uses git credentials helper
2. Use `credential.helper = "store --file=/tmp/.git-cred-local"` with the token in the URL
3. Manually set: `git remote set-url origin https://x-access-token:TOKEN@github.com/...`

## Common Pitfalls

- **Pipeline masking**: The code execution pipeline masks `github_pat_*`, `ghp_*`, and similar patterns with `***`. When patching, you must either know the exact old content or use byte-level matching.
- **Non-interactive .bashrc guard**: `~/.bashrc` exits early for non-interactive shells. Subprocesses spawned by agents may not see env vars set in `.bashrc`.
- **Sandbox Python mismatch**: Code execution uses a different Python binary than the system shell. `pip3 install` may say "already satisfied" but the sandbox Python cannot import the module because it runs a different Python version. Always verify with: `python3 -c "import MODULE"` in the sandbox, not just check `pip3 list`.
- **`.git-credentials` is often committed**: Many projects commit `.git-credentials` to git. Even after adding to `.gitignore`, the file remains in git history. Use `git rm --cached` AND delete the file from disk.
- **Duplicate credentials**: The same credential may appear in multiple files (e.g., `config.py` and `codev10.py` or `github_maintenance.py`). Check all files, not just the main one.
- **Hardcoded in default values**: `os.environ.get('VAR', 'hardcoded_value')` is still hardcoded. The default value must be empty string `''` or omitted entirely.
