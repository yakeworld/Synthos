---

name: argument-expression
description: "将假设转化为结构化学术论证（论文章节+论据链），支持 Toulmin 模型、Hyland 修辞框架、IMRAD 验证。"
author: Synthos
license: MIT
version: 1.0.0
allowed-tools: shell (bash), Read (view), Write (write), task_delegation (agent, inline)
metadata:
  synthos:
    priority: P1
    atom_type: cognitive-atom
    description: "Academic argument construction from hypotheses"
    signature: "claims: list[Claim], evidence: list[Evidence] -> argument_chain: ArgumentChain (structure, strengths, gaps, counterarguments)"
    related_skills: [hypothesis-generation, viewpoint-verification, quality-gate]

---

# Argument Expression — 论证表达

> 将假设转化为结构化学术论证（论文章节 + 论据链），确保每个论断有证据支撑。

## 原理层·文言

> 「立言必立据，立据必立源。」言之无文，行而不远。
> 引经据典，层层递进。不破不立，不破不证。

## 方法层·白话

论证表达是认知管道第5步。输入假设+证据，输出结构化论文章节/论据链。

## 触发条件

- 假设生成 (HYP) 产出可验证假设，需论证后供论文撰写使用
- 观点验证 (VER) 反馈了论证弱点，需补充论据
- 用户要求"写论文/写论证"

## 输入契约

| 字段 | 类型 | 必需 | 说明 |
|------|------|:----:|------|
| `claims` | list[Claim] | ✅ | 待论证的主张列表 |
| `evidence` | list[Evidence] | ✅ | 支持证据 |
| `context` | dict | ❌ | 上下文（论文类型、目标期刊等） |

## 输出契约

| 字段 | 类型 | 说明 |
|------|------|------|
| `argument_chain` | list[dict] | 论据链（claim→evidence→inference→conclusion） |
| `strengths` | list[str] | 论证优势 |
| `gaps` | list[str] | 论证缺口 |
| `counterarguments` | list[dict] | 反方观点 |

## 快速参考

详细内容在 `references/` 目录（Toulmin 模型、Hyland 修辞框架、IMRAD 验证、CARS 模型等）。

1. 加载假设+证据
2. 按 Toulmin 模型构建论据链
3. 识别缺口和反方观点
4. 输出结构化论文章节
5. 保存至 `outputs/{session}/arguments.json`

## 验证清单

- [ ] 每个主张有至少1个直接证据
- [ ] 论据链完整：claim→evidence→inference→conclusion
- [ ] 包含反方观点
- [ ] 引用可追溯至原文

## 边界声明

见 `BOUNDARY.md` — 本原子只做论证构建，不做假设生成、不做观点验证。




# Argument Expression

