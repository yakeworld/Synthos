---
name: pubmed
related_skills: ["knowledge-acquisition"]
description: Deep PubMed/MEDLINE search via NCBI E-utilities — query construction, MeSH terms, batch retrieval, clinical query refinement.
version: 1.0.0
metadata:
  synthos:
    version: 2.0.1
    author: Synthos
    signature: 'query: str -> papers: list[dict]'

---


# PubMed Search

## 快速参考

> ⚠️ **Hermes cron 环境安全扫描拦截（v91 — 2026-06-08）**：`curl | python3` 管道被 `tirith:curl_pipe_shell` 安全扫描拦截。在 cron/Hermes 环境中，**必须使用 `urllib.request` stdlib**（写入脚本文件后执行），不得使用 `curl`。

| 操作 | 安全命令（Hermes cron 环境） |
|:-----|:------|
| 搜索 | 写入脚本文件后执行（见 scripts/pubmed-urllib.py），不可使用 `curl | python3` 管道 |
| 详情 | 写入脚本文件，用 `urllib.request` 读取 XML |
| 摘要 | 写入脚本文件，用 `urllib.request` 读取 text |
| 引用数 | 写入脚本文件，用 `urllib.request` 读取 JSON |
| PMC全文 | 写入脚本文件，用 `urllib.request` 读取 XML |

**正确做法**：将查询写入 `.py` 脚本文件，用 `terminal` 执行。详见 `scripts/pubmed-urllib.py`。

> ⚠️ **Python 3.12 urllib 裸空格拒绝（v106 — 2026-06-08）**：`urllib.request.urlopen()` 拒绝 URL 路径中包含裸空格的请求，报 `InvalidURL: URL can't contain control characters`。**所有 PubMed 查询必须使用 `quote_plus(term, safe='')` 编码**。已在 `scripts/pubmed-urllib.py` 中修复，参见 `references/python312-url-quirk.md`。

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
- `references/python312-url-quirk.md` — Python 3.12 urllib.request 拒绝裸空格URL路径的修复（quote_plus编码，v106）

## 脚本

|- `scripts/pubmed-urllib.py` — 可复用PubMed查询脚本（urllib stdlib，无curl，安全Hermes cron环境，已修复Python 3.12 quote_plus编码）
  - 用法：`python3 pubmed-urllib.py "term"` → count+PMIDs
  - `python3 pubmed-urllib.py "term" "2024/01/01..2026/06/08"` → 日期过滤
  - `python3 pubmed-urllib.py --abstract "PMID1,PMID2"` → 摘要提取

## IO_CONTRACT

**输入**:
- `query: str` — PubMed搜索查询（支持MeSH、标题、摘要、作者、DOI、日期、文献类型字段）
- `api_key: str (optional)` — NCBI API key（提升速率限制3→10 req/s）
- `date_range: str (optional)` — 日期范围过滤器（"YYYY/MM/DD..YYYY/MM/DD"）
- `max_results: int (optional, default=100)` — 最大返回结果数
> 对应原则：P2（机械原子暴露输入输出规范）
**输出**:
- `papers: list[dict]` — 论文列表，每项包含: title, authors, journal, pubdate, pmid, abstract, mesh_terms, citation_count
- `total_count: int` — 符合查询条件的论文总数
- `query_used: str` — 实际执行的搜索查询

**副作用**:
- 调用NCBI E-utilities API（需网络访问）
- 遵守速率限制：免费3 req/s，有key 10 req/s
- 所有请求必须通过 `urllib.request`（cron安全，非curl管道）
