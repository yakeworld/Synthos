# EVIDENCE_SCHEMA.md — task-router

> 对应原则：P0（路径决策是证据，记录到CallGraph）
> 特殊性：路由器不产生 evidence_chain 数据流。路由决策作为 CallGraph 元数据保存。

## 路由证据生命周期

```
Router.run() → Pipeline.record_routing() → CallGraph → callgraph.json
```

路由器的输出不进入数据流 evidence_chain。
