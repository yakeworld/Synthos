# BOUNDARY.md — knowledge-extraction

> 对应原则：P2（非重叠性证明）

## 边界陈述

本原子的唯一职责：将单篇论文元数据/摘要转化为结构化 KnowledgeItem。不做跨论文比较。

## 与其他原子的边界

| vs 原子 | 边界 |
|---------|------|
| knowledge-acquisition (1) | 原子1获取论文，本原子理解论文 |
| association-discovery (3) | 本原子单论文粒度，原子3跨论文粒度 |
| hypothesis-generation (4) | 本原子描述性，原子4生成性 |
| argument-expression (5) | 本原子输出JSON，原子5输出学术文本 |
| viewpoint-verification (6) | 本原子正向提取，原子6反向验证 |
