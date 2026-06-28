---
name: layer-index-system
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
---

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

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

> 对应原则：P3（人机分层 — 路由器负责路由，原子负责执行）