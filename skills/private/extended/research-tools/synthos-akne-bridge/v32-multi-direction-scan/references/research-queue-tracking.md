# Research Queue Tracking — Where Candidates Actually Live

## The Queue Lives in a File (Now)

Despite earlier cleanup, the pipeline has migrated back to a concrete queue file. The queue is tracked across five locations — but `research-queue.json` is authoritative:

| Location | What It Tracks | Example |
|:---------|:--------------|:--------|
| **`_knowledge_only/research-queue.json`** | **Authoritative candidate registry** | `total_candidates=2, total_pending=1, total_completed=1` |
| `outputs/state.json` → `research_scan` | Actively-processing candidate + current step | `OKR-adaptation-PINN: step=literature_scan, score=0.84, gate=PENDING` |
| `outputs/papers/_knowledge_only/<id>/` | Per-candidate files + state.json | `OKR-adaptation-PINN/state.json` has steps_completed, scores |
| `paper-queue.json` | Track A papers (elevated from knowledge to full paper pipeline) | All completed |
| `outputs/agent-log.md` | Chronological record of every cron action | `[Cron] 2026-06-20 direction= action= result=` |

## research-queue.json Schema

The file lives at `outputs/papers/_knowledge_only/research-queue.json`. Example:

```json
{
  "version": "1.0",
  "last_updated": "2026-06-20T12:00:00Z",
  "total_candidates": 2,
  "total_completed": 1,
  "total_pending": 1,
  "candidates": [
    {
      "candidate_id": "motion-sickness-PINN",
      "paper_name": "Motion Sickness PINN: ...",
      "status": "completed",
      "current_step": "knowledge_entry",
      "knowledge_score": 0.86,
      "gate_status": "PASS",
      "verdict": "ABSOLUTE_WHITE (0 PINN/NeuralODE across 8 queries)",
      "steps_completed": ["literature_scan","gap_analysis","hypothesis_generation","knowledge_entry"],
      "last_updated": "2026-06-20T06:30:00Z"
    },
    {
      "candidate_id": "OKR-adaptation-PINN",
      "paper_name": "Optokinetic Response Adaptation PINN: ...",
      "status": "in_progress",
      "current_step": "literature_scan",
      "knowledge_score": 0.84,
      "gate_status": "PENDING",
      "verdict": "ABSOLUTE_WHITE (10 queries, 0 PINN/ODE competitors)",
      "steps_completed": ["literature_scan"],
      "last_updated": "2026-06-20T12:00:00Z"
    }
  ]
}
```

**Key fields**: `total_pending` > 0 means queue is not empty. Check `candidates[i].status` for `in_progress` to find the active one. Do not re-scan candidates whose `status == "completed"`.

## _knowledge_only/ Directory Structure

Each candidate gets its own directory with the 4-step pipeline files:

```
outputs/papers/_knowledge_only/<candidate_id>/
├── state.json                    # Candidate state (status, steps, scores, gate)
├── step_literature_scan.md       # Step 1 output
├── step_gap_analysis.md          # Step 2 output
├── 01-gap_analysis/              # Supporting files for gap analysis
├── step_hypothesis_generation.md # Step 3 output
└── knowledge_entry_<id>.md       # Step 4 output (final)
```

## state.json Schema (per candidate)

```json
{
  "candidate_id": "motion-sickness-PINN",
  "status": "in_progress | completed",
  "current_step": "literature_scan | gap_analysis | hypothesis_generation | knowledge_entry",
  "steps_completed": ["literature_scan", "gap_analysis", ...],
  "knowledge_score": 0.86,
  "gate_status": "PENDING | PASS",
  "last_updated": "2026-06-20T06:30:00Z",
  "scan_results": {
    "pubmed_pinn": 0,
    "pubmed_neuralode": 0,
    "verdict": "ABSOLUTE_WHITE"
  },
  "gap_analysis_score": 0.84,
  "hypothesis_generation_score": 0.85,
  "knowledge_entry_score": 0.88,
  "knowledge_score_6d": 0.86,
  "next_step": null
}
```

## outputs/state.json → research_scan Structure

```json
{
  "paper_library_scan": { ... },
  "research_scan": {
    "scan_date": "2026-06-20",
    "type": "knowledge_pipeline",
    "candidate": "motion-sickness-PINN",
    "step": "knowledge_entry",
    "score": 0.86,
    "gate": "PASS",
    "completed_at": "2026-06-20T06:30:00Z"
  }
}
```

## What Happened to research-queue.json? (Two Lives)

**First life (6/13 — 6/18)**: The file was cleaned up on 2026-06-18 (see `references/research-queue-cleanup-2026-06-18.md` in paper-pipeline). Seven stale entries were removed (all duplicates of Track A papers already in paper-queue.json). The remaining singleton (113-scleral-remodeling-ODE) was tracked via `_knowledge_only/` directory. No replacement `research-queue.json` was created at that time.

**Second life (6/20 — 6/22)**: The motion-sickness-PINN cron run on 2026-06-20 recreated `research-queue.json` at `outputs/papers/_knowledge_only/research-queue.json`. This was the **authoritative queue registry**. Future cron runs should update this file when advancing candidates. The SKILL.md's Step 6 was patched on 2026-06-20 to reflect this state.

**Third life (6/22 — present)**: By 2026-06-22, `research-queue.json` was absent from the entire filesystem (verified by `search_files` across `/media/yakeworld/sda2/Synthos` — zero hits). The cron run on 2026-06-22 (vocal-fold-phonation-PINN hypothesis_generation) used `evolution-state.json` → `knowledge_pipeline` as the fallback state source. The `current` + `current_step` fields in `knowledge_pipeline` serve as the active queue when `research-queue.json` is missing.

**Fallback protocol**: Always try `_knowledge_only/research-queue.json` first. If absent, read `evolution-state.json` → `knowledge_pipeline` for:
- `current` — active candidate ID
- `current_step` — next step to execute
- `knowledge_score` — current composite score
- `completed` — pipeline progress counter

## Cron Decision Flow

```
Start
  ├── Check outputs/state.json → research_scan
  │   ├── If candidate exists and gate=PENDING:
  │   │   └── Resume that candidate's next step
  │   └── If no candidate or gate=PASS/COMPLETED:
  │       └── Queue is empty → run v32 rotation scan
  └── Execute ONE step, update state.json + _knowledge_only/<id>/state.json
```

## History

- **2026-06-13**: Last update to `agent-tracker.json`. After this, tracking moved to `outputs/state.json`.
- **2026-06-18**: research-queue.json cleaned up. 7 stale entries removed. Tracking migrated to implicit file-based system.
- **2026-06-20 (cron #1)**: motion-sickness-PINN completed through all 4 pipeline steps. `research-queue.json` recreated at `_knowledge_only/research-queue.json` to track the candidate lifecycle explicitly.
- **2026-06-20 (cron #2, v247)**: OKR-adaptation-PINN created as second candidate. Queue now has 2 entries (1 completed, 1 in progress). v32 SKILL.md and this reference patched to reflect the new queue reality.
- **2026-06-22**: research-queue.json absent from filesystem. Cron run (Cycle 162) fell back to `evolution-state.json` → `knowledge_pipeline` for state tracking. Hypothesis generation for vocal-fold-phonation-PINN advanced via evolution-state.json. Reference patched to document the fallback protocol.
