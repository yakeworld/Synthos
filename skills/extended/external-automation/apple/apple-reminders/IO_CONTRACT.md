# IO_CONTRACT.md — apple-reminders

> 对应原则：P2（机械原子暴露输入输出规范）

## IO 定义

- **input**: ``task: str, list: str` — 用户请求描述、上下文信息` — 用户请求描述、上下文信息
- **output**: ``reminder_status: dict — 提醒事项`` — 原子执行结果

> 对应原则：P2（机械原子暴露输入输出规范）

## 数据流

本原子的输入由上游编排者提供，输出直接返回给调用者。

## 错误处理

- 输入不合法 → 返回错误状态码 + 原因说明
- 执行失败 → 返回 error_state 节点
- 超时 → 返回 timeout 标记
