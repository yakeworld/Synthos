# GOLDEN SET — task-router

> 本技能通过 pipeline_trace.json 验证，无传统 golden input/output 文件。

## 验证方式

1. 查询输入 → 路由决策 → pipeline_trace.json 输出
2. 模式正确性: standard/exploratory/research/parallel 分类正确
3. 原子链顺序: ACQ→EXT→ASC→HYP→ARG→VER 依赖关系正确
4. 执行日志: 每步独立JSON记录

## Golden 测试数据

无独立 golden 输入文件；测试依赖实际用户查询的 pipeline_trace.json 输出。
