---
name: email
description: email 父级路由金测集 — 验证邮件请求正确路由到 himalaya
---

# 金测集: email（父级路由）

> 来源: SKILL.md（父级技能目录索引，子技能: himalaya）。
> 路由规则: 邮件收发/搜索请求 → himalaya（Himalaya CLI，Genes EMAI-002）。
> IO_CONTRACT: input(email_action: str, email_account: str) → output(result: dict)。
> 每个 case 验证路由决策的正确性（P1 可复现性）。

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常路由：邮件搜索请求 → himalaya | routed=true, target_skill='himalaya', 参数含 email_action/email_account |
| case_002 | 无效输入：email_action 缺失/非法 → 拒绝执行 | routed=false, 错误含上下文与恢复建议 |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: routed=true，target_skill 必须为 himalaya；输入含 email_action 与 email_account
- case_002: 必须拒绝（routed=false），错误信息含上下文与恢复建议（Genes EMAI-001/006）
- 父级目录不得直接执行子技能功能（无功能重叠）

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001） |
| high | 0.7 | 重要但不致命（case_002，Golden Error 路径） |

## 关联

- SKILL.md Genes: EMAI-001~007
- SKILL.md 验证清单：Himalaya CLI 已安装且认证有效、himalaya 可加载、输入参数完整、收件人格式校验、搜索条件明确
