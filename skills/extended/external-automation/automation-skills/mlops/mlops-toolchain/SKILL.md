---
name: mlops-toolchain
description: "MLOps toolchain: model training, inference, evaluation, paper analysis, literature review."
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    atom_type: composite
    priority: P1
    signature: "task_desc: str, context: dict -> result: dict"
    related_skills: []

---

# mlops-toolchain

## Purpose

Composite skill that merges 24 overlapping skills into a unified interface.

## Members (24)

- **audiocraft**: Comprehensive guide to using Meta's AudioCraft for text-to-music and text-to-audio generation with MusicGen, AudioGen, and EnCodec.
- **citation-bib-crossref**: Scan paper directories for mismatches between `\\cite{key}` calls in `.tex` files and `@type{key}` entries in `.bib` files. Produces D8 (bib count) and D10a (match percentage) metrics, plus orphan/zombie classification.
- **comfyui**: Directory index for comfyui: comfyui
- **dspy**: Use DSPy when you need to:
- **huggingface-hub**: HuggingFace hf CLI: search/download/upload models, datasets.
- **inference**: Directory index for inference — mlops/inference   模型推理服务与优化
- **literature-monitor**: Directory index for literature-monitor: literature-monitor
- **llama-cpp**: Use this skill for local GGUF inference, quant selection, or Hugging Face repo discovery for llama.cpp.
- **models**: Directory index for models — mlops/models   模型架构
- **obliteratus**: 9 CLI methods, 28 analysis modules, 116 model presets across 5 compute tiers, tournament evaluation, and telemetry-driven recommendations.
- **outlines**: Use Outlines when you need to:
- **paper-citation-health**: Scan all papers in `outputs/papers/` for citation bibliographic health metrics D8 (bib entries) and D10a (cite-to-bib match %).
- **paper-cron-scan**: Cron job 不是完整的论文管线执行，而是**轻量级扫描**：验证白空间稳定、发现新竞争、推进管线状态。
- **paper-queue-audit**: Directory index for paper-queue-audit: paper-queue-audit
- **paper-references-scanning**: Scan paper library for citation health: D8 (bib entry count), D10a (cite-to-bib match rate),   orphans, zombies. Class of tasks: LaTeX reference integrity auditing.
- **research-skill-audit**: Audit and enhance research skill coverage. Process for identifying gaps, testing existing skills, and creating/enhancing missing capabilities.
- **sci-paper-standard-structure**: Directory index for sci-paper-standard-structure: sci-paper-standard-structure
- **scientific-database-lookup**: Directory index for scientific-database-lookup: scientific-database-lookup
- **segment-anything**: Comprehensive guide to using Meta AI's Segment Anything Model for zero-shot image segmentation.
- **skill-integrity-audit**: | 概念 | 文言 | 义 |
- **training**: Directory index for training — mlops/training   模型训练与微调
- **v32-multi-direction-scan**: Every cron run of autonomous-core-researcher after v31 API fix. Standardized pattern for scanning 5 rotation + 5 new directions per run.
- **vllm**: Use when deploying production LLM APIs, optimizing inference latency/throughput, or serving models with limited GPU memory. Supports OpenAI-compatible endpoints, quantization (GPTQ/AWQ/FP8), and tensor parallelism.
- **writing**: 写作辅助 — 引用完整性修复、LaTeX输出、政治提案、标准论文结构。

## IO_CONTRACT

- **input**: `task_desc: str, context: dict` — Task description and context
- **output**: `result: dict` — Merged results from all member skills

> 对应原则：P3（人机分层 — 路由器负责路由，原子负责执行）