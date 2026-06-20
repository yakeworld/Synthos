# IO_CONTRACT.md — proactive-discovery

> 对应原则：P2（机械原子暴露输入输出规范）

## IO 定义

本原子的输入输出契约已定义在 SKILL.md 的 IO_CONTRACT 段落中。
- 详见：SKILL.md 中的 IO_CONTRACT 部分
- 输入：由上游编排者（task-router）提供
- 输出：原子执行结果直接返回调用者

## 数据流

本原子执行后，输出结果直接返回给调用者或写入 outputs/ 目录。

## 错误处理

- 输入不合法 → 返回错误状态码
- 执行失败 → 返回 error_state 节点
