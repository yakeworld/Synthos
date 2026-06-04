---
name: research-paper-search
description: '主skill | 多源论文检索+全文下载编排器。入口：Semantic Scholar, PubMed, Crossref, OpenAlex, arXiv。下载：arXiv直链→PMC efetch→封锁标记。调用子skill: arxiv, pubmed, openalex。'
metadata:
  synthos:
    version: 1.0.0
    author: Synthos
    signature: 'query: str -> papers: list[dict]'
    related_skills:
    - arxiv
    - pubmed
    - openalex
---

# Research Paper Search

## 搜索编排

| 源 | API | 特点 |
|:---|:----|:------|
| Semantic Scholar | `api.semanticscholar.org/graph/v1/paper/search` | 引用网络+影响评分 |
| PubMed | `eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi` | 生物医学首选 |
| Crossref | `api.crossref.org/works` | DOI验证+元数据 |
| OpenAlex | `api.openalex.org/works` | 250M+开放数据 |
| arXiv | `export.arxiv.org/api/query` | 预印本全文下载 |

## 基本查询

```bash
# Semantic Scholar
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=eye+tracking+vestibular&limit=10"

# PubMed
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=vestibular+disorders&retmax=10&retmode=json"

# OpenAlex
curl -s "https://api.openalex.org/works?search=vestibular+eye+tracking&per_page=10"

# arXiv
curl -s "http://export.arxiv.org/api/query?search_query=all:vestibular+AND+all:eye+tracking&max_results=10"
```

## PDF下载优先级

```
1. arXiv直链 (免费/稳定/快速)
2. PMC efetch (开放获取)
3. Unpaywall (混合OA检测)
4. 标记为paywalled
```

## 子skill调用

| 需求 | 加载skill |
|:-----|:----------|
| 生物医学 | `pubmed` |
| 预印本 | `arxiv` |
| 多学科 | `openalex` |
| 摘要提取 | `knowledge-extraction` |
