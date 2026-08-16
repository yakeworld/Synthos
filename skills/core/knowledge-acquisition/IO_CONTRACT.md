# IO_CONTRACT.md — knowledge-acquisition

> 对应原则：P2
> 权威来源：docs/atom-io-schemas.md

## 概述

原子类型：cognitive
上游依赖：无（入口原子）
下游：knowledge-extraction

详细的 input_schema / output_schema 请参阅 docs/atom-io-schemas.md 对应章节。

## 输入

- `query`（string）：检索关键词或 DOI
- `provider`（string，可选）：指定检索源（Crossref/Medline/SemanticScholar/arXiv/OpenAlex），默认 Crossref

## 输出

- `bibliography`（BibTeX 条目流）：检索结果
- `pdfs`（文件集合）：下载的 PDF（已验证 `%PDF-` 魔数）
- `provenance`（每条记录）：来源源 + DOI + 下载时间

## 错误状态

- 检索无结果 → 空输出 + 非零退出码
- PDF 魔数校验失败 → 标为下载失败，不入库
- 全部 API 源失效 → 报告三源回退过程
