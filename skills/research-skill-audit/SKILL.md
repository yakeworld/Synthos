---
name: research-skill-audit
description: "Audit and enhance research skill coverage. Process for identifying gaps, testing existing skills, and creating/enhancing missing capabilities."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  synthos:
    priority: P1
    atom_type: pipeline
    description: Audit and enhance research skill coverage. Process for identifying gaps, testing existing skills, and creating/enhancing missing capabilities.
    signature: ['skill_inventory: list[Skill], audit_criteria: dict -> audit_report: dict'] -> ['audit_report: dict (gaps, weak_skills, improvement_suggestions)']
    related_skills: [research-paper-search, knowledge-acquisition, knowledge-extraction, association-discovery, hypothesis-generation, argument-expression, viewpoint-verification]


# Research Skill Audit

## 原理层·文言

> 技能如器，久用则钝。审计如砥，常磨则利。
> 不评估不知短板，不审视不见冗余。
> 域有其模，模需时新。旧者汰之，缺者补之。

##

## 触发条件

This skill should be invoked when:

1. **Auditing research skills** — Reviewing an existing set of research-related skills for correctness, completeness, and API health
2. **Finding gaps in coverage** — Identifying missing databases, content types (preprints, dissertations, grey literature), or functionality (systematic review, citation analysis, continuous monitoring)
3. **Periodic quality review** — Performing routine maintenance and quality checks on research skill inventory (recommended monthly or per project milestone)
4. **Preparing competition submissions** — Ensuring research skills meet scoring criteria for completeness and reliability
5. **Onboarding new research capabilities** — Before adding a new research skill, auditing what already exists to avoid duplication and ensure proper cross-referencing

## Audit Process

### Step 1: List All Research Skills

```bash
# List research skills
skills_list category=research

# List related skills (mlops, data-science, etc.)
skills_list category=mlops
skills_list category=data-science
skills_list category=note-taking
skills_list category=productivity
```

### Step 2: Test Each Skill

For each skill, run a real test to verify functionality:

```bash
# Test arxiv
curl -s "https://export.arxiv.org/api/query?search_query=all:TOPIC&max_results=5"

# Test PubMed
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=TOPIC&retmax=5&retmode=json"

# Test OpenAlex
curl -s "https://api.openalex.org/works?search=TOPIC&per_page=5"

# Test bioRxiv
curl -s "https://api.biorxiv.org/details/biorxiv/0"
```

### Step 3: Identify Gaps

Common research gaps:
1. **Missing database coverage** — PubMed, Cochrane, Embase, CNKI
2. **Missing content types** — Preprints, dissertations, conference proceedings, grey literature
3. **Missing functionality** — Systematic review, meta-analysis, quality assessment
4. **Missing continuous monitoring** — Daily/weekly paper digests
5. **Missing citation analysis** — Citation networks, h-index tracking
6. **Missing knowledge synthesis** — Literature maps, research gap identification

### Step 4: Create/Enhance Skills

For each gap, create a new skill or enhance an existing one:

- **PubMed** — Create pubmed skill with full E-utilities coverage
- **Preprints** — Create biorxiv skill for bioRxiv/medRxiv
- **Cross-disciplinary** — Create openalex skill for 250M+ paper database
- **Monitoring** — Create literature-monitor skill for continuous tracking
- **Systematic review** — Create systematic-review skill for PRISMA workflow
- **Quality assessment** — Enhance with GRADE, ROB-2, NOS tools

### Step 5: Cross-Reference Skills

Update related_skills in each skill to point to complementary skills:

```yaml
related_skills: [arxiv, pubmed, openalex, biorxiv, literature-monitor, systematic-review]
```

### Step 6: Audit for Credential Leaks

Before testing APIs, scan any project directories for hardcoded credentials (tokens, API keys, passwords) using patterns from `research-paper-search/references/credential-cleanup.md`. Fix any findings:
- Replace hardcoded values with `os.environ.get('VAR', '')` lookups
- Add `.gitignore` rules for credential files
- Remove committed credential files from git tracking (`git rm --cached`)
- Add env vars to shell profiles (`~/.bashrc` or `~/.profile`)

### Step 7: Document the Audit

Save a summary of what was found and what was enhanced.

### Step 8 (Optional): Philosophical Alignment Audit

When the project has a stated philosophical/architectural framework (e.g., Synthos 八维, first-principles design, self-evolving system), add an alignment audit layer:

1. Load the philosophy framework (e.g., via `research-platform-philosophy`)
2. Map each project capability to the framework's dimensions (not as features but as cognitive behaviors)
3. Score each dimension 0-100% (not as "has this feature" but as "how deeply does this capability embody the principle")
4. Identify the gap between "tool-level" and "architecture-level" implementation
5. **CRITICAL**: The highest-priority fixes are usually NOT more code — they are: cognitive interface definitions, metric redesign (engineering metrics → epistemic metrics), and refactoring existing code to make the architecture visible.
6. If the user asks for "improvements" after an alignment audit, propose architectural rethinking first, then feature additions.

### Step 9: Teaching Project Audit (NEW)

Many projects have embedded teaching/training materials (e.g., 医疗数据智能分析 with 73 sources covering CRISP-DM, AIGC辅助教学, Python科学计算, ML建模, XAI). When found:

1. Identify if the teaching materials map to the 6 cognitive atoms
2. Use teaching materials as "落地场景" evidence for competition submissions
3. Count the sources — 50+ sources = strong "可推广性与生态价值" evidence
4. Document the mapping for integration with the research workflow
5. This can boost scoring by 5-8 points in competition criteria for "实施与效果" and "可推广性"

## Testing Checklist

For each research skill, verify:
- [ ] API endpoint works
- [ ] Query syntax is correct
- [ ] Response parsing works
- [ ] Rate limits are handled
- [ ] Fallback strategies exist
- [ ] Error handling is documented
- [ ] Example queries are provided
- [ ] Related skills are cross-referenced

## 验证检查清单

运行本技能后，确认以下检查项：

- [ ] 所有研究技能已列明并分类
- [ ] 每个技能的实际功能已验证（API端点、查询语法、响应解析）
- [ ] 已识别至少3个具体缺口（功能/数据库/方法论）
- [ ] 每个缺口有明确的修复方案（新建/增强/合并）
- [ ] 对应 skill 的 related_skills 已交叉引用
- [ ] 审计过程无凭据泄露（API key、token 未暴露）
- [ ] 审计结果已保存为文档

---
  io_contract: input: ['skill_inventory: list[Skill], audit_criteria: dict -> audit_report: dict', 'output: ['audit_report: dict (gaps, weak_skills, improvement_suggestions)']


## Common Pitfalls in Research Skills

1. **URL encoding**: All query terms must be URL-encoded
2. **Rate limits**: Always add delays between API calls
3. **Fallbacks**: Never rely on a single API
4. **Deduplication**: Same paper may appear in multiple sources
5. **MeSH terms**: Use MeSH for precision in PubMed searches
6. **Publication types**: Filter by study design for systematic reviews
7. **Abstract parsing**: PubMed abstracts may have labeled sections
8. **Open access**: Check OA status for full-text access
9. **Citation counts**: May be stale for very recent papers
10. **Duplicate detection**: Essential when combining multiple sources

## Cross-Reference Skills
- `research-paper-search/references/credential-cleanup.md` for a complete procedure covering pipeline masking, byte-level replacement, git credentials, and .bashrc guards.
- `references/philosophy-alignment-audit.md` — How to audit a project against a philosophical/architectural framework (Synthos 八维 and similar)
- `references/audit-patterns-2026-05-30.md` — 实战记录: 166-skill 审计的操作模式、archive 评估矩阵、核心技能质量检查清单

## Quick Commands for Common Tasks

```bash
# Find all research skills
skills_list category=research

# Test a specific skill
skill_view name=SKILL_NAME

# Search arXiv
curl -s "https://export.arxiv.org/api/query?search_query=all:TOPIC&max_results=5"

# Search PubMed
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=TOPIC&retmax=5&retmode=json"

# Search OpenAlex
curl -s "https://api.openalex.org/works?search=TOPIC&per_page=5"

# Search bioRxiv
curl -s "https://api.biorxiv.org/details/biorxiv/0"

# Search medRxiv
curl -s "https://api.biorxiv.org/details/medrxiv/0"
```
