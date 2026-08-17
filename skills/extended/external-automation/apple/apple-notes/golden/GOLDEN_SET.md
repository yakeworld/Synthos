---
name: apple-notes
description: apple-notes 金测集 — memo 管理 Apple Notes 的可执行测试
---

# 金测集: apple-notes

> 来源: SKILL.md Golden 集合 + 验证清单 + Genes (APPL-001~007) + IO_CONTRACT。
> 核心能力：通过 `memo` CLI 管理 Apple Notes（查看/搜索/创建/编辑/删除/移动/导出），
> 笔记经 iCloud 跨设备同步。
> IO_CONTRACT: input `note_action: str, content: str` → output `note_result: dict`。
> 每个 case 验证命令选择、参数用法与限制处理（P1 可复现性）。

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常：创建带标题笔记 | 非交互式 `memo notes -a "Title"`（APPL-003）；note_action/content 校验通过（输入约束） |
| case_002 | 正常：模糊搜索笔记 | `memo notes -s "query"`；搜索命中结果以 note_result dict 返回（输出契约一致） |
| case_003 | 错误路径：编辑含附件笔记 | 拒绝直接编辑（APPL-002），错误信息含上下文+恢复建议，建议改为仅查看/手动处理 |
| case_004 | 错误路径：`memo` 未安装 | 检测 `command -v memo` 失败 → 返回安装指引（brew tap + install），不静默失败（异常约束） |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: 命令必须精确为 `memo notes -a "<title>"`，非交互式（不进入交互编辑器）
- case_002: 搜索走 `memo notes -s`，结果结构为 dict 且字段稳定；无命中时返回空集而非崩溃
- case_003: 必须拒绝编辑操作（含图片/附件的笔记），错误含「限制说明 + ≥2 条恢复建议」（仅查看 / 手动处理），且未执行破坏性命令
- case_004: 错误信息必须含上下文（哪一步失败）与可执行恢复命令（`brew tap antoniorodr/memo && brew install antoniorodr/memo/memo`），禁止仅返回通用错误
- 所有 case: 执行前确认 macOS + 自动化权限前置（验证清单第 1 项）；agent 内部记忆请求不得误路由到本技能（APPL-005）

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001 / case_003） |
| high | 0.7 | 重要但不致命（case_002 / case_004） |

## 期望输出

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，包含：
- `expected_output`: 命令 / 结果结构 / 错误结构
- `verification`: 可执行的校验断言列表

期望输出采用**语义等价判定**：
- 命令字符串按 SKILL.md Quick Reference 精确匹配（允许标题/查询参数不同，flag 结构必须一致）
- note_result 必须是 dict，键名稳定（如 `status`, `note_title`, `error`, `recovery`）
- 错误路径必须同时含 `error` 上下文与 `recovery` 建议两个字段（异常约束）

## 关联

- SKILL.md Genes: APPL-001~007
- SKILL.md 验证清单: 5 项（环境就绪 / 场景选择 / 命令用法 / 附件限制 APPL-002 / 交互模式 APPL-004）
- 相关技能: apple（父级路由）, apple-reminders, memory 工具（agent 内部笔记）
