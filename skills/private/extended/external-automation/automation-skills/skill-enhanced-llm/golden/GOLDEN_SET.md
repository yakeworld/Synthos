---
name: skill-enhanced-llm
description: skill-enhanced-llm 金测集 — 技能使用率扫描与未映射目录清理判定的可执行测试
---

# 金测集: skill-enhanced-llm

> 来源: SKILL.md Golden 集合 + 验证清单 + Genes (SKIL-001~006) + 原则（凡数必源 /
> 先核后清 / 源一不二 / 统计可复）。
> 本技能扫描 `skills/` 与 cron 任务目录，基于 `evolution-state.json`（唯一数据源，
> v2 口径）生成技能使用率报告，并对未映射目录做"先核后清"清理判定。
> IO_CONTRACT: input `skills/ + cron 任务目录` + `evolution-state.json` → output
> `references/skill-usage-data(-v2).md` + `unmapped_dirs: list[str]`。
> 每个 case 验证一条真实可执行的操作契约（P1 可复现性）；错误路径必须返回结构化
> Golden Error（含 context + ≥2 条恢复建议），禁止仅返回通用错误。

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常：扫描 27 技能 + 21 cron → 生成 v2 报告（与 v1 同口径）+ `unmapped_dirs: []` | 所有数字（27/21/1352/3）有采集命令溯源（SKIL-001 凡数必源）；v2 与 v1 同口径且以 evolution-state.json 为唯一数据源（SKIL-003 源一不二）；21 个 cron 统计命令可执行可复现（SKIL-004 统计可复）；报告发布前验证通过 |
| case_002 | 错误：扫描发现未映射目录 → 先核后清，核验发现在用则拒绝清理 | 命中 SKIL-002 → 清理前必须核验目录不在用（无 cron 引用 + 无调用记录 + 无在用技能引用）；命中 SKIL-005 → 标记未映射目录；核验发现目录在用 → 不执行清理（防误删，SKIL-006 触发回滚检查）；返回结构化 Golden Error（context + ≥2 recovery） |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: 报告中每个数字声明（27 技能 / 21 cron / 1352 次运行 / 3 已归档）都附带
  采集命令（SKIL-001 凡数必源，无源则删）；v2 与 v1 数据口径一致（SKIL-003 源一不二）；
  `unmapped_dirs == []`；21 个 cron 统计命令均可执行且结果可复现（SKIL-004）
- case_002: 清理判定必须先于删除动作完成（SKIL-002 先核后清）；核验通过才允许清理
  并更新技能库统计（SKIL-005）；核验发现在用 → `cleanup_executed == false` 且
  `unmapped_dirs` 保留标记供人工复核；错误结构必须同时含 `context`
  （核验证据：cron 引用/调用记录/在用引用 的具体检查结果）与 ≥2 条可操作 `recovery`

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001 / case_002） |
| high | 0.7 | 重要但不致命（扩展用例） |

## 期望输出

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，包含：
- `expected_output`: 报告统计 / unmapped_dirs / 错误结构
- `verification`: 可执行的校验断言列表

期望输出采用**语义等价判定**：
- 正常路径每个数字字段都有 `source_command`（P0 证据可溯性）
- 正常路径 v1/v2 口径一致字段相等（`v1_v2_consistent == true`）
- 错误路径必须同时含 `context` 与 `recovery` 两个字段，且 `cleanup_executed`
  与核验结果严格对应（核验失败 → false）

## 关联

- SKILL.md Genes: SKIL-001~006
- SKILL.md 验证清单: 3 项（v2 数据一致 / 21 cron 命令已验证 / 未映射目录清理无误删）
- 参考文件: references/skill-usage-data.md (v1), references/skill-usage-data-v2.md (v2)
