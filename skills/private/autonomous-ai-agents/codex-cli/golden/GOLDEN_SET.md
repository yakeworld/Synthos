# GOLDEN_SET.md — codex-cli

> 对应原则：P1 原子可复现性、P3 人机分层；技能原则「三议先定」「输入未验，不役代理」「五验皆毕」
> golden_set_origin: self_defined
> 单一真理来源：所有功能改进/变更必须通过本 golden 测试（CODE-006）

## 设计依据

本技能调度 codex CLI 执行编码任务。金标准自设，设计目标验证：**协议三选一先行选定后，输入验证通过才启动 codex CLI；执行后五项验证（输入/过程/输出/边界/错误处理）齐备才交付 code_changes；输入非法时拒绝启动并给出含上下文与恢复指引的错误**。

## 金标准覆盖范围

| 维度 | 覆盖 | 说明 |
|------|:--:|------|
| 协议选定 | 3 协议 | OpenAI Responses / Anthropic Messages / OpenAI Chat Completions |
| 正常路径 | 2 case | 输入验证通过 + 五项验证齐备后交付 |
| 错误路径 | 1 case | 输入路径不存在 → 拒绝启动 |
| 验证清单 | 5 项 | 输入/过程/输出/边界/错误处理 |

## 测试用例表 (cases/)

| case | 类型 | 输入摘要 | 期望结论 |
|------|------|----------|----------|
| case_001 | 正常 | `coding_task="为 pima 数据集补写 F1 评估脚本"` + 协议 OpenAI Responses | code_changes（F1 脚本补丁）+ agent_status 五项验证齐备 |
| case_002 | 正常(未指定协议) | `coding_task="为 pima 数据集补写 F1 评估脚本"`，协议未指定 | 按 CODE-001 先选定协议（默认 OpenAI Responses），再校验输入后启动；agent_status 记录协议选定与输入验证通过 |
| case_003 | 错误路径 | `coding_task` 指向不存在的文件路径 | 拒绝启动 codex CLI；agent_status 标记「输入未验，不役代理」；错误含上下文与恢复指引 |

## 通过标准

- **协议先行**：调度前协议三选一已明确（CODE-001）；未指定时默认选定 OpenAI Responses 并在 agent_status 记录。
- **输入验证**：任务描述与后端配置完整有效才启动（CODE-002）。
- **五项验证**：交付前 输入/过程/输出/边界/错误处理 五项齐备，未齐备不交付（CODE-003）。
- **未验之码勿行**：生成的 code_changes 必须经过验证，未验证代码不执行、不暴露内部状态（CODE-004）。
- **错误处理**：失败时错误信息含执行上下文 + 明确恢复指引（CODE-005）。

## pass_threshold: 0.80

3 个 case 权重加权分 ≥ 0.80 且全部 critical 检查通过。
critical 检查：case_001 的五项验证齐备、case_003 的拒绝启动。

## 更新历史

| 版本 | 日期 | 变更 | 审批 |
|------|------|------|------|
| 0.1.0 | 2026-07-30 | 初始自设金标准，3 个 case（正常 2 + 错误 1） | Synthos Agent |
