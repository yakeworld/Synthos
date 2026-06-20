# IO_CONTRACT.md — research-skill-audit

> 对应原则：P2（机械原子暴露输入输出规范）
> 权威来源：SKILL.md 中的 IO_CONTRACT 定义

## IO 定义

对应原则：P2（机械原子暴露输入输出规范）

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

## 数据流

本原子的输入由上游编排者（task-router 或其他原子）提供，输出直接返回给调用者。

## 错误处理

- 输入不合法 → 返回错误状态码 + 原因说明
- 执行失败 → 返回 error_state 节点，不产生半成品输出
- 超时 → 返回 timeout 标记，不阻塞调用者
