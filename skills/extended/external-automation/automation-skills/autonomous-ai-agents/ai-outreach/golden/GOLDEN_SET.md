---
name: ai-outreach
description: GOLDEN_SET.md
---

# 金测集: ai-outreach

> 单一真理来源。基于 SKILL.md 真实契约（Genes AIO-001~007 / 验证清单 / IO_CONTRACT）构造。
> 输入契约: `request: str, context: dict`；输出契约: `result: dict`。
> 每个 case 文件位于 `cases/case_XXX.json`，预期输出位于 `expected/case_XXX.json`。
> 验证方式: `python3 -c "import json; json.load(open('...'))"` 确认可解析，再按 checks 逐项比对。

## 测试用例
| ID | 描述 | 覆盖契约/基因 | 关键检查 | 权重 |
|----|------|---------|---------|------|
| case_001 | 被动发现通道初始化：新建仓库根目录 AGENTS.md + README 链接 | AIO-001 / 验证清单第1项 | AGENTS.md 存在于项目根目录且含 AGENT-TO-AGENT 注释块、Architecture 段、"For AI Agents" 指引；README.md 含指向 AGENTS.md 的链接；git 已跟踪该文件 | critical |
| case_002 | Moltbook 注册错误路径：api_key 经 terminal 输出被脱敏，状态 pending_claim 时尝试发帖 | AIO-003 / AIO-007 / 陷阱4/5 | api_key 未经 Python 直接捕获而被脱敏（`***`）→ 判定安全违规；状态非 `active` 时发帖请求必须被拒绝并给出恢复建议（先完成 claim），不得静默失败 | critical |

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
