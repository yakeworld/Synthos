---

name: viewpoint-verification
description: "对假设和论证进行多角度验证（反方观点、证伪条件、鲁棒性），支持 Bayesian 评分、可证伪性检验。"
author: Synthos
license: MIT
version: 1.0.0
allowed-tools: shell (bash), Read (view), Write (write), task_delegation (agent, inline)
metadata:
  synthos:
    priority: P1
    atom_type: cognitive-atom
    description: "Multi-perspective hypothesis and argument verification"
    signature: "hypothesis: str, context: dict -> verification_report: dict (score, evidence, counter_evidence, confidence)"
    related_skills: [hypothesis-generation, argument-expression, quality-gate]

---

# Viewpoint Verification — 观点验证

> 对假设和论证进行多角度验证：反方观点构造、证伪条件检验、鲁棒性测试、Bayesian 评分。

## 原理层·文言

> 「正观反照，虚实相参。」立论易，破论难。
> 以反证正，以虚验实。不破不立，不证不立。

## 方法层·白话

观点验证是认知管道第6步。输入假设或论证，输出验证报告（置信度、反证、弱点）。

## 触发条件

- 假设生成 (HYP) 或论证表达 (ARG) 产出了可验证内容，需独立验证
- 论文管线进入质量验证阶段（G1-G7）
- 用户要求"评估/检验/验证"

## 输入契约

| 字段 | 类型 | 必需 | 说明 |
|------|------|:----:|------|
| `hypothesis` | str | ✅ | 待验证的假设或论证 |
| `context` | dict | ❌ | 上下文（已执行原子、历史输出） |

## 输出契约

| 字段 | 类型 | 说明 |
|------|------|------|
| `verification_report` | dict | 验证报告 |
| `score` | float | 综合评分 0-1 |
| `evidence` | list[dict] | 支持证据 |
| `counter_evidence` | list[dict] | 反证 |
| `confidence` | float | 置信度 0-1 |
| `weaknesses` | list[str] | 弱点列表 |

## 快速参考

详细内容在 `references/` 目录（Bayesian 假设、Citation F1 方法、可重复性检验、模拟评审等）。

1. 加载假设+上下文
2. 构造反方观点
3. 执行证伪条件检验
4. 执行鲁棒性测试
5. 输出验证报告
6. 保存至 `outputs/{session}/verification.json`

## 验证清单

- [ ] 反方观点已构造
- [ ] 证伪条件已检查
- [ ] 鲁棒性测试已执行
- [ ] 评分有依据（非主观）
- [ ] 弱点有修复建议

## 边界声明

见 `BOUNDARY.md` — 本原子只做验证，不做假设生成、不做论证构建、不做关联发现。




# Viewpoint Verification

