# Paired Anatomical Data Direction Alignment

> Technique discovered 2026-05-28 during SCC morphological fitting.

## Problem

When fitting parametric curves (log spirals, ellipses, splines) to paired anatomical structures — bony vs membranous canals, left vs right organs, pre vs post treatment — the data acquisition direction may be inconsistent between members of the pair. One structure's points may be collected from ampulla → common crus while the paired structure goes common crus → ampulla.

This causes the fitted curve parameters (especially phase φ, which determines start/end position) to diverge between the two members, making them look anatomically misaligned even when the underlying geometry is the same.

## Detection

Compare first/last points of paired datasets:

```python
def check_direction(bony_pts, memb_pts, threshold_mm=3.0):
    """Check if membranous data direction is reversed relative to bony"""
    b_first, b_last = bony_pts[0], bony_pts[-1]
    m_first, m_last = memb_pts[0], memb_pts[-1]
    
    # Case 1: memb start ≈ bony end AND memb end ≈ bony start (clear reversal)
    if np.linalg.norm(m_first - b_last) < threshold_mm and \
       np.linalg.norm(m_last - b_first) < threshold_mm:
        return True  # → flip memb_pts
    
    # Case 2: memb start is closer to bony end than to bony start
    d_start_to_bony_start = np.linalg.norm(m_first - b_first)
    d_start_to_bony_end = np.linalg.norm(m_first - b_last)
    if d_start_to_bony_end < d_start_to_bony_start and d_start_to_bony_end < 5.0:
        return True  # → flip memb_pts
    
    return False  # direction OK
```

## Fix

Reverse the data array when reversal is detected:

```python
flipped_pts = original_pts[::-1].copy()  # Reverse point order
```

This makes the fitted curves share a consistent angular reference, so parameters (a, φ) become directly comparable.

## Post-Fit Alignment

Even after direction alignment, the fitted curves may span different angular ranges if one member has more data points or covers more anatomical extent. Force both to the same θ range for fair comparison:

```python
# Find common theta range
theta_common = (max(b_params['theta_min'], m_params['theta_min']),
                min(b_params['theta_max'], m_params['theta_max']))

# Reconstruct both curves over the SAME range
b_curve = reconstruct_curve(b_params, theta_common)
m_curve = reconstruct_curve(m_params, theta_common)

# Now compare start/end deviations
start_dev = np.linalg.norm(b_curve[0] - m_curve[0])
end_dev = np.linalg.norm(b_curve[-1] - m_curve[-1])
```

## Impact

| Metric | Before | After |
|:-------|:------:|:-----:|
| PC bony/memb start deviation | 5.86mm | **0.63mm** |
| PC memb phase φ | -32.6° | **75.0°** |
| PC memb scale a | 4.05 | **3.84** |
| RMSE (unchanged) | 0.170mm | 0.170mm |

## When to Use This

- Bony vs membranous canal centerline fitting
- Left vs right anatomical structure comparison
- Pre vs post treatment shape analysis
- Any paired curve fitting where acquisition direction is not standardized

## Pitfalls

1. **Not all pairs are reversed** — AC and LC pairs were already consistent in our data. Always check before flipping.
2. **Different arc lengths** — After alignment, the shorter-arc member may not cover the full extent of the longer-arc member. The common theta range will be the intersection, which is shorter than either alone.
3. **The RMSE doesn't change** — Flipping data direction doesn't change fit quality (the algorithm sorts by θ anyway), only parameter representation.
