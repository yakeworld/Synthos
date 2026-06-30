---

name: knowledge-extraction
description: "从单篇论文中提取结构化知识（实体、关系、主张、证据），输出 KnowledgeItem JSON。可选 pwbench 逆向工程模式。"
author: Synthos
license: MIT
version: 1.0.0
allowed-tools: shell (bash), Read (view), Write (write), task_delegation (agent, inline)
metadata:
  synthos:
    priority: P1
    atom_type: cognitive-atom
    description: "Single-paper structured knowledge extraction"
    signature: "paper_content: str, schema: dict -> structured_knowledge: dict (entities, relations, claims, evidence)"
    related_skills: [knowledge-acquisition, paper-knowledge-extraction]

---

# Knowledge Extraction — 知识提取

> 从单篇论文中提取结构化知识。不做跨论文比较、不做假设生成、不做论证表达。

## 原理层·文言

> 「格物致知。物格则知至。」单篇为基，结构为纲。
> 凡文必拆为实体、关系、主张、证据四域。无源不录，无据不传。

## 方法层·白话

知识提取是认知管道第2步。输入单篇论文全文/摘要，输出结构化 KnowledgeItem JSON。

## 触发条件

- 知识获取 (ACQ) 产出论文，需结构化后供关联发现 (ASC) 使用
- 用户要求"提取论文信息/分析某篇论文"
- 上游 `knowledge-acquisition` 产出待处理论文

## 输入契约

| 字段 | 类型 | 必需 | 说明 |
|------|------|:----:|------|
| `paper_content` | string | ✅ | 论文全文或摘要 |
| `schema` | dict | ❌ | 提取schema（默认: entities/relations/claims/evidence） |
| `mode` | string | ❌ | `standard`（默认）或 `pwbench`（逆向工程模式） |

## 输出契约

| 字段 | 类型 | 说明 |
|------|------|------|
| `entities` | list[dict] | 实体（人物、机构、技术、概念） |
| `relations` | list[dict] | 实体间关系 |
| `claims` | list[dict] | 论文主张 |
| `evidence` | list[dict] | 支持证据 |
| `summary` | str | 结构化摘要 |

## 快速参考

详细内容在 `references/` 目录。核心流程和命令已提炼如下：

1. 加载论文内容
2. 按 schema 提取实体、关系、主张、证据
3. 输出 KnowledgeItem JSON
4. 保存至 `outputs/{paper_dir}/knowledge.json`

## 验证清单

- [ ] 输入已验证：论文内容非空
- [ ] 提取完整性：entities, relations, claims, evidence 均有数据
- [ ] 来源可追溯：每条主张有原文引用
- [ ] 输出已保存：JSON 格式正确可解析

## 边界声明

见 `BOUNDARY.md` — 本原子只做单论文结构化提取，不跨论文比较，不生成假设，不表达论证。




# Knowledge Extraction

