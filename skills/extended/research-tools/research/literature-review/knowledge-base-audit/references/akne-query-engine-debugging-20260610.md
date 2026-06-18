# AKNE Query Engine Debugging — 2026-06-10 Session

## Session Context
User asked to fix a broken AKNE query engine. The entire query pipeline (graph→vector→wiki) returned 0 results for all queries despite 1,475 nodes and 6,130 edges in the knowledge graph.

## Bugs Found & Fixed

### Bug 1: networkx 3.x `out_edges()` returns 4-tuple, not 3
**File**: `akne/graph/graph_index.py` line 577
**Symptom**: `ValueError: too many values to unpack (expected 3)`
**Root cause**: `MultiDiGraph.out_edges(start_node, data=True, keys=True)` returns `(u, v, key, data)` — four values. Code unpacked `(neighbor, key, data)` — three values.
**Fix**: `_u, neighbor, _edge_key, data` (4 variables)

### Bug 2: `_edges_by_type` key lookup always fails
**File**: `akne/graph/graph_index.py` line 579
**Symptom**: All `traverse()` results empty even when edges exist
**Root cause**: Code did `if key not in self._edges_by_type:` where `key = (source, target)`. But `_edges_by_type` is `dict[relation_name, list[(source,target)]]` — relation names are strings, not tuples. Tuples never appear as dict keys.
**Fix**: Iterate `for rel_name, pairs in self._edges_by_type.items():` then check `if (source, target) in pairs:`.

### Bug 3: BFS over-traversal explosion
**File**: `akne/graph/graph_index.py` BFS loop
**Symptom**: `traverse("bppv")` returns 685 results (all duplicates) from a node with only 5 outgoing edges
**Root cause**: BFS iterated ALL relation groups for every node, checking every pair against every node. For a node with 200 outgoing edges across 13 relation groups, this is 200×13 checks per node.
**Fix**: Use `self.graph.successors(node)` to iterate only the node's actual outgoing edges, not all relation groups.

### Bug 4: `relation` field is empty in loaded graph
**File**: `akne/graph/graph_index.py` line 520
**Symptom**: `_edges_by_type` has only one entry `""` (empty string) for all 5,868 edges
**Root cause**: JSON stores edge relationship names in `link_type` field, but code reads `edge_data.get("relation", "")`. The `relation` field is always empty string in the JSON.
**Fix**: Read both: `edge_data.get("relation", edge_data.get("link_type", ""))`

### Bug 5: Leaf nodes return zero query results
**File**: `akne/reason/query_engine.py` `_graph_search`
**Symptom**: `query("眼震")` returns 0 results even though nodes containing "眼震" exist
**Root cause**: `resolve_entity("眼震")` finds `sources/BPPV/Dix-Hallpike试验眼震分析` which is a valid graph node, but it has NO outgoing edges (it's a leaf/source node). `traverse()` returns empty. The query chain fails entirely.
**Fix**: After `traverse()` returns 0 with a resolved entity, fall back to substring search across all node names: find nodes whose name contains the original query text.

### Bug 6: `resolve_entity` threshold too high, wrong node prioritization
**Symptom**: `query("ODE")` returns `cuteye-model` (a programming file, not a research node). `query("虹膜")` and `query("眼动")` return 0.
**Root cause**: Single SequenceMatcher at 0.5 threshold; no substring matching; no token overlap; no prioritization of `sources/` and `concepts/` nodes.
**Fix**: Multi-strategy resolution: exact match → substring (0.7+) → token Jaccard (0.3-0.7) → SequenceMatcher (penalized for long names). Lower thresholds for short queries: ≤3 chars → 0.35, ≤5 chars → 0.4, >5 → 0.5.

## Verification Results (Post-fix)

| Query | Before | After |
|-------|--------|-------|
| BPPV | 0 (all empty) | 5 results ✓ |
| 半规管 | 0 | 4 results ✓ |
| 前庭解剖 | 0 | 4 results ✓ |
| 耳石 | 0 | 5 results ✓ |
| Dix-Hallpike | 0 | 4 results ✓ |
| 眼震 | 0 | 1 result ✓ (via substring fallback) |
| 眼动 | 0 | 5 results ✓ |
| 虹膜 | 0 | 3 results ✓ |
| 复位 | 0 | 5 results ✓ |
| 科研 | 0 | 3 results ✓ |
| BPPV诊断 | 0 | 5 results ✓ |
| 耳石复位 | 0 | 5 results ✓ |

**Success rate**: 0% → 100% (12/12 core queries working)

## Key Architecture Notes

- AKNE graph structure: 1,475 nodes, 6,130 edges, 13 relation types
- The graph uses `networkx.MultiDiGraph` — all edge queries must account for 4-tuple unpacking
- Entity resolution is the weakest link in the query chain — it determines whether the graph path is even entered
- When `traverse()` returns empty for a resolved entity, always fall back to substring search across all node names
