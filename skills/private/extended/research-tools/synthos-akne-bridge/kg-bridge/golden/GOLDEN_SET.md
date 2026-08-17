# GOLDEN_SET.md — kg-bridge

> 对应原则：P1（原子可复现性）/ P2（机械原子暴露输入输出规范）
> golden_set_origin: self_defined
>
> golden 三件套 = 本文件 + `cases/` + `expected/`。所有改进必须通过 golden 测试。

## 设计依据

本技能的输入是「知识图谱查询请求」，输出是「图谱查询结果 + 图谱连接健康报告」（见 SKILL.md IO_CONTRACT）。金标准目标：验证实体解析五级降级（精确→子串→分词→反向→模糊）、查询限量（≤20）+ BFS 分层（先 depth=1）、以及 API 正确调用位置（`resolve_entity` 在 `QueryEngine` 而非 `KnowledgeGraph`，`find_related` 返回 3 元组）。

## 金标准覆盖范围

| 维度 | 覆盖 | 说明 |
|------|:--:|------|
| 查询模式 | quick / bridge | 正常路径（KGB-001）+ 错误路径（KGB-006） |
| 实体解析 | 5 级降级 | 精确命中 / AttributeError 回退 |
| 输出约束 | ≤20 条、BFS 分层 | depth=1 优先 |
| 错误处理 | 2 种 | API 位置错误 + 解包元数错误 |

## 测试用例 (cases/)

### case_001: 正常路径 — 已知实体 quick 查询（"BPPV"）
- **输入**: 实体 "BPPV"，模式 quick（`akne-query.sh graph`，<1s），depth=1
- **期望**: 实体经五级解析（精确命中，level=0）后返回恰好 5 个 depth=1 邻居；结果 ≤20 条、结构化可解析；bridge 审计 0 孤儿、全连接（Step 5 场景 1 + 场景 4）

### case_002: 错误路径 — resolve_entity 调用位置错误（KGB-006）
- **输入**: 在 `KnowledgeGraph` 上调用 `kg.resolve_entity(q)`
- **期望**: 报 `AttributeError: 'KnowledgeGraph' object has no attribute 'resolve_entity'`，恢复建议为改经 `QueryEngine(graph_index=kg).resolve_entity(q)` 调用；同时 `find_related` 按 3 元组 `(neighbor, relation_chain, metadata)` 解包（勿 4 元解包致 ValueError）

## 期望输出 (expected/)

每个 case 的期望输出存放于 `golden/expected/case_XXX.json`：
- case_001: `resolved_entity`（精确命中）+ 5 个 depth=1 邻居 + bridge 审计（0 孤儿）
- case_002: `error`（AttributeError）+ `recovery`（QueryEngine 正确调用路径 + 3 元组解包说明）

### 通过标准（判定规则）
1. `resolved_entity.method` 精确匹配期望解析级别
2. `neighbors` 长度精确匹配期望值，且每项含 `relation` + `depth` 字段
3. `results_count` ≤ 20 且 `bridge.orphans` = 0
4. 错误路径 case：`error.type` 精确匹配，`recovery` 含正确 API 调用路径

## pass_threshold: 1.00

机械原子（atom_type=mechanical），输出为确定性结构化 JSON，无语义变异空间 → 全部 case 必须通过。

## 更新历史

| 版本 | 日期 | 变更 | 审批 |
|------|------|------|------|
| 0.1.0 | 2026-06-13 | 初始自设金标准，2 个 case（正常 + 错误） | Synthos Agent |
