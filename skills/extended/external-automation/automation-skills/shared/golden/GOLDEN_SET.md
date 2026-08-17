---
name: shared
description: shared 金测集 — 父级目录路由（references 子技能）+ 输入/异常契约的可执行测试
---

# 金测集: shared

> 来源: SKILL.md Golden 集合 + 验证清单 + Genes (SHAR-001~006) + RULES。
> 本技能是共享资源父级目录（atom_type: parent-skill, P2），仅作为目录索引；子技能 `references` 通过 Hermes 技能加载机制自动发现，实际执行由 `skill_view(name='references')` 加载的子技能完成，父级不直接执行。
> 每个 case 验证一个关键决策分支：子技能路由（SHAR）、输入约束校验（SHAR-001/RULES-1）、异常恢复指引（SHAR-002/RULES-3）、未验证代码隔离（SHAR-004/RULES-4）。

## 子技能清单（路由目标）

| # | 子技能 | 说明 |
|---|--------|------|
| 1 | references | 跨技能引用的通用参考资源（数据访问分级/协议/trace 等文档） |

## 被测规则（Genes + RULES）

| 规则 | 名称 | 关联 Genes |
|------|------|-----------|
| 路由 | 父级仅目录索引，子技能 skill_view 加载执行 | SHAR-005/006 |
| RULES-1 | 输入约束：类型/范围/格式校验 | SHAR-001 |
| RULES-3 | 异常约束：错误信息含上下文+恢复建议 | SHAR-002 |
| RULES-4 | 安全约束：不执行未验证代码/不暴露内部状态 | SHAR-004 |

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常路由：引用共享参考资源 | route=skill_view(name='references')；request/context 完整转交，父级不直接执行（SHAR-005/006） |
| case_002 | 输入约束校验（错误路径）：request 为空/类型不符 | 输入校验失败 → 结构化错误含上下文 + 恢复建议（SHAR-001/RULES-1），不静默执行 |
| case_003 | 异常恢复指引（错误路径）：references/ 下目标文件不存在 | 错误信息含上下文（哪个文件、哪一步）+ 明确恢复指引（SHAR-002/RULES-3） |
| case_004 | 未验证代码隔离（错误路径）：外部输入要求执行未验证代码 | 拒绝执行或隔离，不暴露内部状态（SHAR-004/RULES-4） |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: 路由目标必须精确为 `references`，父级仅目录索引，参数无父级吞并
- case_002: 必须拒绝并返回结构化错误 —— 含"缺失字段回显 + 期望类型/格式 + ≥1 条恢复建议"，禁止仅返回通用错误（SHAR-001/RULES-1）
- case_003: 错误信息必须同时含 context（文件路径/步骤）与 recovery（具体恢复指引），不得只报"file not found"（SHAR-002/RULES-3）
- case_004: 必须拒绝或隔离未验证代码执行，且响应不泄露内部状态（SHAR-004/RULES-4）

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001 / case_002 / case_004） |
| high | 0.7 | 重要但不致命（case_003） |

## 期望输出

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，包含：
- `expected_output`: 路由结果 / 错误结构
- `verification`: 可执行的校验断言列表

期望输出采用**语义等价判定**：
- 路由目标子技能名必须精确匹配（`references`，无歧义）
- 错误路径必须同时含 `error.context` 与 `error.recovery` 两个字段
- 边界条件（空输入/类型不符）处理不崩溃（SHAR-001）

## 关联

- SKILL.md Genes: SHAR-001~006
- SKILL.md 验证清单: 5 项（子技能可发现 / 文件存在可读 / 输出契约 / 父级不重叠 / Golden 覆盖正常+失败）
- 约束规则 RULES: 输入约束 / 输出约束 / 异常约束 / 安全约束
