# CHANGE_LOG.md — knowledge-acquisition

> 对应原则：P3（受控变更留痕）

---

## v1.0.0 — 2026-05-10

**变更类型**: 架构重构（Agent-native 化）
**描述**: 
- 原子类型从 `mechanical` 改为 `cognitive`（不再是 Python 机械原子）
- 删除 939 行 Python 代码，由 Agent 直接执行 SKILL.md 指令
- Agent 加载 Hermes 技能（semantic-scholar, pubmed, arxiv, openalex）并使用 terminal+curl 搜索
- 新增 OpenAlex、Crossref 搜索源（旧 Python 代码只覆盖了 S2、PubMed、arXiv）
- allowed-tools 从 `Read Write` 改为 `terminal web delegate_task Read Write`
- synthos_depends_on: 声明依赖的外部 Hermes 技能
- pipeline 不再做 MECHANICAL/COGNITIVE 二元区分，统一走 Agent 执行
**影响的组件**: SKILL.md（全部重写）、core/atom_pipeline.py（移除短路逻辑）、run_pipeline.py（移除原子1特化显示）、core/atoms/atom1_knowledge_acquisition.py（标记为 DEPRECATED）、evolution-state.json（v4.0.0 → v4.1.0）
**审批人**: 杨晓凯
**审批时间**: 2026-05-10
