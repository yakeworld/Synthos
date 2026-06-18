---
name: research-paper-search
description: '主skill | 多源论文检索+全文下载编排器。入口：Semantic Scholar, PubMed, Crossref, OpenAlex, arXiv。下载：arXiv直链→PMC efetch→封锁标记。调用子skill: arxiv, pubmed, openalex。'
version: 1.0.0
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

## IO_CONTRACT

- **input**: `query: str` — 搜索关键词（如 "vestibular eye tracking"）
- **input**: `domains: list[str]` — 目标领域（如 ["PubMed", "OpenAlex", "arXiv"]）
- **input**: `max_results: int` — 每源最大返回数
- **output**: `papers: list[dict]` — 论文列表，每项含 {title, authors, year, source, doi, url, abstract}
- **output**: `source_stats: dict` — 各源结果计数 {semantic_scholar: N, pubmed: N, ...}
> 对应原则：P2（机械原子暴露输入输出规范）
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
curl -s "https://export.arxiv.org/api/query?search_query=all:vestibular+AND+all:eye+tracking&max_results=10"
```

## Python 3.12 OpenAlex Querying

> ⚠️ **Python 3.12 urllib rejects ALL spaces in URL path** — not just `%20`-encoded ones, but bare spaces too. `urllib.request.urlopen()` raises `InvalidURL: URL can't contain control characters` for any space character in the query string portion of the URL.

> ⚠️ **Old advice (WRONG): bare spaces in query** — `url=f"...?search={query}"` where `query` contains spaces will FAIL. The previous convention of "bare spaces are fine" was incorrect and causes `InvalidURL` errors.

> ⚠️ **Correct approach**: use `urllib.parse.quote_plus(query, safe=' ')` to encode spaces as `+` (plus sign, which is valid in URL path).

```python
# CORRECT — quote_plus with safe=' ' preserves literal spaces in the query string
from urllib.parse import quote_plus
query = "PINN fluid dynamics"
safe_query = quote_plus(query, safe=' ')
url = f"https://api.openalex.org/works?search={safe_query}&per_page=3"
req = urllib.request.Request(url)
with urllib.request.urlopen(req, timeout=15) as r:
    d = json.loads(r.read())
```

> ⚠️ **Why this matters**: OpenAlex search queries almost always contain spaces. All OpenAlex queries in this project MUST use `quote_plus(query, safe=' ')` or the request fails silently with InvalidURL.

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
| 3域验证 | 见 `references/3-domain-gap-verification.md` — PubMed 3-domain gap verification protocol for cron sessions (方法域/理论域/传统域) |
| OpenAlex PINN关键词假阳性 | 见 `references/openalex-pin-n-keyword-false-positive.md` — OpenAlex搜索"PINN"时，"PINN"可能出现在摘要文本中作为不同缩写或词组的一部分，而非指Physics-Informed Neural Networks。必须逐条阅读摘要确认实际方法学。 |
| OpenAlex URL encoding | 见 `references/openalex-python-312-url-quirk.md` — Python 3.12 urllib.request rejects %20-encoded spaces in URLs; use bare spaces or quote_plus() |
| 参考文献验证 | 见 `scripts/verify_refs_template.py` — 论文参考文献OpenAlex交叉验证脚本模板 |
| PubMed 扫描模板 | 见 `scripts/pubmed_scan_template.py` — 可复用的5方向PubMed扫描脚本（含idlist键名修复，无curl|python3管道）|
| Terminal 安全扫描阻塞 | 见 `references/terminal-security-scan-blocking.md` — `curl | python3` 管道被安全扫描拦截（tirith:curl_pipe_shell），必须写入脚本文件再执行，或用 urllib stdlib 替代 |
| PubMed OR 假阳性 | 见 `references/pubmed-or-false-positive-severity.md` — PubMed OR查询假阳性量级数据与阈值规则 |
| PubMed esummary 结构 | 见 `references/pubmed-esummary-flat-structure.md` — esummary JSON 扁平结构陷阱（key是PMID，不在pubmed下） |
| OpenAlex 关键词假阳性模式（v86） | 见 `references/false-positive-keyword-pattern.md`（openalex skill）— neural network→materials/electronics, differential equation→thermodynamics/traffic, fixation→molecular transport/botany. PubMed=0 + OA高计数 = 几乎确定假阳性 |
| v86 综合扫描结果 | 见 `references/v86-scan-results.md` — 第86轮扫描：120+白空间确认稳定，83篇论文完成，cochlear-vestibular-coupling-PINN作为Paper 84候选 |
| v97 综合扫描结果 | 见 `references/v97-scan-results.md` — 第97轮扫描：170+白空间确认稳定，85篇论文完成。重大假阳性：acoustic-vestibular-evoked-PINN=80(肿瘤生物学/有限元分析, 非PINN/ODE)。12附加候选全部ABSOLUTE WHITE PubMed=0。 |
| step_quality_check.md JSON 解析 — LaTeX 反斜杠陷阱 | 见 `references/latex-escape-json-parsing-fix.md` — step_quality_check.md 中的 JSON 块常含 LaTeX 数学表达式的反斜杠（如 `\sigma`），导致 Python json.loads() 报 Invalid \escape。提供修复代码和 15+ 受影响论文清单。 |