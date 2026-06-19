---

name: research
related_skills: ["dspy"]
description: "学术研究 — 论文检索、文献监控、专利挖掘、系统综述、研究创意。"
author: Synthos
license: MIT
version: 2.0.0
license: MIT
metadata:
  synthos:
    priority: P1
    atom_type: parent-skill
    description: "学术研究工具集 — 按功能分为6个子类别"

---


## IO_CONTRACT

- **input**: `research_query: str, domain: str, scope: str` — 研究查询、领域、范围
- **output**: `research_output: dict` — 研究结果（论文/文献/假设/综述）

> 对应原则：P2（机械原子暴露输入输出规范）


# Research Tools

> 父级技能目录，包含 6 个子类别共 33 个技能。

## 子类别

- `paper-retrieval/` — 论文检索与下载（arXiv, PubMed, OpenAlex, bioRxiv, PDF racing）
- `literature-review/` — 文献完整性审查（Bib审计、引文健康、NSFC基金审计、系统综述）
- `research-methodology/` — 研究方法（数据驱动假设、新兴领域扫描、研究创意、ODE建模）
- `clinical-research/` — 临床研究（BPPV专家系统、ADHD眼动、乳腺癌诊断、期刊选择）
- `content-production/` — 内容生产（竞赛方案、视频制作、PDF转换、专利交底书）
- `intelligence-monitoring/` — 情报监控（博客监控、LLM百科、Polymarket、研究者画像）

## 使用方式

直接调用子类别/技能名称即可。例如：`arxiv`、`bib-integrity-audit`、`research-ideation`。
