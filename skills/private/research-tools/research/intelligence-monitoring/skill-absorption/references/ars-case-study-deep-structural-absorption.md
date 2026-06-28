# ARS Deep Structural Absorption — Case Study

> 吸收日期: 2026-05-13
> 源项目: Imbad0202/academic-research-skills v3.7.0 (6,358⭐)
> 目标系统: Synthos v4.3.1 (pure skill-driven cognitive OS)

## 项目画像

| 维度 | 值 |
|------|-----|
| 启动→当前 | 2026-02-26 → 2026-05-05（~2.5个月） |
| 迭代 | v1.0 → v3.7.0（13个大版本） |
| 许可 | CC BY-NC 4.0（不可商用 — 仅吸收方法论） |
| 生态 | Claude Code 插件 + Codex CLI |
| 架构 | 4 SKILL模块 × 32 Agent = 科研流水线 |

## 评估 — 为什么值得深度吸收

| 维度 | 分 | 理由 |
|------|:--:|------|
| 互补性 | 4.5 | 反谄媚/完整性门控/数据分级 — Synthos 缺这三块 |
| 质量 | 4.5 | 31个CI lint脚本, 71+测试, 13个JSON Schema |
| 活跃度 | 4.0 | 6.3k⭐, 频繁release |
| 集成成本 | 4.0 | SKILL.md 架构完全兼容（与Synthos同范式） |
| 许可 | 3.5 | CC BY-NC 4.0（方法论可吸，代码不可直接复制） |
| **综合** | **4.1** | **🔥 强烈吸收** |

## Phase 0: 并行侦查

派出3个 `delegate_task` 并行探索：

| Agent | 文件量 | 核心发现 |
|-------|--------|---------|
| Pipeline & Gates | 20+ | 10阶段流水线+2个不可跳过完整性门控+7模式AI失败清单 |
| Schemas & Contracts | 17 | 13个Schema + Sprint Contract + Material Passport + 数据访问3层 |
| Agents & Protocols | 17+ | 反谄媚协议(1-5打分)+意图检测+对话健康+5类幻觉分类法 |

**耗时**: 140秒 → 产出完整架构图、机制映射表、优先级矩阵

## Phase 1: 核心注入（本会话完成）

| # | 机制 | 目标 | 文件变更 | 行数 |
|---|------|------|---------|:----:|
| 1 | 反谄媚门控 | viewpoint-verification | SKILL.md + CHANGE_LOG.md | +45 |
| 2 | 5类幻觉分类法 | knowledge-acquisition | CITATION_VERIFICATION.md + SKILL.md + CHANGE_LOG.md | +60 |
| 3 | 数据访问分级 P6 | CONSTITUTION.md + 全部8原子 | CONSTITUTION.md + 8× frontmatter + DATA_ACCESS_LEVELS.md | +40 |
| 4 | 进化引擎增强 | evolution | SKILL.md PROBE检查项 + evolution-state.json吸收记录 | +20 |

**注入模式**（可复用）：
- 反谄媚协议 → 在原子推理流程中插入 Step（带表格+规则+反模式）
- 分类法 → 增强已有 reference 文件（不破坏现有流程）
- 宪法原则 → 新增 P6 条文 + 更新宪法映射表
- 元数据字段 → 在所有原子 frontmatter 中统一声明

## Phase 2 & 3（待执行）

| Phase | 机制 | 优先级 | 依赖 |
|-------|------|--------|------|
| 2 | Material Passport Schema 9 | 🟡 中 | 需要设计跨原子数据合约 |
| 2 | Sprint Contract | 🟡 中 | 需要 task-router 增强 |
| 3 | 协作深度观察 | 🟢 低 | 需要 evolution engine 增强 |
| 3 | 跨模型验证 | 🟢 低 | 模型无关性已具备 |

## 关键教训

1. **并行侦查是效率关键** — 3个子Agent 140秒完成单Agent 30分钟的工作
2. **Phase 1 独立可执行** — 不依赖 Phase 2/3，不影响I/O合约
3. **同架构吸收成本最低** — ARS和Synthos都用SKILL.md，集成无摩擦
4. **"难以验证"陷阱** — ARS v2.7压力测试检出31%引用错误率，证明外部验证的必要性
5. **思维框锁是根本问题** — AI和人类共享同一框架时，双方都看不到盲区

## 参考

完整吸收报告: Synthos/docs/ars_absorption_report.md
ARS项目: https://github.com/Imbad0202/academic-research-skills
