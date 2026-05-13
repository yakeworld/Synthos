---
name: evolution
description: Synthos evolution engine v2.3. Agent-native self-evolution cycle — structural probes + functional benchmarks + active external absorption + lesson learning + golden validation + self-expanding keyword discovery. Runs autonomously via cron. Atoms stable unless user approves changes.
metadata:
  synthos_atom_type: "meta-evolution"
  synthos_version: "2.3.0"
  synthos_skill_md_hash: "dd7136ad55d0846c700ccae0dec27eb5fe4edacfdf1834f089f0c4972626a52a"
  synthos_model_tested_on: "2026-05-11T00:00:00Z"
  synthos_io_contract_ref: "references/IO_CONTRACT.md"
  synthos_benchmarks_ref: "references/BENCHMARKS.md"
  synthos_absorption_ref: "references/ABSORPTION.md"
  synthos_skill_tree_ref: "references/SKILL_TREE.md"
  synthos_lessons_ref: "references/LESSONS.md"
  synthos_change_log_ref: "references/CHANGE_LOG.md"
  synthos_asserted_compliance: "P0,P2,P3"
  synthos_depends_on: "task-router, knowledge-acquisition, knowledge-extraction, association-discovery, hypothesis-generation, argument-expression, viewpoint-verification"
  synthos_author: "Synthos Evolution Engine v2.3"
  synthos_data_access_level: "redacted"
allowed-tools: terminal skill_view Read Write patch cronjob web_search delegate_task
---

# Synthos 进化引擎 v2.3 — 自进化、自测评、自吸收、自学习

## 概述

v2.3 在 v2.2（Golden验证+Lesson学习）基础上重构 EXTERNAL 步骤为**主动吸收引擎**：
- 每轮执行吸收扫描（不再等7轮）
- 项目追踪数据库 + 自扩展关键词
- 从PRORE/DIAGNOSE结果自动发现新搜索方向

```
v2.0: 结构探测 + 基准测试 + 外部吸收（每7轮）
v2.1: + Lesson学习
v2.2: + Golden验证 + evolution-latest.json
v2.3: + 主动吸收引擎 + 自扩展关键词 + Progressive Disclosure
```

完整循环（9步）：

```
[1] LOAD_STATE    → 读取当前状态（三级渐进式加载）
[2] LESSONS       → 加载 lessons.jsonl，注入相关教训
[3] PROBE         → 结构健康检查（7原子全量）
[4] BENCHMARK     → 功能测试（2-3原子轮转）+ Golden验证
[5] EXTERNAL      → 主动吸收引擎（每轮执行）
[6] DIAGNOSE      → 综合评分 + 缺陷诊断
[7] IMPROVE       → 修复结构 + 生成吸收提议
[8] VERIFY        → 验证修复效果
[9] RECORD        → 更新状态 + 日志 + 教训 + evolution-latest.json
```

**核心原则**：
- 6原子+1路由器是核心层——绝对稳定
- 技能树是扩展层——可吸收新技能
- Task完成验证是关键——结构健康 ≠ 功能正常
- 零Python——所有步骤 Agent 自然语言推理执行
- **吸收由评估驱动**——每个吸收决策必须基于评估框架的缺口分析

## 工作目录

```
Synthos 项目根: /media/yakeworld/sda2/Synthos
状态文件:       evolution-state.json
日志文件:       evolution-log.md
报告目录:       outputs/evolution/
吸收追踪库:     outputs/evolution/absorption-tracked.json
评估基线:       outputs/evaluation/baseline_v1.json
参考文献:       skills/evolution/references/
  BENCHMARKS.md     ← 基准测试场景定义
  ABSORPTION.md     ← 外部技能吸收流程
  SKILL_TREE.md     ← 技能树增长策略
  LESSONS.md        ← 教训学习机制
```

---

## 执行流程

### 第一步：LOAD_STATE — 加载当前状态（Progressive Disclosure）

采用三级上下文加载模式（吸收自 KILO-KIT Progressive Disclosure）：

| 级别 | 加载内容 | 时机 |
|------|---------|------|
| L1 元数据 | evolution-state.json（last_run, evolution_count, 简略评分） | 始终加载 |
| L2 详细 | evolution-log.md 最近20行 + lessons.jsonl 最近20条 | 条件加载 |
| L3 按需 | absorption-tracked.json（项目库） | 仅EXTERNAL步骤 |

**输出**：
- `prev_scores` = 各原子信任度
- `prev_benchmark` = 上次基准分
- `current_cycle` = cycle + 1

**失败处理**：state.json 不可读 → 跳过对比，从 L1 开始重建。

---

### 第二步：LESSONS — 加载历史教训

从 `outputs/evolution/lessons.jsonl` 加载历史教训，过滤出与本次BENCHMARK要测试的原子相关的条目（timestamp在30天内）。

---

### 第三步：PROBE — 结构探测

用 `terminal(cat path)` 检查7原子的结构健康：
| 检查项 | 权重 | 方法 |
|--------|------|------|
| 文件存在 | 0.25 | cat 返回非空 |
| name匹配目录 | 0.10 | 正则匹配 |
| desc ≥80字符 | 0.10 | 行长度 |
| allowed-tools存在 | 0.10 | "allowed-tools:" in text |
| IO_CONTRACT.md | 0.10 | 有内容 |
| EVIDENCE_SCHEMA.md | 0.05 | 有内容 |
| BOUNDARY.md | 0.05 | 有内容 |
| CHANGE_LOG.md | 0.05 | 有内容 |
| **synthos_data_access_level** | **0.15** | **json中"synthos_data_access_level"存在且值为"raw"/"redacted"/"verified_only"** |
| **反谄媚协议（VER原子专属）** | **0.05** | **viewpoint-verification/SKILL.md含"Concession Threshold Protocol"或"对反驳打分 1-5"** |

评分公式详见 `references/QUALITY_CRITERIA.md`。

---

### 第四步：BENCHMARK — 功能测试 + Golden验证

#### 轮转策略
| 轮次 | 测试原子 |
|------|---------|
| 奇数轮 | knowledge-acquisition + knowledge-extraction + association-discovery |
| 偶数轮 | hypothesis-generation + argument-expression + viewpoint-verification |
| 每轮都测 | task-router |

#### 测试方法
1. 加载 `references/BENCHMARKS.md` 获取测试场景
2. 选第1个测试场景
3. 按routine执行
4. **Golden验证子步骤**：加载 `golden/cases/case_001.json` 和 `golden/expected/case_001.json`，验证JSON有效且含GOLDEN_SET.md定义的所有必填字段
5. 评分：pass(1.0) / partial(0.5) / fail(0.0)

#### 历史教训注入
回顾LESSONS步骤加载的教训。如果某个原子反复失败（同一atom ≥ 2次），对该原子执行更全面测试。

---

### 第四步：EXTERNAL — 主动吸收引擎（v2.3 重构）

每轮执行，不再等7轮。

```
[1] LOAD_DB     → 读取 absorption-tracked.json（项目DB + 关键词库）
[2] FOLLOW_UP   → 对状态=tracking/evaluating的项目检查更新
[3] SCAN_NEW    → 用关键词库搜索新项目（每轮选2-3组关键词，轮转）
[4] EVALUATE    → 按5维标准评分新项目 (0-5)
[5] EXPAND      → 从新项目描述中提取新关键词 → 追加到关键词库
[6] SELF_INSPECT→ 从本轮DIAGNOSE结果发现新搜索方向
[7] UPDATE_DB   → 写入 absorption-tracked.json
```

详见 `references/ABSORPTION.md`。

**关键词轮转**（8类别）：

| 类别 | 示例 | 节奏 |
|------|------|------|
| research_agent | AI research assistant | 每2轮 |
| architecture | cognitive skill framework | 每3轮 |
| literature | academic literature automation | 每3轮 |
| knowledge | knowledge graph extraction | 每3轮 |
| reasoning | hypothesis generation AI | 每4轮 |
| pipeline | research paper agent LLM pipeline | 每4轮 |
| evaluation | benchmark research agent | 每4轮 |
| self_discovered | 动态生成的词 | 每2轮 |

---

### 第五步：DIAGNOSE — 综合诊断

#### 5.1 结构分对比
- current < 0.5 → CRITICAL
- current < prev - 0.1 → DEGRADED

#### 5.2 基准分对比
- benchmark < 0.5 → FUNCTIONAL_DEGRADED
- 同一测试连续3轮不通过 → PERSISTENT_FAILURE

#### 5.3 技能树健康
读取 skill_tree 字段，评估 core_atoms + extended_skills + benchmark_pass_rate。

#### 5.4 综合评分公式

```
综合分 = 结构平均分 × 0.30 + 基准分 × 0.40 + 技能树覆盖率 × 0.20 + 吸收潜力 × 0.10
```

| 等级 | 范围 | 行为 |
|------|------|------|
| EXCELLENT | ≥0.85 | 仅记录 |
| GOOD | 0.70-0.84 | 小幅修复 |
| FAIR | 0.50-0.69 | 生成改进建议 |
| POOR | <0.50 | 请用户介入 |

#### 5.5 评估框架对照（v2.3 新增）

每次DIAGNOSE后，对照 `docs/synthos-evaluation-framework.md` 的6维评估标准，记录当前基线：
- 检查最近一次运行输出（outputs/runs/ 最新目录）
- 对照D1-D6 checklist评分
- 记录哪个维度 < 70 作为吸收驱动信号

---

### 第六步：IMPROVE — 应用改进

自动修复（无需审批）：缺失reference文件、版本号过期、损坏的frontmatter。

吸收提议（需用户审批）：当EXTERNAL找到高价值候选（综合分 ≥ 4.0）。

原子变更（需用户明确批准）：绝对禁止自动修改任何原子SKILL.md的核心逻辑。

---

### 第七步：VERIFY — 验证

对已patch的原子：确认可加载，重新计算结构分。
如果无任何修复 → 跳过此步。

---

### 第八步：RECORD — 更新状态和日志

#### 8.1 更新 evolution-state.json
使用 `patch()` 更新 `last_run`, `evolution_count`, `quality_metrics`, `evolution`, `skill_tree`。

#### 8.2 追加 evolution-log.md
记录本轮结果。

#### 8.3 提取教训
失败/警告提取为教训，追加到 lessons.jsonl。

#### 8.4 生成进化报告
写入 `outputs/evolution/report_{cycle}.json`。

#### 8.5 生成快速摘要
写入 `outputs/evolution/evolution-latest.json`。

#### 8.6 更新吸收追踪库
如果本轮有吸收操作，更新 `absorption-tracked.json` 的项目状态。

---

## 已知陷阱

1. 功能测试不执行完整链路
2. 外部搜索关键词可能过期——自扩展机制可自动发现新关键词
3. 吸收提议不自动执行——Agent只提议，用户批准才动手
4. 基准测试失败的三种可能：API临时故障 / 原子逻辑过时 / 外部依赖变化
5. SKILL.md被意外覆盖——每次Patch前备份到 `backups/` 目录
6. 用 terminal cat 避免 read_file 去重

---

## 变更日志
2026-05-11: v2.3.0 — 主动吸收引擎重构 + 评估框架集成 + Progressive Disclosure。
  新增: EXTERNAL 从"每7轮"改为每轮执行
  新增: absorption-tracked.json 项目追踪数据库（20项目, 1已吸收）
  新增: 关键词自我扩展 + 自检关键词生成
  新增: 三级上下文加载（Progressive Disclosure，吸收自 KILO-KIT）
  新增: DIAGNOSE 5.5 评估框架对照（对接 synthos-evaluation-framework.md）
  新增: RECORD 8.6 吸收追踪库更新
  修复: SKILL.md 意外覆盖保护——每次patch前备份
2026-05-11: v2.2.0 — 新增Golden金标准验证 + evolution-latest.json快速摘要。
2026-05-11: v2.1.0 — 新增Lesson学习机制。
2026-05-11: v2.0.0 — 升级自进化引擎：BENCHMARK+EXTERNAL+技能树+综合评分。
2026-05-11: v1.0.0 — 初始版本，6步循环。
