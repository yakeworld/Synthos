# Skill Tree Growth Trap (Cycle 72)

## Phenomenon
When the skill tree grows (via merge, cron sync, or manual addition), the `total` in
`pct = count / total` changes but state.json keeps old numerators and denominators.

### Cycle 72 Example
| Cycle | Total SKILL.md | Version Count | Version Pct | Benchmark |
|-------|---------------|---------------|-------------|-----------|
| 71    | 109           | 100           | 91.74%      | 0.488 (claimed) / 0.1195 (actual) |
| 72    | 194           | 60→61         | 30.93%→31.44% | 0.1212 |

The "version 100/109 = 91.74%" from cycle 71 state was interpreted as 60/109 = 55%
at cycle 72 because:
- state.json was not tracking the total count
- 85 NEW skills lacked version (60 had version at 109, but only 60 have it at 194)
- The old "100" was actually stale — the true count at 194 was 60

## Root Cause
state.json stores `dimensions.benchmark` as a scalar. It does NOT store:
- The skill tree size at time of measurement
- The numerator/denominator breakdown
- A snapshot of `total_skill_files` used for pct calculation

When total changes, the scalar benchmark becomes meaningless unless the new total
is used with fresh counts.

## Symptoms
1. state.json claims benchmark=0.488 at cycle 71, but at cycle 72 actual=0.1195 (75% gap)
2. Numerator counts in state become meaningless because total changed
3. "version 100/109" in cycle 71 lessons → "version 60/194" in cycle 72 = 40 skill drop

## Remediation

### In evolution-state.json, store denominator alongside benchmark:
```json
{
  "dimensions": {
    "benchmark": 0.1212,
    "benchmark_total": 194,
    "benchmark_numerators": {
      "version": 61,
      "signature": 2,
      "io_contract": 8
    }
  }
}
```

### In BENCHMARK step, always verify:
```
if state.benchmark_total != actual_total:
    WARN: "Skill tree grew/shrunk — full recalculation required, not incremental"
    state.benchmark = recalculate_from_scratch()
    state.downgrade_if_gap > 5%
```

### In LOAD_STATE step, check:
```bash
actual_total=$(find skills/ -name SKILL.md | wc -l)
if [ "$actual_total" != "$state.benchmark_total" ]; then
    echo "SKILL_TREE_GROWTH: state says $state.benchmark_total, actual $actual_total"
    echo "Must recalculate benchmark from scratch, not incrementally."
fi
```

## Cycle 72 Resolution
- Recalculated benchmark from scratch at 194 skills
- Found actual = 0.1195 (claimed 0.488 in state) — 75% discrepancy
- Downgraded overall grade: GOOD -> OK
- Updated state.json with correct values
- Noted 801 untracked quality artifact files (new pattern from cron sync)
- Noted 7 untracked SKILL.md files

## Key Takeaway
The benchmark scalar is **not incrementally updatable** when the skill tree changes size.
Any merge, sync, or manual addition that changes `total` requires a full recalculation.
This makes state.json's benchmark field fragile — always verify with fresh disk scan.

## Prevention
1. Store `benchmark_total` (the skill tree size) in state.json alongside benchmark score
2. On LOAD_STATE, compare stored total vs actual `find skills/ -name SKILL.md | wc -l`
3. If mismatch, mark benchmark as "stale" and recalculate from scratch
4. Never add a delta to benchmark — only replace with fresh calculation
5. After any merge/cron-sync that changes skill count, force a benchmark recalculation