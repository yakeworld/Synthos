# Pipeline Short-Circuit Logic (Synthos v4.0+)

## When Short-Circuit Triggers

The pipeline stops executing the remaining atom chain when:

| Trigger | Condition | CallGraph `triggered_by` |
|---------|-----------|--------------------------|
| `empty_result` | Atom 1 returns `raw_papers: []` (0 papers across all sources) | `"empty_result"` |
| `error` | Any mechanical atom throws an exception | `"error"` |

## What Happens

1. Pipeline sets `short_circuited = True`
2. Remaining atoms in `atom_chain` are iterated but **not executed**
3. Each skipped atom is recorded in CallGraph with:
   - `invoked: false`
   - `skipped: true`
   - `skip_reason: "short_circuit: upstream empty result"`
4. CallGraph records `short_circuit` metadata:
   ```json
   {
     "short_circuit": {
       "at_atom": "knowledge-acquisition",
       "reason": "Search returned zero papers across all sources",
       "triggered_by": "empty_result",
       "executed_count": 1,
       "skipped_count": 5
     }
   }
   ```
5. Pipeline status becomes `"short_circuited"` (distinct from `"ok"` / `"error"` / `"needs_agent"`)
6. Empty result evidence saved to `empty_result_evidence.json` (databases queried, query string, timestamp, synonym expansion)

## Constitution Compliance

- **P2.2**: Short-circuit is pipeline logic, NOT atom logic. Atoms don't know about short-circuiting.
- **P0.3**: Zero results is structured evidence (`empty_result_evidence.json`), not "no data"
- **P0.2**: Short-circuit decision recorded in CallGraph with full rationale

## CLI Output Example

```
$ python3 run_pipeline.py run 'xyznonexistentquery'
Run ID:    20260510_004530
Status:    short_circuited
Complexity: medium
Chain:     knowledge-acquisition → knowledge-extraction → association-discovery

⚠ Short-circuit at: knowledge-acquisition
  Reason: Search returned zero papers across all sources
  Triggered by: empty_result
  Executed: 1, Skipped: 2
```

## Implementation Location

`core/atom_pipeline.py` — Pipeline.run() method, inside the atom execution loop:

```python
short_circuited = False
for atom_name in atom_chain:
    if short_circuited:
        # Mark as skipped in CallGraph
        ctx.record_atom_execution(...)
        ctx.call_graph.nodes[-1].invoked = False
        ctx.call_graph.nodes[-1].skipped = True
        ctx.call_graph.nodes[-1].skip_reason = "short_circuit: upstream empty result"
        continue
    # ... normal execution ...
    if atom_name == "knowledge-acquisition" and not papers:
        short_circuited = True
        ctx.call_graph.record_short_circuit(
            at_atom="knowledge-acquisition",
            reason="Search returned zero papers across all sources",
            triggered_by="empty_result",
        )
```
