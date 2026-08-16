---
name: citation-verification
description: citation-verification
version: 1.0.0
category: quality
signature: 'citation-verification -> quality: 引用三验 — 参考文献是否存在(L1) + 引用是否得当(L2) + 引用是否全面(L3)。三位一体验证管线。'
author: Synthos
license: MIT
metadata:
  synthos:
    priority: P0
    atom_type: quality
    signature: 'paper_dir: str -> citation_report: dict (phase1, phase2, phase3, overall)'
    related_skills:
    - paper-pipeline
    - quality-gate
---


## Operational Steps
1. 确认输入参数完整
2. 执行核心操作（参考本目录下的 scripts/ 或 references/）
3. 验证输出符合契约
4. 保存结果并报告

## Pitfalls
- 
- 

## Verification
- 
- 
- 
- 
1. 
2. 
3. 

# 引用三验 — 参考文献验证

## 原理

> 引必可验，无源即删。道有归处，方为真引。
> 引之所在，文献确然。不读全文，不验引用。
> 篇篇过堂，无一遗漏。当引则引，不当引者弃。

每条引用必须可验证。验证分三层：
1. **Phase 1 — 是否存在**：DOI验真、假DOI检测、替代文献、PDF分诊
2. **Phase 2 — 是否得当**：读PDF全文、语义比对、错误检测
3. **Phase 3 — 是否全面**：独立检索、遗漏检测、补充建议

## IO Contract

- **input**: `paper_dir: str` — 论文管线目录（含01-manuscript、06-references）
- **output**: 三位验证报告 + 修复后的bib
- **side_effects**: 更新bib、修复DOI、替换虚假文献、生成验证报告

## 管线流程

```
输入: paper_dir
  ↓
Phase 1: 是否存在（DOI验真 → 假DOI检测 → 替代 → PDF Triage）
  ↓
Phase 2: 是否得当（提取语境 → 读PDF → 语义比对 → 错误检测）
  ↓
Phase 3: 是否全面（提取主题 → 独立检索 → 对比 → 遗漏检测）
  ↓
输出: 三位验证报告 + 修复后的bib
```

## Phase 1: 是否存在

### 启动检查

每次Phase 1开始前必须检查SS API密钥。不带key的SS搜索会静默返回空（429被catch为空列表）。

```python
import os
assert os.environ.get("SEMANTIC_SCHOLAR_API_KEY", ""), (
    "SEMANTIC_SCHOLAR_API_KEY not set — SS search will silently fail"
)
```

### 数据集引用替换（Phase 0.5）

**原则**：`@misc`数据集条目应替换为引入/描述该数据集的论文（`@article`/`@inproceedings`）。

原因：论文引用比原始数据集元数据更规范、更可检索、有DOI/PMID可验证、审稿人更认可。

流程：检测`@misc` → 查UCI/OpenML页→找官方intro paper或SS首引 → 替换为`@article` → 更新tex引用 → D10a回归检查。

### 假DOI检测

| 信号 | 含义 | 行动 |
|: