---
name: codex-cli
description: '1. **输入验证**: 输入参数/文件/路径是否完整且有效'
signature: 'codex-cli -> autonomous-ai-agents: synthetic skill for codex cli'
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
    description: '1. **输入验证**: 输入参数/文件/路径是否完整且有效'
    signature: 'codex-cli -> autonomous-ai-agents: synthetic skill for codex cli'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---


|
| API 协议 | OpenAI Responses | Anthropic Messages | OpenAI Chat Completions |
| 供应商 | OpenAI/自定义 | Anthropic | 任意 OpenAI 兼容 |
| 安装 | npm | npm/pip | 自定义 |
| 角色 | 主力编码代理 | 辅助代理 | 轻量替代 |

## IO_CONTRACT

- **input**: `coding_task: str` — 交给 codex CLI 的编码任务描述
- **input**: `provider/protocol: config` — 代理后端选择（OpenAI Responses / Anthropic Messages / OpenAI Chat Completions）
- **output**: `code_changes` — codex CLI 生成的代码修改/补丁结果
- **output**: `agent_status: str` — 执行状态与验证清单结论（输入/过程/输出/边界/错误处理五项）

## 原则 (Principles)

1. **「三议先定，方授以役。」** — 协议三选一（OpenAI Responses / Anthropic Messages / Chat Completions）须先行选定，再行调度。
2. **「输入未验，不役代理。」** — 任务描述与后端配置完整有效之前，不启动 codex CLI 执行。
3. **「五验皆毕，乃陈其果。」** — 输入/过程/输出/边界/错误五项验证齐备，方可交付代码修改结果。
4. **「未验之码，虽生勿行。」** — 不执行未验证的任意代码，不暴露内部状态。


## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[CODE-001]** 协议未选定 → 先行确定 OpenAI Responses / Anthropic Messages / Chat Completions 之一，再调度代理
- **[CODE-002]** 输入参数/文件/路径不完整或无效 → 拒绝启动 codex CLI，直至输入验证通过
- **[CODE-003]** 五项验证（输入/过程/输出/边界/错误）未齐备 → 禁止交付代码修改结果
- **[CODE-004]** 代码未经过验证 → 严禁执行任意代码，防止暴露内部状态
- **[CODE-005]** 发生执行失败 → 错误信息必须包含上下文和明确的恢复指引
- **[CODE-006]** 进行功能改进或变更 → 必须通过 Golden 集合（Input/Output/Error）测试作为单一真理来源
- **[CODE-007]** 验证过程执行 → 确保每项验证可执行、可记录、可复现，失败时记录原因和修复

## 验证清单 · VERIFICATION

- [ ] 协议已选定：OpenAI Responses / Anthropic Messages / OpenAI Chat Completions 三者明确其一（CODE-001，原则「三议先定」）
- [ ] 任务描述与后端配置完整有效后才启动 codex CLI，未验不役（CODE-002，原则「输入未验」）
- [ ] 执行过程中验证可执行、可记录、可复现，失败时已记录原因和修复（CODE-007）
- [ ] 交付前五项验证（输入/过程/输出/边界/错误处理）齐备，未齐备不交付（CODE-003，原则「五验皆毕」）
- [ ] 生成的代码修改/补丁已通过验证，未验证代码严禁执行、不暴露内部状态（CODE-004，原则「未验之码」）
- [ ] 失败时错误信息包含执行上下文和明确的恢复指引（CODE-005）
- [ ] 功能改进或变更已通过 Golden 集合（Input/Output/Error）测试（CODE-006）

## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

## Golden 集合 · GOLDEN SET

- **Golden Input**: `coding_task="为 pima 数据集补写 F1 评估脚本"` + 已选定协议 OpenAI Responses，覆盖输入验证通过的正常路径（CODE-001/002）
- **Golden Output**: `code_changes`（F1 评估脚本补丁）+ `agent_status` 记录五项验证（输入/过程/输出/边界/错误处理）齐备（CODE-003，原则「五验皆毕」）
- **Golden Error**: 输入路径指向不存在的文件 → 拒绝启动 codex CLI，`agent_status` 标记「输入未验，不役代理」，错误含上下文与恢复指引（CODE-002/005）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

## 示例 · EXAMPLES

- **示例 1**：输入 `coding_task="为 pima 数据集补写 F1 评估脚本"` 但未指定协议 → 按 CODE-001/原则「三议先定」先选定 OpenAI Responses，再按 IO_CONTRACT 校验任务描述与后端配置完整有效后启动 codex CLI → 验证：`agent_status` 记录协议选定与输入验证通过，五项验证清单（输入/过程/输出/边界/错误处理）齐备后才交付 `code_changes`（CODE-002/003）。
- **示例 2**：输入不完整的路径（如指向不存在的文件）→ 按 CODE-002 拒绝启动 codex CLI 直至输入验证通过，错误信息包含上下文与恢复指引（CODE-005/规则「异常约束」）→ 验证：未启动执行，`agent_status` 明确标记「输入未验，不役代理」。
- **示例 3**：输入功能改进需求（修改 codex 输出解析逻辑）→ 按 CODE-006 先跑 Golden 集合（Golden Input 正常路径 / Golden Output 精确匹配 / Golden Error 失败路径）→ 验证：Golden 测试全过后才交付补丁，未验证代码严禁执行（CODE-004），失败项已记录原因和修复（CODE-007）。
