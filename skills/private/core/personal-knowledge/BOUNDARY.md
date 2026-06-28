# BOUNDARY.md — personal-knowledge

> 对应原则：P2（非重叠性证明）

## 边界陈述

本原子的唯一职责：Output Files。仅执行本职责，不做超出范围的操作。

## 与其他原子的边界

| vs 原子 | 边界 |
|---------|------|
| task-router | 本原子不执行路由决策 |
| knowledge-acquisition | 本原子不执行文献检索 |
| knowledge-extraction | 本原子不执行知识提取 |
| association-discovery | 本原子不执行关联发现 |
| hypothesis-generation | 本原子不生成假设 |
| argument-expression | 本原子不构建论证 |
| viewpoint-verification | 本原子不执行验证 |

## 数据源边界

本原子仅处理输入中明确指定的数据和操作。以下不属于本原子职责：
- 结果持久化（由客户端处理）
- 错误恢复/重试（由上层调用者处理）
- API 密钥管理（由环境变量处理）
