# BOUNDARY.md — repo-path-sanity

> 对应原则：P2（非重叠性证明）

## 边界陈述

本原子的唯一职责：**Purpose:** Diagnose and fix broken directory relationships when `~/Synthos` and `/media/yakeworld/sda2/Synthos` diverge into independent copies instead of symlink.。仅执行本职责，不做超出范围的操作。

## 与其他原子的边界

| vs 原子 | 边界 |
|---------|------|

| 通用 | 本原子不替代上层编排逻辑，只执行具体操作 |

## 数据源边界

本原子仅处理输入中明确指定的数据和操作。以下不属于本原子职责：
- 结果持久化（由客户端处理）
- 错误恢复/重试（由上层调用者处理）
- API 密钥管理（由环境变量处理）
- 其他原子特有的操作逻辑
