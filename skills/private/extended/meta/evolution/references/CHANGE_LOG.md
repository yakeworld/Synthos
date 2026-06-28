# 变更日志

## 2026-05-11: v1.0.0 — 初始版本
- 创建 Evolution Engine SKILL.md
- 6 步自进化循环：LOAD_STATE → PROBE → DIAGNOSE → IMPROVE → VERIFY → RECORD
- 7 原子结构探测 + 3 API 健康检查
- 保守进化原则：仅修复结构问题，不改核心逻辑
- 所有输出可追溯：evolution-state.json + evolution-log.md + 报告

## 2026-05-22: v2.12.0 — L+1 吸收: hermes-agent-self-evolution (NousResearch, ⭐3446)
- 新增 REFLECTIVE_ANALYSIS 阶段到 OPTIMIZE（读取轨迹→理解失败→针对性修复）
- 新增 AUTO_DATASET 阶段到 BENCHMARK（无 golden 时从 SKILL.md 自动生成测试集）
- 新增 Pareto 多维评分到 DIAGNOSE（多目标 Pareto 前沿替代单指标聚焦）
- 步骤从 11 步扩展到 12 步（含 5.5 AUTO_DATASET + 6.5 REFLECTIVE_ANALYSIS）
- 路径 B 增加反射式分析 + Pareto 诊断阶段
- 吸收来源: NousResearch/hermes-agent-self-evolution (MIT, ICLR 2026 Oral)
