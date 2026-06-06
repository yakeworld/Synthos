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
  references:
  - references/pubmed-api-key-casing.md
  - references/pubmed-template-query-antipatterns.md — v22: OR-heavy DEFAULT_QUERIES produce massive false positives; all queries must use AND composition
  - references/efetch-response-quirks.md — v27: efetch may return text/plain or HTML instead of JSON/XML; rate-limit behavior; esummary key is PMID
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

## Python 3.12 OpenAlex Querying

> ⚠️ Python 3.12's `urllib.request.urlopen()` rejects `%20` URL-encoded spaces with "URL can't contain control characters." See `references/openalex-python-312-url-quirk.md`.

```python
# SAFE: bare spaces in query, no urllib.parse.quote()
query = "PINN fluid dynamics"
url = f"https://api.openalex.org/works?search={query}&per_page=3"
req = urllib.request.Request(url)
with urllib.request.urlopen(req, timeout=10) as r:
    d = json.loads(r.read())
```

## PubMed eSearch 键名陷阱（v4 — 2026-06-06）

> ⚠️ PubMed eSearch 返回的 JSON 中，论文 ID 列表的键名是 `idlist`（小写），不是 `IdList`（首字母大写）。使用 `IdList` 会返回 `[]`，不报错、不警告，导致后续处理产生零结果。

```python
# WRONG — empty list, no error
ids = d.get("esearchresult", {}).get("IdList", [])

# CORRECT
ids = d.get("esearchresult", {}).get("idlist", [])
```

## PubMed esummary 扁平结构陷阱（v42 — 2026-06-06）

> ⚠️ **`esummary` 响应结构**: 条目位于 `d["result"]` 下，key 是 PMID 字符串。不在 `d["result"]["pubmed"]` 或 `d["pubmed"]` 下。使用 `d.get(pid, {})` 时若 `pid` 不在 `result` 直接子级 → 返回 `{}`，所有标题变成 `"N/A"`。
>
> **验证**: 每次 esummary 后检查 `d.get("result", {}).get("pubmed")` 是否为 None。如果是 → 扁平结构，需要用 `for pid in d.get("result", {}): ...` 迭代。

## XML efetch 解析（v31 — retmode=json 系统性破坏）

> ⚠️ **NCBI June 2026 API 变更**: `retmode=json` 对 eFetch 单 ID 请求返回原始整数（`b'41400465\n'`），不是 JSON。所有 eFetch 必须使用 `retmode=xml`。eSearch 的 `retmode=json` 仍然正常。

- 使用 `retmode=xml` 获取结构化数据
- `<ArticleTitle>` 标签可能包含 CDATA 包裹的内容
- 使用 `re.search(r'<ArticleTitle[^>]*>(.*?)</ArticleTitle>', xml, re.DOTALL)` 提取标题
- 详见 `references/efetch-response-quirks.md` — v31: retmode=json returns raw integer for single IDs

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
| 白空间扫描 | 见 `references/white-space-scan-2026-06-05.md` — 多层验证协议 |
| 3域验证 | 见 `references/3-domain-gap-verification.md` — PubMed 3-domain gap verification protocol for cron sessions |
| OpenAlex URL encoding | 见 `references/openalex-python-312-url-quirk.md` — Python 3.12 urllib.request rejects %20-encoded spaces in URLs; use bare spaces or quote_plus() |
| 参考文献验证 | 见 `scripts/verify_refs_template.py` — 论文参考文献OpenAlex交叉验证脚本模板 |
| PubMed 扫描模板 | 见 `scripts/pubmed_scan_template.py` — 可复用的5方向PubMed扫描脚本（含idlist键名修复）|
| PubMed OR 假阳性 | 见 `references/pubmed-or-false-positive-severity.md` — PubMed OR查询假阳性量级数据与阈值规则 |
| PubMed esummary 结构 | 见 `references/pubmed-esummary-flat-structure.md` — esummary JSON 扁平结构陷阱（key是PMID，不在pubmed下） |