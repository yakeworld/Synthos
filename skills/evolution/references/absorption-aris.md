# ARIS Absorption Record — 深度吸收

> 吸收日期: 2026-06-03
> 源项目: wanshuiyin/Auto-claude-code-research-in-sleep (9,300⭐)
> 目标系统: Synthos v2.18.0
> 范式匹配: 100% — 纯 SKILL.md 驱动，零框架依赖

## 项目画像

| 维度 | 值 |
|------|-----|
| 范式 | 纯 SKILL.md + 独立 CLI (Rust) |
| 技能数 | 74+ 用户技能 + 54+ helper |
| 工作流 | 13 个命名流程 (W1-W6 + Wiki + Assurance + Oracle) |
| 版本 | v0.4.15 (2026-05-29) — 11 次打磨发布 |
| 许可 | 未明确标注（方法论可吸，参考级） |

## 五层提取

### L+0 文言（底层哲学）

| ARIS | Synthos 对应 | 吸收判定 |
|:-----|:-------------|:---------|
| "research while you sleep" | "自进化不息" | 同方向，略 |
| cross-model adversarial review | L0.5 + Layer B 双质检 | **补充** |
| "no infrastructure, zero lock-in" | "纯 skill 驱动，零 Python" | 同哲学，略 |

### L+1 改制（规范层）—— 核心吸收

| # | ARIS 机制 | Synthos 缺口 | 吸收目标 |
|:-:|:----------|:-------------|:---------|
| 1 | **Cross-model adversarial review** | L0.5/Layer B 是串行非对抗 | quality-gate 增加"对抗评审"子门 |
| 2 | **Research Wiki** (持久知识库) | knowledge-extraction 无持久存储 | 增加 research-wiki 概念和持久化流程 |
| 3 | **13 named workflows** (W1-W6) | paper-pipeline 有 P0-P6 但无 W 系列 | 作为 paper-pipeline 的备用分类 |
| 4 | **Meta-optimize self-evolution** | evolution 引擎有类似但有缺口 | 补 skill bundle 模式和 drift-CI |
| 5 | **Skill helper resolver** (4层) | allowed-tools 声明了但无 resolver | 增加 helper 解析协议 |
| 6 | **ARIS-Monitor** | 无会话监控 | 知识记录，非立即吸收 |

### L+2 验质（质量层）

| 机制 | 吸收判定 | 理由 |
|:-----|:---------|:------|
| 跨模型对抗评审 | ✅ **吸收** | 填补 L0.5→Layer B 的"盲区"缺口 |
| Research Wiki | ✅ **吸收** | 填补 EXT 无持久存储 |
| W1-W6 工作流 | 🟡 **参考** | paper-pipeline P0-P6 已覆盖 |
| Meta-optimize | ✅ **部分吸收** | skill bundle + drift-CI 模式 |
| Skill resolver | 🟡 **参考** | Synthos 架构不同 |

### L+3 证用（应用层）

**注入后验证**:
- [ ] quality-gate: "对抗评审"子门 可独立触发
- [ ] knowledge-extraction: 有 research-wiki 持久化步骤
- [ ] evolution: 有 skill bundle 版本对齐检查

## 关键教训

1. **对抗评审 > 串行评审** — 同一模型的两次评审落入 local minima，不同模型的碰撞才能发现盲区
2. **持久知识库是必备** — 没有 Research Wiki，每次会话从零开始
3. **技能 resolver 4 层** — Synthos 的 allowed-tools 声明可升级为 resolver 协议
4. **13 个 W 流程比 7 个 P 阶段更精细** — 但 P0-P6 更符合 Synthos 的流水线式编排
