# Benchmark Recalculation Trap

## Context
Cycle 66 evolution-state.json claimed `benchmark=0.95` based on a partial or
incorrect calculation. Cycle 67 recomputed from scratch and found `benchmark=0.77`.

## Root Causes of the Discrepancy
| Component | State Claim | Actual | Gap |
|-----------|-------------|--------|-----|
| YAML valid | 1.0 (110/110) | 1.0 (110/110) | 0 |
| Version | ? | 0.9182 (101/110) | -0.082 |
| Signature | ? | 0.5000 (55/110) | -0.50 |
| IO_CONTRACT | ? | 0.1909 (21/110) | -0.81 |
| Git tracked | ? | 1.0 (110/110) | 0 |
| Encoding | ? | 1.0 (0 errors) | 0 |
| Git clean | ? | ~0.93 | variable |

The 0.95 claim likely only considered the top 3-4 components or weighted
YAML and git tracking too heavily while ignoring signature and IO_CONTRACT.

## Cycle 71 Escalation (2026-06-12)

> The self-inflation problem was far worse than cycle 67 suggested. Cycle 71 revealed
> a **35.5% gap** between claimed and actual benchmark, persisting across 4 consecutive
> cycles (68-71).

| Cycle | State Claim | Actual | Gap |
|-------|-------------|--------|-----|
| 68    | 0.8459      | 0.7303 | 11.56% |
| 69    | ~0.7303     | ~0.7303 | 0% (corrected) |
| 70    | 0.7479      | 0.4818 | 35.53% |
| 71    | 0.7479      | 0.488  | 34.22% |

> **Key insight**: state.json was stuck at 0.7479 from cycle 70 but never updated
> to actual because no cycle ran VERIFY before recording. The "IO_CONTRACT 5→6"
> improvement was real, but the base formula was miscalculated — IO_CONTRACT only
> exists in 5/109 skills (4.59%), contributing 0.0459 × 0.34 = 0.0156 to the total.
> Even at 100% coverage, IO_CONTRACT can only contribute 1 × 0.34 = 0.34.
> Signature at 50% contributes 0.5 × 0.33 = 0.165. Version at 90% contributes
> 0.9 × 0.33 = 0.297. **Maximum theoretical benchmark = 0.762** (if version=100%,
> signature=100%, io_contract=100%). The claimed 0.8459+ was always impossible.

## Remediation Protocol (Updated for Cycle 71)
1. Always recalculate ALL sub-scores from scratch on disk using explicit formula.
2. Use the explicit formula: `version_pct × 0.33 + signature_pct × 0.33 + io_contract_pct × 0.34`
   Note: this is a weighted sum of 3 dimensions, NOT mean of 7.
3. After each IMPROVE step, re-run PROBE+BENCHMARK and **compare result with state.json**.
   If difference > 5%, downgrade status and record correction in highlights.
4. Never trust state.json's benchmark field as source of truth — always verify independently.
5. If `git diff --cached --name-only | wc -l > 10` before commit, stop and review —
   `git add -A` may have captured unintended changes from prior sessions.
6. After each commit, verify `git status --porcelain` returns empty (except untracked ??).

## Verification Commands

### CRITICAL: grep anchor trap (Cycle 70 fix)
```bash
# WRONG: ^ anchor fails for indented YAML keys
grep -r "^version:" skills/          # → 0/109 (false negative)
grep -r "^signature:" skills/       # → 0/109 (false negative)

# RIGHT: flexible grep works for indented keys
grep -r "version:" skills/           # → 100/109 (correct)
grep -r "signature:" skills/        # → 56/109 (correct)
```

### Full verification suite
```bash
# Count SKILL.md files
find skills/ -name "SKILL.md" | wc -l

# Check YAML validity (all should start with ---)
for f in $(find skills/ -name SKILL.md); do
  head -1 "$f" | grep -q '^---' || echo "NO YAML: $f"
done

# Count version (flexible grep — NEVER use ^)
count=0; total=0
for f in $(find skills/ -name "SKILL.md"); do
  total=$((total+1))
  grep -q "version:" "$f" && count=$((count+1))
done
echo "Version: $count/$total"

# Count signature (flexible grep — NEVER use ^)
count=0; total=0
for f in $(find skills/ -name "SKILL.md"); do
  total=$((total+1))
  grep -q "signature:" "$f" && count=$((count+1))
done
echo "Signature: $count/$total"

# Count IO_CONTRACT (body content, not frontmatter — grep OK)
count=0; total=0
for f in $(find skills/ -name "SKILL.md"); do
  total=$((total+1))
  grep -q "IO_CONTRACT" "$f" && count=$((count+1))
done
echo "IO_CONTRACT: $count/$total"

# Encoding check
python3 -c "
import os
errors = 0
for root, dirs, files in os.walk('skills'):
    for f in files:
        if f == 'SKILL.md':
            try:
                open(os.path.join(root, f), 'r', encoding='utf-8').read()
            except UnicodeDecodeError:
                errors += 1
print(f'Encoding errors: {errors}')
"

# Check git tracking of SKILL.md
git status --porcelain | grep "SKILL.md"

# Check dirty files (structural degradation signal)
git status --porcelain | grep "SKILL.md" | grep "^[ M]" | wc -l
```

### Dirty File Accumulation Trap (Cycle 70)
> Manual edits between cron cycles create dirty SKILL.md files that silently
> degrade the structural score. After IMPROVE, always verify `git status --porcelain`
> returns empty before recording.

### State Lag Trap (Cycle 65)
> If a previous cycle committed to git but didn't update state.json, the next
> cycle's LOAD_STATE reads stale data. Always check `git log --oneline | grep "cycle-" | head -1`
> against state.json's cycle number after LOAD_STATE.

### Skill Tree Growth Trap (Cycle 72)
> **New**: When the skill tree changes size (109→194 in cycle 72), the denominator
> in `pct = count/total` changes but state.json keeps old numerators. The benchmark
> scalar is NOT incrementally updatable — any merge/cron-sync that changes skill
> count requires full recalculation.
>
> In cycle 72: state.json claimed benchmark=0.488 (based on 109 skills), but
> actual was 0.1195 (at 194 skills) — 75% discrepancy. Root cause: new skills
> lacked version/signature/IO_CONTRACT, and state.json numerators were stale.
>
> **Rule**: On LOAD_STATE, always check `find skills/ -name SKILL.md | wc -l`.
> If the count differs from state, mark benchmark as stale and recalculate from scratch.
> See references/skill-tree-growth-trap.md for full detail.
