---
name: paper-pipeline
description: "Complete paper pipeline: retrieval, extraction, quality review, analysis, and publication."
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    atom_type: composite
    priority: P0
    signature: "paper_path: str -> analysis_report: dict"
    related_skills: []

---

# Paper Pipeline

## Purpose

Composite skill that merges 35 paper-related skills into a unified pipeline.

## Members (35)

- **adhd-eye-tracking-review**: Directory index for adhd-eye-tracking-review: adhd-eye-tracking-review
- **arxiv**: arXiv论文搜索 — 按关键词/作者/类别/ID检索。支持Tor SOCKS代理访问。
- **bib-integrity-audit**: Audit `.bib` reference files across a paper library for:
- **biorxiv**: Directory index for biorxiv: biorxiv
- **citation-bib-crossref**: Scan paper directories for mismatches between `\\cite{key}` calls in `.tex` files and `@type{key}` entries in `.bib` files. Produces D8 (bib count) and D10a (match percentage) metrics, plus orphan/zombie classification.
- **citation-integrity-fix**: ```python
- **emerging-field-landscape-scan**: Skill: emerging-field-landscape-scan
- **gif-search**: Search and download GIFs directly via the Tenor API using curl. No extra tools needed.
- **knowledge-base-audit**: Audit and maintain personal knowledge management systems (AKNE, NotebookLM,
- **latex-output**: Directory index for latex-output: latex-output
- **nano-pdf**: Edit PDFs using natural-language instructions. Point it at a page and describe what to change.
- **nature-paper2ppt**: Nature-style Chinese PPTX from academic papers — argument-driven slide
- **nsfc-grant-audit**: Directory index for nsfc-grant-audit: nsfc-grant-audit
- **openalex**: Directory index for openalex: openalex
- **paper-citation-health**: Scan all papers in `outputs/papers/` for citation bibliographic health metrics D8 (bib entries) and D10a (cite-to-bib match %).
- **paper-cron-scan**: Cron job 不是完整的论文管线执行，而是**轻量级扫描**：验证白空间稳定、发现新竞争、推进管线状态。
- **paper-pipeline**: 主skill | SCI论文全流程编排器。v3.18.10新增Trap#42跨项目参考文献污染检测（Synthos Paper ID后缀/占位符键名/空条目/Prose提及无cite）。v3.18.9新增Trap#41 paper-queue.json幽灵条目逆方向。v3.18.5-8: D10a批量扫描+natbib盲区+注释过滤+路由修复。v3.18: Track A晋升协议。v3.16: 队列自愈+ABSOLUTE WHITE独立验证。v3.15: 轨道B四步工作流。
- **paper-quality-deep-review**: 论文质量深度审查引擎 — 从文献下载→内容分析→研究空白验证→科学假设评估→解决方法评估→文献引用质量评分→综合评分。
- **paper-queue-audit**: Directory index for paper-queue-audit: paper-queue-audit
- **paper-references-scanning**: Scan paper library for citation health: D8 (bib entry count), D10a (cite-to-bib match rate),   orphans, zombies. Class of tasks: LaTeX reference integrity auditing.
- **pdf-download-racing**: 并行竞速PDF下载引擎 — curl_cffi TLS指纹绕过 + Sci-Hub域轮换 + LibGen + MedData。依赖 tools/paper-manager/src/。
- **pdf-to-md-notebooklm**: PDF→Markdown→NotebookLM 全流程管线。支持批量上传、自动类型检测、大文件处理。
- **pubmed**: Deep PubMed/MEDLINE search via NCBI E-utilities — query construction, MeSH terms, batch retrieval, clinical query refinement.
- **quality**: 质量保障 — 伪证验证、黄金测试、SCI论文质量评审。
- **quality-score-assignment**: Paper satisfies `current_step in steps_completed` AND `len(steps_completed) >= 8`.
- **research**: 直接调用子类别/技能名称即可。例如：`arxiv`、`bib-integrity-audit`、`research-ideation`。
- **research-ideation**: 研究创意发散与认知引擎（RIF+CCF）。三层架构：Layer 1（10操作框架）→ 产出研究方向候选； Layer 2（8认知引擎）→
- **research-paper-search**: 主skill | 多源论文检索+全文下载编排器。入口：Semantic Scholar (API Key), PubMed, OpenAlex, arXiv (Tor), Crossref。调用子skill: arxiv, pubmed, openalex。
- **research-skill-audit**: Audit and enhance research skill coverage. Process for identifying gaps, testing existing skills, and creating/enhancing missing capabilities.
- **researcher-portrait**: Directory index for researcher-portrait: researcher-portrait
- **sci-paper-quality-review**: Directory index for sci-paper-quality-review: sci-paper-quality-review
- **sci-paper-standard-structure**: Directory index for sci-paper-standard-structure: sci-paper-standard-structure
- **skill-integrity-audit**: | 概念 | 文言 | 义 |
- **systematic-review**: 系统综述与Meta分析工作流助手 — PRISMA流程、搜索策略设计、研究选择、质量评估、数据提取和综合支持。
- **v32-multi-direction-scan**: Every cron run of autonomous-core-researcher after v31 API fix. Standardized pattern for scanning 5 rotation + 5 new directions per run.

## IO_CONTRACT

- **input**: `paper_path: str, analysis_type: str` — Paper path and analysis type
- **output**: `analysis_report: dict` — Complete analysis report

> 对应原则：P3（人机分层 — 路由器负责路由，原子负责执行）