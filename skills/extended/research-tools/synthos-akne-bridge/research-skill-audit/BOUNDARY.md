# BOUNDARY.md — research-skill-audit

> 对应原则：P2（非重叠性证明）

## 边界陈述

本原子的唯一职责：Audit and enhance research skill coverage. Process for identifying gaps, testing existing skills, and creating/enhancing missing capabilities.。仅执行本职责，不做超出范围的操作。

## 与其他原子的边界

| vs 原子 | 边界 |
|---------|------|
| research-paper-search | 本原子不执行 research-paper-search 的功能 |\n| knowledge-acquisition | 本原子不执行 knowledge-acquisition 的功能 |\n| knowledge-extraction | 本原子不执行 knowledge-extraction 的功能 |\n| association-discovery | 本原子不执行 association-discovery 的功能 |\n| hypothesis-generation | 本原子不执行 hypothesis-generation 的功能 |\n| argument-expression | 本原子不执行 argument-expression 的功能 |\n| viewpoint-verification | 本原子不执行 viewpoint-verification 的功能 |\n
| 通用 | 本原子不替代上层编排逻辑，只执行具体操作 |

## 数据源边界

本原子仅处理输入中明确指定的数据和操作。以下不属于本原子职责：
- 结果持久化（由客户端处理）
- 错误恢复/重试（由上层调用者处理）
- API 密钥管理（由环境变量处理）
- 其他原子特有的操作逻辑
