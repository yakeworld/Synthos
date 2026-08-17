---
name: creative-ideation
description: GOLDEN_SET.md
---

# 金测集: creative-ideation

> 来源: SKILL.md Genes CREA-001~007 + 验证清单 + Output Format 模板。
> 语义判定: 创意生成无确定性输出，golden 校验的是**结构契约**（约束来源、3 个想法、每想法字段、匹配表一致性、Output Format 合规），而非具体文案。
> P1 可复现性: 同一 input 必须产生符合 expected 结构约束的输出（文案可不同，结构必须一致）。

## 设计依据

核心契约（来自 SKILL.md）:
1. 约束必须来自约束库（含 references/full-prompt-library.md），且按"最宽泛"原则解读（CREA-001/002）
2. **恰好 3 个**具体项目想法，每个含一行 pitch + 2-3 句说明（CREA-003）
3. 每个想法附 `⏱` 时间预算（weekend/week/month）+ `🔧` 技术栈（验证清单第 3 条）
4. 约束选择匹配用户画像（Matching Constraints to Users 表）（CREA-004/005/006）
5. 输出符合 Output Format 模板（## Constraint: 头 + 引用块 + ### Ideas 编号列表）
6. 用户选定后必须立即进入构建阶段（CREA-007）
7. 空/无意义输入 → 结构化错误（约束规则第 3 条: 错误信息含上下文和恢复建议）

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常: 实用型用户（"I want something useful"） | constraint ∈ 痛点类约束（匹配表）; ideas 恰好 3 个; 每 idea 含 pitch+description+time_budget+stack; 输出符合 Output Format |
| case_002 | 错误路径: 空请求 | 返回结构化错误（error_type/context/recovery 非空）; ideas_count == 0; 不崩溃 |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: `constraint` 非空且属于痛点类约束集合（Solve your own itch / The CLI tool that should exist / Automate the annoying thing）；`ideas` 数组长度 == 3；每个 idea 的 `pitch`/`description`/`time_budget`/`stack` 四字段非空，`time_budget ∈ {weekend, week, month}`；`format_compliant == true`（## Constraint: 头 + 引用块 + ### Ideas 编号列表）
- case_002: `error` 非空且含 `error_type`、`context`、`recovery` 三个子字段；`ideas_count == 0`；不崩溃（进程正常退出）

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（ideas 数量 == 3 / 错误路径结构化） |
| high | 0.7 | 约束匹配用户画像、Output Format 合规 |
| medium | 0.4 | 时间预算/技术栈字段完备 |

## 关联

- SKILL.md Genes: CREA-001~007
- 约束库: SKILL.md § Constraint Library + references/full-prompt-library.md
- 验证清单: SKILL.md § 验证清单 · VERIFICATION
- IO_CONTRACT: `request: str, context: dict -> result: dict`

## 更新历史

| 版本 | 日期 | 变更 | 审批 |
|------|------|------|------|
| 0.1.0 | 2026-07-02 | 初始金测集，2 个 case（实用型正常路径 + 空请求错误路径） | Synthos Agent |
