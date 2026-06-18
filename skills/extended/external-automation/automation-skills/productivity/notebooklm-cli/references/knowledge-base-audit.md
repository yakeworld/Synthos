---
name: knowledge-base-audit
description: Audit and maintain personal knowledge management systems (AKNE, NotebookLM, Obsidian vaults, etc.) to keep them healthy and evolving.
---

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
- 眼科/虹膜/3D眼球: ["眼", "虹膜", "iris", "瞳孔", "pupil", "角膜", "眼球", "eyeball", "ocul"]
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