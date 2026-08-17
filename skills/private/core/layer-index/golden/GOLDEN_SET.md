---
name: layer-index
description: GOLDEN_SET.md
---

# 金测集: layer-index

> 核心科研栈导航索引：映射 88 个技能（7 认知原子 + 论文流水线 + 研究方法 + AI/ML 工具），按 layer/query/context 过滤并返回匹配技能列表。
> IO_CONTRACT: input `layer: str, query: str, context: dict` → output `skill_list: list[dict]`。
> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

## 测试用例

| ID | 描述 | 关键检查 | 权重 |
|----|------|---------|------|
| 1 | 正常路径：按 query 检索认知原子技能（"假设生成"） | `skill_list` 命中 hypothesis-generation 等匹配项；输出结构符合 IO_CONTRACT `list[dict]`；命中条目与 SKILL.md "Skills in this Layer" 清单一致，无失效条目 | critical |
| 2 | 错误路径：query 无匹配 + 输入参数不完整 | 无匹配时返回空列表且附检索建议（含上下文与恢复建议）；`layer`/`query` 缺失时返回错误状态码而非静默执行（异常约束） | critical |

## 通过标准

- 加权总分 ≥ 0.80
- 所有 critical 检查通过
- 输出结构严格符合 IO_CONTRACT（`skill_list: list[dict]`，每项含 name/description）
- 索引条目与 SKILL.md 清单（88 个技能）逐一对应，无遗漏无重复（验证清单第 1 条）
- 错误信息包含上下文和恢复建议（RULES 异常约束）

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |

## 已知陷阱（对应 LAYE 基因）

1. 执行核心操作前未确认输入参数完整 → 违反 LAYE-002，必须先校验参数
2. 输出未保存/未报告 → 违反 LAYE-003，须闭环质量保障
3. 索引与 SKILL.md 清单漂移 → 条目数/名称不一致即失准，须同步更新
