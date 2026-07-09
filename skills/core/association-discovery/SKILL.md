---
name: association-discovery
version: 1.0.0
---

## Operational Steps
1. 从上游知识提取获取结构化知识项
   对知识项两两配对，检查7类关系：矛盾/补充/演进/空白/因果/并行/依赖
   对每对关系标注confidence (0-1)
   按confidence排序，输出关联报告
   发现研究空白 → 标记为HYP输入

## Pitfalls
- 不要跳过低confidence关联 — 可能发现创新点
- 不要只找同领域关联 — 跨领域关联更有价值
- 7类关系必须全检查，不可跳过

## Verification
- [ ] 7类关系均检查过
- [ ] 每对关联有confidence评分
- [ ] 关联按confidence排序
- [ ] 研究空白已标记
1. 
2. 
3. 
category: core
signature: "association-discovery -> core: 跨论文识别知识关联（矛盾、补充、演进、空白），构建知识图谱。基于 Boden 创造力理论分类关联类型。"
description: "跨论文识别知识关联（矛盾、补充、演进、空白），构建知识图谱。基于 Boden 创造力理论分类关联类型。"
author: Synthos
license: MIT
version: 1.0.0
allowed-tools: shell (bash), Read (view), Write (write), task_delegation (agent, inline)
metadata:
  synthos:
    priority: P1
    atom_type: cognitive-atom
    description: "Cross-paper association discovery — identify contradictions, complements, evolution, gaps"
    signature: "knowledge_base: dict, query: str -> associations: list[Association] (type, strength, confidence, source)"
    related_skills: ['knowledge-extraction', 'hypothesis-generation']


# Association Discovery — 关联发现

> 跨论文识别知识项之间的关联（矛盾、补充、演进、空白），并报告研究空白。

## 原理层·文言

> 「观其会通，明其异同。」万物互联，非孤立存在。
> 知同知异，知缺知全。不执一端，不蔽于片。

## 方法层·白话

关联发现是认知管道第3步。输入多篇论文的结构化知识，识别跨论文的知识关联类型。

## 触发条件

- 知识提取 (EXT) 产出多篇结构化知识，需关联后供假设生成 (HYP) 使用
- 用户要求"找论文间矛盾/补充关系/研究空白"
- 上游 `knowledge-extraction` 产出待关联知识项

## 输入契约

| 字段 | 类型 | 必需 | 说明 |
|------|------|:----:|------|
| `knowledge_base` | list[KnowledgeItem] | ✅ | 多篇论文的结构化知识 |
| `query` | str | ❌ | 分析焦点（默认: 全量关联） |

## 输出契约

| 字段 | 类型 | 说明 |
|------|------|------|
| `associations` | list[dict] | 关联列表（type: contradiction/complement/evolution/gap） |
| `strength` | float | 关联强度 0-1 |
| `confidence` | float | 置信度 0-1 |
| `gaps` | list[str] | 识别的研究空白 |

## 快速参考

详细内容在 `references/boden-creativity/` 和 `references/` 目录。

1. 加载知识库
2. 逐对比较知识项
3. 分类关联类型（矛盾/补充/演进/空白）
4. 输出关联列表和研究空白
5. 保存至 `outputs/{session}/associations.json`

## 验证清单

- [ ] 所有知识项均已比较
- [ ] 关联类型覆盖4类（矛盾、补充、演进、空白）
- [ ] 每条关联有双向引用（A→B, B→A）
- [ ] 研究空白有具体定位

## 边界声明

见 `BOUNDARY.md` — 本原子只做跨论文关联发现，不做单论文提取、不做假设生成、不做观点验证。

# Association Discovery
