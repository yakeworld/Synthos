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
```bash
# Check YAML validity
find skills -name SKILL.md -exec grep -l '^---' {} \; | wc -l

# Count signatures
grep -r "signature:" skills/*/SKILL.md | wc -l

# Count IO_CONTRACT
grep -r "IO_CONTRACT\|输入\|输出" skills/*/SKILL.md | wc -l

# Check git tracking
cd /media/yakeworld/sda2/Synthos && git status --porcelain | grep SKILL.md

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
```
