# PaperDebugger Absorption Record

> 吸收日期: 2026-06-05
> 源项目: PaperDebugger/paperdebugger (1,479⭐, AGPL-3.0 — 仅方法论，忽略许可)
> 目标系统: Synthos v2.19.0
> 吸收分数: 3.3/5.0 (方法论评估)
> 吸收状态: absorbed_methodology
> 用户校正: "吸收思想和理论，技巧，消化吸收，不需要考虑许可"

## 项目画像

| 维度 | 值 |
|------|-----|
| 范式 | Chrome 扩展 + Overleaf 插件 + MCP 编排 |
| 核心 | XtraMCP — 自定义 MCP-based 研究→评审→修订流水线 |
| 目标 | AI 辅助学术写作调试与改进 |

## 五层提取

### L+0 文言（底层哲学）

| PaperDebugger | Synthos 对应 | 吸收判定 |
|:-------------|:-------------|:---------|
| Research → Critique → Revision | 格物→通理→立言 | **吸收** — 完美对应 Synthos ACQ→EXT→ASC→HYP→ARG 管线 |
| Conference-style structured review | 双质检 | **吸收** — 填补 quality-gate 的 conference-reviewer 视角 |
| Citation verification & traceability | P0 证据可溯性 | **吸收** — 强化 P0 的可操作性 |

### L+1 改制（规范层）—— 核心吸收

| # | PaperDebugger 机制 | Synthos 缺口 | 吸收目标 |
|:-:|:-------------------|:-------------|:---------|
| 1 | conference-style structured review | quality-gate 无会议审稿人视角 | 注入 quality-gate "Reviewer" 子门 |
| 2 | section-level review (static + semantic) | 无分段评审 | 注入 quality-gate 分段审核机制 |
| 3 | verify_citations (grounded, valid, traceable) | P0 有原则无工具化 | 注入 P0 可验证引用链机制 |
| 4 | generate_citations (arxiv/DOI/URL → BibTeX) | 引用生成需手动 | 注入引用自动生成工具 |

### L+2 验质（质量层）

| 机制 | 吸收判定 | 理由 |
|:-----|:---------|:------|
| Research→Critique→Revision 流水线 | ✅ 吸收 | 填补 paper-pipeline 的完整闭环 |
| Conference-style structured review | ✅ 吸收 | 注入 quality-gate Reviewer 子门 |
| Section-level review | ✅ 吸收 | 分段审核填补质量门空白 |
| Citation verification | ✅ 吸收 | 强化 P0 可操作化 |

### L+3 证用（应用层）

**注入后验证**:
- [x] quality-gate: "Reviewer" 子门可独立触发
- [x] P0: verify_citations 可验证引用链
- [x] paper-pipeline: Research→Critique→Revision 闭环注入

## 关键教训

1. 格物通理立言 — PaperDebugger 的三阶段流水线完美对应 Synthos 的 ACQ→EXT→ARG 管线
2. 分段审核，逐段精进 — section-level review 比全局 review 更有效
3. 引用可溯，证据可验 — verify_citations 是 P0 证据可溯性的工具化实现

## 文言提炼

> 格物通理，立言成章。分段审核，逐段精进。引用可溯，证据可验。