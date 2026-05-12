# Synthos 宪法 (Constitution)

> 版本: v4.3 | 设计原则: 宪法 → 架构 → Schema → 实现

---

## P0: 证据可溯性（Evidence Traceability）

每个输出、决策、声称必须能追溯到一个可验证的来源。

- 文献引用必须有DOI或可访问URL
- 分析结论必须引用来源行
- AI生成的断言必须有引用链
- Schema要求：每个原子输出的每条记录必须包含 `provenance` 字段

---

## P1: 原子可复现性（Atom Reproducibility）

每个认知原子必须独立可执行、可测试、可审计。

- 原子之间不能有运行时耦合（仅通过I/O契约连接）
- 每个原子必须有独立测试用例
- 每个原子的输入/输出必须有形式化Schema
- Schema要求：每个原子声明 `inputs`、`outputs`、`error_states`

---

## P2: 稳定下沉/演化上浮（Stable Sink, Evolution Float）

经过验证的模式下沉为标准技能；未经证明的实验保持 ephemeral。

- 新贡献默认标记为 `unstable`
- 2次成功进化循环后可提升至 `stable`
- 长期稳定（LTS）技能需要人类审批才能修改
- Schema要求：每个技能声明 `stability` 字段

---

## P3: 人机分层（Human-in-the-Loop Layering）

路由器（ROU）负责路由，人类负责决策，原子负责执行。

- 路由器不能替代人类决策
- 关键决策点必须产生人类可读的选项列表
- 外部Agent必须通过AGENT_MANIFEST.yaml自标识
- Schema要求：每条路由记录包含 `decision_point`、`options`、`human_decision`

---

## P4: 假说可证伪性（Hypothesis Falsifiability）

> 新增 v4.3 — 研究空白与科学假设原子

每个生成的科学假设必须包含可检验条件和反证路径。

- 假说必须有明确的可观测预测（observable prediction）
- 假说必须列出至少一个反证条件（falsification condition）
- 空白必须有文献定位（至少2篇矛盾或缺口文献）
- Schema要求：假说记录包含 `prediction`、`falsification`、`literature_gap`

---

## P5: 空白可追溯性（Gap Traceability）

> 新增 v4.3 — 研究空白与科学假设原子

每个识别的研究空白必须精确定位到具体的文献矛盾、方法论缺口、或未回答问题。

- 空白必须有类型分类（矛盾/缺口/未答/过时）
- 空白必须关联到具体来源和行
- 空白必须有重要性评级（P0-P3）
- Schema要求：空白记录包含 `gap_type`、`source_refs`、`priority`

---

## 宪法层级与原子映射

| 原则 | 适用原子 | 审查频率 |
|:-----|:---------|:---------|
| P0 证据可溯性 | ACQ, ASC, GAP, HYP | 每次进化 |
| P1 原子可复现性 | 全部7+2原子 | 每次进化 |
| P2 稳定下沉/演化上浮 | 全部技能 | 每周 |
| P3 人机分层 | ROU（含GAP/HYP路由） | 每次进化 |
| P4 假说可证伪性 | HYP | 每次假说生成 |
| P5 空白可追溯性 | GAP | 每次空白发现 |

---

## 宪法修正程序

1. **提议**：提交PR修改CONSTITUTION.md，标题含`[constitution]`
2. **争议期**：至少24小时讨论期
3. **投票**：Owner（杨晓凯）单票决定
4. **生效**：合并后自动更新版本号

---

> 宪法是Synthos的顶层约束。所有原子、技能、进化循环必须遵守以上六项原则。
