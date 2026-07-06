---



name: biorxiv
description: "Directory index for biorxiv: biorxiv"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "search_terms: list[str], date_range: str -> preprints: list[Preprint] (title, authors, abstract, url, preprint_id)"
    atom_type: skill
    priority: P1
    related_skills: []
---




## IO_CONTRACT

- **input**: `search_terms: list[str], date_range: str` — 任务描述、参数配置
- **output**: `preprints: list[Preprint] (title, authors, abstract, url, preprint_id)` — 执行结果

> 对应原则：P2（机械原子暴露输入输出规范）

## 快速参考

详细文档和完整命令列表已被移至 `references/` 目录以保持简洁。
This skill has been compressed. Full content is available in references/.
