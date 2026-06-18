# Absorption Potential Audit Protocol

> **2026-06-02 实战教训**：Synthos 有 121 个 SKILL.md 文件，但只有 20 个被 git tracked。absorption_potential 从 0.80 暴跌到 0.17。

## Problem Statement

The `absorption_potential` dimension in `evolution-state.json` measures what fraction of skills are git-tracked:

```
absorption_potential = git_tracked_skills / total_skills
```

When new skills are created but not committed to git, this drops to near zero even though the system has 121 valid skills.

## Audit Procedure

```bash
# Step 1: Count total SKILL.md files in skills/
cd /media/yakeworld/sda2/Synthos
total=$(find skills/ -name "SKILL.md" | wc -l)
echo "Total SKILL.md: $total"

# Step 2: Count git-tracked SKILL.md files
tracked=$(git ls-files "skills/" | grep "SKILL.md" | wc -l)
echo "Git-tracked: $tracked"

# Step 3: Calculate absorption_potential
absorption_potential=$((tracked * 100 / total))
echo "Absorption potential: $absorption_potential%"

# Step 4: List untracked files
git status --porcelain | grep "?? " | grep "SKILL.md"
echo "Untracked SKILL.md: $(git status --porcelain | grep '?? .*SKILL.md' | wc -l)"
```

## Symptoms

| Signal | Value |
|:-------|:------|
| absorption_potential < 0.5 | Critical — more than half skills not tracked |
| absorption_potential < 0.8 | Warning — significant uncommitted work |
| Untracked SKILL.md > 10 | Action required |

## Fix

```bash
# Step 1: Audit what needs to be committed
git status --porcelain

# Step 2: Exclude non-core directories
# research/, data/, literature/ are NOT for GitHub upload
# Add to .gitignore: research/ data/ literature/

# Step 3: Remove from tracking but keep local
git rm --cached research/ data/ literature/  # if already tracked

# Step 4: Add all new skills
git add skills/

# Step 5: Commit
git commit -m "[chore] commit N new SKILL.md files"

# Step 6: Update state.json
# cycle = N+1, absorption_potential = committed/total, edit_budget consumed = 0
```

## Verification

After fixing:
- `git ls-files skills/ | grep SKILL.md | wc -l` should equal `find skills/ -name SKILL.md | wc -l`
- absorption_potential in evolution-state.json should be 1.0
- `git status --short` should show 0 uncommitted files (or only expected uncommitted files)

## Prevention

Add to evolution PROBE step:
```
IF git_status_untracked > 10:
    WARN: "X SKILL.md files not git tracked — absorption_potential = Y/Z"
```

## Related

- `evolution/SKILL.md` — "关键陷阱与教训" section 3
- `project-experience-distillation/SKILL.md` — Trap 7 & 8
- `evolution-state.json` — absorption_potential dimension
