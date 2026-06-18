# Hermes Agent Subprocess Environment Isolation

Tested 2026-05-08 during BPPV paper search and GUI debugging.

## The Problem

When Hermes Agent runs `execute_code` with `shell=True`, it spawns a `bash -c` process. This subprocess:
1. Is **non-interactive** (no `i` flag), so `.bashrc`'s `case $- in *) return;; esac` guard exits early
2. Does **NOT** source `.bashrc` by default (non-interactive, non-login shell)
3. Even when `source ~/.bashrc` is explicitly called, child processes (Python, curl) may not inherit the exported variables

## Evidence

```bash
# Test 1: Direct export works
bash -c "export TEST=hello; echo $TEST"
# Output: (empty) — .bashrc not sourced

# Test 2: Explicit source works for echo
bash -c "source ~/.bashrc; echo $SEMANTIC_SCHOLAR_API_KEY"
# Output: s2k-7b... — the variable IS set in bash

# Test 3: But Python can't see it
bash -c "source ~/.bashrc; python3 -c 'import os; print(os.environ.get(\"SEMANTIC_SCHOLAR_API_KEY\", \"EMPTY\"))'"
# Output: EMPTY — Python doesn't see it

# Test 4: Direct Python export fails too
bash -c "export MY_VAR=test; python3 -c 'import os; print(os.environ.get(\"MY_VAR\", \"EMPTY\"))'"
# Output: EMPTY — even direct export doesn't propagate to Python
```

## Root Cause

The `subprocess.run(shell=True)` call in Hermes Agent's sandbox environment creates an isolated shell. The `bash -c` process runs in a child scope that does NOT propagate exported variables to grandchild processes (Python) due to how the sandbox spawns subprocesses.

## Workarounds

### 1. File-based fallback (recommended)
Store API keys in a local file and have Python read it:
```python
# In config.py
import pathlib
_key_file = pathlib.Path(__file__).parent / '.api_key'
if _key_file.is_file():
    self.api_key = _key_file.read_text().strip()
```

### 2. Pass as command-line argument
```python
subprocess.run(f'python3 script.py --api-key {api_key}', shell=True)
```

### 3. Use environment file with explicit loading
```python
import subprocess
env = os.environ.copy()
env['SEMANTIC_SCHOLAR_API_KEY'] = 's2k-...'
subprocess.run('python3 script.py', shell=True, env=env)
```

### 4. Avoid bash -c for Python calls
Run Python scripts directly without wrapping in bash -c:
```python
subprocess.run(['python3', 'script.py'], shell=False)
```

## Debugging Steps

1. Test `bash -c "echo $VAR"` — if empty, .bashrc isn't sourced
2. Test `bash -c "source ~/.bashrc; echo $VAR"` — if works, bash can see it
3. Test `bash -c "source ~/.bashrc; python3 -c 'print...'` — if empty, Python can't see it
4. The variable disappears at the Python subprocess boundary, not at the .bashrc boundary

## Key Takeaway

Never rely on environment variables set in `.bashrc` or via `bash -c` for automated Python processes in Hermes Agent. Use file-based fallback or explicit environment passing instead.
