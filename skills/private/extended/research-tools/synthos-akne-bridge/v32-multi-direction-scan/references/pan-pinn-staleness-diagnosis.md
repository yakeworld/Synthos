# PAN-PINN State.json Staleness — Cycle 112 Diagnosis

## Symptoms

When cycle 112 loaded PAN-PINN from the parent `research-queue.json`:
- `next_candidate: PAN-PINN`, `next_step: knowledge_entry`
- `status: in_progress`, `steps_completed: [literature_scan, gap_analysis, hypothesis_generation]`

Checking candidate's own `state.json` at `_knowledge_only/PAN-PINN/state.json`:
- `status: in_progress`, `current_step: hypothesis_generation`
- `steps_completed: [literature_scan, gap_analysis, hypothesis_generation]`
- **knowledge_entry NOT in steps_completed, current_step NOT advanced**

But `knowledge_entry_PAN-PINN.md` (290 lines, comprehensive, score 0.90) already existed on disk, and `evolution-state.json` showed cycle 111 with `knowledge_pipeline.completed: 5`.

## Root Cause

The previous cron run (cycle 111) **wrote the knowledge_entry file** and **updated evolution-state.json**, but **skipped updating PAN-PINN's own state.json**. This is a sync gap distinct from the parent-queue staleness already documented in the v32 skill:

| Staleness Variant | What's Correct | What's Stale | Detection Method |
|:------------------|:---------------|:-------------|:-----------------|
| **Variant A** (v39, parent queue) | Candidate's state.json | Parent research-queue.json | `research-queue.json[next].steps_completed.length < _knowledge_only/<id>/state.json.steps_completed.length` |
| **Variant B** (v39, evolution-state) | Paper's paper-queue.json entry | evolution-state.json quality score | Check paper-queue JSON entry before trusting evolution-state |
| **Variant C** (v112, candidate's own state) | Output file on disk (`knowledge_entry_*.md`) | Candidate's own state.json | File exists on disk but state.json not updated |
| **Variant D** (new, cycle-123, 2026-06-22) | Parent state.json + agent-log.md | Entire `_knowledge_only/<candidate_id>/` directory | `os.path.isdir(kb_dir)` returns False for candidate in state.json |

## Detection Protocol (for Variant C)

After Step 6's staleness cross-check (Variant A detection), ALSO check:

```python
For each candidate where next_step is defined:
  1. Read candidate's _knowledge_only/<id>/state.json
  2. Compute expected_step = pipeline[steps_completed.length]  (pipeline = [literature_scan, gap_analysis, hypothesis_generation, knowledge_entry])
  3. If expected_step differs from state.json's current_step -> drift detected, advance
  4. If expected_step would be "knowledge_entry" -> check if knowledge_entry_<id>.md exists on disk
  5. If knowledge_entry file exists BUT state.json doesn't have it -> file-on-disk staleness (Variant C)
```

## Recovery Actions (for Variant C)

1. Write correct `state.json` for the candidate: `status: completed, current_step: knowledge_entry, steps_completed: [...4 steps]`
2. Sync parent `research-queue.json`: mark candidate completed, update next_candidate/next_step
3. Sync `_knowledge_only/research-queue.json`: same update
4. Update `evolution-state.json` if it was also stale (add `knowledge_pipeline` fields)
5. Append `agent-log.md` entry

## Variant D: No Infrastructure Created at All (New, 2026-06-22)

**Symptoms**: The `_knowledge_only/` directory is completely missing for a candidate. No `_knowledge_only/<candidate_id>/` directory, no `state.json`, no step files (`step_gap_analysis.md`, `step_hypothesis_generation.md`, etc.), no `research-queue.json` at `_knowledge_only/` level. Yet `outputs/state.json` and `outputs/agent-log.md` show the candidate has completed one or more pipeline steps.

This is distinct from Variants A-C because those all assume the `_knowledge_only/` infrastructure exists but is stale. In Variant D, the infrastructure was never created — the previous cron run updated parent state and agent-log but skipped the Step 5 requirement to create the candidate's `_knowledge_only/` directory and contents.

**Detection**: Check -- before trusting any pipeline state -- whether the candidate's `_knowledge_only/` directory actually exists on disk. If `outputs/state.json` shows `research_scan.candidate = "Foo"` and `research_scan.step = "gap_analysis"` (or later), but `os.path.isdir("outputs/papers/_knowledge_only/Foo/")` returns False, Variant D is present. Cross-check agent-log.md to verify the prior action is real (not a hallucination from a stale state.json).

**Recovery** (executed on cycle-123 for CupulaDeflection-PINN):
1. `mkdir -p _knowledge_only/<candidate_id>/`
2. Write candidate `state.json` -- reconstruct from parent `state.json` research_scan verdict
3. Reconstruct the latest step's output file (e.g. `step_gap_analysis.md`) from parent `state.json` verdict. The verdict field contains enough detail (architecture, scores, clinical conditions, proposed hypotheses) to produce a meaningful step file using the gap-analysis-template
4. If the candidate is not the only one: scan `_knowledge_only/` for existing completed candidates and create `_knowledge_only/research-queue.json` containing the full queue state
5. THEN execute the NEXT pipeline step for this candidate (infrastructure bootstrapping is prerequisite, not the pipeline step itself)
6. After the pipeline step, update ALL 6 sync targets (candidate state.json, research-queue.json, parent state.json, evolution-state.json, agent-log.md) to prevent recurrence

**Prevention**: Every cron run that updates `outputs/state.json` with a candidate's progress MUST also create/update the `_knowledge_only/<candidate_id>/` directory. The parent state.json update and the infrastructure creation are both required -- not alternatives.

## Files Updated (cycle-123)

| File | Before | After |
|:-----|:-------|:------|
| `_knowledge_only/CupulaDeflection-PINN/state.json` | DID NOT EXIST | current_step=knowledge_entry, steps=3, score=0.86 |
| `_knowledge_only/CupulaDeflection-PINN/step_gap_analysis.md` | DID NOT EXIST | Reconstructed from parent state.json verdict |
| `_knowledge_only/CupulaDeflection-PINN/step_hypothesis_generation.md` | DID NOT EXIST | Written as pipeline step output |
| `_knowledge_only/research-queue.json` | DID NOT EXIST | Pending=1, Completed=7, Next=CupulaDeflection-PINN -> knowledge_entry |
| `outputs/state.json` | step=gap_analysis, score=0.85 | step=hypothesis_generation, score=0.86 |
| `evolution-state.json` | cycle=120, no variant D awareness | cycle=123 |

## Prevention (general)

The `knowledge_entry` step in Step 5 should have an explicit sequence:

```
After writing knowledge_entry_<id>.md:
  ✓ Update <id>/state.json -> steps_completed += knowledge_entry, status=completed
  ✓ Update outputs/papers/research-queue.json -> mark candidate completed
  ✓ Update outputs/papers/_knowledge_only/research-queue.json -> same
  ✓ Update evolution-state.json -> knowledge_pipeline.completed count, last_entry, score, completed_at
  ✓ Append agent-log.md
  ✓ Update outputs/state.json research_scan field
```

If any step is skipped, the chain breaks and the next cron run pays the gap cost. Every step in the pipeline (literature_scan, gap_analysis, hypothesis_generation, knowledge_entry) should follow the same 6-target sync checklist described in the v32-multi-direction-scan SKILL.md Step 5.
