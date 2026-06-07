---
name: cognitive-atom-architecture
description: 认知原子架构方法论——将操作技能集转化为独立认知原子，DAG依赖关系，输入/输出契约，7+1框架对齐。
metadata:
  synthos:
    version: 4.0.0
    author: Synthos
    signature: 'skill_set: list -> atom_architecture: dict'
---

# Cognitive Atom Architecture

## 核心理念（文言）

| 概念 | 文言 | 义 |
|:-----|:-----|:----|
| 原子化 | **化整为零，各司其职** | 每个原子独立，有明确I/O契约 |
| DAG依赖 | **有向无环，不可逆序** | 原子按DAG顺序执行，不循环 |
| 三语表达 | **三层三语，各安其位** | 原理文言/方法白话/命令英文 |
| 声明式 | **以文为码，不以码为文** | 纯SKILL.md，无Python编排 |

## 原子类型

| 类型 | 职责 | 示例 |
|:-----|:-----|:------|
| ACQ | 知识获取 | research-paper-search |
| EXT | 知识提取 | knowledge-extraction |
| ASC | 关联发现 | association-discovery |
| HYP | 假设生成 | hypothesis-generation |
| ARG | 论证表达 | paper-pipeline |
| VER | 观点验证 | viewpoint-verification |

## DAG顺序

```
ACQ → EXT → ASC → GAP → HYP → ARG → VER
                                       ↑
                                    quality-gate
```

## 7+1框架对齐

| 维度 | 对应原子 |
|:-----|:---------|
| 格物通理 | ACQ + EXT |
| 取象通变 | ASC |
| 天人合一 | 跨原子编排 |
| 经权度信 | quality-gate |
| 墨证求真 | VER |
| 庄周观模 | HYP |
| 熵减生生 | evolution |
| 大道至简 | skill-authoring |

## 参考文件

- `references/atom-creation-template.md` — 新原子创建模板
- `references/dag-topology.md` — DAG拓扑定义
- `references/contract-schema.md` — I/O契约Schema
- `references/cross-system-bridging.md` — 跨系统连接模式（两个独立系统之间的双向桥接，Synthos→AKNE案例）
