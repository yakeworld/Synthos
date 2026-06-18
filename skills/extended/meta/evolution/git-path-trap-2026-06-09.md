# Git Path Trap — ls-files vs os.path.exists

## Context

Cycle 68 discovered that `git ls-files "skills/**/SKILL.md"` returns 110 relative paths
(e.g., `skills/evolution/SKILL.md`). When these relative paths are passed to
`os.path.exists()`, ALL return False — because `os.path.exists()` checks relative to
the **current working directory** (`/tmp/hermes_sandbox`), not relative to the
Synthos repo root (`/media/yakeworld/sda2/Synthos`).

This caused a false diagnosis of "110 missing files" when in fact all 110 files exist
on disk. The os.walk-based count (109) was actually correct at the time.

## Root Cause

`git ls-files` uses paths relative to the repository root. `os.path.exists()` resolves
paths relative to the process CWD. In the Hermes sandbox, CWD is `/tmp/hermes_sandbox`,
NOT the Synthos repo root.

## Remediation

| Method | Path Type | Safe for os.path.exists()? |
|--------|-----------|---------------------------|
| `git ls-files` | relative to repo root | NO — must prefix with WORKDIR |
| `git status --porcelain` | relative to repo root | NO — must prefix with WORKDIR |
| `os.walk(WORKDIR/skills)` | absolute | YES |
| `os.path.join(WORKDIR, git_path)` | absolute | YES |

## Correct Pattern

```python
WORKDIR = "/media/yakeworld/sda2/Synthos"

# WRONG — relative path, checks against /tmp/hermes_sandbox
git_path = "skills/evolution/SKILL.md"
os.path.exists(git_path)  # False!

# CORRECT — absolute path
os.path.exists(os.path.join(WORKDIR, git_path))  # True!

# CORRECT — use os.walk for on-disk counting
skill_count = sum(
    1 for root, _, files in os.walk(f"{WORKDIR}/skills")
    if "SKILL.md" in files
)
```

## Verification Commands

```bash
# git ls-files returns relative paths — prefix with repo root for FS checks
git ls-files "skills/**/SKILL.md" | while read f; do
    if [ ! -f "/media/yakeworld/sda2/Synthos/$f" ]; then
        echo "MISSING: $f"
    fi
done

# Count SKILL.md on disk (absolute paths via os.walk equivalent)
find /media/yakeworld/sda2/Synthos/skills -name "SKILL.md" | wc -l

# Count SKILL.md tracked by git
git ls-files "skills/**/SKILL.md" | wc -l
```

## Lesson

Git and filesystem tools use different path bases. Always be explicit about the
working directory. This is not a Synthos-specific issue — it applies to any
git-managed project used from a different CWD.

文言: 名同实异，路不同基
