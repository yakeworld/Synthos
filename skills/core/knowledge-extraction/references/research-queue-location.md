# Research Queue Location & Structure

> The autonomous-core-researcher pipeline's candidate queue.

## File Location

```
<synthos_root>/outputs/papers/_knowledge_only/research-queue.json
```

Not at the project root, not at `outputs/papers/`. The queue lives alongside the knowledge entries it tracks.

## Structure

```json
{
  "total_candidates": 20,
  "total_pending": 1,
  "total_completed": 19,
  "completed_candidates": [...],
  "queue": [
    {
      "id": "candidate-name-PINN",
      "status": "in_progress",
      "current_step": "gap_analysis",
      "steps_completed": ["literature_scan"],
      "literature_scan_score": 21,
      "feasibility": 4,
      "gap_analysis_score": 0.85,
      "gate_status": "PASS",
      "last_updated": "2026-06-22T23:30:00Z"
    }
  ],
  "next_candidate": "candidate-name-PINN",
  "next_step": "hypothesis_generation",
  "last_updated": "2026-06-22T23:30:00Z"
}
```

## Pipeline Steps (4-step flow)

```
literature_scan → gap_analysis → hypothesis_generation → knowledge_entry
```

Each cron run advances ONE step for ONE candidate.

## State Consistency Rules

### Rule 1: Both files must be updated each run
Every cron run must update BOTH:
- `_knowledge_only/<candidate-id>/state.json` (candidate-level)
- `_knowledge_only/research-queue.json` (queue-level)

### Rule 2: Metadata counters
- `total_candidates` = `total_completed` + `total_pending`
- `total_pending` = count of candidates with `status: "in_progress"`
- `total_completed` = count of candidates with `status: "completed"`
- If a candidate has `steps_completed` but `status: "in_progress"`, it counts as pending

### Rule 3: Step transition
When advancing a step, update ALL of:
1. `current_step` → new step name
2. `steps_completed` → append new step
3. Score field for just-completed step (e.g., `gap_analysis_score: 0.85`)
4. `gate_status` → new gate status (PENDING→CONDITIONAL→PASS)
5. `last_updated` → current timestamp
6. `next_step` in queue metadata → new next step
7. `notes` → summary of what this cycle produced

### Rule 4: Stale state detection
Stale states (parent queue vs candidate state.json divergence) are documented in `v32-multi-direction-scan/references/stale-state-variants.md`.

### Rule 5: Queue exhaustion
When `total_pending == 0`, all candidates completed all 4 steps. Next: new v32 rotation scan or Track A submission preparation.
