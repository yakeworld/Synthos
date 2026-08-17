---
name: smart-home
description: smart-home 父级路由金测集 — 验证请求正确路由到子技能 openhue
---

# 金测集: smart-home（父级路由）

> 来源: SKILL.md（父级技能目录索引，子技能: openhue）。
> 本技能是路由入口：父级 SKILL.md 仅作为目录索引，实际执行由子技能完成（Genes SMAR-002）。
> 每个 case 验证路由决策的正确性（P1 可复现性）。

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常路由：Hue 灯光控制请求 → openhue | routed=true, target_skill='openhue', 父级不直接执行 |
| case_002 | 未知子技能：请求目标不在子技能列表 → 拒绝路由 | routed=false, 错误含上下文与恢复建议 |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: routed=true，target_skill 必须为 openhue；result 结构符合 IO_CONTRACT（dict）
- case_002: 必须拒绝（routed=false），错误信息含上下文与恢复建议（RULES-异常约束）
- 父级目录不得直接执行子技能功能（无功能重叠，VERIFICATION 第5项）

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001） |
| high | 0.7 | 重要但不致命（case_002，Golden Error 路径） |

## 关联

- SKILL.md Genes: SMAR-001~007
- SKILL.md 验证清单：openhue 可发现、Hue Bridge 局域网配对、IO_CONTRACT 结构、无功能重叠
