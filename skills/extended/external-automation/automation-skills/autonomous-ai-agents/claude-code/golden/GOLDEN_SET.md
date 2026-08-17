---
name: claude-code
description: GOLDEN_SET.md
---

# 金测集: claude-code

> 单一真理来源。基于 SKILL.md 真实契约（Genes CLAU-001~006 / 验证清单 / IO_CONTRACT）构造。
> 输入契约: `request: str, context: dict`；输出契约: `result: dict`。
> 每个 case 文件位于 `cases/case_XXX.json`，预期输出位于 `expected/case_XXX.json`。
> 验证方式: `python3 -c "import json; json.load(open('...'))"` 确认可解析，再按 checks 逐项比对。

## 测试用例
| ID | 描述 | 覆盖契约/基因 | 关键检查 | 权重 |
|----|------|---------|---------|------|
| case_001 | 长任务委托：`which claude` 预检通过后，`claude "task"` 以 background+notify 运行 | CLAU-001 / CLAU-002 / CLAU-003 / 验证清单第1/3/4项 | CLI 已安装（which claude 非空）；REPL 场景 `pty=true`；长任务 `background=true` 且 `notify_on_complete=true`；单次任务携带明确项目上下文 | critical |
| case_002 | 错误路径：`which claude` 为空（CLI 未安装）→ 必须失败并给出安装恢复建议，而非盲目执行 | CLAU-005 / RULES 第3条 | 执行前预检 `which claude`；缺失时 result.status=error，errors 含上下文与安装命令（npm install -g @anthropic-ai/claude-code），不得静默执行 | critical |

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
