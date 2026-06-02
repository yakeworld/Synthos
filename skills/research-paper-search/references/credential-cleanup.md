# Credential Cleanup Guide

> 检测项目中硬编码的凭证、token 和 API key，并提供修复方案。

## Detection

Scan all source files for hardcoded credentials using common patterns:

```python
import re
import os

# Common token formats that GitHub scanner detects:
TOKEN_PATTERNS = [
    rb'ghp_[A-Za-z0-9_]{20,}',          # GitHub Personal Access Token
    rb'gho_[A-Za-z0-9_]{20,}',          # GitHub OAuth Token
    rb'ghs_[A-Za-z0-9_]{20,}',          # GitHub Server Token
    rb'github_pat_[A-Za-z0-9_]{86}',    # GitHub PAT (v2)
    rb'x-api-key',                       # Generic API key headers
    rb'Bearer [A-Za-z0-9_/.+-]{20,}',    # Generic bearer tokens
]
```

### Step 1: Replace with env var lookups

```python
# Before (hardcoded):
GITHUB_TOKEN="[REDACTED]"

# After (env var):
GITHUB_TOKEN=os.getenv('GITHUB_TOKEN', '')
```

### Step 2: Use byte-level replacement when pipeline masks tokens

When the code execution environment masks sensitive strings (replacing them with `***`), standard `patch` or string replacement will fail. Use byte-level replacement instead:

```python
# Example: Replace a masked token
# If the pipeline shows `github_pat_***` or `ghp_***`, you need byte-level matching
# to find and replace the original content.

new_bytes = b"# GitHub token — set via GITHUB_TOKEN environment variable.\n# DO NOT hardcode tokens in source files.\nGITHUB_TOKEN=os.getenv('GITHUB_TOKEN', '')\n"
```

### Step 3: Verify cleanup

```bash
# Check no more hardcoded tokens remain
grep -rn '[TOKEN_PATTERN]' src/  # should be empty
```

### Notes

- A token may authenticate to `/user` (public user info) but fail for authenticated API calls like `/rate_limit`. This usually means the token has restricted scopes.
- When pushing via HTTPS, authentication may fail with device errors. Solutions:
  1. Use `gh auth login --with-token` to register the token with the CLI
  2. Use `credential.helper = "store --file=..."` with the token in the URL
  3. Manually set: `git remote set-url origin https://x-access-token:***@github.com/...`

- **Pipeline masking**: The code execution pipeline masks token patterns with `***`. When patching, you must either know the exact old content or use byte-level matching.
