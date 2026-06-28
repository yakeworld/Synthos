# Kanban × Synthos Integration Analysis

## Decision: Kanban ABOVE Synthos, not inside it

Kanban should operate at the **project management layer**, above the Synthos cognitive pipeline. The pipeline handles the atomic cognitive chain; Kanban handles multi-topic decomposition and parallel batch processing.

## Fit Matrix

| Scenario | Use Kanban? | Why |
|----------|:--:|------|
| Batch literature review (20+ papers) | ✅ YES | Fan-out 4 researchers × 5 papers → 1 analyst → 1 writer |
| Multi-direction parallel research | ✅ YES | 3 parallel researcher tasks, 1 synthesizer |
| Scheduled periodic monitoring | ✅ YES | Cron → Kanban task → `run_pipeline.py` |
| Single 3-paper analysis | ❌ NO | Pipeline: 6s. Kanban overhead > benefit. |
| Inside 6-atom chain | ❌ NO | Atoms 3→4→5→6 are strictly sequential. No parallelization. |
| Current single-user scale | ❌ NO | Agent direct execution is optimal. |

## Recommended Architecture

```
Kanban (Project Management Layer)
  ├── Task: "Review ADHD eye-tracking" → researcher
  │     └── Calls: run_pipeline.py 'ADHD eye-tracking review'
  ├── Task: "Review ADHD EEG methods" → researcher (parallel)
  │     └── Calls: run_pipeline.py 'ADHD EEG diagnosis'
  ├── Task: "Synthesize comparison" → analyst (waits for above)
  │     └── Reads previous task outputs
  └── Task: "Draft NSFC proposal" → writer (waits for analyst)
        └── Reads synthesis → atom5 argument generation

Synthos Pipeline (Execution Engine)
  run_pipeline.py → atoms 1→2→3→4→5→6
```

## Trigger Condition

Introduce Kanban when: user first says "do A, B, and C simultaneously" — multi-task parallel decomposition. Not before.
