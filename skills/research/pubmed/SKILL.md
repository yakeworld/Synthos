---
name: pubmed
description: Deep PubMed/MEDLINE search via NCBI E-utilities — query construction, MeSH terms, batch retrieval, clinical query refinement.
metadata:
  synthos:
    version: 2.0.0
    author: Synthos
    signature: 'query: str -> papers: list[dict]'
---

# PubMed Search

## 快速参考

| 操作 | 命令 |
|:-----|:------|
| 搜索 | `curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=QUERY&retmax=10&retmode=json"` |
| 详情 | `curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=PMID1,PMID2&retmode=xml"` |
| 摘要 | `curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=PMID1,PMID2&rettype=abstract&retmode=text"` |
| 引用数 | `curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=PMID1,PMID2&retmode=json"` |
| PMC全文 | `curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=PMC_ID&retmode=xml"` |

## 搜索语法

| 字段 | 示例 |
|:-----|:------|
| MeSH | `"vestibular diseases"[MeSH Terms]` |
| 标题 | `vestibular[Title]` |
| 摘要 | `vestibular[Abstract]` |
| 作者 | `"Smith J"[Author]` |
| DOI | `"10.1016/..."[DOI]` |
| 日期 | `"2020/01/01"[Date - Publication] : "2024/12/31"[Date - Publication]` |
| 文献类型 | `review[PT]`, `randomized controlled trial[PT]` |
| 临床查询 | `"query"[filter]` (therapy/diagnosis/prognosis/etiology) |

## 逻辑运算符

- AND / OR / NOT
- 精确短语: `"vestibular rehabilitation"`
- 通配: `vestibul*` (匹配 vestibular, vestibule等)
- 邻近: `saccade NEAR3 visual`

## 速率限制

- 免费: 3 req/s (无API key)
- 有API key: 10 req/s (加 `&tool=hermes-agent&email=user@example.com`)
- 最大单次: 10,000结果, 200 PMIDs/efetch

## 参考文件

- `references/mesh-terms.md` — 眼动/前庭MeSH术语列表
- `references/clinical-queries.md` — 临床查询过滤器详解
- `references/batch-retrieval.md` — 批量检索和XML解析
- `references/efetch-response-quirks.md` — efetch 可能返回 text/plain 或 HTML（非JSON/XML）；esummary key 是 PMID 不在 pubmed 下；idlist 键名小写
