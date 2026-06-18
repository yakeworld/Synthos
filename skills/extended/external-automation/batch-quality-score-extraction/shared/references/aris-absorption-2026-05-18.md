# ARIS 吸收报告

## L+0 来源标注

- **项目**: ARIS CLI — Autonomous Research Iteration System
- **URL**: https://github.com/HaiyangDiiing/aris-cli
- **⭐**: 8 (2026-05-18)
- **语言**: Rust + Markdown Skill
- **许可证**: MIT
- **创建**: 2026-05-07 (11天)
- **最后更新**: 2026-05-17
- **灵感来源**: Karpathy's autoresearch
- **核心定位**: 让 AI Agent 通过纪律化流程优化任何可量化目标的自主实验循环系统

## 五层分析

### 第1层 思想 (Philosophy)

| ARIS 原则 | SynthOS 对应 | 对比 |
|:----------|:-------------|:------|
| Constraint = Enabler（通过约束实现自主） | Constitution 宪法约束 | 同频 — 都认同约束是自主的前提 |
| Separate Strategy from Tactics | evolution 的用户确认门 | ARIS 更明确：「人类设方向，Agent 执行」 |
| Metrics Must Be Mechanical | 6维质量+8维认知 | ARIS 只优化单一机械指标 → 更聚焦 |
| Verification Must Be Fast | BENCHMARK 循环 | ARIS 强调验证速度决定迭代频率 |
| Git as Memory and Audit Trail | 文件系统状态 + JSON trace | **ARIS优 — 可审计版本化的进化历史** |
| Honest Limitations | Limitations 章节 | 同频 — 都强调诚实边界 |
| Iteration Cost Shapes Behavior | — | SynthOS 未量化迭代成本 |

**相容性判定**: 高度相容。ARIS 的 7 原则与 SynthOS 的宪法原则无冲突。

### 第2层 规范 (Standard)

| 规范 | ARIS | SynthOS | 吸收? |
|:-----|:-----|:---------|:------|
| 配置格式 | `autoresearch.toml` (单一文件) | 分散的 JSON 文件 | 🟡 参考级 |
| 实验日志 | JSONL + TSV 双模式 | `pipeline_trace.json` | ✅ **P0 吸收** |
| 提交前缀 | `[aris]` 前缀 | 无标准格式 | ✅ 吸收 |
| 8-相循环 | 8个 binary 阶段 | 11-step 状态机 | 🟡 参考级 |
| 状态枚举 | 7种状态 (baseline/kept/discarded/crash/no-op/hook-blocked/metric-error) | PASS/FAIL/GAP | ✅ **P1 吸收** |
| 预检验证 | `aris doctor` (14项) | 无 | ✅ **P1 吸收** |

### 第3层 规律 (Pattern)

| 模式 | ARIS | 吸收到? |
|:-----|:------|:---------|
| **提交→验证→回滚** | git commit BEFORE verify, safe_revert on failure | **evolution SKILL.md** |
| **单次一变更** | One change per experiment, 5-file limit | **evolution CLOSE 策略** |
| **假设先行** | Write hypothesis BEFORE modifying | **HYP 原子** |
| **停滞检测** | 5 discards → stuck, 15 no-improvement → plateau | **evolution 第0步** |
| **奖励作弊检测** | 标记 implausible jumps | **VER 原子** |
| **进度报告** | 每10轮打印小结 | **evolution 输出** |

### 第4层 能力 (Capability)

| 能力 | ARIS | SynthOS | 动作 |
|:-----|:------|:---------|:------|
| Git 版本化进化历史 | ✅ 完整的 git loop | ❌ 文件系统状态 | **P0: 创建 git-loop 协议** |
| 结构化实验日志 | `aris log`, `aris best`, `aris export` | ❌ 仅有 pipeline_trace | P2: 扩展日志 |
| TUI 仪表盘 | `aris watch` (ratatui) | ❌ 无 | P2: 将来 |
| 多 Agent 支持 | Claude Code/Codex/Cursor 等6+ | Hermes 专属 | P2: 将来 |
| 奖励作弊检测 | ✅ | ❌ | **P1: 吸收** |

### 第5层 任务规律 (Task Pattern)

ARIS 的 8-相循环协议极其细致（每相有精确的 bash 命令），可作为 evolution 引擎的参考实现。

## 差距分类与吸收计划

| 优先级 | 吸收项 | 目标技能 | 改动量 | 预期收益 |
|:------:|:-------|:---------|:------:|:---------|
| **🔴 P0** | Git-as-memory | evolution SKILL.md | 新增 git 步骤到 11-step | 可审计回滚 |
| **🔴 P0** | 单指标聚焦 | evolution CLOSE 策略 | 修改循环策略 | 避免重心漂移 |
| **🔴 P0** | 假设先行 | HYP SKILL.md | HYP 前置到进化循环 | 每轮可验证预期 |
| 🟡 P1 | 预检闸门 | evolution SKILL.md 第0步 | 新增 health check | 减少空跑 |
| 🟡 P1 | 停滞检测 | evolution 循环控制 | 新增退出条件 | 避免死循环 |
| 🟡 P1 | 状态枚举标准 | quality-gate | 统一状态名 | 一致性好 |
| 🟡 P1 | 奖励作弊检测 | VER SKILL.md | 新增检测逻辑 | 防自欺 |
| 🟢 P2 | 结构化日志 | evolution references/ | 扩展 pipeline_trace | 更好分析 |

## L+1 适配改造要点

1. **Git-as-memory**: 适配到 evolution 的 11-step 状态机，不是替代，而是嵌入。evolution 第0步增加 git branch 创建，每轮先 commit 再 BENCHMARK
2. **单指标聚焦**: 不直接复制 ARIS 的"一个指标"，而是改为"每轮只提升分数最低的维度"
3. **假设先行**: HYP 原子增加进化前置模式——生成当前维度的预期提升假说

## 当前状态
- L+0: ✅ 已完成
- L+1: ✅ 已完成（7项适配改造：git循环嵌入evolution、单指标聚焦适配、假设先行适配）
- L+2: ✅ 已完成（五层验证通过：思想相容、规范适配、规律吸收到evolution SKILL.md）
- L+3: ⏳ 待独立验证（需跑一轮evolution验证git-as-memory循环工作）
