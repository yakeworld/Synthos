---
name: literature
category: research-tools
signature: "literature -> research-tools: 文献检索统一入口"
description: 文献检索统一入口 — 搜索、下载、验证三位一体，多源聚合，管道编排。
version: 3.0.0
author: Synthos
license: MIT
updated: 2026-07-06
metadata:
  synthos:
    signature: "literature search/download/verify/pipeline"
    atom_type: unified-entry
    priority: P0
    description: "文献检索统一包 — 搜索7源（统一返回 pdf_url+local_links+links）、下载核心（pdf_download_engine + unified_download），搜索即获取全文链接。"
    linked_files:
      - citation-verification
      - reference-enrichment-pipeline
      - paper-pipeline
      - bib-structure-audit
  linked_scripts:
    - scripts/literature.py
    - scripts/unified_search.py  # DEPRECATED — 见 literature.py cmd_search
    - scripts/multi_source_search.py  # DEPRECATED — 见 literature.py parse_query
    - scripts/normalized_output.py
    - scripts/pubmed_search.py
    - scripts/pubmed_search_clean.py
    - scripts/pubmed_batch_doi.py
    - scripts/s2_batch_doi.py
    - scripts/search_arxiv.py
    - scripts/audit-sources-consistency.py
    - scripts/sources/semantic_scholar.py
    - scripts/sources/pubmed.py
    - scripts/sources/crossref.py
    - scripts/sources/openalex.py
    - scripts/sources/arxiv.py
    - scripts/sources/pubscholar.py
    - scripts/sources/scihub.py
    - scripts/download/pdf_download_engine.py
    - scripts/download/unified_download.py
---

# 文献检索 (Literature)

> 多源求索，博观约取。

## 原理

文献检索是一个统一的包（package），不是多个独立 skill。所有检索、下载、验证逻辑集中管理，通过统一 CLI 入口调用。

**核心原则：搜索即获取全文链接。** 每个搜索源在 `search()` 时就把所有可用的 PDF 链接一起返回。下载阶段只需遍历链接下载，不再按 DOI 重新查源。

**完整链路**：`search() → 获取 {pdf_url, local_links, links} → 遍历 links 下载 → 保存到目标目录`

## 触发条件

- 需要检索学术文献（主题/关键词/研究问题）
- 需要下载论文全文
- 需要验证论文引用质量
- 需要执行完整的检索→下载→验证管线

## 架构

```
literature/             ← P0 统一入口
  scripts/
    literature.py        — 统一 CLI 入口（search/download/pipeline/verify）
    unified_search.py    — DEPRECATED — 统一检索入口（字段过滤），已被 literature.py search 取代
    multi_source_search.py — DEPRECATED — 四源搜索，已被 literature.py search 取代
    normalized_output.py — 输出标准化
    pubmed_search.py     — PubMed 独立检索
    pubmed_search_clean.py — PubMed 清理版
    pubmed_batch_doi.py  — PubMed 批量 DOI 查询
    s2_batch_doi.py      — S2 批量 DOI 查询
    search_arxiv.py      — arXiv 独立检索
    audit-sources-consistency.py — 源一致性审计
    sources/             — 8 个搜索源（公开，搜索即获取全文链接）
      __init__.py        — 注册表（公开源 + DEFAULT_SOURCES）
      semantic_scholar.py — class SemanticScholar ✅ 双key轮换，返回pdf_url+local_links+links
      pubmed.py          — class PubMed ✅ 返回pmc字段+links
      crossref.py        — class CrossRef ✅ 返回open_access链接
      openalex.py        — class OpenAlex ✅ 返回oa_pdf+links
      arxiv.py           — class ArXiv ✅ 返回完整links(含pdf)
      pubscholar.py      — class PubScholar ✅ curl直调API，返回cdn直链
      scihub.py          — class SciHub ✅ URL即PDF直链，作为兜底源
    download/            — 下载核心（单一引擎，统一导出）
      __init__.py        — 统一导出所有下载函数
      pdf_download_engine.py — **唯一下载引擎**，43 种下载方法
      unified_download.py  — 编排层辅助
  references/            — 59 个参考文档（合并自 paper-retrieval 下所有子技能）
```

**统一原则**：文献检索、下载、验证全部集中在此一个目录。不再存在 paper-retrieval 或 paper-search 等分散技能。每个数据源有独立 Python 适配器，统一通过 `literature.py` CLI 调用（支持字段过滤和 DOI 精确检索）。
- `references/pmc-fulltext-coverage-analysis.md` — PMC 全文覆盖分析（期刊类型 vs 发表时间，预检查方法）
    - `references/bashrc-export-concatenation-bug.md` — bashrc 中两个 export 写一行的 bug：key 值被污染
    - `references/pubscholar-fix-2026-07-06.md` — PubScholar 修复实录：RSSHub 路径错误、XML 解析、国内实例
    - `references/session-2026-07-07-search-troubleshooting.md` — 多源搜索排障实录
- `references/pubscholar-api-signature.md` — PubScholar 签名规范
- `references/pubscholar-curl-api-fix.md` — PubScholar 迁移记录
- `references/s2-dual-key-failover.md` — S2 双 key 轮换
    - `references/pmc-fulltext-coverage-analysis.md` — PMC 全文覆盖分析（期刊类型 vs 发表时间，预检查方法）
    - `references/pmc-fulltext-coverage-analysis.md` — PMC 全文覆盖分析（期刊类型 vs 发表时间，预检查方法）
```

**私人源**：MedData 已移至 `private/meddata-download/`（含脚本、SKILL.md、参考文档）。

## 数据源覆盖

### 搜索（7 公开源 + 1 私人源）

| 数据源 | API | Key | PDF 链接 | 用途 |
|--------|-----|-----|----------|------|
| Semantic Scholar | 直连 | 双 key 轮换 | ✅ openAccessPdf + pdfUrls + urls | 主要检索源，返回引用数、OA PDF、PMC/GitHub 链接 |
| PubMed | NCBI E-utilities | 无 | ⚠️ 无直链（有 pmc 字段） | 生物医学/临床文献 |
| CrossRef | 直连 | 无 | ⚠️ open_access 字段（如有） | 元数据补入、DOI 验证、OA 来源 |
| OpenAlex | 直连 | 无 | ✅ oa_url + oa_pdf | 开放学术图谱、引用网络、OA PDF |
| arXiv | 直连 | 无 | ✅ 直接 PDF 链接 | CS/AI 预印本 |
| PubScholar | curl直调POST | 无 | ✅ local_links CDN | 中文文献，签名头认证 |
| Sci-Hub | 直连 | 无 | ✅ URL 本身就是 PDF 直链 | 非 OA 论文兜底，按域名顺序尝试（sci-hub.se → .ru → .st） |

> **设计原则**：搜索阶段收集所有可用的全文链接。下载阶段只需遍历 `links` 字典下载，不再按 DOI 重新查源。单一下载引擎 `pdf_download_engine.py`（43 种方法）覆盖所有场景。
>
> **私人资源（最后保障）**：MedData 是机构付费全文库，需要用户名密码，**不加入默认搜索管线**。作为最后兜底，仅在以下情况调用：① 其他 7 个源均返回空 PDF 链接 ② 已知该论文在 MedData 全文库中。通过 `private/meddata-download/scripts/meddata_download.py`（`search_by_pmid`/`download_by_pmid`）或 `pdf_download_engine.download_meddata()` 手动调用。凭据存于 `~/.secrets`，`.bashrc` 自动 source。设置 `MEDDATA_USERNAME` + `MEDDATA_PASSWORD` 环境变量即可使用。

### 数据契约（搜索输出）

所有 7 个源的 `search()` 返回的 paper dict **统一包含**以下字段：

```json
{
  "title": "论文标题",
  "authors": ["作者1", "作者2"],
  "year": 2024,
  "source": "semantic_scholar",
  "doi": "10.xxxx",
  "abstract": "摘要...",
  "url": "https://...",
  "pdf_url": "https://...",        // 最优先的免费 PDF 直链（可能为空）
  "local_links": ["https://...", ...],  // 所有 PDF 直链数组
  "links": {                       // 所有可用链接（含 publisher 页面、DOI 重定向等）
    "openAccessPdf": "https://...",
    "pdfUrl": "https://...",
    "doi": "https://doi.org/...",
    "oa": "https://...",
    "oa_pdf": "https://...",
    "pmc": "https://...",
    ...
  },
  "citation_count": 42,
  "venue": "期刊名",
  "provenance": "source=semantic_scholar",
  "pmc": "...",                    // 如有
  "arxiv_id": "...",               // 如有
  "is_free": false                 // 如有
}
```

**下载时的正确做法**：
```python
paper = source.search("breast cancer", max_results=1)[0]

# 方法 1: 直接下载 pdf_url（最优先）
if paper["pdf_url"]:
    download(paper["pdf_url"], output_path="paper.pdf")

# 方法 2: 遍历 local_links（所有 PDF 直链）
for url in paper["local_links"]:
    download(url, output_path="paper.pdf")

# 方法 3: 遍历 links（所有可用链接，含 publisher 页面、DOI 等）
for source_name, url in paper["links"].items():
    download(url, output_path=f"paper_{source_name}.pdf")
```

> **设计原则**：搜索阶段收集所有可用的全文链接。下载阶段只需遍历 `links` 字典下载，不再按 DOI 重新查源。单一下载引擎 `pdf_download_engine.py`（43 种方法）覆盖所有场景。
>
> **私人资源（最后保障）**：MedData 已移至 `private/meddata-download/`。通过 `private/meddata-download/scripts/meddata_download.py`（`search_by_pmid`/`download_by_pmid`）或 `pdf_download_engine.download_meddata()` 手动调用。凭据存于 `~/.secrets`，`.bashrc` 自动 source。

### 下载（单一引擎）

| 模块 | 优先级 | 用途 |
|------|--------|------|
| pdf_download_engine.py | 1 | **唯一下载引擎**，43 种下载方法，覆盖 curl_cffi、tor、DOI2PDF、ScienceDirect、Springer、Wiley 等 |
| unified_download.py | 2 | 编排层辅助（`_download_single()` / `_download_batch()`） |

### 验证（4 方法）

| 验证方法 | 检查内容 |
|----------|----------|
| DOI Crossref | DOI 是否存在、元数据是否匹配 |
| PDF Title | 下载 PDF 后验证标题与 bib 一致 |
| Withdrawn | 检测论文是否已被撤回 |
| Content Match | 阅读 PDF 验证引用语境是否得当 |

## 数据契约

### 输入（搜索）

```json
{
  "topic": "字符串",
  "max_results": 10,
  "year_range": "2020-2024"
}
```

### 输出（搜索）

每个 paper dict 包含完整的全文链接集（pdf_url + local_links + links）：

```json
{
  "papers": [{
    "title": "论文标题",
    "authors": ["作者1", "作者2"],
    "year": 2024,
    "source": "semantic_scholar",
    "doi": "10.xxxx",
    "pmc": "...",          // 如有
    "arxiv_id": "...",     // 如有
    "abstract": "摘要...",
    "url": "https://...",
    "pdf_url": "https://...",           // 最优先免费 PDF 直链（可能为空）
    "local_links": ["https://...", ...], // 所有 PDF 直链数组
    "links": {                          // 所有可用链接（含 publisher、DOI、PMC、GitHub 等）
      "openAccessPdf": "https://...",
      "oa": "https://...",
      "oa_pdf": "https://...",
      "doi": "https://doi.org/...",
      "pmc": "https://...",
      "cdn": "https://...",
      ...
    },
    "citation_count": 42,
    "venue": "期刊名",
    "provenance": "source=semantic_scholar",
    "is_free": false                   // 如有
  }],
  "total": 10,
  "sources_queried": ["semantic_scholar", "pubmed"],
  "errors": []
}
```

### 输出（下载）

```json
{
  "status": "success" | "fail",
  "path": "/path/to/file.pdf",
  "size": 123456
}
```

## CLI 用法

### 搜索

```bash
# 七源检索，最多10篇
python3 scripts/literature.py search "three-way decision clinical" --sources semantic_scholar pubmed crossref arxiv pubscholar scihub --max 10

# 仅 S2 检索
python3 scripts/literature.py search "vestibular ocular reflex" --sources semantic_scholar --max 5
```

### 下载

```bash
# 默认尝试 DOI 直连 → Sci-Hub
python3 scripts/literature.py download --doi 10.3322/caac.21694 -o paper.pdf
```

### 管线

```bash
# 搜索 → 下载 → 报告，完整管线
python3 scripts/literature.py pipeline "three-way decision" --sources semantic_scholar pubmed --max 15 --output-dir /path/to/results
```

## 环境变量配置

必须设置以下环境变量，脚本通过 `os.environ` 直接读取，不依赖 `.bashrc` 加载：

```bash
# Semantic Scholar 双 key（主备轮换）
export SEMANTIC_SCHOLAR_API_KEY="你的主S2_API密钥"
export S2_FALLBACK_KEY="s2k-你的备用S2_API密钥"
```

- `SEMANTIC_SCHOLAR_API_KEY` — 主 key，优先使用
- `S2_FALLBACK_KEY` — 备用 key，主 key 限流(429)时自动切换
- 其他源（arXiv、CrossRef、OpenAlex、PubMed、PubScholar）均无需 API key
- 建议写入 `~/.bashrc` 或 `~/.hermes/.env`

**S2 API key 自动读取**：`semantic_scholar.py` 从 `~/.bashrc` 中解析 `export S2_*` 或 `export SEMANTIC_*` 变量获取 key，不依赖系统环境变量注入。这是为了防止 cron/tmux 会话中环境丢失。

**MedData 凭据**：`~/.secrets` 自动 source，包含 `MEDDATA_USERNAME` + `MEDDATA_PASSWORD`。

## 附录：参考文件

（详见各文件：search-download-architecture.md, pubscholar-api-signature.md, pubscholar-curl-api-fix.md, s2-dual-key-failover.md）

**实际可靠源: 7/7 全部通过。每个源统一返回 pdf_url + local_links + links。**

| 源 | 实测状态 |
|----|---------|
| Semantic Scholar | ✅ 已修复 bashrc export 合并 bug，key 恢复正常 |
| PubScholar | ✅ 已修复：RSSHub 路径+国内实例+XML 解析+year_range 参数 |
| OpenAlex | ✅ |
| arXiv | ✅ |
| CrossRef | ✅ |
| PubMed | ✅ |
| Sci-Hub | ✅ |

**实际可靠源: 7/7 全部通过。每个源统一返回 pdf_url + local_links + links。**

## Pitfalls

- **S2 双 key 轮换**: `semantic_scholar.py` 内置主备双 key 自动轮换。key 从环境变量 `SEMANTIC_SCHOLAR_API_KEY` 和 `S2_FALLBACK_KEY` 读取。`_try_next_key()` 在每次请求失败时调用。
- **OpenAlex filter 日期格式**: `from_publication_date:2020` → 400 Bad Request。正确: `from_publication_date:2020-01-01`（`YYYY-MM-DD`）。
- **搜索接口一致性**: 所有 7 个活跃源的 `search()` 方法签名一致: `search(topic, max_results=10, year_range=None) → list[dict]`。返回字段含 title/authors/source/doi/provenance/year/abstract/url/pdf_url/citation_count/venue/local_links/links。
- **搜索即获取全文链接**: 所有 7 个源的 `search()` 必须返回 `{pdf_url, local_links, links}` 完整下载地址集。下载阶段不再按 DOI 重新查源。
- **下载统一入口**: `pdf_download_engine.py` 是唯一下载引擎（43 种方法）。`doi_direct.py`、`scihub.py`、`libgen.py`、`meddata.py` 已从 `download/` 删除。
- **MedData 是私人资源**: 不加入 `DEFAULT_SOURCES`，不推 GitHub。代码在 `private/meddata-download/scripts/`，凭据在 `~/.secrets`。
- **Sci-Hub 是搜索源**: `sources/scihub.py` 是公开搜索源，`search()` 返回空列表（不支持关键词搜索），`search_by_doi()` 返回 PDF 直链。不默认查询，仅手动调用。
- **API 参数泄露**: PubScholar、OpenAlex 的返回 dict 中可能混入请求参数（nonce/timestamp/fields/query），属冗余数据但不影响功能。Semantic Scholar 已修复，provenance 不再包含 API key。
- **PubScholar curl直调**: 必须用 `requests` 库（非 `urllib`，urllib 返回 403）。Cookie `XSRF-TOKEN` 必须填入真实 UUID（`uid` 变量值），不能是 `***`。必须带 Chrome UA 指纹。境外 IP 被频率限制（A0500），需国内 IP。签名头顺序必须按字典序排序后拼接：`sorted([salt, timestamp, nonce])`。
- **PubScholar Cookie 陷阱**: `Cookie` 头中 `XSRF-TOKEN` 的值必须是真实 `uid`，不能硬编码 `XSRF-TOKEN=***` — 否则返回 403。
- **PMC 全文管线（经实测验证 2026-07-07）**：PubMed PMID → ELink(db=pmc) → PMCID → EFetch(db=pmc, retmode=xml) → JATS XML 全文 → pandoc(--from=jats --to=markdown) → Markdown → pandoc(--pdf-engine=xelatex) → PDF。实测 3 篇 BPPV 文章 2/3 成功（67%），失败原因为部分期刊在 JATS XML 中嵌入了错误的 LaTeX preamble（`\documentclass[12pt]{minimal}`），pandoc 无法处理。HTML 输出仍可用（pandoc --from=jats --to=html5 无此问题）。NCBI 限速 10 req/sec（0.4s 间隔）。2025+ 年新发表文章大多无 PMC 全文链接（elink 返回 None）。PMC PDF 直链对 curl/wget/requests 一律拦截返回 HTML，必须浏览器手动过 reCAPTCHA。
- **PubMed 2025+ PMID**: esummary 返回空结果，需 fallback 到 web search 或 CrossRef。
- **S2 限流 CLI 卡死**: 调用 `literature.py` CLI 或 Python 直接 import 调用 S2 时，若 API key 被限流 429，整个 `search()` 调用会阻塞直到 terminal timeout（通常 60s+），不返回任何结果。**修复**：先 `curl -s -o /dev/null -w "%{http_code}" URL -H "X-API-Token: $KEY"` 快速探测 S2 状态（200=可用, 429=限流）。被限流时直接跳过 S2，不等待。fallback 到 PubMed/CrossRef/OpenAlex/arXiv/PubScholar。
- **S2 双 key 同时限流**: 当主 key 和 fallback key 均返回 429 时，两个 key 都被同一 IP 限流。需申请新 key 或等待 30-60 分钟配额恢复。不要反复重试。
- **S2 有 key 反而限流更低**: 有 S2 API key（免费 tier）的限制是 25 req/min + 50 req/day，而**无 key** 才是 60 req/min + 2000 req/day。**关键结论**：有 key = 更低的配额。有 key 的 429 是 key 频率限制（与 IP 无关），无 key 的 429 是 IP 频率限制。两者互相不影响。有 key 的 key 被限流后，无 key 也可能被限（IP 重叠）。**修复**：优先用无 key 访问 S2，或等待有 key 的配额重置（24h）。
- **S2 key 在 bashrc 中不能两个 export 写一行**: 两行 `export` 写在同一行（`export KEY1="value"export KEY2="value"`），shell 解析时 `export` 被当作前一个 key 的值，导致两个 key 都被污染。**修复**：每个 `export` 必须单独一行。
- **PubScholar 必须用国内 RSSHub 实例**: `rsshub.app` 被 GFW 墙（DNS 可解析但 100% 丢包），必须用 `hub.slarker.me` 或 `rsshub.js.org`（国内实例）。
- **PubScholar RSSHub 正确路径**: `/pubscholar/explore/articles/:keyword`，不是 `/pubscholar/api/search?keyword=`。返回 RSS XML（非 JSON），需用正则解析 `<item>` 提取 title/description/link/pubDate/author/category。
- **PubScholar 代码必须移除 year_range 参数**: `__init__.py` 中调用 `source.search(topic, max_results, year_range)` 会传给所有源，但 PubScholar 的 `search()` 签名只有 `topic` 和 `max_results`。必须用 `if year_range:` 条件判断再传参。
- **PubScholar 中文关键词 0 返回**: 直接搜索"乳腺癌 预测模型"可能返回 0 条。**修复**：尝试"乳腺癌 风险预测"、"乳腺癌 预后"、"breast cancer risk prediction"等变体，或先用交叉检索（PubMed/CrossRef 查英文→发现中文论文→在 PubScholar 单独搜标题）。
- **OpenAlex year=None KeyError**: OpenAlex 返回的 paper dict 中 year 字段可能为 None（非字符串），在切片 `r.get('year','N/A')[:300]` 时导致 TypeError/KeyError。**修复**：先做类型检查 `str(r.get('year','N/A'))` 再切片。
- **OpenAlex 搜索过滤日期格式**: `from_publication_date:2020` → 400 Bad Request。正确: `from_publication_date:2020-01-01`（`YYYY-MM-DD`）。
- **PMC 全文预检查**: 对每篇有 PMID 的文章，先 efetch 检查 ArticleIdList 中是否有 IdType="pmc" 的条目。有则走 PMC 全文管线，无则跳过。避免对无 PMC 全文的文章浪费 efetch + pandoc 调用。详见 `references/pmc-fulltext-coverage-analysis.md`。
- **NIH PMC PDF 反爬**: `pmc.ncbi.nlm.nih.gov/.../pdf/...` 对 ALL HTTP 客户端一律拦截（curl/wget/requests/curl_cffi/Selenium），返回 200 + text/html + "Preparing to download..." HTML。无头浏览器返回 reCAPTCHA。唯一解：真实人类在 GUI 浏览器中手动完成。
- **PMC 全文覆盖的期刊类型规律（实测 2026-07-07）**：PMC 全文收录取决于期刊是否在 PMC 合作名单内，**不是时间延迟问题**。
  - ✅ 开放获取期刊（Frontiers, MDPI, BMC 等）→ 自动收录，发表后 ~15 天即入 PMC
  - ✗ Springer/Wiley/SAGE/Elsevier 等付费期刊 → 不收录（除非作者自存档）
  - 实测：PMID 42388699 (Front Neurol, 2026-06-17) → PMCID 13318616 ✅；PMID 42402503 (Eur Arch Otol, Springer, 2026) → 无 PMC ✗
  - 管线优化：在 PMC 全文管线前增加期刊类型预筛 — Frontiers/MDPI/BMC 等 OA 期刊优先走 PMC 管线，Springer/Wiley/Elsevier 跳过 PMC 管线改用 S2/Sci-Hub
- **不另起入口**: 检索管线已有 `literature` 统一入口（P0）。创建新搜索/下载脚本前，先检查是否可复用已有源。已有入口时勿重复创造。

## 架构变更记录

### 2026-07-08: 文献技能统一合并

**关键变化**：paper-retrieval 下所有子技能（pubmed/openalex/biorxiv/research-paper-search/scientific-database-lookup）均为空壳（仅有元数据文件，无实际代码），其 references 全部合并进 `literature/references/`。删除了 paper-retrieval 整个目录，文献检索=下载=验证全部在 `literature/` 一个目录下。

**合并结果**：
- references 从 26 个增至 59 个（PubMed 6 + OpenAlex 5 + BioRxiv 1 + SciDB 6 + PDF/下载/API 16 + 原始 26 - 重叠 0）
- scripts 统一为一个入口点，无分散副本
- 之前分散在 hermes/skills/paper-retrieval、hermes/skills/paper-search、sda2/research-tools/paper-retrieval 的多处副本已全部清理

**Pitfall — 空壳子技能识别**：
paper-retrieval 下的子技能（pubmed/openalex/biorxiv/research-paper-search/scientific-database-lookup）只有 BOUNDARY/EVIDENCE_SCHEMA/CHANGE_LOG/IO_CONTRACT/SKILL.md，scripts 为空。这些是历史遗留的空壳，合并其 references 后直接删除即可，不必保留。

**Pitfall — 脚本重复检测**：
合并脚本前必须对比文件签名（函数列表、行数、文件大小）。literature 下的新版本统一替代 paper-retrieval 的旧版本。重复文件包括：pdf_download_engine.py、unified_download.py、arxiv_final.py、crossref_search.py、openalex_search.py、search_s2.py、pubmed_search.py 等。

**Pitfall — 项目特定 references 不合并**：
research-paper-search 的 50 个 references 中，约 34 个是具体论文排雷记录（adhd-notebook-optimization、stroke-paper-api-quirks、v86-scan-results 等），属于历史垃圾，不应合并进 literature，仅合并通用 PDF/下载/API/元数据相关的 16 个。

## 附录：参考文件

（详见各文件：search-download-architecture.md, pubscholar-api-signature.md, pubscholar-curl-api-fix.md, s2-dual-key-failover.md）

## 验证清单

- [ ] 每个数据源有独立 Python 模块
- [ ] 每个模块导出统一接口（search 函数）
- [ ] 输入输出符合数据契约（包含 pdf_url + local_links + links）
- [ ] CLI 入口支持 search/download/verify/pipeline 四个子命令
- [ ] 多源检索有去重逻辑
- [ ] API 错误不阻塞主流程
- [ ] 每个 paper dict 包含 pdf_url（最优先 PDF 直链）
- [ ] 每个 paper dict 包含 local_links（PDF 直链数组）
- [ ] 每个 paper dict 包含 links（所有可用链接字典）