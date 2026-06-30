---

name: knowledge-base-audit
io_contract: "input: kb_path: str, audit_type: str -> audit_report: dict | output: audit_report: dict, recommendations: list[str]"

description: Audit and maintain personal knowledge management systems (AKNE, NotebookLM,
author: Synthos
license: MIT
version: 1.0.0
license: MIT
  Obsidian vaults, etc.) to keep them healthy and evolving.
allowed-tools:
- terminal
- read_file
- write_file
- search_files
metadata:
  synthos:
    signature: 'kb_path: str -> audit_report: dict'
    related_skills:
    - academic-paper-completion
    - adhd-eye-tracking-review
    - arxiv
    - biorxiv
    - blogwatcher


---


## IO_CONTRACT

- **input**: `kb_path: str, audit_type: str` — 用户请求描述、上下文信息
- **output**: `audit_report: dict — 知识库审计`


> 对应原则：P2（机械原子暴露输入输出规范）


# Knowledge Base Audit & Maintenance

## 原理层·文言

> 知识如林，不修则芜。笔记如剑，不磨则钝。
> 旧知需巩固，新知需链接。冗余合之，断裂连之。
> 定期审计，持续修剪。林清则见路，知整则明理。

## When to Use
- User asks to "review", "audit", or "check" their knowledge base
- Knowledge base appears to have corruption, duplication, or inconsistencies
- User wants to keep their knowledge system "continuously evolving"
- After bulk operations that might have introduced errors (tagging, importing, syncing)
- User asks to "manage NotebookLM", "audit notebooks", or "organize NotebookLM"
- After adding/removing many sources from NotebookLM notebooks

## Core Workflow

### Phase 1: Discovery & Diagnostics
1. **Count and categorize** all files (source docs, wiki pages, generated files)
2. **Check data integrity**:
   - Are all internal links/resolutions working?
   - Are there duplicate entries or corrupted files?
   - Are generated artifacts (graphs, indexes) non-empty?
3. **Check process health**:
   - Is the auto-evolution daemon running?
   - Are scheduled tasks executing?
   - Is the CLI importable?

### Phase 2: Cleanup
4. **Remove duplicates**: Identify and deduplicate repeated tags/entries
5. **Fix broken links**: Ensure all internal references resolve
6. **Remove empty/corrupted files**: Delete placeholder files or noise
7. **Normalize formatting**: Remove excessive whitespace, fix encoding issues

### Phase 3: Population
8. **Build knowledge graph**: Extract entities and relationships from content
9. **Embed documents**: Generate vector embeddings for semantic search
10. **Create cross-references**: Link related pages/entities

### Phase 4: Persistence
11. **Ensure daemon runs**: Set up systemd service or cron job
12. **Add .gitignore**: Exclude generated files, logs, node_modules
13. **Fix imports**: Add __init__.py if needed for package structure
14. **Document health**: Create status report with score

## AKNE Graph Index Bugs & Fixes

### networkx out_edges unpacking bug (graph_index.py line 577)
`nx.MultiDiGraph.out_edges(node, data=True, keys=True)` returns **4 values**: `(u, v, key, data)`, NOT 3. Always unpack as `_u, neighbor, _edge_key, data`.

### link_type vs relation field mismatch
JSON stores relation type in `link_type`, not `relation`. When loading from graph.json, use:
```python
relation = edge_data.get("relation", edge_data.get("link_type", ""))
```
If not fixed, `_edges_by_type` will have all edges under key `""` (empty string), making all traversals fail silently.

### traverse() initial segment over-traversal
Original code iterated ALL `_edges_by_type[found_relation]` pairs for each outgoing edge from start node, causing O(n*m) blowup. Fix: use `self.graph.successors(node)` or `self.graph.out_edges()` directly — these only return actual outgoing edges.

### traverse() BFS over-traversal
Original code iterated ALL `_edges_by_type` items for each node in queue. Fix: iterate `self.graph.successors(node)` directly, then look up the relation in `_edges_by_type` by checking `(node, neighbor)` in each relation's pair list.

### resolve_entity threshold too high
Default 0.5 threshold rejects useful matches like "ODE" matching "endolymph-hydropressure-ode" (0.20 ratio). Implement 4-tier strategy:
1. Exact match → return immediately
2. Substring match (query in name or name in query) → 0.7+ ratio
3. Token overlap (Jaccard) → 0.5 combined score
4. SequenceMatcher fallback → penalize names >50 chars

Short queries (≤3 chars) need lower threshold (0.35), medium (≤5) need 0.40, long queries keep 0.50.

### Leaf node fallback in _graph_search
When `resolve_entity` finds a node but `traverse` returns 0 (leaf/no outgoing edges), add substring search: scan all node names for `text_lower in name_lower` and return best match. This captures cases where the query term exists in a filename but the resolved entity is a leaf in the graph.

### Content string format in SearchResult
Don't include raw weight in the relation field: `content = f"{seed} --[{relation_type}]--> {end_node}"` — not `f"Relation: {end_node} --[{weight}]--> {seed}"`. The relation_type should be the semantic relation name (e.g., "references", "paper_concept"), not a numeric weight.

## Known Issues & Debugging

### AKNE Graph Query Bug (2026-06-10)
- **File**: `akne/graph/graph_index.py` line 577
- **Symptom**: `query("BPPV")` returns 0 results despite 1,475 nodes
- **Root cause**: `MultiDiGraph.out_edges(data=True, keys=True)` returns `(neighbor, key, data)` in networkx 3.x, but code unpacks 2 values
- **Fix**: Change to `for neighbor, key, data in self.graph.out_edges(start_node, data=True, keys=True):`
- **Impact**: All graph traversal queries fail silently; query chain (vector→graph→wiki) all return empty
- **See**: `references/akne-integration-audit.md` for full integration audit and fix priorities

## NotebookLM Audit Workflow

For environments with 10-100+ NotebookLM notebooks, use this structured audit workflow:

### Step 1: Full Inventory with `--json`
```bash
notebooklm list --json
```
Parse the JSON to get all notebook IDs, titles, ownership, and creation dates.

### Step 2: Topic Categorization
Create a keyword-based category mapping. Common medical research categories:
- ADHD/眼动追踪: ["ADHD", "眼动", "eye tracking", "eyetracking", "注视", "扫视"]
- 前庭/VOR/BPPV: ["VOR", "前庭", "BPPV", "眩晕", "耳石", "vestibular"]
- 眼科/虹膜/3D眼球: ["眼", "虹膜", "iris", "瞳孔", "pupil", "角膜", "眼球", "ocul"]
- AI/ML/编程: ["AI", "ML", "机器学习", "深度", "神经网", "OpenCode", "智能体", "agent"]
- NSFC/基金/项目申报: ["NSFC", "国自然", "基金", "标书", "申报", "英才计划"]
- 教学/课程: ["教学", "课程", "教案", "培养", "AIGC", "通识"]
- 科研方法论/论文写作: ["CRISP", "TRIPOD", "论文写作", "科研设计"]
- 医院管理/报告: ["医院", "报告", "奖励", "创新门诊", "绩效"]

Iterate through notebooks, matching titles to categories. Unmatched notebooks go to "其他".

### Step 3: Source Quality Assessment
For key notebooks, check source counts and types:
```bash
notebooklm use <partial_id>
notebooklm source list
```
Key metrics:
- **Source count**: Rich (30+ PDF/MD) vs Thin (1-5 sources)
- **Source types**: PDF (full text), Markdown (summaries), Pasted Text (fragments)
- **Freshness**: Preferred dates within last 1-2 years
- **Status**: All "ready" is good; stale sources need refresh

### Step 4: Gap Identification
Compare notebooks against each other:
- Notebooks with only 1-2 sources → needs expansion
- Duplicate notebooks (same title) → suggest merge
- Chronological gaps → need newer sources
- Cross-topic gaps (e.g., ADHD notebook lacking VOR literature despite the NSFC focus on 3D eye tracking + VOR)

### Step 5: Prioritized Action Plan
| Priority | Action | Criteria |
|----------|--------|----------|
| P0 (immediate) | Add critical missing sources | ≤2 sources in core project notebooks |
| P1 (pre-deadline) | Rename non-standard source titles | PDFs named "201806596.pdf" or with number prefixes |
| P2 (maintenance) | Cross-link related notebooks, classify 其他 | >10 notebooks in "其他", duplicate notebooks |

### Step 6: Execute Source Operations
- **Add sources**: `notebooklm source add <file_path>`
- **Rename sources** (using 12-char UUID prefix for reliability): `echo "y" | notebooklm source rename "uuid_prefix_12chars" "NewTitle"`
- **Delete duplicate sources**: `echo "y" | notebooklm source delete "uuid_prefix_12chars"`
### NotebookLM Auth Troubleshooting (2026-06-30)

**Problem**: `notebooklm list` returns "Not authenticated. Run notebooklm login first." despite having `~/.notebooklm/profiles/<name>/storage_state.json` with 148 cookies.

**Diagnosis flow**:
1. Check `cat ~/.notebooklm/profiles/<name>/context.json` — should have `notebook_id`, `is_owner: true`
2. Check storage state: `cat ~/.notebooklm/profiles/<name>/storage_state.json | python3 -c "import json,sys; d=json.load(sys.stdin); print('Keys:', list(d.keys()), 'Cookies:', len(d.get('cookies',[])))"`
3. If cookies > 0 and has Google domains → auth data exists but CLI isn't reading it

**Key findings**:
- The CLI looks for `NOTEBOOKLM_STORAGE_STATE` env variable or `~/.notebooklm/storage-state.json` (not the per-profile path)
- `--storage-state` and `-s` are NOT valid CLI options
- `export PLAYWRIGHT_STORAGE_STATE=~/.notebooklm/profiles/<name>/storage_state.json` did NOT fix it
- Direct node invocation: `node /path/to/notebooklm/dist/cli/index.js list` also reads from default path
- The auth system is built into the CLI and requires the default storage path, not custom paths

**Resolution**: The only reliable path is to `notebooklm login` via browser (or `--headless` which may fail with Google OAuth). Profile switching is not natively supported.

### Cannot merge notebooks or move sources between them

There is no `notebooklm source move` command. Sources are per-notebook. To "split" a notebook:

1. **Create** new notebooks with focused themes: `notebooklm create "Focused Notebook Title"`
2. **Rename** the original to "Archive - OriginalName" to preserve it: `notebooklm rename -n OLD_ID "Archive - OriginalName"`
3. **Populate** the new notebooks with **fresh** literature via Synthos ACQ (search Semantic Scholar/OpenAlex for the focused topic, create a markdown summary, add as source)
4. **Do NOT attempt** to re-add old sources to new notebooks — they're Pasted Text fragments with no extractable file

The "split" is conceptual: the old notebook becomes an archive, the new notebooks start fresh with targeted literature.

### Cross-Notebook Linking Pattern

NotebookLM doesn't support cross-notebook links natively. To create conceptual connections:

1. **Create a mapping document** as a markdown file that explains the relationship between notebooks
2. **Add the mapping document to BOTH notebooks** as a source
3. The document should explain: what concept maps to what, why they're related, and what questions they answer together

Example (智医天问→超级个体 mapping):
```
智医天问 concept    →    Super Individual equivalent
碳硅共生哲学         →    方法论基础
半人马协作模式       →    T型能力模型
认知负荷危机        →    自动化流水线
```

### Knowledge Enrichment via ACQ
Use Synthos knowledge-acquisition to automatically source new papers:
```bash
curl -s 'https://api.openalex.org/works?search=KEYWORDS&filter=from_publication_date:2025-01-01&per_page=5&sort=cited_by_count:desc'
```
Create a summary markdown file with the top findings, then add to the relevant notebook:
```bash
notebooklm source add /tmp/new_papers_summary.md
```

### Output Template
See `references/notebooklm-audit-template.md` for the full audit report format.
The report should be saved to a **private** directory (e.g. `~/notebooklm-audit/`), NOT in the project's `docs/` directory.

## Common Issues Found in Real Systems

### Pitfall: `networkx.MultiDiGraph.out_edges()` returns 4-tuple in 3.x
`graph.out_edges(start_node, data=True, keys=True)` on a `MultiDiGraph` returns
`(u, v, key, data)` — **four values**, not three. Code that unpacks as
`(neighbor, key, data)` or `(neighbor, data)` will crash with
`ValueError: too many values to unpack`.

**Fix**: Always unpack as `_u, neighbor, _edge_key, data`. The `u` (start node)
is always included even for `out_edges`.

### Pitfall: `_edges_by_type` key mismatch in `traverse()`
`self._edges_by_type` is indexed by **relation name** (string like `"paper_concept"`),
with values being **lists of `(source, target)` tuples**. A `traverse()` implementation
that does `if key not in self._edges_by_type:` where `key = (source, target)` will
always find the key missing — tuples are never dict keys in this structure.

**Correct approach**: Iterate `for rel_name, pairs in self._edges_by_type.items():`
and check `if (source, target) in pairs:`.

### Pitfall: `relation` vs `link_type` field naming
AKNE graph JSON uses `link_type` for edge relationship names but `relation` for the
edge data attribute in `MultiDiGraph`. Loading code that reads
`edge_data.get("relation", "")` will get empty strings when the JSON uses
`link_type`. Fix: read both `edge_data.get("relation", edge_data.get("link_type", ""))`.

### Pitfall: BFS over-traversal explosion
`traverse()` BFS loop that iterates ALL relation groups for every node at every
depth can produce hundreds/thousands of results from a single query. Apply
`seen` set deduplication at the BFS level and cap output.

### Pitfall: `resolve_entity` threshold too high for fuzzy queries
`resolve_entity` uses `difflib.SequenceMatcher` with a **0.5 threshold**. Queries
like "ODE" or "PINN" that don't exactly match a node name (node names are things
like `endolymph-hydropressure-ode`) will fail to resolve, causing the query to
fall through with zero results. Consider queries against actual node names or
Use lower thresholds for short queries (≤3 chars → 0.35, ≤5 chars → 0.4, >5 → 0.5).

### Pitfall: Leaf node (no outgoing edges) returns zero query results
When `resolve_entity` finds a valid node but `traverse()` returns empty (node has
no outgoing edges), the entire query chain returns zero results. This is common for
leaf nodes like `sources/BPPV/Dix-Hallpike试验眼震分析` which exist in the graph
as sources but have no outgoing relationships.

**Fix**: After `traverse()` returns 0 with a resolved entity, fall back to substring
search across all node names: find nodes whose name contains the original query text.
This catches the user's intent even when the resolved entity is a graph leaf.

### Pitfall: `resolve_entity` picks wrong nodes for abstract terms
Short abstract terms (ODE, PINN, VOR) may resolve to unrelated nodes with those
strings in their names (e.g., `cuteye-model` for "ODE", a programming file, not a
research node). The fix is to prioritize `sources/` and `concepts/` nodes over
`.knowledge/sources/` paths when both match.

## Skill Reference Files

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引


## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态


## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。



# Knowledge Base Audit

