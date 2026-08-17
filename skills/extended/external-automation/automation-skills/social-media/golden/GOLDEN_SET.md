---
name: social-media
description: social-media 父级路由金测集 — 验证请求正确路由到 xurl 或 xhs-content
---

# 金测集: social-media（父级路由）

> 来源: SKILL.md（父级技能目录索引，子技能: xurl, xhs-content）。
> 路由规则: X/Twitter 发帖/搜索/DM → xurl；小红书内容生成 → xhs-content（Genes SOCI-001）。
> 每个 case 验证路由决策的正确性（P1 可复现性）。

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常路由：X/Twitter 发帖 → xurl | routed=true, target_skill='xurl' |
| case_002 | 正常路由：小红书内容生成 → xhs-content | routed=true, target_skill='xhs-content' |
| case_003 | 未知子技能：抖音/WeChat 等不在子技能列表 → 拒绝路由 | routed=false, 错误含上下文与恢复建议 |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001/002: routed=true，target_skill 必须与请求平台匹配（X→xurl，小红书→xhs-content）
- case_003: 必须拒绝（routed=false），错误信息含上下文与恢复建议（RULES-异常约束）
- 父级目录不得直接执行子技能功能（VERIFICATION 第2项）

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001） |
| high | 0.7 | 重要但不致命（case_002/003） |

## 关联

- SKILL.md Genes: SOCI-001~006
- SKILL.md 验证清单：目录结构完整、请求路由正确、XHS 内容包四要素、IO 契约一致
