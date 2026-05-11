---
name: knowledge-acquisition
description: Search and retrieve academic papers from multiple sources (Semantic Scholar, PubMed, Crossref, OpenAlex, arXiv) using Agent tools. Returns paper metadata, abstracts, and PDF files. Agent-native — uses Hermes skills + terminal/curl, no Python code.
license: MIT
metadata:
  synthos_atom_type: "cognitive"
  synthos_version: "1.0.0"
  synthos_skill_md_hash: "2f7b3ee8e9f5d1a6c4b8a0e3d9f2c7b5a1e6d4f8c0a3b7e9d2f5c1a4b8e0d7"
  synthos_io_contract_ref: "references/IO_CONTRACT.md"
  synthos_citation_verification_ref: "references/CITATION_VERIFICATION.md"
  synthos_change_log_ref: "references/CHANGE_LOG.md"
  synthos_asserted_compliance: "P0,P2,P3"
  synthos_depends_on: "semantic-scholar, pubmed, arxiv, openalex, research-paper-search"
  synthos_author: "Synthos Agent (v4.0 agent-native refactor)"
allowed-tools: terminal web delegate_task Read Write
---

# 知识获取 (Knowledge Acquisition) - 认知原子 #1

## 概述
从外部源获取学术知识：检索论文、提取摘要、下载全文。是认知链条的起点。
**Agent-native**: 本原子由 Agent 直接执行，使用 Hermes 技能库中的搜索工具和 terminal + curl，没有 Python 依赖。

## 输入契约
- `search_query`: 搜索查询字符串（必填）
- `sources`: 数据来源列表，可选（默认全部）。有效值: `semantic_scholar`, `pubmed`, `arxiv`, `openalex`, `crossref`
- `max_results`: 最大结果数，默认 10
- `domain`: 研究领域（可选，用于过滤）

## 输出契约
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
    "sources_used": ["semantic_scholar", "pubmed"],
    "sources_attempted": ["semantic_scholar", "pubmed", "arxiv"],
    "sources_failed": ["openalex"]
  },
  "evidence_chain": [
    {"source": "semantic_scholar", "query": "ADHD eye tracking", "papers_returned": 5, "timestamp": "..."},
    {"source": "pubmed", "query": "ADHD eye tracking", "papers_returned": 3, "timestamp": "..."}
  ]
}
```

## 执行步骤

### 0. 加载外部技能
在开始之前，加载以下 Hermes 技能作为参考：
- `semantic-scholar` — S2 API 端点、字段、格式
- `pubmed` — PubMed E-utilities 端点
- `arxiv` — arXiv API 格式
- `research-paper-search` — 多源搜索 + PDF 下载参考
- `openalex` — OpenAlex API（可选，无 key 即可用）

### 1. 并行搜索各数据源

使用 terminal + curl 并发查询，每个源独立 curl 调用。用 `delegate_task` 并行搜索多个源然后合并结果，或者串行逐个搜索（源数少时串行更简单可靠）。

#### Semantic Scholar
```
curl -s -H "x-api-key: $SEMANTIC_SCHOLAR_API_KEY" \
  "https://api.semanticscholar.org/graph/v1/paper/search?query=<encoded_query>&limit=<N>&fields=title,year,abstract,authors,externalIds,citationCount,openAccessPdf"
```
- 返回 JSON，从 `data` 数组提取论文
- `externalIds.DOI` 拿到 DOI，`openAccessPdf.url` 拿到 OA PDF 链接
- 注意：S2 返回的 `externalIds` 可能没有 DOI，用 `CorpusId` 或 `ArXiv` 替代
- 如果 key 无效（403），跳过此源

#### PubMed
```
# Step 1: ESearch — 拿 PMID 列表
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=<encoded_query>&retmax=<N>&retmode=json"

# Step 2: ESummary — 拿元数据
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=<comma_separated_ids>&retmode=json"
```
- PubMed 不需要 API key（但无 key 有速率限制，每秒最多 3 请求）
- ESummary 返回 `result` 按 PMID 索引，每个条目有 `title`, `pubdate`, `authors[]`, `articleids[]`
- DOI 在 `articleids` 中找 `idtype=="doi"`

#### arXiv
```
curl -s "http://export.arxiv.org/api/query?search_query=all:<encoded_query>&max_results=<N>"
```
- 返回 XML/Atom 格式，解析 `<entry>` 元素
- `<title>`, `<summary>`, `<arxiv:doi>`, `<author><name>`, `<id>` (arxiv ID)
- 注意：arXiv API 是 HTTP 不是 HTTPS

#### OpenAlex
```
curl -s "https://api.openalex.org/works?search=<encoded_query>&per_page=<N>&sort=relevance_score:desc"
```
- 免费，不需要 API key
- `abstract_inverted_index` 需要按数字键排序后拼接
- `doi` 字段包含 `https://doi.org/` 前缀需要去掉

#### Crossref
```
curl -s "https://api.crossref.org/works?query=<encoded_query>&rows=<N>&select=DOI,title,author,abstract,issued,container-title"
```
- 免费，不需要 API key
- 注意 `select` 参数不要包含 `publication-date` 或 `citation-count`（会导致空结果）
- 返回 JSON 的 `message.items` 数组

### 2. 去重

按 DOI 精确匹配去重。无 DOI 的按标题归一化后模糊匹配（忽略大小写、标点）。

### 2.5 [新增] 引用验证

对去重后的每篇论文执行4层引用验证。读取 `references/CITATION_VERIFICATION.md` 获取完整流程。

验证策略：
1. **L1: DOI验证** — `curl -s "https://api.crossref.org/works/{doi}"` 检查200
2. **L2: arXiv验证**（如有arxiv_id）— `curl -s "http://export.arxiv.org/api/query?id_list={id}"` 检查返回
3. **L3: S2标题交叉搜索** — 搜索标题，计算相似度
4. **L4: LLM相关性评分** — Agent判断论文是否与研究主题相关

输出：在每篇论文中添加 `citation_verification` 字段。状态为 `hallucinated` 的论文从输出中排除（记录到 evidence_chain）。

预期耗时：每篇论文约5-10秒（curl API调用+Agent推理评分）。

### 3. 下载 PDF

对每篇论文尝试下载全文 PDF，按以下策略链（从 `research-paper-search` 技能文档）：
1. **OA URL** — 用 S2 返回的 `openAccessPdf.url` 下载
2. **arXiv PDF** — `https://arxiv.org/pdf/<arxiv_id>.pdf`
3. **PMC** — PMID → PMC ID 转换后用 `https://www.ncbi.nlm.nih.gov/pmc/articles/<PMCID>/pdf/`
4. **DOI redirect** — `curl -L "https://doi.org/<doi>" -H "Accept: application/pdf"`
5. **Sci-Hub** — 作为最后手段

记录每篇论文的 `pdf_status`。

### 4. 保存输出

将去重后的论文列表 + metadata + evidence_chain 写入输出文件：
```
<output_path>/knowledge-acquisition_agent_output.json
```

## 质量要求
- **检索覆盖率**：至少覆盖 2 个数据源
- **相关性**：标题/摘要需与查询语义相关
- **时效性**：优先近 5 年文献（除非查询明确要求更早）
- **准确性**：DOI/作者/年份等字段须正确提取
- **引用验证**：每篇论文完成至少 L1+L3 两层验证（DOI + S2标题交叉搜索）
- **幻觉控制**：HALLUCINATED 状态的论文从输出中排除，0篇输出是有效结果（非错误）

## 边界判断
- 如果所有源都返回 0 篇论文，这是有效结果（不是错误）：输出空 `raw_papers` + 带详细 evidence_chain（记录每个源的查询、时间戳、返回数）
- 不要自行修改搜索查询（除非用户要求）
- 不要虚构论文：如果搜索结果不足，如实报告

## 已知陷阱

### 1. S2 API key 格式
- 有效 key 是 40 位字母数字，无前缀
- `s2k-xxx` 前缀的 key 一定返回 403
- 如果 403，跳过此源，不要重试

### 2. PubMed rate limit
- 无 key 时每秒最多 3 次请求
- 搜索 + 摘要各算一次，中间至少等 0.4 秒

### 3. arXiv API 是 HTTP（非 HTTPS）
- URL 必须以 `http://` 开头，不是 `https://`

### 4. Crossref `select` 参数
- 不能包含 `publication-date` 或 `citation-count`
- 如果带 `abstract` 则可能丢失 `author` 字段

### 5. OpenAlex abstract 格式
- `abstract_inverted_index` 是倒排索引 `{ position: word }`
- 须按 position 排序后拼接成句子

### 6. PDF 下载失败
- 很多 OA 链接返回 403（MDPI、BMJ 等）。这不是异常，如实记录状态。
- 标记为 `pdf_status: "unavailable"` 即可，不影响论文元数据。

## 输出格式必须与上游兼容
下游 atoms (2-6) 期望的 `raw_papers` 字段名必须保持一致：
`title, doi, abstract, year, authors (list), source, open_access_url, arxiv_id`

## 变更日志
2026-05-11: v1.1.0 — 新增4层引用验证（吸收自AutoResearchClaw）。
  新增: CITATION_VERIFICATION.md 参考文件
  新增: Step 2.5 引用验证（L1 DOI + L2 arXiv + L3 S2标题 + L4 LLM相关性）
  新增: citation_verification 字段到输出契约
  影响: 每篇论文增加5-10秒验证延迟，消除引用幻觉
2026-05-10: v1.0.0 — 从 Python mechanical 重构为 Agent-native cognitive 原子。
  Agent 直接执行，加载 Hermes 技能 + terminal/curl 完成搜索
  影响: 新增 OpenAlex 和 Crossref 源
