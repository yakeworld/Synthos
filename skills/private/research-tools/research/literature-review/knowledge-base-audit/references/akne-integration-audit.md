# AKNE Integration Audit — 2026-06-10

## Scope
Audit of AKNE knowledge graph integrity, Synthos↔AKNE bridge health, and query engine functionality.

## Audit Results

### Graph Integrity
- Total nodes: 1,475
- Total edges: 6,130 (5,868 indexed in _edges_by_type)
- Node types: synthos_paper(148), synthos_skill(25), synthos_misc(7), source(1145), source_category(24), entity(126)
- Edge types: references(137), paper_concept(335), concept_paper(281), paper_source_domain(285), skill_source_domain(42), skill_concept(18), source_co_occurrence(1970), source_category_membership(1145), source_category(1145), domain_overlap(252), paper_source_match(10), paper_category(255)
- All relations load correctly after fix (link_type → relation mapping)

### Synthos Paper Connection
- 148/148 synthos papers connected (0 isolated)
- Paper→Domain edges: 285 total across BPPV(24), ODE/PINN(0 direct), 眼动研究(31), 半规管(25), 投稿(36), 科研(89), 编程(80)
- Paper→Concept edges: 335 total
- Top concepts: 科研课题研究(67 papers), 模型依赖实在论(67), 前庭解剖(39), 虚拟仿真研究(23)

### Synthos Skill Connection
- 25/25 synthos skills connected (0 isolated)
- Skill→Concept edges: 18 (average 0.72 per skill)
- Skill→SourceDomain edges: 42 (average 1.68 per skill)
- **Assessment**: Skills are sparsely connected to concepts. Most skills have 0-2 concept connections.

### Query Engine Health
- Before fix: 0% queries returning results (complete failure)
- After fix: 100% core queries returning results (12/12)
- Traversal depth: 2 (BFS from resolved entity)
- Deduplication: by entity_name (case-insensitive), then content overlap
- Wiki fallback: active for graph results with wiki pages
- Cache: enabled with MD5 hash, TTL-based invalidation

### Known Issues (Fixed)
1. networkx 3.x out_edges() 4-tuple unpacking → fixed (4 variables)
2. _edges_by_type key mismatch (tuple vs string) → fixed (iterate items)
3. BFS over-traversal → fixed (use graph.successors)
4. relation vs link_type field name → fixed (read both)
5. Leaf node zero results → fixed (substring fallback)
6. resolve_entity threshold → fixed (multi-strategy, lower thresholds)

### Recommendations
1. **Skill connectivity**: Increase skill→concept edges. Currently 18 total for 25 skills. Target: 2-3 concepts per skill.
2. **BFS depth cap**: Depth 2 traversal from a node with 100 outgoing edges can produce hundreds of results. Consider capping at depth 1 for broad queries, depth 2 only for specific entity exploration.
3. **Node name consistency**: Some nodes have long paths (`.knowledge/sources/...`) while others are short (`bppv`). Consider normalizing node naming for better resolve_entity performance.
4. **Vector store**: Currently None — semantic search is disabled. Consider populating with document embeddings for queries that don't have graph-resolved entities.
