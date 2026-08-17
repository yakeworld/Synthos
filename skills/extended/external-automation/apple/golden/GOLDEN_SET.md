name: apple
description: apple 金测集 — 父级路由（5 个子技能）的可执行测试
---

# 金测集: apple

> 来源: SKILL.md Golden 集合 + 验证清单 + Genes (APPL-001~006)。
> 本技能是 Apple 生态工具链父级聚合入口（atom_type: parent-skill），仅作为目录索引；
> 子技能通过 Hermes 技能加载机制自动发现，实际执行由 `skill_view(name='...')` 加载的子技能完成，父级不直接执行（APPL-001）。
> 每个 case 验证路由决策的正确性（P1 可复现性）。

## 子技能清单（路由目标）

| # | 子技能 | 典型能力 |
|---|--------|---------|
| 1 | apple-notes | Apple 备忘录读写 |
| 2 | apple-reminders | Apple 提醒事项管理 |
| 3 | findmy | 查找设备/物品定位 |
| 4 | imessage | iMessage 短信收发 |
| 5 | macos-computer-use | macOS 桌面自动化操作 |

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常路由：备忘录创建请求 | route=skill_view(name='apple-notes')；request/context 完整转交（APPL-002）；结果归属子技能 |
| case_002 | 正常路由：查找设备请求 | route=skill_view(name='findmy')；路由目标与能力匹配精确一致 |
| case_003 | 未知子技能（错误路径） | 请求能力不属于 5 个子技能任何一个 → 结构化错误：含上下文（哪个子技能、哪一步）+ 恢复建议（APPL-003） |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: 路由目标必须精确为 `apple-notes`，父级仅作目录索引，参数无父级吞并
- case_002: 路由目标必须精确为 `findmy`，设备定位能力→子技能映射无歧义
- case_003: 必须拒绝并返回 Golden Error 路径 —— 错误信息含"请求回声 + 5 个已知子技能清单 + 失败上下文 + ≥2 条恢复建议"，禁止仅返回通用错误（APPL-003）

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001 / case_003） |
| high | 0.7 | 重要但不致命（case_002） |

## 期望输出

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，包含：
- `expected_output`: 路由结果 / 错误结构
- `verification`: 可执行的校验断言列表

期望输出采用**语义等价判定**：
- 路由目标子技能名必须精确匹配（5 选 1，无歧义）
- 错误路径必须同时含 context 与 recovery 两个字段
- 边界条件（空输入/极大值）处理不崩溃（APPL-004）

## 关联

- SKILL.md Genes: APPL-001~006
- SKILL.md 验证清单: 5 项（路由正确 APPL-001 / skill_view 调用方式 / 参数无吞并 / 结果归属 / 失败恢复指引 APPL-003）
- 子技能: apple-notes, apple-reminders, findmy, imessage, macos-computer-use
