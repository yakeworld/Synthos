---
name: arxiv
description: >-
version: 1.0.0
  arXiv论文搜索 — 按关键词/作者/类别/ID检索。
metadata:
  synthos:
    version: 1.0.0
    author: Synthos

---


# Arxiv

## IO_CONTRACT

- **input**: `query_params: dict` — 搜索参数（keyword/author/category/id/max_results/date_range）
- **output**: `paper_results: list[dict]` — 论文列表（title/authors/abstract/arxiv_id/pdf_url/date）
- **side_effects**: arXiv API HTTP GET → 无状态变更

详细内容请加载此skill后按需执行。核心流程和命令已提炼如下：

## 快速参考

详细文档和完整命令列表已被移至 `references/` 目录以保持简洁。
This skill has been compressed. Full content is available in references/.
