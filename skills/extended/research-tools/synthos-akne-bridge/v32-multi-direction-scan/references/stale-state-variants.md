# Research Queue Stale State Variants

> Consolidation of all known staleness patterns in the dual-queue tracking system.
> When the parent `outputs/papers/research-queue.json` and candidate `_knowledge_only/<id>/state.json` diverge.

## Variant Registry

| Variant | First Seen | Severity | Pattern | Detection | Fix |
|:--------|:----------:|:--------:|:--------|:----------|:----|
| **v1: Candidate stale** | v101 (2026-06-18) | 1 step | Parent shows completed but candidate shows in_progress (parent was updated by one cron run but the candidate's own state.json wasn't) | Compare candidate status vs parent status | Overwrite candidate state.json from parent |
| **v2: Parent stale (1 step)** | v133 (2026-06-21) | 1 step | Parent shows in_progress (3/4 steps) but candidate shows completed (4/4 steps) — inverse of v1 | Compare parent's `steps_completed` length vs candidate | Overwrite parent entry from candidate state.json |
| **v3: Parent stale (2+ steps)** | v167 (2026-06-22) | 2+ steps | Parent shows in_progress at `hypothesis_generation` (2/4 steps) but candidate completed (4/4 steps) — multiple cron runs failed to sync parent | Compare parent's `current_step` vs candidate's `status` + last_updated timestamp. If parent is >1 step stale, check ALL other candidates for similar drift | Overwrite entire parent candidate entry from authoritative candidate state.json |

## Detection Flow

```python
def check_staleness(parent, candidate):
    """Check if parent queue file is stale relative to candidate state."""
    # v1: Candidate stale
    if parent.get('status') == 'completed' and candidate.get('status') == 'in_progress':
        return 'candidate_stale'
    # v2: Parent stale (1 step)
    if candidate.get('status') == 'completed' and parent.get('status') == 'in_progress':
        p_steps = len(parent.get('steps_completed', []))
        c_steps = len(candidate.get('steps_completed', []))
        if c_steps - p_steps == 1:
            return 'parent_stale_1step'
        elif c_steps - p_steps >= 2:
            return 'parent_stale_2step'
    return 'in_sync'
```

## Prevention

- Every cron run should update BOTH the candidate's `_knowledge_only/<id>/state.json` AND the parent `outputs/papers/research-queue.json` simultaneously
- When initializing a new candidate, create both files in the same step
- When the parent queue reports empty but there should be a next candidate, first verify all candidate state.json files are up to date before assuming queue exhaustion
