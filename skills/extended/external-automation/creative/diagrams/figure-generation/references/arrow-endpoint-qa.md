# Arrow Endpoint QA — 2026-06-26 HCS-3WT

## Problem

Arrows in matplotlib architecture figures had endpoints outside target boxes. User repeatedly flagged: "箭头没有从这个边缘或者是这个框的终点过去", "箭头连线是斜的", "箭头跟这个框有交叉".

## Root Cause

Arrow endpoints checked with `check_arrow_inside()` existed in code but were **never executed**. QA was written as dead code. No automated gate ran before sending to user.

## Fix

1. Every arrow endpoint must be inside the target box AABB: `tx <= x2 <= tx+tw and ty <= y2 <= ty+th`
2. If arrow connects two boxes on different x-ranges (e.g. Input Box at x=7 → Expert B at x=0.3-4.5), the endpoint must still be inside the TARGET box x-range, not the source box
3. `check_arrow_inside()` must be called BEFORE `plt.subplots()`
4. If QA fails → `sys.exit(1)` → no output → fix and rerun

## Example: arrow1 (Input Box → Expert B)

```
Input Box: x=5.3-8.7, y=7.55-8.15
Expert B:  x=0.3-4.5, y=5.3-6.7

Original: (7, 7.55) → (7, 6.95)
  - Endpoint (7, 6.95): x=7 NOT in [0.3, 4.5] → FAIL
  - Endpoint (7, 6.95): y=6.95 NOT in [5.3, 6.7] → FAIL

Fixed: (7, 7.55) → (4.35, 6.68)
  - Endpoint (4.35, 6.68): x=4.35 IN [0.3, 4.5] ✓
  - Endpoint (4.35, 6.68): y=6.68 IN [5.3, 6.7] ✓
```

## All 6 arrows after fix

| Arrow | End | Target | Check |
|-------|-----|--------|-------|
| input_to_b | (4.35, 6.68) | Expert B [0.3,4.5]×[5.3,6.7] | ✓ |
| b_to_clear_neg | (5.3, 5.97) | Clear Neg [5.3,8.5]×[5.55,6.4] | ✓ |
| a_to_clear_pos | (5.3, 3.47) | Clear Pos [5.3,8.5]×[3.05,3.9] | ✓ |
| b_to_c | (2.4, 1.62) | Expert C [0.3,4.5]×[0.2,1.65] | ✓ |
| a_to_c | (2.4, 1.62) | Expert C [0.3,4.5]×[0.2,1.65] | ✓ |
| c_to_gray | (5.3, 0.92) | Gray Zone [5.3,8.5]×[0.55,1.4] | ✓ |
