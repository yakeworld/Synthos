---
name: knowledge-acquisition
category: core
signature: "knowledge-acquisition -> core: 多源学术论文检索"
description: 多源学术论文检索 — 脚本驱动，零临时编程。
author: Synthos
license: MIT
version: 2.0.0
author_type: cognitive-atom
priority: P0
description: 多源学术论文检索：Semantic Scholar / PubMed / Crossref / OpenAlex / arXiv。脚本驱动执行，零临时编程。
allowed-tools: terminal, Read, Write
metadata:
  synthos:
    priority: P0
    atom_type: cognitive-atom
    description: External knowledge acquisition — script-driven search. No ad-hoc curl.
    signature: "topic: str, sources: list[str], date_range: str -> candidates: list[PaperCandidate]"
    related_skills: ['knowledge-extraction', 'association-discovery', 'pdf-download-racing']
---

# 知识获取 (Knowledge Acquisition)

> 致知在格物。物格而后知至。

## 原理层·文言

> 多源求索，博观约取。宁缺毋滥，求真为要。
> 凡文必求真，凡数必溯源，凡引必可验。
> 搜于六方而不偏，核于四维而不妄。

## 方法层·白话

**Agent-native 认知原子。文献检索 100% 通过脚本执行，禁止临时拼 curl 命令。**

- 检索 → 调用 `scripts/literature.py search`（统一入口，支持字段过滤和 DOI 精确检索）
- PDF 下载 → 调用 `scripts/unified_download.py`
- 所有逻辑封装在脚本中，SKILL.md 只定义**何时调用、传什么参数、如何处理输出**

## 触发条件

- 需要检索学术文献（主题/关键词/研究问题）
- 上游 research-ideation 产出方向需文献支撑
- 下游 knowledge-extraction / association-discovery 等待输入
- 用户要求"搜索文献/查论文/找论文"

## 执行步骤（固定流程）

### Step 1: 提取查询参数

从用户输入提取：
- `topic` — 研究主题（必需）
- `keywords` — 关键词列表（可选，不提供则自动推导）
- `year_range` — 年份范围 [起始, 终止]（可选，默认 [2020, 2026]）
- `max_papers` — 最大返回数（可选，默认 15）

### Step 2: 执行检索（调用脚本）

```bash
cd /media/yakeworld/sda2/Synthos/skills/extended/research-tools/research/paper-retrieval/scripts/

# 方案 A: 四源统一检索（推荐，快速）
python3 literature.py search "{topic}" --max {max_papers} --output {output_dir}/search_results.json

# 方案 B: 8 源统一入口（需更完整结果）
python3 literature.py search "{topic}" --sources crossref pubmed openalex arxiv --max {max_papers} --output {output_dir}/search_results.json

# 前置检查：连通性测试（首次执行或怀疑网络异常时）
python3 literature.py test
```

**环境要求**：
- `SEMANTIC_SCHOLAR_API_KEY` — 必需（检测空值后自动回退）
- 网络可达：Semantic Scholar / PubMed / OpenAlex / arXiv API

**脚本输出**：标准 JSON 格式，包含 `papers` 列表 + `search_meta`。字段见输出契约。

### Step 3: 去重与验证

脚本已内置去重。Agent 只需验证：
- [ ] 脚本 exit code 为 0
- [ ] 输出 JSON 解析成功
- [ ] 结果数 ≥ 1（无结果 → 报告"未找到相关文献"）
- [ ] 每条结果有 `provenance` 字段

### Step 4: 幻觉检测（调用验证脚本）

对检索结果执行引用验证：
- TF（完全虚构）/ PAC（部分虚构）/ IH（不完整引用）/ PH（幻影引用）/ SH（来源混淆）
- 参考：`refs/CITATION_VERIFICATION.md`

### Step 5: PDF 下载（可选）

```bash
cd /media/yakeworld/sda2/Synthos/skills/extended/research-tools/research/paper-retrieval/scripts/

# 批量下载 — unified_download.py 要求 JSON 格式为 {"papers": [{"title":"...", "doi":"...", "source":"..."}, ...]}
# 如果搜索结果不是此格式，需要先转换（见陷阱）
python3 unified_download.py --batch {output_dir}/search_results.json --output-dir {pdf_output_dir}

# 单篇下载
python3 unified_download.py {DOI_or_ID} --output {output_dir}/paper.pdf
```

**输出**：PDF 文件 + `download_record.json`（来源、MD5、耗时）

### Step 6: 输出交付

将检索结果 JSON 保存为 `{session_dir}/ka_results.json`，供下游知识提取使用。

## 输入契约

| 字段 | 类型 | 必需 | 说明 |
|:-----|:-----|:----:|:-----|
| topic | string | ✅ | 研究主题 / 关键问题 |
| keywords | list[str] | ❌ | 关键词（不提供则自动推导） |
| max_papers | int | ❌ | 最大返回数（默认 15） |
| year_range | [int, int] | ❌ | 年份范围（默认 [2020, 2026]） |

## 输出契约

```json
{
  "papers": [{
    "title": "论文标题",
    "authors": ["作者1", "作者2"],
    "year": 2024,
    "source": "semantic_scholar | pubmed | arxiv | openalex | crossref",
    "external_ids": {"DOI": "10.xxx", "arXiv": "xxxx.xxxxx"},
    "abstract": "摘要...",
    "url": "https://...",
    "pdf_url": "https://...",
    "citation_count": 42,
    "provenance": "source=source_name, query=关键词"
  }],
  "total_found": 15,
  "search_meta": {
    "sources_queried": ["S2", "PubMed", "OpenAlex"],
    "sources_failed": [],
    "query_time_ms": 1234
  }
}
```

## 脚本清单

| 脚本 | 路径 | 用途 | 入口 |
|------|------|------|------|
| literature.py | `../extended/.../scripts/` | 统一检索/下载/验证 | `python3 literature.py search "query"` |
# 废弃: unified_search.py 和 multi_source_search.py 已被 literature.py 取代
| unified_download.py | `../extended/.../scripts/` | PDF 全文下载 | `python3 unified_download.py --batch results.json` |
| pdf_download_engine.py | `../extended/.../scripts/` | 下载核心引擎（30+ 源） | 被 unified_download.py 调用 |

**脚本工作目录**：`../extended/research-tools/research/paper-retrieval/scripts/`

## 陷阱（快速参考）

> 完整陷阱见 `refs/academic-api-troubleshooting.md`

- **严禁使用临时脚本** — 文献检索 100% 走 `literature.py` 统一入口。禁止在 `/tmp/` 写临时 Python 文件或用 `subprocess` 调用脚本 — 所有逻辑已在脚本中封装。这是用户明确纠正过的纪律。
- **S2 API Key 为空** — `literature.py` 使用 sources/semantic_scholar.py，双 key 轮换自动回退到 PubMed + OpenAlex + arXiv。
- **unified_download.py 批量格式不兼容** — `unified_download.py --batch` 期望 `{"papers": [...]}` 格式。`literature.py search` 输出包含 `papers` 数组，可直接提取传给 `--batch`，或改用单篇下载。
- **PubMed 多词静默失败**：用 `+` 或 `AND` 连接词 → 详见 refs
- **PubMed 多词静默失败**：用 `+` 或 `AND` 连接词 → 详见 refs
- **OpenAlex 返回 NoneType 错误** — 某些关键词查询（如带连字符的词组）触发 `AttributeError: 'NoneType' object has no attribute 'get'`，原因是 `authorships` 字段为 None。处理方案：在 `_reconstruct_abstract` 和作者列表构建时增加 `or []` 保护。
- **OpenAlex `search` 是全文搜索**：用 `filter=` 而非 `from_publication_date=` → 详见 refs
- **arXiv 需加 `-L` 跟随重定向** → 由脚本处理，Agent 无需关心
- **PubMed E-Utilities 是当前主力检索源（2026-07-10 实测）**：无需认证，完全可用。ESearch（搜索）+ EFetch（摘要 XML）。XML 解析需用 `<PMID>` 标签（非 `PMID-xxx`），作者用 `<Author><LastName><FirstName>` 结构。
- **OA 直链 100% 被出版商反爬（2026-07-09 实测）**：MDPI/IOP/Nature/Elsevier/Springer/JAMA 全部返回 403/HTML。必须用 `verify_pdf()` 检查 `%PDF-` magic number，空字符串 `pdf_url` 不等于无链接（可能 `links.oa` 中有有效链接）。
- **Sci-Hub 所有域名需人机验证（2026-07-10）**：仅 `sci-hub.ru` 的 Altcha 数学题可自动化；需通过 `100.65.157.17:8118` HTTP 代理。ss 代理（`SS_CONFIG empty`）不可用。Playwright 自动化需用户授权。

## 验证清单

- [ ] 检索脚本 exit code = 0
- [ ] 至少 3 个数据源查询成功（在 search_meta.sources_queried 中）
- [ ] 所有结果有 provenance 字段
- [ ] 去重完成（无重复标题）
- [ ] PDF 下载失败不阻塞主流程
- [ ] 输出 JSON 兼容下游 knowledge-extraction

## 边界声明

- 不保证找到任何论文（查询无效或网络不可达时返回空）
- 不保证找到全文 PDF（受限于 OA/Sci-Hub 可用性）
- 不执行自行编写的 curl 命令 — 所有检索走脚本
- 不缓存结果 — 每次调用脚本产生新结果

## Golden 集合

- Golden Input: `{topic: "vestibular ocular reflex", max_papers: 10}`
- Golden Output: JSON with ≥3 papers, provenance, source coverage
- Golden Error: exit code 1 when all sources fail

## 参考文档

- `references/academic-api-troubleshooting.md` — API 常见问题与解决方案
- `references/literature-scan-without-s2-key.md` — 无 S2 Key 时的回退方案
- `references/supplementary-literature-search.md` — 参考文献补充检索与质量筛选流程（多方向检索→评分→筛选→下载→Markdown）
## 参考文档

- `references/academic-api-troubleshooting.md` — API 常见问题与解决方案
- `references/literature-scan-without-s2-key.md` — 无 S2 Key 时的回退方案
- `references/supplementary-literature-search.md` — 参考文献补充检索与质量筛选流程（多方向检索→评分→筛选→下载→Markdown）
- `refs/literature-scan-without-s2-key.md` — 无 S2 Key 时的回退方案
- `refs/CHANGE_LOG.md` — 技能变更记录
- `refs/IO_CONTRACT.md` — 输入输出契约详情
