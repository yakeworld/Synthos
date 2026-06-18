# BOUNDARY.md — knowledge-acquisition

> 对应原则：P2（非重叠性证明）

## 边界陈述

本原子的唯一职责：从多个学术数据库检索论文、下载PDF、输出论文元数据列表。不做文本分析、不做关联判断。

## 与其他原子的边界

| vs 原子 | 边界 |
|---------|------|
| knowledge-extraction (2) | 本原子获取论文，原子2理解论文 |
| association-discovery (3) | 本原子收集语料，原子3分析关系 |
| hypothesis-generation (4) | 本原子只检索，不生成假设 |
| argument-expression (5) | 本原子输出论文列表，原子5输出学术文本 |
| viewpoint-verification (6) | 本原子无观点，不参与验证 |

## 数据源边界

本原子仅负责调用API并返回结果。以下操作不属于本原子职责：
- 缓存管理（由客户端 Agent 处理）
- API密钥管理（由环境变量处理）
- 结果去重（由数据消费方处理）
