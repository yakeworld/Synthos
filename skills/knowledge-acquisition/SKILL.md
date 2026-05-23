---
name: knowledge-acquisition
description: Search and retrieve academic papers from multiple sources (Semantic Scholar, PubMed, Crossref, OpenAlex, arXiv, bioRxiv/medRxiv, local-absorption-db) using Agent tools. Includes API resilience layer: local cache, automatic fallback chain, and offline absorption database backup. Returns paper metadata, abstracts, and PDF files. Agent-native — uses Hermes skills + terminal/curl, no Python code.
version: 1.5.0
author: Synthos Agent
license: MIT
allowed-tools: terminal web delegate_task Read Write
signature: "topic: str, sources: list -> papers: list[Paper], total_found: int"
metadata:
  synthos_atom_type: "cognitive"
  synthos_version: "1.5.0"
  synthos_skill_md_hash: "2f7b3ee8e9f5d1a6c4b8a0e3d9f2c7b5a1e6d4f8c0a3b7e9d2f5c1a4b8e0d7"
  synthos_io_contract_ref: "references/IO_CONTRACT.md"
  synthos_citation_verification_ref: "references/CITATION_VERIFICATION.md"
  synthos_change_log_ref: "references/CHANGE_LOG.md"
  synthos_asserted_compliance: "P0,P2,P3"
  synthos_depends_on: "semantic-scholar, pubmed, arxiv, openalex, biorxiv, research-paper-search, scientific-database-lookup"
  synthos_author: "Synthos Agent (v1.4.0 — API resilience layer + local cache)"
  synthos_data_access_level: "raw"
---

# 知识获取 (Knowledge Acquisition) - 认知原子 #1

## 原理层·文言

### 求知之道

> 知者，认知之始也。先求于外，而后内化。
> 无求则无知，无源则无流。
> 搜于六方而不偏，核于四维而不妄。
> 凡文必求真，凡数必溯源，凡引必可验。
> 宁无所得，不取伪术。诚则明矣，伪则暗矣。

**核心理念**：知识获取是认知链的起点。六方之搜（S2/PubMed/Crossref/OpenAlex/arXiv/bioRxiv）不可偏废，四维之验（DOI/arXiv/S2/相关性）不可省略。不虚构、不编造、不臆测。零篇论文是有效结果，虚构论文是致命错误。

## 方法层·白话

### 触发条件

在以下情况加载本技能：

- 需要检索学术文献时（给定研究主题/关键词/研究问题）
- 上游 research-ideation 原子产出了研究方向，需要配套文献支撑
- 下游 knowledge-extraction 原子等待输入
- 用户明确要求"搜索文献/查论文/找资料"

### 概述
从外部源获取学术知识：检索论文、提取摘要、下载全文。是认知链条的起点。
**Agent-native**: 本原子由 Agent 直接执行，使用 Hermes 技能库中的搜索工具和 terminal + curl，没有 Python 依赖。

**v1.4.0 新增API弹性层**: 本地查询缓存 + 自动回退链 + 离线吸收库兜底。当所有外部API都失败时，从本地吸收追踪数据库(absorption-tracked.json)构建最少文献基。

**v1.5.0 新增铁律（写作闭环审计强制）**:
- 🚫 **严禁模拟输出** — 所有文献必须真实搜索、真实下载。不存在则如实报告0篇。不得虚构DOI/标题/作者/摘要。
- 📄 **PDF命名规范** — 每篇下载的PDF文件名 = `{BibTeX_key}.pdf`（如 `Chen2025.pdf`），一目了然区分已下载/未下载。
- 📚 **摘要BibTeX格式** — 每篇论文的摘要/元数据必须以 `.bib` 格式保存到 `references/` 目录下。

### 输入契约
- `search_query`: 搜索查询字符串（必填）
- `sources`: 数据来源列表，可选（默认全部）。有效值: `semantic_scholar`, `pubmed`, `arxiv`, `openalex`, `crossref`, `biorxiv`, `local_absorption_db`
- `max_results`: 最大结果数，默认 100
- `domain`: 研究领域（可选，用于过滤）
- `use_cache`: 是否使用本地缓存，默认 true（可选）

### 输出契约
```json
{
  "raw_papers": [
    {
      "title": "论文标题",
      "doi": "10.xxx/...",
      "abstract": "摘要文本",
      "year": 2024,
      "authors": ["Author A"],
      "source": "semantic_scholar",
      "open_access_url": "https://...",
      "arxiv_id": "",
      "pdf_status": "open_access|pmc|arxiv|unavailable",
      "citation_verification": {
        "status": "verified|suspicious|hallucinated|skipped",
        "confidence": 0.95,
        "methods_used": ["doi", "title_search"],
        "integrity_score": 0.95,
        "relevance_score": 0.85,
        "details": "DOI resolved via Crossref. Title match confirmed via S2."
      }
    }
  ],
  "metadata": {
    "total_found": 15,
    "sources_used": ["semantic_scholar", "pubmed", "local_absorption_db"],
    "sources_attempted": ["semantic_scholar", "pubmed", "arxiv", "openalex", "crossref", "biorxiv", "local_absorption_db"],
    "sources_failed": ["arxiv", "openalex"],
    "cache_hit": true,
    "cache_path": "outputs/search-cache/20260518_adhd_mld5j2.json"
  },
  "evidence_chain": [
    {"source": "semantic_scholar", "query": "ADHD eye tracking", "papers_returned": 5, "timestamp": "..."},
    {"source": "pubmed", "query": "ADHD eye tracking", "papers_returned": 3, "timestamp": "..."}
  ]
}
```

### 执行步骤

#### 0. 加载外部技能
在开始之前，加载以下 Hermes 技能作为参考：
- `semantic-scholar` — S2 API 端点、字段、格式
- `pubmed` — PubMed E-utilities 端点
- `arxiv` — arXiv API 格式
- `research-paper-search` — 多源搜索 + PDF 下载参考
- `openalex` — OpenAlex API（可选，无 key 即可用）
- `biorxiv` — bioRxiv/medRxiv 预印本 API
- `scientific-database-lookup` — 科学数据库路由（备选源）

#### 0.5 [v1.4.0新增] 本地缓存检查
在调用任何外部API之前，先检查本地缓存：

```
cache_key = sha256(降格查询字符串)的前12位
cache_path = "outputs/search-cache/{cache_key}.json"

if use_cache and file_exists(cache_path):
    读取缓存文件
    如果 < 24小时旧 → 直接返回缓存结果（记录 cache_hit=true）
    如果 >= 24小时旧 → 作为后备数据源同步搜索（记录 cache_hit=stale）
```

缓存路径：`/media/yakeworld/sda2/Synthos/outputs/search-cache/{cache_key}.json`

#### 0.6 [v1.4.0新增] API回退策略定义
定义搜索源的回退优先级链。当高级别源失败时自动降级到下一级：

| 优先级 | 源 | 依赖 | 典型失败模式 | 回退动作 |
|:------:|:---|:-----|:------------|:---------|
| 1 | Semantic Scholar | 外部API + 有效key | 1次/秒速率限制 | sleep 1s后重试1次 → 失败则尝试PubMed |
| 2 | PubMed | 外部API（无key） | 3次/秒无key限速 | sleep 0.4s后重试 → 失败则尝试Crossref |
| 3 | Crossref | 外部API | 偶尔空结果/slow | 标记failed→尝试OpenAlex |
| 3 | OpenAlex | 外部API | 偶尔不可用 | 标记failed→尝试arXiv |
| 4 | arXiv | 外部API | HTTP (非HTTPS) | 标记failed→尝试bioRxiv |
| 5 | bioRxiv/medRxiv | 外部API | 空collection | 标记failed→尝试web_scrape |
| 6 | **web_scrape** | **浏览器/curl** | **无结构化数据** | **降级→尝试local_absorption_db** |
| 7 | **local_absorption_db** | **本地文件** | **无（保证可用）** | **提取相关项目作为文献** |

关键规则：
- **每个源最多重试1次**（重试间隔1秒）
- 连续2个源失败后，**自动启用缓存兜底**（即使缓存已过期）
- 连续3个源失败后，**自动启用 local_absorption_db 兜底**
- 所有失败记录到 `sources_failed`

#### 1. 多关键词搜索策略 [v1.5.0]

对同一个研究主题，生成 **3-5 个不同关键词组合** 并行搜索，最大化覆盖率：

| 关键词变体 | 示例（BPPV + 机器学习） | 侧重 |
|:----------|:----------------------|:-----|
| 核心词 | `BPPV machine learning diagnosis` | 最精确，limit=100 |
| 同义词 | `benign paroxysmal positional vertigo deep learning` | 覆盖术语变体，limit=100 |
| 方法学 | `nystagmus classification automated BPPV` | 覆盖方法类文献，limit=100 |
| 中英文 | `良性阵发性位置性眩晕 机器学习 诊断` | 中英文语料，limit=100 |
| 拓展词 | `vestibular disease AI eye tracking` | 扩大范围，limit=100 |

策略：
1. 先用核心词搜索（最高精准度）
2. 如果结果 < 5 篇，自动用同义词/拓展词补搜
3. 去重后合并结果
4. 每换一个关键词，**必须遵守对应 API 的速率限制**

#### 1b. 并行搜索各数据源（带回退链）

使用 terminal + curl 并发查询。按优先级顺序启动，首个成功的源即返回结果。
如果首选源失败，自动降级到下一个优先级。

##### 优先级1: Semantic Scholar
```
curl -s --max-time 15 -H "x-api-key: $SEMANTIC_SCHOLAR_API_KEY" \
  "https://api.semanticscholar.org/graph/v1/paper/search?query=<encoded_query>&limit=100&fields=title,year,abstract,authors,externalIds,citationCount,openAccessPdf"
```
- timeout=15s，超过即视为失败
- **速率限制: 1次/秒** — 每次 curl 调用后必须 sleep 1s
- 如果返回429 → sleep 1s后重试1次 → 仍429则跳过此源
- 如果返回空data数组 → 视为成功（0结果），不降级

##### 优先级2: PubMed
```
# Step 1: ESearch — 拿 PMID 列表
curl -s --max-time 10 "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=<encoded_query>&retmax=100&retmode=json"

# Step 2: ESummary — 拿元数据
curl -s --max-time 10 "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=<comma_separated_ids>&retmode=json"
```
- timeout=10s per call
- 中间 sleep 0.5s（无key时）

##### 优先级3: Crossref
```
curl -s --max-time 15 "https://api.crossref.org/works?query=<encoded_query>&rows=100&select=DOI,title,author,abstract,issued,container-title,reference"
```
- timeout=15s
- 注意：`select` 参数不能包含 `publication-date` 或 `citation-count`

##### 优先级3: OpenAlex
```
curl -s --max-time 15 "https://api.openalex.org/works?search=<encoded_query>&per_page=100&sort=relevance_score:desc"
```
- timeout=15s
- `abstract_inverted_index` 需要按数字键排序后拼接

##### 优先级4: arXiv
```
curl -s --max-time 15 "http://export.arxiv.org/api/query?search_query=all:<encoded_query>&max_results=100"
```
- timeout=15s
- 注意：HTTP 不是 HTTPS

##### 优先级5: bioRxiv / medRxiv
```
curl -s --max-time 10 "https://api.biorxiv.org/details/biorxiv/<encoded_query>"
curl -s --max-time 10 "https://api.biorxiv.org/details/medrxiv/<encoded_query>"
```

##### 优先级6: Web Scrape — 深度网页抓取 [v1.6.0 新增]

**当所有结构化 API 都无结果时，用无头浏览器或 curl 抓取非结构化网页。**

**吸收自 GPT-Researcher 的深度网页搜索方法论，但以纯 skill 方式实现（零 Python）。**

```bash
# 策略A: 学术搜索引擎（无需浏览器）
curl -sL --max-time 15 "https://scholar.google.com/scholar?q=<encoded_query>&hl=en&as_sdt=0%2C5&as_ylo=2020"
# 注意: Google Scholar 有反爬，可能返回 503

# 策略B: 通用搜索引擎（降级兜底）
curl -sL --max-time 15 "https://html.duckduckgo.com/html/?q=<encoded_query>"

# 策略C: 直接抓取已知 URL 列表（如会议主页、实验室页面）
curl -sL --max-time 30 "<target_url>"
```

**提取方法**：通过 `terminal` 调用 `pandoc` 或 `lynx -dump` 将 HTML 转为纯文本，再用 EXT 原子提取结构化信息：

```bash
# 方法1: lynx 转纯文本（推荐，最快）
lynx -dump -nolist <html_file> 2>/dev/null | head -200

# 方法2: pandoc 转 markdown
pandoc <html_file> -t markdown --wrap=none 2>/dev/null
```

**适用场景**：
| 场景 | 示例 URL | 提取内容 |
|:-----|:---------|:---------|
| 预印本平台 | `https://arxiv.org/abs/<id>` | 摘要、作者、引用格式 |
| 会议主页 | `https://2026.iclr.cc/` | Call for papers、截稿日期 |
| 实验室主页 | `https://<lab>.github.io/publications/` | 最新出版物列表 |
| 学术博客 | `https://<blog>/*.html` | 前沿研究评论、对比分析 |

**边界判断**：
- 仅在所有结构化 API（S2/PubMed/Crossref/OpenAlex/arXiv/bioRxiv）失败后启动
- 每次抓取 timeout ≤ 30s
- 抓取结果以纯文本保存到 `outputs/web-scrape/<query>/`，供 EXT 原子提取
- 不抓取需登录/付费的页面
- 遵守 `robots.txt`（通过 `-A "Synthos Academic Research Agent"` User-Agent 声明身份）
- timeout=10s
- 注意：该 API 有时返回空 collection

##### 优先级6: [v1.4.0新增] local_absorption_db（离线兜底）
当所有外部API都失败时，使用本地吸收追踪数据库作为最后的数据源：

```
# 读取 absorption-tracked.json
# 提取所有状态为"absorbed"的项目
# 按与查询关键词的相关性排序
# 返回前N个项目作为 paper-like 条目

搜索策略：
1. 读取 absorption-tracked.json 的 projects 列表
2. 对每个项目：检查 name 和 description 是否包含查询关键词（模糊匹配）
3. 按 star 数量排序（相关性假设：高star项目更相关）
4. 返回匹配的前 max_results 个条目
```

**优势**：保证100%可用（本地文件），数据100%真实（已验证的项目）
**局限**：项目级数据（非论文级），star数需定期更新

#### 2. 去重

按 DOI 精确匹配去重。无 DOI 的按标题归一化后模糊匹配（忽略大小写、标点）。

#### 2.5 [ARS增强] 引用验证 + 5类幻觉检测

对去重后的每篇论文执行4层引用验证 + 5类幻觉分类。读取 `references/CITATION_VERIFICATION.md` 获取完整流程（含TF/PAC/IH/PH/SH五分类法及5种复合欺骗模式）。

验证策略：
1. **L1: DOI验证** — `curl -s "https://api.crossref.org/works/{doi}"` 检查200
2. **L2: arXiv验证**（如有arxiv_id）— `curl -s "http://export.arxiv.org/api/query?id_list={id}"` 检查返回
3. **L3: S2标题交叉搜索** — 搜索标题，计算相似度
4. **L4: LLM相关性评分** — Agent判断论文是否与研究主题相关

输出：在每篇论文中添加 `citation_verification` 字段。状态为 `hallucinated` 的论文从输出中排除（记录到 evidence_chain）。

预期耗时：每篇论文约5-10秒（curl API调用+Agent推理评分）。

#### 3. 下载 PDF [命名规范 v1.5.0]

对每篇论文尝试下载全文 PDF，按以下策略链（从 `research-paper-search` 技能文档）：
1. **OA URL** — 用 S2 返回的 `openAccessPdf.url` 下载
2. **arXiv PDF** — `https://arxiv.org/pdf/<arxiv_id>.pdf`
3. **PMC** — PMID → PMC ID 转换后用 `https://www.ncbi.nlm.nih.gov/pmc/articles/<PMCID>/pdf/`
4. **DOI redirect** — `curl -L "https://doi.org/<doi>" -H "Accept: application/pdf"`
5. **Sci-Hub** — 作为最后手段

**PDF 命名规则**: 每篇论文的 BibTeX key = `{第一作者姓}{年份}`。下载的 PDF 以该 key 命名：
```
Chen2025.pdf     ← 第一作者 Chen, 2025
Wang2026.pdf     ← 第一作者 Wang, 2026
```
记录每篇论文的 `pdf_status` 和 `bibkey`。

#### 3.5 [v1.5.0新增] 合并保存为单一 references.bib

对所有检索到的论文,合并为一个统一的 BibTeX 文件：
```
latex/references.bib     ← 所有论文的 BibTeX 条目合并于此文件
```

合并格式（全部条目写在一个 .bib 文件中）：
```bibtex
@article{Chen2025,
  author    = {Chen, X. and Wang, S.},
  title     = {论文标题},
  journal   = {期刊名},
  year      = {2025},
  doi       = {10.xxx/...},
  abstract  = {摘要全文}
}

@article{Wang2026,
  author    = {Wang, S. and Li, Z.},
  title     = {另一篇论文标题},
  journal   = {另一期刊},
  year      = {2026},
  doi       = {10.xxx/...},
  abstract  = {摘要全文}
}
```

**关键规则**:
- BibTeX key = `{第一作者姓}{年份}`（如 Chen2025），用于 PDF 文件名和 LaTeX 引用
- 如果第一作者未知，用 PMID/arXiv ID 替代
- 所有元数据字段必须从 API 返回的真实数据提取，**严禁虚构**
- 如果论文未成功下载 PDF，仍加入 references.bib（标记 `pdf_status = "unavailable"`）

#### 3.6 [v1.4.0] 保存到本地缓存

将搜索结果保存到本地缓存，供后续搜索复用：
```
cache_key = sha256(降格查询字符串).hexdigest()[:12]
mkdir -p outputs/search-cache/
write_file("outputs/search-cache/{cache_key}.json", {
  "query": search_query,
  "timestamp": current_time_iso,
  "total_found": total_found,
  "papers": raw_papers (摘要截断到200字),
  "sources_used": sources_used,
  "sources_failed": sources_failed
})
```

缓存有效期：24小时。过期缓存作为后备数据源（stale cache）。

#### 4. 保存输出

将去重后的论文列表 + metadata + evidence_chain 写入输出文件：
```
<output_path>/knowledge-acquisition_agent_output.json
```

### 质量要求
- **检索覆盖率**：至少覆盖 2 个数据源（含local_absorption_db兜底）
- **多关键词**：至少使用 3 个不同关键词变体搜索（核心词 + 同义词 + 方法学）
- **相关性**：标题/摘要需与查询语义相关
- **时效性**：优先近 5 年文献（除非查询明确要求更早）
- **准确性**：DOI/作者/年份等字段须正确提取
- **引用验证**：每篇论文完成至少 L1+L3 两层验证（DOI + S2标题交叉搜索）
- **幻觉控制**：HALLUCINATED 状态的论文从输出中排除，0篇输出是有效结果（非错误）
- **API弹性**：任何源失败不影响整体结果（自动降级）
- **质量门槛 [v1.5.0]**：输出的论文应引用 ≥ 40 篇参考文献。因此在检索阶段需搜索足够多的相关文献（目标累计 80-120 篇候选），去重后至少保留 60 篇以上供引用筛选。如果无法获取全文（真实不可下载），标记 `pdf_status = "unavailable"` 并如实记录原因，不禁用该论文。

### 边界判断
- 如果所有源都返回 0 篇论文，这是有效结果（不是错误）：输出空 `raw_papers` + 带详细 evidence_chain（记录每个源的查询、时间戳、返回数）
- 不要自行修改搜索查询（除非用户要求）
- 不要虚构论文：如果搜索结果不足，如实报告

### 已知陷阱

#### 1. S2 API 速率限制
- 无 key 时 1次/秒；**有有效 key 时也是 1次/秒**
- 每次 curl 调用后强制 `sleep 1`
- 如果收到 429（Too Many Requests），sleep 1s 后重试 1 次
- 如果返回空结果但不是错误，视为正常（0篇论文）

#### 2. PubMed rate limit
- 无 key 时每秒最多 3 次请求
- 搜索 + 摘要各算一次，中间至少等 0.4 秒

#### 3. arXiv API 是 HTTP（非 HTTPS）
- URL 必须以 `http://` 开头，不是 `https://`

#### 4. Crossref `select` 参数
- 不能包含 `publication-date` 或 `citation-count`
- 如果带 `abstract` 则可能丢失 `author` 字段

#### 5. OpenAlex abstract 格式
- `abstract_inverted_index` 是倒排索引 `{ position: word }`
- 须按 position 排序后拼接成句子

#### 6. PDF 下载失败
- 很多 OA 链接返回 403（MDPI、BMJ 等）。这不是异常，如实记录状态。
- 标记为 `pdf_status: "unavailable"` 即可，不影响论文元数据。

#### 7. [v1.4.0新增] local_absorption_db 局限
- 只包含已吸收的项目级数据，不是论文级
- star 数可能过时（需定期 GitHub API 刷新）
- 适合作为"最后手段"而非主要来源

#### 8. [v1.4.0新增] 缓存过期
- 缓存24小时过期后标记为 stale，不作为主数据源
- 但可作为"离线模式"的数据源（当所有API都失败时）

### 输出格式必须与上游兼容
下游 atoms (2-6) 期望的 `raw_papers` 字段名必须保持一致：
`title, doi, abstract, year, authors (list), source, open_access_url, arxiv_id`

### 验证清单

运行本技能后，确认以下检查项：

- [ ] 至少覆盖 2 个数据源（S2/PubMed/arXiv/OpenAlex/Crossref/bioRxiv/local_absorption_db）
- [ ] 所有检索到的论文有 DOI 或可访问的标识符
- [ ] 每篇论文完成至少 L1+L3 引用验证（DOI + S2标题交叉搜索）
- [ ] HALLUCINATED 状态的论文已从输出中排除
- [ ] sources_failed 已如实记录失败的源
- [ ] 缓存已保存到 outputs/search-cache/
- [ ] 如果所有API都失败：local_absorption_db 已作为兜底使用
- [ ] 输出符合上游契约格式（raw_papers → metadata → evidence_chain）
- [ ] 无 Python 代码生成（Agent-native 执行）

### 变更日志
2026-05-18: v1.4.0 — API弹性层 + 本地缓存 + 离线吸收库兜底。
  新增: Step 0.5 本地缓存检查 + Step 0.6 API回退策略
  新增: Step 3.5 保存到本地缓存 + 缓存有效期管理
  新增: 第7优先级 local_absorption_db 离线兜底（从absorption-tracked.json读取）
  新增: metadata.cache_hit, metadata.cache_path 字段
  新增: 陷阱#7 (DB局限) + #8 (缓存过期)
  原因: 写作闭环测试发现S2 API完全不可用，ACQ需要API弹性
2026-05-11: v1.3.0 — 2.5节引入 CITAION_VERIFICATION.md 引用验证流程
2026-05-11: v1.2.0 — 新增 bioRxiv/medRxiv 预印本源

## 命令层·English

- **Signature**: `topic: str, sources: list -> papers: list[Paper], total_found: int`
- **Allowed tools**: `terminal`, `web`, `delegate_task`, `Read`, `Write`
- **Input**: `search_query` (str), `sources` (list[str]), `max_results` (int, default 100)
- **Output**: `raw_papers` (list[Paper]), `metadata` (Metadata), `evidence_chain` (list[EvidenceNode])
- **Reference**: Semantic Scholar API v1, PubMed E-utilities, arXiv API, OpenAlex API, Crossref REST API, bioRxiv API
- **Cache path**: `outputs/search-cache/{cache_key}.json`
