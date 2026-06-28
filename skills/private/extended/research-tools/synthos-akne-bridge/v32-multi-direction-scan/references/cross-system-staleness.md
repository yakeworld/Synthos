# Cross-System State Staleness

## Pattern: evolution-state.json vs Knowledge Pipeline

The evolution engine (`evolution-state.json`) and the knowledge pipeline (`research-queue.json` + per-candidate `state.json`) are **independent systems** that can become severely desynchronized.

### 2026-06-22 Finding

| System | cycle | Last Updated |
|:-------|:-----:|:------------|
| `evolution-state.json` | cycle 64 | 2026-06-05 |
| `research-queue.json` | cycle 170 | 2026-06-22 |
| Per-candidate state.json | cycle 170 | 2026-06-22 |

The evolution engine stopped updating when the knowledge pipeline began autonomous expansion. evolution-state.json still shows:
- `status: healthy`, `grade: EXCELLENT`, `overall_score: 0.98` (stale)
- No `knowledge_pipeline` or `paper_submission` fields (these were added to the spec after cycle 64)
- No awareness of the 7 domain expansions (105+ pipeline cycles) completed since June 5

### Root Cause

The knowledge pipeline cron runs execute `knowledge-acquisition` → `knowledge-extraction` pipeline steps. They update `research-queue.json` and per-candidate `state.json`, but do NOT update `evolution-state.json`. Conversely, the evolution engine cron runs (DIAGNOSE → OPTIMIZE → VERIFY → CRYSTALLIZE) have their own cycle counter and never read the knowledge pipeline's state.

### Detection

Check `evolution-state.json`'s `cycle` field vs `research-queue.json`'s `last_updated`:
```bash
python3 -c "import json; ev=json.load(open('outputs/evolution/evolution-state.json')); rq=json.load(open('outputs/papers/_knowledge_only/research-queue.json')); print(f'Evolution cycle: {ev[\"cycle\"]} ({ev.get(\"last_updated\",\"?\")}), Queue cycle: {rq.get(\"last_updated\",\"?\")}')"
```

If the dates differ by more than 24h, the evolution-state is stale.

### Remedy

Run the evolution engine's DIAGNOSE step with an explicit knowledge_pipeline override:
```python
# evolution-state.json needs knowledge_pipeline field populated:
knowledge_pipeline = {
  "current_step": "completed",
  "completed": 20,
  "total": 20,
  "knowledge_score": 0.86,
  "last_entry": "respiratory-mechanics-PINN",
  "completed_at": "2026-06-22T23:59:00Z",
  "next_actions": ["domain-expansion-8-bronchomotor-tone", "track-a-binaural-vestibular-PINN"]
}
```
Then re-run BENCHMARK with the corrected state.
