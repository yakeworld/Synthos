# CHANGE_LOG.md — task-router

> 对应原则：P3（受控变更留痕）

---

## v1.2.0 — 2026-05-18

**变更类型**: 架构增强
**描述**: 吸收 AI-Research-SKILLs (Orchestra) Autoresearch 双循环编排协议。新增 research 模式（两循环）+ exploratory 模式（仅内循环）。新增循环状态追踪（迭代计数器、累积结果、退出条件）。更新 pipeline_trace.json schema 支持 loop_state。更新 BOUNDARY 声明循环编排边界。
**影响的组件**: task-router（SKILL.md 执行流程 + pipeline_trace.json schema + IO_CONTRACT + BOUNDARY）
**吸收来源**: Orchestra Research / AI-Research-SKILLs — Autoresearch two-loop architecture (8,492⭐, MIT)
**审批人**: Hermes Agent (autonomous — 自主执行阈值≥80%)
**审批时间**: 2026-05-18
**金标准通过率**: 待下次 BENCHMARK 验证

## v0.1.0 — 2026-05-10

**变更类型**: 初始版本
**描述**: 创建 task-router 认知原子。定义 SKILL.md、IO_CONTRACT、EVIDENCE_SCHEMA、BOUNDARY、GOLDEN_SET。路由规则为关键词匹配，四种复杂度（simple/medium/complex/full）+ 默认 medium。
**影响的组件**: task-router（全部）
**审批人**: Synthos Agent
**审批时间**: 2026-05-10
**金标准通过率**: 待首次测试（pass_threshold=1.0）
