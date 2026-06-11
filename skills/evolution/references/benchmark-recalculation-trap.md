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

## Remediation Protocol
1. Always recalculate ALL 7 sub-scores from scratch on disk.
2. Use the explicit formula: mean(yaml_valid, version, signature, io_contract, git_tracked, encoding_clean, git_clean)
3. Never trust state.json's benchmark field as a source of truth.
4. After each IMPROVE step, re-run PROBE+BENCHMARK to confirm improvement.
5. Document actual sub-scores in evolution-log.md and evolution-state.json.

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
