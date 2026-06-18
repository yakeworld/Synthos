# .bashrc Non-Interactive Shell Pitfall

## Problem

`.bashrc` on Ubuntu/Debian systems contains this guard at the top:

```bash
case $- in
    *i*) ;;
      *) return;;
esac
```

This means **non-interactive shells** (e.g., `subprocess.run('bash -c "..."', ...)`, `ssh host "cmd"`, background scripts) will `return` immediately and **never load any subsequent lines**, including `export` statements, aliases, PATH modifications, etc.

## Symptom

- API keys, tokens, or environment variables set via `export` in `.bashrc` are not available to subprocesses.
- `source ~/.bashrc; echo $VAR` in a non-interactive shell returns empty.
- `bash -c "source ~/.bashrc; echo $VAR"` returns empty.
- Works fine in interactive terminal, fails in scripts/cron/subprocess.

## Diagnosis

Check if `.bashrc` has a non-interactive guard:
```bash
grep -n "case \$-" ~/.bashrc
grep -n "return" ~/.bashrc
```

If lines like `case $- in ... *) return;; esac` appear before your `export` statements, the exports won't be seen by non-interactive shells.

## Solutions (pick one)

### Option 1: Move exports BEFORE the guard (quick fix)

Place all `export` statements for API keys/tokens **before** the `case $-` guard in `.bashrc`. This way, non-interactive shells still see them (they return after the guard, but exports before it are already applied).

```bash
# BEFORE the case statement
export GITHUB_TOKEN="..."
export SEMANTIC_SCHOLAR_API_KEY="..."

# Then the guard
case $- in
    *i*) ;;
      *) return;;
esac
```

### Option 2: Move exports to `.profile` (recommended)

`.profile` (or `.bash_profile`) is sourced by login shells and is **not** guarded against non-interactive execution in the same way. It's the canonical place for persistent environment variables.

```bash
# In ~/.profile:
export GITHUB_TOKEN="..."
export SEMANTIC_SCHOLAR_API_KEY="..."
```

### Option 3: Use `/etc/environment` (most robust, needs root)

`/etc/environment` is read by PAM on login, not by bash at all. It's simple `KEY=VALUE` syntax (no `export`, no quotes needed for the value itself). All processes see it.

```
# /etc/environment
GITHUB_TOKEN=...
SEMANTIC_SCHOLAR_API_KEY=...
```

Note: No shell expansions, no `export` keyword, no quoting of the value itself.

## Verification

After applying a fix, test with a truly non-interactive shell:

```bash
# This simulates a non-interactive subprocess environment
bash --noprofile --norc -c "source ~/.bashrc 2>/dev/null; echo [\$SEMANTIC_SCHOLAR_API_KEY]"

# Or with completely clean env
env -i HOME=/home/yakeworld SHELL=/bin/bash bash --noprofile --norc -c "source ~/.bashrc; echo [\$SEMANTIC_SCHOLAR_API_KEY]"
```

Both should show the value, not empty brackets `[]`.

## Key Insight

**Always test environment variable loading in a non-interactive shell context.** If a tool, script, or GUI app spawns subprocesses, they won't see interactive-only environment variables. The pattern `case $- in *i*) ;; *) return;; esac` in `.bashrc` is the #1 cause of "it works in my terminal but not in my script" for Linux desktop users.
