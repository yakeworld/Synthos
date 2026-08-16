---
name: layer-index-system
description: 1. 确认输入参数完整
signature: 'layer-index-system -> meta: synthetic skill for layer index system'
allowed-tools:
- terminal
- read_file
- write_file
- session_search
version: 1.0.0
license: MIT
metadata:
  synthos:
    atom_type: mechanical
    description: 1. 确认输入参数完整
    signature: 'layer-index-system -> meta: synthetic skill for layer index system'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
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
category: meta
signature: "layer-index-system -> meta: Navigation index for system infrastructure — devops, automation, tool integratio"
related_skills: ['layer-index', 'synthos']
description: "Navigation index for system infrastructure — devops, automation, tool integration, and monitoring."
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    priority: P3
    atom_type: layer-index
    signature: "layer: str, query: str, context: dict -> skill_list: list[dict]"
    related_skills: []

# System Infrastructure — 系统基础设施

## Purpose

Navigation index for system maintenance: devops, automation, tool integration, and monitoring.

## Skills in this Layer (50 total)

- **3d-curve-fitting-figures**: 3D曲线拟合图的生成规范：从点云到拟合曲线到出版级Figure。 覆盖拟合重建陷阱、多标本复合布局、分段数据合并、argsort路径错乱。
- **automation-skills**: **触发条件**: 对一批论文（10-34 篇）批量处理 `step_quality_check.md` 中的 quality_score 并写入 `state.json`。
- **autonomous-ai-agents**: 自主AI智能体编排 — 多Agent协作、委托任务、跨Agent通信。
- **axolotl**: Expert guidance for fine-tuning LLMs with Axolotl — YAML configs, 100+ models, LoRA/QLoRA, DPO/KTO/ORPO/GRPO, multimodal support.
- **chinese-form-automation**: Directory index for chinese-form-automation: chinese-form-automation
- **claude-code**: Delegate coding to Claude Code CLI — features, PRs, refactoring, review.
- **codebase-inspection**: Analyze repositories for lines of code, language breakdown, file counts, and code-vs-comment ratios using `pygount`.
- **codex**: Delegate coding to OpenAI Codex CLI — 主力编码代理。覆盖多节点profile配置、无PTY执行、Cron集成、多模型并行。
- **computational-ode-modeling**: Directory index for computational-ode-modeling: computational-ode-modeling
- **cron-system-maintenance**: Cron任务运维：诊断error状态、修复脚本缺陷、验证连接性。覆盖cron job list分析、错误分类、脚本语法验证、prompt更新、vLLM多节点负载均衡。
- **debug-env-variables**: DevOps — environment configuration, subprocess shells, credential injection.
- **devops**: DevOps运维 — Cron任务管理、看板编排、worker管理。
- **dogfood**: This skill guides you through systematic exploratory QA testing of web applications using the browser toolset. You will navigate the application, interact with elements, capture evidence of issues, and produce a structured bug report.
- **evaluation**: Directory index for evaluation — mlops/evaluation   模型评估与实验追踪
- **evaluation**: Directory index for evaluation — mlops/evaluation   模型评估与实验追踪
- **excalidraw**: Hand-drawn Excalidraw JSON diagrams (arch, flow, seq).
- **github**: GitHub工作流 — PR审查、Issue管理、仓库管理、CI/CD。
- **github-auth**: Skill: github-auth
- **github-code-review**: Skill: github-code-review
- **github-discussions**: Create, list, search, and manage GitHub Discussions via GraphQL API.
- **github-issues**: Skill: github-issues
- **github-pr-workflow**: Skill: github-pr-workflow
- **github-repo-management**: ```bash
- **godmode**: Bypass safety filters on API-served LLMs using techniques from [G0DM0D3](https://github.com/elder-plinius/G0DM0D3) and [L1B3RT4S](https://github.com/elder-plinius/L1B3RT4S). Three attack modes plus Hermes-native configuration for persistent jailbreaking.
- **hermes**: Hermes Agent管理 — Cron生命周期、配置、工具管理。
- **hermes-agent**: Configure, extend, or contribute to Hermes Agent — the open-source AI agent framework by Nous Research.
- **hermes-scheduler**: 本技能适用于以下场景：
- **kanban-orchestrator**: Create Kanban tasks when any of these are true:
- **kanban-worker**: Your workspace kind determines how you should behave inside `$HERMES_KANBAN_WORKSPACE`:
- **lm-evaluation-harness**: Evaluates LLMs across 60+ academic benchmarks (MMLU, HumanEval, GSM8K, TruthfulQA, HellaSwag). Use when benchmarking model quality, comparing models, reporting academic results, or tracking training progress. Industry standard used by EleutherAI, HuggingFace, and major labs. Supports HuggingFace, vLLM, APIs.
- **maintenance**: Synthos维护 — 认知原子结构完整性验证。
- **mcp**: MCP集成 — 模型上下文协议服务器配置与工具注册。
- **mcp-ecosystem-guide**: Directory index for mcp-ecosystem-guide: mcp-ecosystem-guide
- **medical-image-centerline**: Directory index for medical-image-centerline: medical-image-centerline
- **memory-optimization-system**: Directory index for memory-optimization-system — > **注意**: 本技能是记忆管理的唯一入口。`memory-enhancement` 已合并至此。
- **mlops**: 机器学习运维 — ODE建模、实验管理、模型训练、推理部署、模型架构。
- **native-mcp**: Directory index for native-mcp: native-mcp
- **opencode**: 1. **非常驻服务** — OpenCode 不是 daemon，按需启动、用完即关。`ps aux | grep opencode` 无进程是正常状态，不是故障。
- **python-docx**: 创建/读取/编辑.docx — python-docx: 表格/字体/页面设置。
- **red-teaming**: 红队测试 — LLM越狱攻击（Parseltongue、GODMODE、ULTRAPLINIAN）。
- **remote-gpu-training**: Directory index for remote-gpu-training: remote-gpu-training
- **repo-path-sanity**: **Purpose:** Diagnose and fix broken directory relationships when `~/Synthos` and `/media/yakeworld/sda2/Synthos` diverge into independent copies instead of symlink.
- **shared**: 共享资源 — 跨技能引用的通用资源。
- **sklearn-benchmark**: 设计、运行和优化scikit-learn多模型基准测试。覆盖预赛时序检测、失败模型预判、大数据集模型过滤、OOM防护、并行策略、结果整合。
- **synthos-probe**: Class: maintenance / audit
- **training-pipeline-principles**: Skill: training-pipeline-principles
- **trl-fine-tuning**: TRL provides post-training methods for aligning language models with human preferences.
- **unsloth**: Comprehensive assistance with unsloth development, generated from official documentation.
- **webhook-subscriptions**: Webhook subscriptions: event-driven agent runs.
- **weights-and-biases**: Use Weights & Biases (W&B) when you need to:

## IO_CONTRACT

- **input**: `layer: str, query: str, context: dict` — Layer name, search query, and context
- **output**: `skill_list: list[dict]` — Filtered list of skills matching the query

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引

## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

> 对应原则：P3（人机分层 — 路由器负责路由，原子负责执行）

# Layer Index System---

> (P032 去重: 以下为合并前第二份中的 1 行独有内容, 保留以防丢失)
# Layer Index System
## Genes (策略基因)
> 紧凑策略表示。条件→策略。需要深度时参考完整文档。
- **[LAYE-001]** 输入参数（layer, query, context）不完整或无效 → 立即执行输入验证并拒绝执行，确保参数类型、范围及格式符合契约
- **[LAYE-002]** 执行核心操作前 → 必须确认输入参数完整，并参考目录下的 scripts/ 或 references/ 进行标准化处理
- **[LAYE-003]** 生成输出结果时 → 严格校验输出结构（skill_list: list[dict]）是否符合 IO_CONTRACT 定义，确保命名与编码一致
- **[LAYE-004]** 遇到空输入、极大值或异常场景 → 触发边界验证逻辑，提供包含上下文和恢复建议的明确错误信息
- **[LAYE-005]** 涉及代码执行或状态变更 → 遵循安全约束，不执行未验证的任意代码，不暴露内部状态，违规操作必须拒绝或隔离
- **[LAYE-006]** 进行系统改进或功能迭代 → 必须通过 Golden 集合（标准输入/预期输出/预期错误）测试，将其作为单一真理来源
- **[LAYE-007]** 验证过程执行中 → 确保每项验证可执行、可记录、可复现，失败时详细记录原因及修复方案