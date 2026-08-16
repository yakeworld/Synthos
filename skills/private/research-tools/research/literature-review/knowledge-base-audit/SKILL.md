---
name: knowledge-base-audit
description: '**Problem**: `notebooklm list` returns "Not authenticated. Run notebooklm login first." despite havi'
signature: 'knowledge-base-audit -> literature-review: synthetic skill for knowledge base audit'
allowed-tools:
- terminal
- read_file
- write_file
- session_search
version: 1.0.0
license: MIT
metadata:
  synthos:
    atom_type: mechanical
    description: '**Problem**: `notebooklm list` returns "Not authenticated. Run notebooklm login first." despite havi'
    signature: 'knowledge-base-audit -> literature-review: synthetic skill for knowledge base audit'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---


## IO_CONTRACT

- **input**: NotebookLM 知识库 — notebook/source 清单（list 输出）+ 各 notebook 主题与文献来源
- **input**: 认证状态 — ~/.notebooklm/profiles/ 下 context.json / storage_state.json（auth 排障输入）
- **output**: 分级审计结果 — P0 缺失核心文献 / P1 非标准命名 source / P2 notebook 分类与重复问题
- **output**: 修复操作执行结果 — source add/rename/delete（12-char UUID 前缀）、notebook 重命名归档记录

## 原则 (Principles)

> **分级而治，急者先行。** P0 核心文献缺失立即补，P1 命名非标准限期改，P2 分类与重复缓图，轻重有序。
> **库不可迁，分而新立。** NotebookLM 无跨库迁移，"拆分"实为新立主题库、旧库改名归档，不搬旧源。
> **以图代链，映射互植。** 跨笔记本关系以映射文档同时植入两库为联，无原生链接则以文档为桥。

|
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


## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[KNOW-001]** 审计发现核心文献缺失 (P0) → 立即执行 `notebooklm source add` 补充关键来源，优先保障核心项目完整性
- **[KNOW-002]** 遇到 NotebookLM 认证失败且存在本地 profile 数据 → 确认 CLI 仅读取默认路径 `~/.notebooklm/storage-state.json`，必须通过 `notebooklm login` 重新建立会话，忽略自定义 profile 路径
- **[KNOW-003]** 需要拆分或重组知识库主题 → 禁止尝试迁移旧源，应新建聚焦主题库并填充新文献，同时将旧库重命名为 "Archive - [原名]" 进行归档
- **[KNOW-004]** 需要建立跨笔记本的概念关联 → 创建映射文档 (Markdown) 解释关系，并将其作为 Source 同时添加到两个相关笔记本中以实现逻辑桥接
- **[KNOW-005]** 执行 Source 重命名或删除操作 → 使用 12 字符 UUID 前缀作为标识符，并通过 `echo "y" |` 管道自动确认，避免交互式阻塞
- **[KNOW-006]** 处理非标准命名的 PDF 来源 (P1) → 识别以数字或日期开头的文件名，限期执行重命名操作以符合标准命名规范
- **[KNOW-007]** 知识库出现大量未分类或重复笔记本 (P2) → 执行分类整理与去重，将超过阈值的 "其他" 类笔记本进行归类，删除重复项以维持库结构清晰

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

- [ ] P0 分级：核心项目 notebook 缺失的关键文献已用 `notebooklm source add` 补齐，核心库完整性已确认（KNOW-001）
- [ ] 认证排障：确认 CLI 仅读取默认路径 `~/.notebooklm/storage-state.json`，若 `list` 报 "Not authenticated" 则执行 `notebooklm login` 重建会话，而非依赖自定义 profile 路径（KNOW-002）
- [ ] 拆分操作：新建聚焦主题库后，旧库已重命名为 "Archive - [原名]" 归档，未尝试将旧源重新添加到新库（KNOW-003）
- [ ] 跨库关联：映射文档（Markdown）已创建并作为 source 同时添加到两个相关 notebook，文档含概念映射说明（KNOW-004）
- [ ] source 操作：rename/delete 均使用 12 字符 UUID 前缀标识符并以 `echo "y" |` 管道自动确认，无交互式阻塞（KNOW-005）
- [ ] P1 命名：数字/日期前缀命名的非标准 PDF 来源已识别并限期重命名为标准命名（KNOW-006）
- [ ] P2 整理："其他" 类 notebook 数量超过 10 个的已归类，重复 notebook 已删除，库结构清晰（KNOW-007）
- [ ] 审计报告已保存到私有目录（如 `~/notebooklm-audit/`），未写入项目 `docs/` 目录

## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

## Golden 集合 · GOLDEN SET

- **Golden Input**: 一个真实 NotebookLM 库状态 — `notebooklm list` 输出的 notebook/source 清单 + `~/.notebooklm/profiles/<name>/storage_state.json` 认证快照，库内含数字前缀 PDF（如 "201806596.pdf"）与 >10 个"其他"类 notebook（源: IO_CONTRACT + 分级表 P0/P1/P2）
- **Golden Output**: 分级审计报告落盘私有目录（`~/notebooklm-audit/`，非项目 docs/）— P0 缺失文献已 `notebooklm source add` 补齐、P1 非标准命名已用 12-char UUID 前缀 `echo "y" | notebooklm source rename` 重命名、P2 "其他"归类+重复删除，格式符合 `references/notebooklm-audit-template.md`（源: 验证清单 KNOW-001/005/006/007）
- **Golden Error**: `notebooklm list` 返回 "Not authenticated. Run notebooklm login first." 且 profile 目录存有 148 cookies → 诊断判定 CLI 只读默认路径 `~/.notebooklm/storage-state.json`，输出"执行 `notebooklm login` 重建会话"而非继续尝试自定义 profile 路径（源: Auth Troubleshooting 小节 + KNOW-002）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
