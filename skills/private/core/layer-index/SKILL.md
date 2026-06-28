---
name: layer-index
description: "Navigation index for the core research stack — 7 cognitive atoms, paper pipeline, research methodology, and AI/ML tools."
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    priority: P3
    atom_type: layer-index
    signature: "layer: str, query: str, context: dict -> skill_list: list[dict]"
    related_skills: []
---

# Core Research Stack — 核心科研栈

## Purpose

Navigation index for the core research stack: 7 cognitive atoms, paper pipeline, research methodology, and AI/ML tools.

## Skills in this Layer (88 total)

- **academic-diagram**: Directory index for academic-diagram: academic-diagram
- **adhd-eye-tracking-review**: Directory index for adhd-eye-tracking-review: adhd-eye-tracking-review
- **akne-knowledge-manager**: AKNE 知识管理系统的双向整合审计、Synthos-桥接诊断、知识流分析、内容级审计。与 akne-maintenance 不同，专注两系统间的连接质量及知识内容质量而非内部运维。
- **akne-maintenance**: 维护个人知识库系统AKNE — 图谱诊断、修复、向量填充、源文件覆盖、Wiki清理、自动进化守护。覆盖AKNE仓库的完整运维生命周期。
- **architecture-diagram**: Directory index for architecture-diagram: architecture-diagram
- **argument-expression**: Directory index for argument-expression: argument-expression
- **arxiv**: arXiv论文搜索 — 按关键词/作者/类别/ID检索。支持Tor SOCKS代理访问。
- **association-discovery**: Directory index for association-discovery: association-discovery
- **audiocraft**: Comprehensive guide to using Meta's AudioCraft for text-to-music and text-to-audio generation with MusicGen, AudioGen, and EnCodec.
- **autonomous-execution-threshold**: **≥80%置信度 = 闭嘴执行。** 不输出推测文案、不给选项、不喊"开始自主执行"口号。用户看到的是执行结果，不是选择题。
- **bib-integrity-audit**: Audit `.bib` reference files across a paper library for:
- **biomechanical-regulation-ode**: Class-level skill for building computational dynamical models of physiological regulation systems using 2-ODE systems with PINN training. Covers model formulation, bifurcation analysis, Sobol sensitivity, and ablation studies.
- **biorxiv**: Directory index for biorxiv: biorxiv
- **bppv-expert**: Structured BPPV (Benign Paroxysmal Positional Vertigo) medical knowledge version: 1.0.0 extracted from AKNE knowledge graph. Covers diagnosis techniques (Dix-Hallpike, supine head flexion test), repositioning maneuvers (Epley, Gufoni, Semont, Barbecue, roll-over), canalith conversion mechanisms, 3D biomechanical simulation, and clinical decision workflows. Source: AKNE wiki (126 nodes, 137 edges, proven correctness via falsification testing).
- **citation-bib-crossref**: Scan paper directories for mismatches between `\\cite{key}` calls in `.tex` files and `@type{key}` entries in `.bib` files. Produces D8 (bib count) and D10a (match percentage) metrics, plus orphan/zombie classification.
- **citation-integrity-fix**: ```python
- **cognitive-atom-architecture**: Methodology for transforming operational skill sets into independent cognitive atoms with strict DAG dependencies, input/output contracts, and Synthos framework alignment. v4.0.0 syncretic framework: Eastern ontology (格物通理/取象通变/天人合一) + Western epistemology (经权度信/墨证求真/庄周观模) + 熵减律·生生之谓易 (ultimate purpose) + 大道至简 (cross-cutting razor).
- **comfyui**: Directory index for comfyui: comfyui
- **competition-submission**: End-to-end preparation of AI/tech/innovation competition submissions. Extract requirements, map to scoring criteria, generate documents, produce submission checklist. Covers medical AI, tech innovation, academic conferences, Chinese government grants.
- **conversation-to-memory**: ⚡ P0 辅助技能。从会话中提取高价值信息，在2,200字符限制内最大化记忆ROI。动灵记忆三问(生长方向?框架维度?发酵潜力?)+宪法护栏(记忆不能覆写CONSTITUTION)+凝练压缩策略。防记忆膨胀同时保留高信号事实。每条记忆标注生长方向和发酵潜力。
- **crispdm-helix-experiment**: CRISP-DM Helix methodology — strict CV-fold-isolated preprocessing for clinical ML experiments on public datasets. Generates real, traceable L0.5-compliant data.
- **data-driven-hypothesis**: 从公开数据出发→数据探索→文献调研→发现gap→提出可验证假设。与"先有假设再找数据"相反，适合公开数据集方向探索。
- **dataset-discovery**: | Platform | REST API | Scraping | Auth Required | Notes |
- **dspy**: Use DSPy when you need to:
- **emerging-field-landscape-scan**: Skill: emerging-field-landscape-scan
- **evolution**: ⚡ P0 自进化引擎。Synthos evolution engine v2.20 — 四态决策+硬收敛+GEPA反射分析+自动基准+Pareto优化+外部吸收+教训学习+黄金验证+自扩关键词+漂移检测+渐进披露+Git即记忆。Hooks注入+置信度评分+并行Agent审计+会话上下文注入+Prompt Snippets。
- **experiment-recipes**: ML训练配方与预设——架构选择、训练循环、优化器、调度器、混合精度、内存优化、调试。 提炼自实战经验，非外部代码搬运。每个配方记录原理而非逐行代码。
- **falsification-validation**: Systematic approach to validating AI agent skills through falsification
- **golden-test-methodology**: Methodology for creating, maintaining, and evaluating golden test suites version: 1.0.0 across all skills. Defines: three-file golden structure (GOLDEN_SET.md + cases/ + expected/), weighted verification criteria, coverage scoring, and DIAGNOSE integration. Covers the systematic gap where golden coverage is the weakest dimension in a multi-skill system.
- **gradient-alignment-loss**: Skill: gradient-alignment-loss
- **hcs-3wt-breast-cancer-diagnosis**: HCS-3WT (Hybrid Cascade-Stacking Three-Way Triage) breast cancer diagnostic
- **healthcare-dataset-discovery**: Public healthcare dataset discovery — known accessible sources, dead sources, and API patterns for medical AI research.
- **huggingface-hub**: HuggingFace hf CLI: search/download/upload models, datasets.
- **hypothesis-generation**: Directory index for hypothesis-generation: hypothesis-generation
- **inference**: Directory index for inference — mlops/inference   模型推理服务与优化
- **journal-selection-medical-ai**: Systematic methodology for evaluating and ranking SCI journals as publication
- **kg-bridge**: Knowledge Graph — Agent Bridge. 将大型知识图谱接入 Agent 记忆层的方法论，覆盖查询分层、环境隔离、语义搜索增强、脚本化接口。
- **knowledge-acquisition**: 多源学术论文检索：Semantic Scholar / PubMed / Crossref / OpenAlex / arXiv / bioRxiv。
- **knowledge-base-audit**: Audit and maintain personal knowledge management systems (AKNE, NotebookLM,
- **knowledge-extraction**: Directory index for knowledge-extraction: knowledge-extraction
- **latex-output**: Directory index for latex-output: latex-output
- **literature-monitor**: Directory index for literature-monitor: literature-monitor
- **llama-cpp**: Use this skill for local GGUF inference, quant selection, or Hugging Face repo discovery for llama.cpp.
- **metacognition**: 元认知 — 自主执行阈值、记忆增强、记忆优化系统。
- **models**: Directory index for models — mlops/models   模型架构
- **nano-pdf**: Edit PDFs using natural-language instructions. Point it at a page and describe what to change.
- **nature-paper2ppt**: Nature-style Chinese PPTX from academic papers — argument-driven slide
- **nsfc-grant-audit**: Directory index for nsfc-grant-audit: nsfc-grant-audit
- **obliteratus**: 9 CLI methods, 28 analysis modules, 116 model presets across 5 compute tiers, tournament evaluation, and telemetry-driven recommendations.
- **ode-simulation-tuning**: When building 2-ODE computational models for SCI papers, the simulation rarely passes all quality gates on first run. Metrics that commonly fail: R² (needs smooth fit), AUC (needs proper distribution comparison), ablation (needs dominant coupling), accuracy (needs clean transitions). This skill captures the systematic tuning methodology used across papers 90–140+.
- **openalex**: Directory index for openalex: openalex
- **outlines**: Use Outlines when you need to:
- **paper-citation-health**: Scan all papers in `outputs/papers/` for citation bibliographic health metrics D8 (bib entries) and D10a (cite-to-bib match %).
- **paper-cron-scan**: Cron job 不是完整的论文管线执行，而是**轻量级扫描**：验证白空间稳定、发现新竞争、推进管线状态。
- **paper-pipeline**: 主skill | SCI论文全流程编排器。v3.18.10新增Trap#42跨项目参考文献污染检测（Synthos Paper ID后缀/占位符键名/空条目/Prose提及无cite）。v3.18.9新增Trap#41 paper-queue.json幽灵条目逆方向。v3.18.5-8: D10a批量扫描+natbib盲区+注释过滤+路由修复。v3.18: Track A晋升协议。v3.16: 队列自愈+ABSOLUTE WHITE独立验证。v3.15: 轨道B四步工作流。
- **paper-quality-deep-review**: 论文质量深度审查引擎 — 从文献下载→内容分析→研究空白验证→科学假设评估→解决方法评估→文献引用质量评分→综合评分。
- **paper-queue-audit**: Directory index for paper-queue-audit: paper-queue-audit
- **paper-references-scanning**: Scan paper library for citation health: D8 (bib entry count), D10a (cite-to-bib match rate),   orphans, zombies. Class of tasks: LaTeX reference integrity auditing.
- **patent-disclosure**: 该技能以Synthos仓库为主版本。Hermes镜像为查找索引，执行时请加载Synthos路径版本。
- **pdf-download-racing**: 并行竞速PDF下载引擎 — curl_cffi TLS指纹绕过 + Sci-Hub域轮换 + LibGen + MedData。依赖 tools/paper-manager/src/。
- **pdf-to-md-notebooklm**: PDF→Markdown→NotebookLM 全流程管线。支持批量上传、自动类型检测、大文件处理。
- **political-proposal**: 参政议政提案全流程(民进/政协/人大) — 三段式: 基本情况→问题→对策。
- **project-experience-distillation**: ⚡ 最高优先级技能。From project experience to reusable skill — extract workflow patterns, design principles, and pitfalls from completed project work, abstract them into general form, and formalize as SKILL.md. Also: philosophical implementation gap analysis to drive mechanism-level improvements. The reflexive learning engine of Synthos: self-evolution through self-observation.
- **pubmed**: Deep PubMed/MEDLINE search via NCBI E-utilities — query construction, MeSH terms, batch retrieval, clinical query refinement.
- **quality**: 质量保障 — 伪证验证、黄金测试、SCI论文质量评审。
- **quality-score-assignment**: Paper satisfies `current_step in steps_completed` AND `len(steps_completed) >= 8`.
- **research**: 直接调用子类别/技能名称即可。例如：`arxiv`、`bib-integrity-audit`、`research-ideation`。
- **research-ideation**: 研究创意发散与认知引擎（RIF+CCF）。三层架构：Layer 1（10操作框架）→ 产出研究方向候选； Layer 2（8认知引擎）→
- **research-paper-search**: 主skill | 多源论文检索+全文下载编排器。入口：Semantic Scholar (API Key), PubMed, OpenAlex, arXiv (Tor), Crossref。调用子skill: arxiv, pubmed, openalex。
- **research-skill-audit**: Audit and enhance research skill coverage. Process for identifying gaps, testing existing skills, and creating/enhancing missing capabilities.
- **researcher-portrait**: Directory index for researcher-portrait: researcher-portrait
- **scc-bppv-kinematics**: Skill: scc-bppv-kinematics
- **sci-paper-quality-review**: Directory index for sci-paper-quality-review: sci-paper-quality-review
- **sci-paper-standard-structure**: Directory index for sci-paper-standard-structure: sci-paper-standard-structure
- **scientific-database-lookup**: Directory index for scientific-database-lookup: scientific-database-lookup
- **segment-anything**: Comprehensive guide to using Meta AI's Segment Anything Model for zero-shot image segmentation.
- **skill-absorption**: 双循环进化：内部反思(P0) + 外部吸收(P1)。Cross-project absorption methodology — multi-round cross-project comparison, active project tracking, self-expanding keyword discovery. 动灵驱动吸收(Entelechy-Driven Absorption v4.3).
- **skill-integrity-audit**: | 概念 | 文言 | 义 |
- **synthos**: >
- **synthos-akne-bridge**: Synthos 与 AKNE 之间双向桥接 — 论文目录规范化、技能连接、逆向边创建、Wiki 清理、自动守护重启、内容摘要注入、向量化补全。与 akne-maintenance（内部运维）和 akne-knowledge-manager（审计诊断）不同，本技能管具体的桥接操作。
- **system-bridging**: 跨系统连接模式 — 两个独立系统（知识图谱/论文管线/技能库/监控系统）之间的双向桥接。覆盖连接协议、数据注入、反向查询、同步守护、重叠检测。
- **systematic-review**: 系统综述与Meta分析工作流助手 — PRISMA流程、搜索策略设计、研究选择、质量评估、数据提取和综合支持。
- **task-router**: Synthos系统入口。路由用户查询到正确的认知原子链或执行模式。 四模式：标准链 / 探索循环 / 研究双循环 / 并行执行。 Agent-native执行，纯skill驱动零Python。
- **training**: Directory index for training — mlops/training   模型训练与微调
- **v32-multi-direction-scan**: Every cron run of autonomous-core-researcher after v31 API fix. Standardized pattern for scanning 5 rotation + 5 new directions per run.
- **viewpoint-verification**: Directory index for viewpoint-verification: viewpoint-verification
- **vllm**: Use when deploying production LLM APIs, optimizing inference latency/throughput, or serving models with limited GPU memory. Supports OpenAI-compatible endpoints, quantization (GPTQ/AWQ/FP8), and tensor parallelism.
- **writing**: 写作辅助 — 引用完整性修复、LaTeX输出、政治提案、标准论文结构。

## IO_CONTRACT

- **input**: `layer: str, query: str, context: dict` — Layer name, search query, and context
- **output**: `skill_list: list[dict]` — Filtered list of skills matching the query


## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

> 对应原则：P3（人机分层 — 路由器负责路由，原子负责执行）