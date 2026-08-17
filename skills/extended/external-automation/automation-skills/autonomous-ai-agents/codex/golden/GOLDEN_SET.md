---
name: codex
description: GOLDEN_SET.md
---

# 金测集: codex

> 单一真理来源。基于 SKILL.md 真实契约（Genes CODE-001~007 / 验证清单 / IO_CONTRACT / Pitfalls）构造。
> 输入契约: `request: str, context: dict`；输出契约: `result: dict`。
> 每个 case 文件位于 `cases/case_XXX.json`，预期输出位于 `expected/case_XXX.json`。
> 验证方式: `python3 -c "import json; json.load(open('...'))"` 确认可解析，再按 checks 逐项比对。

## 测试用例
| ID | 描述 | 覆盖契约/基因 | 关键检查 | 权重 |
|----|------|---------|---------|------|
| case_001 | 主力节点一次性编码任务（cron 脚本模式，无 PTY） | CODE-001 / CODE-005 / CODE-006 / 验证清单第5项 | 运行目录是 git 仓库；`codex exec` 将 prompt 作为 CLI 参数（非 stdin/stdin-only）；`--yolo` 仅用于可信/隔离环境；脚本含 `#!/bin/bash` + `set -euo pipefail` + `cd` 到工作目录；无 PTY 依赖 | critical |
| case_002 | 错误路径：非 git 目录 + DeepSeek 供应商 → Codex 拒绝运行 + wire_api 不兼容 | CODE-004 / CODE-007 / Pitfall 1/10 / 验证清单第1/6项 | 非 git 目录必须先 `git init` 临时仓库否则拒绝（Pitfall 1）；供应商 wire_api 必须为 `responses`，DeepSeek 仅 chat/completions → 401/端点不存在 → 必须失败并给出降级建议（改走 OpenCode 或 cron agent provider），不得通过 Codex 调用 | critical |

## 通过标准
- 加权总分 ≥ 0.80
- 所有 critical 检查通过（case_001 / case_002 任一 critical 失败则整体不通过）
- 输出 result 为合法 dict 且含 `status`、`checks`、`errors` 三个键
- 错误路径必须包含上下文与恢复建议（RULES 第3条：异常约束）

## 权重
| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |

## 用例索引
| 用例 | 输入 | 预期输出 | 类型 |
|------|------|---------|------|
| case_001 | cases/case_001.json | expected/case_001.json | 正常路径 |
| case_002 | cases/case_002.json | expected/case_002.json | 错误路径 |
