---
name: literature
category: research-tools
signature: "literature -> research-tools: 文献检索统一入口"
description: 文献检索统一入口 — 搜索、下载、验证三位一体，多源聚合，管道编排。
version: 4.0.0
author: Synthos
license: MIT
updated: 2026-07-12
metadata:
  synthos:
    signature: "literature search/download/verify/pipeline"
    atom_type: unified-entry
    priority: P0
    description: "文献检索统一包 — 搜索11源（统一返回 pdf_url+local_links+links）、下载核心（pdf_download_engine + unified_download），搜索即获取全文链接。"
    linked_files:
      - references/sci-hub-cdn-bban-top.md
      - references/scihub-domain-scan-2026-07-10.md
      - references/s2-dual-key-failover.md
      - references/s2-deprecated-fields-400-fix-2026-07-11.md
      - references/pmc-fulltext-coverage-analysis.md
      - references/sci-hub-bban-endpoint-notes.md
      - references/paper-pdf-completion-workflow.md
      - references/cornerstone-bib-rebuild-2026-07-11.md
      - references/core-api-2026-07-12.md
      - references/new-sources-2026-07-12.md
      - references/code-recovery-and-source-mismatch.md
      - references/bban-top-cdn-recovery-2026-07-13.md
      - references/libgen-playwright-search.md
      - references/libgen-download-mirror-status.md
      - references/s2-single-key-consolidation-2026-07-15.md
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
- **用户要求"用文献检索技能"** — 这是唯一入口，不要自行调用 Crossref/PubMed 等独立 API

## 数据源（7 源 + 4 扩展源）

**已持久化到代码（sources/*.py）：**

| 数据源 | API | Key | PDF 链接 | 状态 | 用途 |
|--------|-----|-----|----------|------|------|
| Semantic Scholar | 直连 | 单 key（SEMANTIC_SCHOLAR_API_KEY） | ✅ openAccessPdf | 可用（带key） | 主要检索源 |
| PubMed | NCBI E-utilities | 无 | ⚠️ 无直链（有 pmc） | ✅ 可用 | 生物医学文献 |
| CrossRef | 直连 | 无 | ✅ open_access 字段 | ✅ 可用 | 元数据补入、DOI 验证 |
| OpenAlex | 直连 | 无 | ✅ oa_url + oa_pdf | ✅ 可用 | 开放学术图谱 |
| arXiv | 直连 | 无 | ✅ 直接 PDF 链接 | ✅ 可用 | CS/AI 预印本 |
| PubScholar | curl直调POST | 无 | ✅ local_links CDN | ✅ 可用 | 中文文献 |
| Sci-Hub | CDN | 无 | ✅ bban.top/pdf/{DOI}.pdf | ✅ 可用（直连PDF） | 灰区论文兜底 |
| LibGen | Playwright浏览器模拟 | 无 | ✅ 搜索可用，下载需第三方 | ⚠️ 检索可用，下载受限 | 期刊论文+图书备份 |

**LibGen 检索特性（2026-07-15 实测）**:
- **搜索**: POST `https://libgen.bz/batchsearchindex.php`，支持关键词/DOI/书名
- **DOI精确搜索**: 输入 DOI（如 `10.1167/jov.23.9.5216`）直接定位条目
- **返回数据**: 标题、作者、出版社、年份、格式(pdf/epub/djvu)、文件大小、镜像链接
- **条目详情**: 包含完整元数据（DOI、PMC、PMID、作者、出版社、格式、大小）
- **文件列表**: 通过 Playwright 模拟浏览器获取（页面内容 JS 渲染，requests 无法解析）
- **镜像下载**: `randombook.org`、`annas-archive.gl`、`libgen.pw`、`sci-hub.ru`
- ⚠️ **下载受限**: 大部分第三方镜像不可用（randombook返回广告、libgen.pw连接拒绝、annas-archive重定向循环）
- ✅ **检索强大**: 支持期刊论文（Scientific Articles）和图书两个库，DOI 精确检索可用
- 代码位置: `sources/libgen.py`（Playwright 模拟浏览器，~250行）

**已添加到 SKILL.md 但未持久化到代码：**

| 数据源 | 状态 | 说明 |
|--------|------|------|
| Unpaywall | 代码缺失 | 逻辑已描述在 SKILL.md，但 sources/unpaywall.py 不存在 |
| bioRxiv | 代码缺失 | 同上 |
| medRxiv | 代码缺失 | 同上 |
| CORE | 代码缺失 | 同上 |

**私人源**：MedData（机构付费库，不默认使用）

## 实际可运行源

实际代码 `sources/__init__.py` 中的 SOURCE_REGISTRY（6 源）：
```python
SOURCE_REGISTRY = {
    "semantic_scholar", "pubmed", "crossref", "openalex",
    "arxiv", "pubscholar"
}
```

Sci-Hub 和 LibGen 在 `__all__` 中声明但未入 registry（需手动 `--sources scihub libgen` 使用）。

默认源 DEFAULT_SOURCES（5 源）：
```python
["semantic_scholar", "pubmed", "crossref", "arxiv", "pubscholar"]
```

注意：SKILL.md 数据源表格描述 8 源（含 Sci-Hub/LibGen），但 registry 中仅 6 源。Sci-Hub（bban.top CDN）和 LibGen（Playwright）需在 CLI 中手动指定。

下载方法: 所有 PDF 下载统一通过 bban.top CDN 直连完成。
原理: `https://sci.bban.top/pdf/{DOI}.pdf` → 直接返回 PDF 字节（%PDF-）。
无需 HTML 中转，无需域名解析，无需代理。
下载流程: literature.py 中任何有 DOI 的论文，`download` 子命令会自动构建 bban.top URL 下载 PDF。
代码位置: `download/scientific_hub.py`（78 行，仅 bban.top 逻辑）。
旧实现已删除: `tier2_scihub.py`（HTML 中转）、`sci_hud_download.py`（独立脚本）、`aa-scihub-download` 技能。

注意：SKILL.md 声称的 11 源中，只有 7 源有对应 Python 文件。CORE/Unpaywall/bioRxiv/medRxiv 在 SKILL.md 和数据源表格中有描述，但 `sources/` 目录中没有对应 `.py` 文件。这些是**记忆中的知识，代码中不存在**。如果从 git 恢复代码（如 git checkout），这 4 个源会丢失。

## 默认检索策略

**文献监控替代搜索（当 literature.py 不可用时）**：
通过 PubMed E-utilities API 直接搜索（见 `research/daily-intelligence-briefing/references/literature-search-pubmed-pattern.md`）。
步骤：esearch → esummary → 过滤 → efetch 获取摘要。无需 API key。

- 默认含 S2（有API key，不会卡死）
- 论文检索优先：PubMed + CrossRef + OpenAlex + arXiv（4源不可少）
- ODE/PINN/CS类论文 PubMed 覆盖差，必须同时搜 S2 + CrossRef + OpenAlex

## CLI用法

```bash
# 基本检索
python3 literature.py search "topic" --sources pubmed crossref openalex arxiv core --max 10

# DOI精确检索
python3 literature.py search "doi:10.1038/s41586-019-1799-6"

# 字段过滤
python3 literature.py search "deep learning author:hinton year:2020"

# 下载
python3 literature.py download --input search_results.json --output-dir /tmp/pdfs

# 管线
python3 literature.py pipeline "topic" --sources crossref pubmed --output-dir /path

# 测试连通性
python3 literature.py test
```

## 环境变量

```bash
# 唯一需要的 API key（单 key，无双 key 轮换）
export SEMANTIC_SCHOLAR_API_KEY="..."
# S2_FALLBACK_KEY 已移除 — 不再需要

export CORE_API_KEY="..."      # 免费注册 https://core.ac.uk/api-key/
export UNPAYWALL_EMAIL="..."   # 可选，提高速率限制
```

**2026-07-15 S2 单 key 修正**：S2_FALLBACK_KEY 已删除，`semantic_scholar.py` 仅读取 `SEMANTIC_SCHOLAR_API_KEY`。`_try_next_key()` 机制移除。key 同时存在于 `~/.bashrc` 和 `~/.secrets`，值一致。S2 不卡死。

## 代码恢复与版本管理

**代码位置**：`skills/extended/research-tools/research/literature/scripts/`

**git 恢复方法**（代码被删除时）：
```bash
cd /media/yakeworld/sda2/Synthos
# 完整恢复 literature 代码（含 download/ 目录）
git checkout d18616e -- skills/extended/research-tools/research/literature/
```
commit `d18616e` 是最后完整包含 literature 代码的提交。恢复后需修复 `download/http.py` 中 `\:` SyntaxWarning。

**已知代码丢失**（git 中不存在但 SKILL.md 有描述）：
- `sources/unpaywall.py` — 在 memory 中有逻辑描述，但代码未提交
- `sources/bioRxiv.py` — 同上
- `sources/medRxiv.py` — 同上
- `sources/core.py` — 同上

这些需要在下次会话中重新从 memory 中恢复或重新编写。

## Pitfalls

- **LibGen 搜索需要 Playwright（JS 渲染）** — libgen.bz 的条目详情和文件列表完全由 JS 渲染，requests/curl 无法解析。必须使用 Playwright 模拟浏览器：`from sources.libgen import LibGen; LibGen.search("query")`。纯 HTTP 搜索只返回 MD5 ID 列表，不含详细信息。
- **LibGen 下载链接不可靠** — LibGen 提供的第三方镜像（randombook.org、annas-archive.gl、libgen.pw）大部分不可用：randombook 返回广告页面、libgen.pw 连接拒绝、annas-archive 重定向循环。仅 Sci-Hub.ru 返回 HTML 但不一定是 PDF。**LibGen 作为检索源非常强大（DOI精确检索、期刊论文+图书），但作为下载源需要备用方案。** 下载策略：(1) 第一优先 bban.top CDN，(2) 第二优先 Crossref/PubMed/OA 直链，(3) 第三优先 S2 openAccessPdf，(4) LibGen 仅作为检索源。
- **bban.top 是唯一可靠的 Sci-Hub 下载入口** — `https://sci.bban.top/pdf/{DOI}.pdf` 直连返回 PDF 字节。旧实现（HTML 中转、域名查找）已全部删除。
- **S2 有 API key 不卡死**：默认包含 S2，单 key，无自动轮换。如遇限流可手动去掉 S2 用三源替代。
- **Crossref不精确**：通用作者名（Smith, Wang, Kim）会被匹配到错误论文。用标题+作者全名精确搜索，或用S2。
- **CrossRef API 参数变更（2026-07-13 确认）**：`mail` 参数已被移除，带该参数会返回 400 `unknown-parameter`。`order` 参数必须为 `desc` 或 `asc`（不是 `descending`/`ascending`）。正确的 query 格式：`GET /works?query=...&sort=published-print&order=desc&rows=10`。Python urllib 的 `urlencode` 会产生 `+` 编码，需转为空格后与 curl 一致，或直接使用 `+`（CrossRef 接受两种格式）。
- **PubMed esummary 结构（2026-07-13 确认）**：`esummary` 返回的 `result` 是扁平字典，键是 PMID 字符串。结构是 `{... "result": {"42432319": {...}, "42430971": {...}}}`，**不是** `result.pubmed`。解析时必须遍历 `result` 的所有键值对（跳过非字典类型的键如 `uids`）。
- **文献监控替代搜索路径（2026-07-13）**：当 literature.py 不可用时（脚本缺失），可通过 PubMed E-utilities API 直接搜索。PubMed 搜索覆盖广、精度高，是文献监控的首选替代方案。OpenAlex API 在 cron 环境中可能因搜索词编码问题返回 400，需 URL encode 空格为 `+`。
- **bban.top CDN 恢复（2026-07-13 最终确认）** — `https://sci.bban.top/pdf/{DOI}.pdf` 直连返回真实 PDF（791KB，7页，DOI 10.1016/j.jcrs.2019.04.024 验证通过）。唯一有效 Sci-Hub 入口。GET 返回 PDF 字节（%PDF-），无需 HTML 中转，无需 iframe 解析，无需域名查找。代码简化为 78 行（download/scientific_hub.py），所有文献下载通过此链路完成。
- **PIPELINE PDF 来源**：管线中 724 篇参考文献 PDF（709 真实，1179 MB）是通过 literature.py 多源获取的（Crossref、PubMed、CORE 等），不是通过 bban.top 下载的。bban.top 失效不影响已下载的文献，但影响新论文获取。
- **PMC URL 不是 PDF 直链**：PubMed PMC 文章返回的 `pdf_url` 是 HTML 页面（`https://www.ncbi.nlm.nih.gov/pmc/articles/PMC.../`），不是 PDF 文件。`smart_download()` 下载后 `verify_pdf()` 失败（HTML 不是 `%PDF-`），返回 None。**解决方案**：使用 `pmc_fulltext.py` 通过 E-utilities 获取 JATS XML → pandoc 转换 PDF；或从 `tier1_oa.py` 中 `download_pubmed_central()` 调用（需传入 PMCID）。
- **literature.py download 需要 JSON 文件**：`--input` 参数必须指向文件路径，不支持 stdin。JSON 格式必须是 `{"papers": [...]}`，不是纯列表。
- **CORE需要API key**：Cloudflare拦截无key请求。免费注册获取key。
- **OpenAlex year=None KeyError**：先做类型检查再切片。
- **SyntaxWarning `\\:`**：`download/http.py` 第 32 行 docstring 中有非法转义序列 `/\\\\:`，会导致 Python 3.12 语法警告。修复：改为 `/\\\\\\\\:` 或直接写冒号 `/ : ? " < > |`。
- **literature.py 脚本缺失**：`skills/extended/research-tools/research/literature/` 目录下无 Python 脚本文件，SKILL.md 中描述的来源处理代码均不存在。git 中也不存在。如需执行文献检索，必须通过独立 API 调用（PubMed/E-utilities、CrossRef、OpenAlex）或先恢复代码（`git checkout d18616e`）。