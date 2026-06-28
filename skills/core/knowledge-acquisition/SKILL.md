---

name: knowledge-acquisition
description: 多源学术论文检索：Semantic Scholar / PubMed / Crossref / OpenAlex / arXiv / bioRxiv。
author: Synthos
license: MIT
version: 1.0.0
  Agent-native执行，纯skill+curl零Python。含API弹性层、本地缓存、自动回退链。 返回论文元数据、摘要、PDF。宁无所得，不取伪术。
license: MIT
allowed-tools: terminal Read Write task_delegation (bash, view/write, agent, inline)
metadata:
  synthos:
    priority: P0
    atom_type: cognitive-atom
    description: External knowledge acquisition — search PubMed, Semantic Scholar, OpenAlex, arXiv, bioRxiv, etc.
    signature: "query: str, sources: list[str], date_range: str -> candidates: list[PaperCandidate] -> candidates: list[PaperCandidate] (title, doi, source, relevance, abstract_summary, pdf_url)"
    related_skills: []


---




# 知识获取 (Knowledge Acquisition)

## 原理层·文言

> 「致知在格物。物格而后知至。」多源求索，博观约取。
> 「博学之，审问之，慎思之，明辨之，笃行之。」不取伪术，不引虚言。
> 宁缺毋滥，求真为要。

### 求知之道

> 知者，认知之始也。先求于外，而后内化。
> 无求则无知，无源则无流。
> 搜于六方而不偏，核于四维而不妄。
> 凡文必求真，凡数必溯源，凡引必可验。
> 宁无所得，不取伪术。诚则明矣，伪则暗矣。

## 方法层·白话

Agent-native认知原子。使用技能库+终端curl检索学术文献，零Python依赖。

## 触发条件

- 需要检索学术文献（主题/关键词/研究问题）
- 上游 research-ideation 产出方向需文献支撑
- 下游 knowledge-extraction 等待输入
- 用户要求"搜索文献/查论文"

## 输入契约

| 字段 | 类型 | 必需 | 说明 |
|:-----|:---
  io_contract: input: ['query: str, sources: list[str], date_range: str -> candidates: list[PaperCandidate]', 'output: ['candidates: list[PaperCandidate] (title, doi, source, relevance, abstract_summary, pdf_url)']
--|:----:|:-----|
| topic | string | ✅ | 研究主题 / 关键问题 |
| keywords | list[str] | ❌ | 具体关键词（不提供则自动从 topic 推导） |
| source_priority | list[str] | ❌ | 数据源优先级（默认: S2→PubMed→arXiv→OpenAlex→Crossref→bioRxiv） |
| max_papers | int | ❌ | 最大返回数（默认 15） |
| year_range | list[int] | ❌ | 年份范围，如 [2020, 2025] |

## 输出契约

```json
{
  "papers": [{
    "title": "论文标题",
    "authors": ["作者1", "作者2"],
    "year": 2024,
    "source": "semantic_scholar | pubmed | arxiv | ...",
    "external_ids": {"DOI": "10.xxx", "arXiv": "xxxx.xxxxx"},
    "abstract": "摘要...",
    "url": "https://...",
    "pdf_url": "https://...",
    "citation_count": 42,
    "relevance_score": 0.85,
    "provenance": "source=source_name, query=关键词, api_status=ok"
  }],
  "total_found": 15,
  "search_meta": {"sources_queried": ["S2","PubMed"], "sources_failed": []}
}
```

## 执行步骤

### 0. 加载外部技能
`scientific-database-lookup`（多源搜索） + `research-paper-search`（论文检索辅助）

### 1. 多关键词搜索
从 topic 自动推导 2-5 个搜索关键词。每个关键词搜索所有已配源。

### 2. 并行搜索各源（带回退链）

| 优先级 | 源 | 回退策略 |
|:------:|:---|:---------|
| 1 | Semantic Scholar (API Key) → 429→OpenAlex|
| 2 | PubMed | 无响应→Crossref |
| 3 | arXiv (Tor SOCKS5) → HTTPS + curl -L --socks5-hostname 127.0.0.1:9050|
| 4 | OpenAlex → {word: [positions]} 反转重建摘要|
| 5 | **PubScholar 🆕** → curl直调API（中文/中科院论文）|
| 6 | bioRxiv/medRxiv | 无结果→直接API |
| 7 | Web scrape | 深度抓取 |
| 8 | 本地缓存 | 离线兜底 |

API具体命令 → 参考 `scientific-database-lookup` 和 `research-paper-search` 技能

### 3. 去重
按 title 归一化匹配，同论文保留信息最全的版本。

### 4. 引用验证
5类幻觉检测：TF(完全虚构) / PAC(部分虚构) / IH(不完整引用) / PH(幻影引用) / SH(来源混淆)

### 5. 下载PDF（可选）
命名规范: `{bibkey}.pdf` → `outputs/papers/pdfs/`。自动生成 `references.bib`。

### 6. PDF → Markdown → NotebookLM 上传（D7 文献门用）

> 子 skill: `pdf-to-md-notebooklm` — 含完整命令和陷阱

下载后的 PDF 转为 Markdown 再上传到 NotebookLM（替代 PDF 直传，避免文本层问题）：

```bash
# 6a. 检查文本层
pdftotext pdfs/{bibkey}.pdf - | wc -c

# 6b. MarkItDown 转 MD（推荐）
uvx markitdown pdfs/{bibkey}.pdf > pdfs/{bibkey}.md 2>/dev/null

# 6c. 上传到 NotebookLM（必须 --type text + $(cat) 传内容）
notebooklm source add "$(cat pdfs/{bibkey}.md)" --type text --title "{bibkey}" -n <notebook_id> --timeout 120
```

**为什么必须 `--type text` 且用 `$(cat ...)` 传内容：**
- `source add file.md` → ❌ error（后端不识 `.md` 格式）
- `source add file.md --type text` → ❌ 只传了路径字符串
- **`source add "$(cat file.md)" --type text`** → ✅ Markdown 类型，内容完整（实战验证）

## 质量要求

- **零虚构**：宁返回空结果，不返回编造论文
- **provenance 必填**：每条结果含 `source=源名, query=关键词, api_status=ok/429/timeout`
- **去重严格**：同论文仅保留一次
- **引用验证**：至少通过 TF/PAC 检测

## 边界判断

- topic 过于模糊（如"脑科学"）→ 追问具体维度
- 结果为空 → 明确报告"search_exhausted"，非虚构填充
- S2 429 → 自动切换到 OpenAlex（已验证有效）
## 陷阱

| # | 陷阱 | 正确做法 |
|:-:|:-----|:---------|
| 1 | S2 API 429 — 使用环境变量 SEMANTIC_SCHOLAR_API_KEY；无 key 则回退 OpenAlex
| 2 | PubMed rate limit — 串行请求+3s延迟
| 3 | arXiv API 必须 HTTPS — 通过 Tor SOCKS5（`--socks5-hostname 127.0.0.1:9050`）+ `curl -L`
| 4 | Crossref `select` 参数 — 逗号分隔字段名
| 5 | OpenAlex abstract_inverted_index 格式为 `{word: [positions]}`，需反转重建摘要
| 6 | PDF 下载失败 — 跳过，不阻塞流程
| 7 | 缓存过期 — 24h后自动重新检索
| 8 | arXiv 标题含换行符 — XML 解析后需 `.strip()`
| 9 | arXiv PDF URL 在 `<link rel="related">`，非 `rel="alternate"`
| 10 | **CNKI (kns.cnki.net) 海外 IP 返回 HTTP 418** — 知网有严格 IP 地理围栏，海外直接拒绝。RSSHub 的 cnki 路由代码已分析但无法从海外节点部署。中文文献替代方案：PubScholar（中科院公益平台，纯 curl ✅）。
| 11 | **HuggingFace SSL 证书过期/无效** — `ERR_CERT_COMMON_NAME_INVALID` 或 `SSL certificate problem: certificate has expired`。HuggingFace API (HTTPS) 和页面可能完全不可用，curl 和浏览器都会失败。 | 如果目标是 Ollama 模型追踪，直接从 Ollama 页面提取数据即可，不需要 HuggingFace。如果确实需要 HF 数据，用 `curl --insecure` 跳过证书验证。这是一个已知的环境状态问题，HF 的证书可能临时失效 |
| 12 | **browser_snapshot 截断** — 页面内容超过 8000 字符时会被截断，丢失模型/论文列表。 | 必须用 `browser_console` + JavaScript 直接提取 DOM 数据，这是最可靠的方式 |
| 13 | **下载量/统计数字格式多样** — 有的是 `15.9M` (百万)，有的是 `108.8K` (千)，有的是 `8,901` (纯数字)。 | 用正则 `([\d,\.]+)K?` 提取，然后判断后缀 K/M 进行数量级转换 |

## 验证清单

- [ ] 至少搜索了 ≥3 个数据源
- [ ] 所有结果有 provenance 字段
- [ ] 无虚构论文（引用验证通过）
- [ ] 去重完成
- [ ] PDF下载失败的不阻塞主流程
- [ ] 输出格式兼容下游 knowledge-extraction

## 命令层

- **Signature**: `topic: str, sources: list -> papers: list[Paper], total_found: int`
- **Allowed tools**: shell, task_delegation, Read, Write
- **Output**: JSON with papers list + search_meta
- **Zero Python**: 全部使用 shell+curl，无Python运行时依赖

## IO_CONTRACT

- **input**: `query: str, sources: list[str], max_results: int, date_range: str`
- **output**: `candidates: list[PaperCandidate]` — 包含 title, doi, source, relevance, abstract_summary, pdf_url

> 对应原则：P2（机械原子暴露输入输出规范）

## 执行脚本

- `../../extended/research-tools/research/paper-retrieval/scripts/multi_source_search.py` — 四源统一检索引擎（Semantic Scholar + PubMed + OpenAlex + arXiv via torsocks）
  - 用法: python3 multi_source_search.py "query" --max 5 --verbose --output result.json
  - 环境变量: SEMANTIC_SCHOLAR_API_KEY（必需）
  - 输出: 符合 SKILL.md IO_CONTRACT 的标准 JSON（papers + search_meta + sources_success/failed）
- `../../extended/research-tools/research/paper-retrieval/scripts/pdf_download_engine.py` — 多源竞速PDF下载引擎
  - 用法: python3 pdf_download_engine.py DOI_or_arXiv_ID --output path.pdf
  - 文件名规范: PDF 保存为 {bibkey}.pdf (如 V2019GrandmasterLevelStarcraft.pdf)，基于作者+年份+标题生成 BibTeX 风格标识符
  - 用法: python3 pdf_download_engine.py --batch candidates.json  # 批量下载
  - 用法: python3 pdf_download_engine.py --test  # 连通性测试
  - 下载策略: OA直连(arXiv→Crossref→Unpaywall→PMC) → Sci-Hub(curl_cffi→Tor) → LibGen → MedData（Semantic Scholar + PubMed + OpenAlex + arXiv via torsocks）
  - 用法: `python3 multi_source_search.py "query" --max 5 --verbose --output result.json`
  - 环境变量: `SEMANTIC_SCHOLAR_API_KEY`（必需）
  - 输出: 符合 SKILL.md IO_CONTRACT 的标准 JSON（papers + search_meta + sources_success/failed）
  - 特性: 自动去重、回退链、速率限制、provenance 标注、exit code 0/1


## 示例 · EXAMPLES

1. **基本用法**: 标准输入 → 标准输出
2. **边界用例**: 空输入、特殊字符、异常路径
3. **错误场景**: 缺失依赖、权限不足、网络异常


## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每个示例必须可独立运行、有明确输入输出、包含错误处理。
