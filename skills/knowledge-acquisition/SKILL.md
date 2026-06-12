---
name: knowledge-acquisition
description: 多源学术论文检索：Semantic Scholar / PubMed / Crossref / OpenAlex / arXiv / bioRxiv。
  Agent-native执行，纯skill+curl零Python。含API弹性层、本地缓存、自动回退链。 返回论文元数据、摘要、PDF。宁无所得，不取伪术。
license: MIT
allowed-tools: terminal Read Write task_delegation (bash, view/write, agent, inline)
metadata:
  synthos:
    priority: P0
    atom_type: cognitive-atom
    description: External knowledge acquisition — search PubMed, Semantic Scholar, OpenAlex, arXiv, bioRxiv, etc.
    signature: ['query: str, sources: list[str], date_range: str -> candidates: list[PaperCandidate]'] -> ['candidates: list[PaperCandidate] (title, doi, source, relevance, abstract_summary, pdf_url)']
    related_skills: [knowledge-extraction, association-discovery, hypothesis-generation, argument-expression, research-paper-search, academic-diagram, nature-paper2ppt]



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
| 1 | Semantic Scholar | 429→OpenAlex |
| 2 | PubMed | 无响应→Crossref |
| 3 | arXiv | HTTP redirect→curl -L |
| 4 | OpenAlex | 复杂查询→分解为简单短语 |
| 5 | bioRxiv/medRxiv | 无结果→直接API |
| 6 | Web scrape | 深度抓取 |
| 7 | 本地缓存 | 离线兜底 |

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
- 所有源失败 → 返回空结果 + 错误报告

## 已知陷阱

1. S2 API 429 — 自动重试+OpenAlex回退
2. PubMed rate limit — 串行请求+3s延迟
3. arXiv API 是 HTTP（非 HTTPS）— 用 `curl -L` 处理301
4. Crossref `select` 参数 — 逗号分隔字段名
5. OpenAlex abstract 是 inverted index — 需重建
6. PDF 下载失败 — 跳过，不阻塞流程
7. 缓存过期 — 24h后自动重新检索

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
