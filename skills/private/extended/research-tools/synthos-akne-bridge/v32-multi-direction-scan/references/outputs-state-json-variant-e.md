# Variant E: outputs/state.json research_scan Multi-Step Lag

**Discovered**: cycle-173 (2026-06-22), chest-wall-mechanics-PINN

## Pattern

`outputs/state.json` → `research_scan` field lags behind the actual candidate pipeline state by TWO or more steps, while all other state files (`_knowledge_only/<id>/state.json`, `_knowledge_only/research-queue.json`) are current.

## Detection

Before starting any work, check:
```
outputs/state.json.research_scan.step
  vs
_knowledge_only/<candidate>/state.json.current_step
```

If `outputs/state.json` step is >1 step behind the candidate's own state.json, it's stale.

## Fix

Sync `step`, `gate`, `verdict`, and `completed_at` from the most recent completed step. Example (cycle-173 fix):

```json
// In outputs/state.json research_scan:
{
  "step": "hypothesis_generation",   // was: "literature_scan"
  "score": 21,
  "score_max": 21,
  "gate": "CONDITIONAL",             // was: "PENDING"
  "verdict": "Cycle 172: ...Next: hypothesis_generation.",  // updated
  "completed_at": "2026-06-22T23:00:00Z"  // updated
}
```

## Root Cause

A prior cron run updated `_knowledge_only/research-queue.json` and the candidate's own `state.json` but **skipped `outputs/state.json` entirely**. Unlike the per-candidate state.json (updated per-step by whoever runs the step) and the research-queue.json (updated by specific sync actions), `outputs/state.json` has no automatic ground truth — it only moves when a cron run explicitly patches it. If three consecutive cron runs all forget to patch it, it stays frozen at the step from the LAST run that remembered.

## Distinction from Other Staleness Variants

| Variant | Stale File | Ground Truth | Scope |
|:--------|:-----------|:-------------|:------|
| A | candidate state.json | output files on disk | per-candidate |
| B | parent research-queue.json | candidate's own state.json | per-candidate in parent queue |
| C | candidate state.json (inverse) | output files on disk | per-candidate |
| D | missing `_knowledge_only/<id>/` | outputs/state.json + agent-log | infrastructure |
| **E (NEW)** | **outputs/state.json** | **candidate's own state.json** | **top-level only** |

## Prevention

Every pipeline step's sync checklist must include `outputs/state.json` as an explicit target. The sync target order should be:

1. Step output file (e.g., `step_hypothesis_generation.md`)
2. Candidate's own `state.json`
3. `_knowledge_only/research-queue.json`
4. `outputs/papers/research-queue.json` (parent queue)
5. **`outputs/state.json` ← easily forgotten**
6. `evolution-state.json`
7. `outputs/papers/agent-log.md`
