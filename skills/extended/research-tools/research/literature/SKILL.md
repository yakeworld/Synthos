---
name: literature
category: research-tools
signature: 'literature -> research-tools: 文献检索统一入口'
description: 文献检索统一入口 — 搜索、下载、验证三位一体，多源聚合，管道编排。
version: 5.2.0
author: Synthos
license: MIT
updated: 2026-07-19
metadata:
  synthos:
    signature: 'literature -> research-tools: 文献检索统一入口'
    atom_type: mechanical
    priority: P2
    description: 文献检索统一入口 — 搜索、下载、验证三位一体，多源聚合，管道编排。
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
    - references/ncbi-pmc-pdf-access-change-2026-07-14.md
    - references/s2-api-fields-2026-07-15.md
    - references/pubscholar-api-2026-07-15.md
    - references/knowledge-acquisition-source-status-2026-07-15.md
    - references/pmc-pdf-pandoc-replacement-2026-07-15.md
    - references/literature-cli-bug-workaround.md
    synthos_version: 5.2.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
allowed-tools:
- terminal
- read_file
- write_file
- session_search
---


# 文献检索 (Literature)

> 多源求索，博观约取。

## IO_CONTRACT

- **input**: `query: str` — 检索主题词（`literature search` / `jabkit-rs fetch --query` 入口）
- **input**: `--sources: list[str]` — 数据源选择（默认 5 源: semantic_scholar, pubmed, crossref, arxiv, pubscholar）
- **input**: `SEMANTIC_SCHOLAR_API_KEY: env` — S2 单 key（必需，无轮换）
- **input**: `papers.json: file` — `download --input` 所需的 `{"papers": [...]}` 列表文件
- **output**: `candidate_records: json` — 多源聚合的候选论文元数据（title/authors/DOI/pdf_url）
- **output**: `output_dir/*.pdf` — `literature.py pipeline` 下载并 `%PDF-` 魔数验证的全文 PDF
- **output**: `diagnose_report: json` — `literature diagnose` 三阶段诊断（7 源检索 + DOI 解析 + 12 通道下载测试）

## 原则 (Principles)

> **多源求索，博观约取。** 默认 5 源聚合，交叉印证去偏；单源结论易失之偏，博观而后约取。
> **凡下必验，魔数为准。** PDF 落盘必验 `%PDF-` 魔数与 pdfinfo 标题，排除串流与伪件，下载以验证为准绳。
> **源常变易，以诊为凭。** API 屡有更易（S2 字段、Crossref mail 参数、PMC 直链失效），以 `literature diagnose` 三阶段实测判定源之可用性，不凭记忆行事。


## Golden 集合 · GOLDEN SET

- **Golden Input**: `literature search "pupil light reflex ODE" --sources crossref pubmed --max 100`（检索）+ `{"papers": [...]}` 文件 → `literature.py pipeline --input`
- **Golden Output**: 候选 records JSON（title/authors/DOI/pdf_url 齐备）；管线落盘 `output_dir/*.pdf` 且每篇 `%PDF-` 魔数 + pdfinfo 标题验证通过；`literature diagnose` 输出三阶段 JSON（7 源检索 + DOI 解析 + 12 通道下载测试）
- **Golden Error**: S2 请求仍带 `pdfUrls`/`urls` 字段 → API 返回 400 `Unrecognized or unsupported fields`；PubScholar 已关闭 API → 静默返回空列表，须降级其余 4 源

## 2026-07-20 清理说明

**scripts/ 已删除**。旧检索脚本代码已迁移到独立 pip 包：
- **`tools/literature-search/`** — pip 包（`pip install .` 即可安装），代码路径 `src/literature_search/`
- GitHub: `github.com/yakeworld/literature-search`
- 检索已统一使用 **jabkit**（26 源，本地 recompiled）

本 SKILL.md 保留作为**下载管道架构和陷阱的知识参考**。`tools/` 目录不在 git 追踪中（`tools/` 已入 .gitignore）。

## 架构变更（2026-07）

**文献检索已统一为 `jabkit` 入口。** `literature.py`（本 skill）降级为 **PDF 下载与管线编排**的辅助工具。

```
检索（搜索 BibTeX） → jabkit-rs fetch（26 源，统一入口）
下载（获取全文 PDF） → literature.py download（bban.top / Sci-Hub 等）
管线（批量处理）     → literature.py pipeline
```

**完整链路**：`search() → 获取 {pdf_url, local_links, links} → 遍历 links 下载 → 保存到目标目录`

## 触发条件
- 需要**下载**论文全文（PDF 下载层）
- 需要验证论文引用质量
- 需要执行**下载→验证**管线
- jabkit 不可用时的检索回退

## 数据源（7 源 + 4 扩展源）

**已持久化到代码（sources/*.py）：**

| 数据源 | API | Key | PDF 链接 | 状态 | 用途 |
|--------|-----|-----|----------|------|------|
| Semantic Scholar | 直连 | 单 key（SEMANTIC_SCHOLAR_API_KEY） | ✅ openAccessPdf | 可用（带key） | 主要检索源 |
| PubMed | NCBI E-utilities | 无 | ⚠️ 无直链（有 pmc） | ✅ 可用 | 生物医学文献 |
| CrossRef | 直连 | 无 | ✅ open_access 字段 | ✅ 可用 | 元数据补入、DOI 验证 |
| OpenAlex | 直连 | 无 | ✅ oa_url + oa_pdf | ✅ 可用 | 开放学术图谱 |
| arXiv | 直连 | 无 | ✅ 直接 PDF 链接 | ✅ 可用 | CS/AI 预印本 |
| PubScholar | curl直调POST | APP_ID/SECRET | ✅ local_links CDN | ❌ 开放API关闭，IP封锁 | 中文文献（需开发者凭证/国内IP） |
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

**检索（jabkit 优先）：**

```bash
# jabkit 检索（26 源，S2 已修复）
jabkit-rs fetch --provider=Crossref --query="topic" --porcelain
jabkit-rs fetch --provider=SemanticScholar --query="topic" --porcelain
```

**下载（已迁移至 knowledge-acquisition）：**
PDF 全文下载统一使用 `doi-fetch`，详见 `knowledge-acquisition` skill 的"全文下载"章节。

**管线（literature.py）：**
```bash
python3 literature.py pipeline "topic" --sources crossref pubmed --output-dir /path
python3 literature.py diagnose
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

**2026-07-15 S2 API 字段修复**：S2 Graph API 移除了 `pdfUrls` 和 `urls` 字段（返回 400 `Unrecognized or unsupported fields`）。`fields` 参数改为：`title,authors,year,openAccessPdf,externalIds,venue,citationCount,tldr,abstract,publicationTypes`。

**2026-07-15 S2 Key 多源加载**：`SemanticScholar.API_KEYS` 类属性在模块加载时计算，优先级：(1) `SEMANTIC_SCHOLAR_API_KEY` 环境变量 → (2) `~/.hermes/.env` → (3) `~/.secrets`。`execute_code` 沙箱不 source `.bashrc`/`.secrets`，需从 `.env` 或 `~/.secrets` 手动读取 key。

**2026-07-15 PubScholar API 关闭**：PubScholar 开放 API 已关闭，改为第三方应用认证。POST 返回 {"cause":"第三方应用独立请求时，无此操作权限","failure":true}。IP 级别封锁（当前服务器 IP 被拒）。代码在 `sources/pubscholar.py` 中已加入 `PUBSCHOLAR_APP_ID`/`APP_SECRET` 检查，无凭证时静默返回空列表。**注意**：重大 API 变更需征求用户意见，不应擅自修改默认源配置。恢复路径：RSSHub 路由/国内住宅 IP/浏览器自动化/等待开放 API 恢复。详见 `references/pubscholar-full-analysis-2026-07-15.md`。

**2026-07-15 PMC PDF 替换**：NCBI `/articles/PMC{id}/pdf/` 路径不再提供 PDF（返回 HTML）。`download_pubmed_central()` 重构为：JATS XML → 提取标题/正文 → Markdown → pdflatex → PDF。Unicode 数学符号（≥ ≤ → ∑ μ α）需替换为 ASCII。详见 `references/pmc-pdf-pandoc-replacement-2026-07-15.md`。

**2026-07-15 知识获取源测试**：S2(2.4s, 3篇, 2有PDF)、PubMed(3.7s, 3篇, 1有PDF)、CrossRef(1.7s, 3篇, 0有PDF)、OpenAlex(62.6s, 3篇, 3有PDF)、arXiv(0.3s, 2篇, 0有PDF)、PubScholar(0.3s, 0篇, 需认证)。4 源正常运行。详见 `references/knowledge-acquisition-source-status-2026-07-15.md`。

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

- ~~**literature.py search 子命令完全失效 (2026-07-15)**:~~ ✅ **已修复 (2026-07-19)**。原因为 CLI 包装层 JSON 输出格式不匹配各源返回，现已修正。search 子命令当前工作正常。
- **`literature test` 传参 bug (2026-07-18 发现, 2026-07-19 修复)**: 原 `run_test()` 函数调下载函数时不传 DOI 参数，导致所有下载层报告 `"error"`。现已修正。改用 `literature diagnose` 进行综合诊断。
- **`literature diagnose` 新增 (2026-07-19)**: 三阶段综合诊断：检索测试（遍历7源）+ DOI解析测试 + 下载测试（12通道，20s超时保护）。输出结构化 JSON。命令：`literature diagnose`。
- **`download/http.py` 文件名冲突**: 文件名 `http.py` 与 Python 标准库 `http` 模块同名。当从 `download/` 目录运行时，`import http.client` 会错误解析到本地文件。目前从 `scripts/` 目录调用可避免。长期需重命名文件。
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
- **PMC PDF 直链已失效（2026-07-14）**：NCBI 不再通过 `/articles/PMC{id}/pdf/{filename}` 提供 PDF（返回 HTML 或 301 重定向），旧实现返回 None 或超时 30s。使用 `download_pubmed_central(pmcs_id)` 函数，它已重构为 XML→Markdown→pandoc→PDF 管线。Unicode 数学符号（≥ ≤ →）必须替换为 ASCII 兼容形式。详见 `references/ncbi-pmc-pdf-access-change-2026-07-14.md`。
- **PubScholar API 已失效（2026-07-15 实测）**：POST `https://www.pubscholar.cn/hky/open/resources/api/v1/articles` 返回 HTML（SPA），非 JSON。`requests.post().json()` 抛 `JSONDecodeError`。状态码 200 但 content-type 为 text/html。代码中 `if resp.status_code != 200: return []` 不会触发（200 是正常状态码），后续 `resp.json()` 失败被 `except Exception: return []` 捕获，返回空列表。如需中文文献，手动通过 PubScholar 网页搜索或等待 API 恢复。
- **literature.py download 需要 JSON 文件**：`--input` 参数必须指向文件路径，不支持 stdin。JSON 格式必须是 `{"papers": [...]}`，不是纯列表。
- **CORE需要API key**：Cloudflare拦截无key请求。免费注册获取key。
- **OpenAlex year=None KeyError**：先做类型检查再切片。
- ~~**SyntaxWarning `\\\\:`**~~: `download/http.py` 第 32 行 docstring 中的非法转义序列。已知。
- ~~**literature.py 脚本缺失**~~: ✅ 脚本存在。
- ~~**PDF 魔数验证用 `startswith` 而非切片**~~: ✅ 已修复。

## 示例 · EXAMPLES

**输入**：`jabkit-rs fetch --provider=Crossref --query="pupil light reflex ODE" --porcelain`
**输出**：~2s 返回 BibTeX 条目（title/authors/DOI/year 齐备），`--max 100` 默认返回 100 篇候选

**输入**：`python3 literature.py pipeline "iris recognition" --sources crossref pubmed --output-dir ./pdfs`
**输出**：`./pdfs/` 下落盘 12 篇 PDF，每篇 `%PDF-` 魔数 + pdfinfo 标题验证通过；diagnose 报告 7 源检索 + 12 通道下载测试全绿

## 约束规则 · RULES

- 检索统一走 `jabkit-rs fetch`（26 源），本 skill 仅负责 PDF 下载与管线编排
- S2 请求 fields 不得含 `pdfUrls`/`urls`（已移除，否则 400）
- CrossRef 请求不带 `mail` 参数，`order` 仅 `desc`/`asc`
- 下载 PDF 必须通过 `%PDF-` 魔数验证 + pdfinfo 标题核对，排除串流
- PubScholar API 已关闭，无凭证时静默返回空列表，须降级其余 4 源

## 验证清单 (Verification)

- [ ] 检索用 `jabkit-rs fetch`（26 源统一入口）；PDF 下载已迁移至 doi-fetch/knowledge-acquisition
- [ ] S2 请求的 fields 已更新（`pdfUrls`/`urls` 已移除，否则 400）；单 key `SEMANTIC_SCHOLAR_API_KEY` 生效
- [ ] CrossRef 请求不带 `mail` 参数、`order` 为 `desc`/`asc`
- [ ] PubMed `esummary` 按扁平 `result` 字典解析（跳过 `uids` 等非字典键）
- [ ] `literature diagnose` 通过（检索 7 源 + DOI 解析 + 12 通道下载测试）
- [ ] 下载 PDF 魔数 `%PDF-` 验证；LibGen 仅作检索源，下载走 bban.top
