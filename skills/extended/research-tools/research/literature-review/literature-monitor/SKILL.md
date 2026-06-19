---



name: literature-monitor
description: "Directory index for literature-monitor: literature-monitor"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "keywords: list[str], date_range: str -> new_papers: list[Paper] (title, abstract, source, relevance_score)"
    atom_type: skill
    priority: P1
    related_skills: []
---




## IO_CONTRACT

- **input**: `keywords: list[str], date_range: str` — 任务描述、参数配置
- **output**: `new_papers: list[Paper] (title, abstract, source, relevance_score)` — 执行结果

> 对应原则：P2（机械原子暴露输入输出规范）

## 数据源选择规则

- **临床/医学/眼动/前庭/脑机接口**：优先 OpenAlex（无API key，250M+论文，medical topics 覆盖好）
- **生物医学**：优先 PubMed
- **预印本**：arXiv（仅计算机/物理/数学方向；医学方向 arXiv 覆盖率低，勿作为主力源）
- **DOI验证/元数据**：Crossref
- **预印本全文**：bioRxiv/medRxiv

## OpenAlex 医学领域搜索

arXiv 对临床/医学/眼动/前庭等主题的搜索效果很差（返回数学/物理噪声）。OpenAlex 是更可靠的主力源。

### 常见陷阱
1. OpenAlex 搜索"PINN"时可能返回 physics-PINNs（非医学领域）→ 需逐条阅读摘要确认
2. OpenAlex 搜索"eye tracking"可能返回计算机视觉/OCR 论文 → 需用 `AND` 组合医学术语
3. PubMed 搜索 "OR" 太多 → 大量假阳性，必须用 `AND` 组合
4. PubMed eSearch 返回 JSON 中 ID 列表的键名是 `idlist`（小写），不是 `IdList`

## 脑机接口搜索策略（2026-06-09 注入）

BCI/脑机接口方向搜索关键词组合：
- 主关键词：`brain computer interface` / `BCI` / `neural interface`
- 辅助关键词：`eye tracking` / `vestibular` / `BPPV` / `VOR`
- 疾病关键词：`Parkinson` / `Alzheimer` / `ALS` / `stroke`
- 技术关键词：`neural decoding` / `motor imagery` / `EEG` / `eye-BCI`

搜索优先级：OpenAlex → PubMed → Semantic Scholar → arXiv

