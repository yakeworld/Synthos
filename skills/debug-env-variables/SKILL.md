---
name: debug-env-variables
description: Debug environment variable issues across shell boundaries, subprocesses, and application configuration layers.
---

# Debug Environment Variables

## 原理层·文言

> 环境之变，变量之惑。
> 壳有界而境无边，子不知父之所有。
> 知其源则知其变，明其界则明其惑。

##
DevOps — environment configuration, subprocess shells, credential injection.

## When to Use
- Environment variables work in interactive shell but not in scripts
- `subprocess.run(shell=True)` seems to lose environment variables
- API keys, tokens, or credentials are empty at runtime despite being set
- `.bashrc`/`.profile`/`.env` files seem to be ignored by automated processes

## Pitfalls

### The Non-Interactive Shell Trap
Bash's `.bashrc` contains this guard by default:
```bash
case $- in
    *i*) ;;
      *) return;;
esac
```
Non-interactive shells (e.g., `bash -c "..."`, `subprocess.run(shell=True)`) do NOT have the `i` flag, so they hit `return` before reaching any code after the guard. **Exports placed after `esac` are invisible to non-interactive shells.**

### Process Substitution and Quoting
When nesting `bash -c` with Python inside `subprocess.run(shell=True)`:
- Single quotes inside double-quoted `-c` args get consumed by the outer shell
- `bash -c "export X=hello; python3 -c 'print(os...)'` — the inner single quotes are eaten
- Use `&&` chaining or heredocs to avoid quoting issues

### `.bashrc` Is Not Loaded Everywhere
- Non-interactive, non-login shells: **never** source `.bashrc`
- Login shells: source `.profile` → which may source `.bashrc`
- `bash --login`: sources `.profile` (not `.bashrc` directly)
- `bash -i`: sources `.bashrc` (interactive)
- `bash -c`: does NOT source anything unless `BASH_ENV` is set

## Debugging Steps

1. **Isolate the boundary**: Does the variable exist in the parent process?
   ```python
   import os; print(os.environ.get("VAR", "NOTSET"))
   ```

2. **Test at each layer**:
   - Interactive shell: `echo $VAR`
   - Non-interactive shell: `bash -c "echo $VAR"`
   - After sourcing: `bash -c "source ~/.bashrc; echo $VAR"`
   - In Python: `bash -c "python3 -c 'import os; print(os.environ.get(\"VAR\"))'"`

3. **Trace through the chain**: Check where the variable disappears:
   - If it exists interactively but not in `bash -c`: the `.bashrc` guard is the culprit
   - If it exists in `bash -c` but not in Python: quoting/subprocess boundary issue
   - If it never exists: the variable was never set correctly

## Fixes (in order of reliability)

### Fix 1: Move Exports Before the Guard
Place `export VAR=...` **before** the `case $- in ... esac` block in `.bashrc`. Non-interactive shells will hit the export before hitting `return`.

### Fix 2: Set BASH_ENV
```bash
export BASH_ENV=~/.bashrc
```
Non-interactive shells read the file pointed to by `BASH_ENV`.

### Fix 3: File-Based Fallback (Most Reliable for Automated Systems)
Store credentials in a local file and have the application read it as fallback:
```python
# In config.py or equivalent
import pathlib
_key_file = pathlib.Path(__file__).parent / '.api_key'
if _key_file.is_file():
    self.api_key = _key_file.read_text().strip()
```
Place the file in a tracked but gitignored location (e.g., `.api_key` in `.gitignore`).

### Fix 4: Use `/etc/environment` (Root Required)
All PAM-authenticated sessions read `/etc/environment`. This is the most reliable but requires root/sudo.

## Verification Checklist
- [ ] Variable exists in interactive shell (`echo $VAR`)
- [ ] Variable survives `bash -c` (non-interactive)
- [ ] Variable is accessible in Python subprocess
- [ ] The application can read the variable (directly or via fallback)

## Hermes Agent / Python Subprocess Specific Pitfalls

### The `subprocess.run(shell=True)` Trap in Hermes
When Hermes Agent runs `execute_code` with `shell=True`, it invokes `bash -c`. This shell:
- Does **NOT** have the `i` flag (non-interactive)
- Does **NOT** source `.bashrc` by default (even with `BASH_ENV` in some configurations)
- Exports inside `bash -c "..."` do **NOT** always propagate to child processes due to quoting/subprocess isolation

**Symptoms**: `os.environ.get('API_KEY')` returns empty even after `source ~/.bashrc` succeeds.

**Why**: The Python process inside `bash -c` runs in a child scope that may not inherit the exported variables due to how this environment spawns subprocesses. The `echo` inside bash works, but `python3` cannot see them.

**Reliable workaround**: Don't rely on `bash -c` to propagate env vars to Python. Instead, use one of these:
1. **File-based fallback** (best): Store API keys in a local file (e.g., `.api_key`) and have Python read it as fallback when `os.environ` is empty.
2. **Hardcode at call site**: Pass the key as a parameter when calling the subprocess.
3. **Never put secrets in `.bashrc` for automated systems** — use a dedicated secrets manager or file.

### `.bashrc` Exports Are Not Reliable for Subprocesses
Even when `.bashrc` exports are placed **before** the `case $- in ... esac` guard, non-interactive bash (`bash -c`) may still not source `.bashrc` at all (it depends on how bash was invoked). In Hermes Agent's environment, `bash -c` does NOT source `.bashrc` by default.

**Rule of thumb**: Never rely on `.bashrc` exports for any automated process (CI, cron, subprocess, daemon). Use `/etc/environment` or a file-based fallback instead.

## Session Details
- [Ubuntu .bashrc non-interactive trap](references/ubuntu-bashrc-trap.md) — full case study from 2026-05-08 session with Semantic Scholar API key (Hermes Agent subprocess isolation discovered)
- [API Key Fallback Pattern](references/api-key-fallback-pattern.md) — file-based fallback for API keys in subprocess contexts (most reliable for automated systems)
