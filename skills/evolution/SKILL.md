---
name: evolution
description: ⚡ P0 自进化引擎。Synthos evolution engine v2.20 — 四态决策+硬收敛+GEPA反射分析+自动基准+Pareto优化+外部吸收+教训学习+黄金验证+自扩关键词+漂移检测+渐进披露+Git即记忆。Hooks注入+置信度评分+并行Agent审计+会话上下文注入+Prompt Snippets。
license: MIT
metadata:
  synthos:
    version: 2.20.0
    priority: P0
    atom_type: meta-evolution
    author: Synthos
    signature: 'cycle: int -> evolution_report: dict'
    related_skills:
    - project-experience-distillation
    - quality-gate
    - skill-absorption
    - cognitive-atom-architecture
---

# Evolution Engine — 自进化引擎

## IO_CONTRACT

- **input**: `cycle: int` — 当前进化周期编号
- **input**: `prev_state: dict` — 上一周期 evolution-state.json 快照
- **input**: `lessons: dict` — 历史教训（近30天）
- **input**: `skill_inventory: list[Skill]` — 全部 110 技能清单
- **output**: `evolution_report: dict` — 完整进化报告（含 score, dimensions, improvements, lessons）
- **output**: `new_state: evolution-state.json` — 更新后的状态文件
- **output**: `log_entry: evolution-log.md` — 追加日志条目

## 外部吸收记录 (v2.20 新增)

> 吸收自 anthropics/claude-code (130,221⭐, 2026-06-05, 分数 4.5/5.0)

### Claude Code 关键方法论注入

| Claude Code 机制 | Synthos 注入点 | 效果 |
|:-----------------|:---------------|:-----|
| Hooks 系统 (PreToolUse, SessionStart, Stop) | evolution + quality-gate | 结构约束 > prompt 约束 |
| 自信度评分 (0-100, 阈值 80 过滤假阳性) | quality-gate | 大幅减少误报 |
| 并行 Agent 独立审计 (4 agents) | task-router | 并行编排增强 |
| 会话初始化注入上下文 (SessionStart) | evolution | 渐进披露机制 |
| 对话分析 (自动识别需防错行为) | evolution (增强 Nudge) | 行为监测增强 |
| Prompt Snippets (工具过度触发/过度工程化) | quality-gate | Prompt 优化 |

### 验证结论

**Claude Code 130K⭐ 验证了 Synthos SKILL.md 范式：相同哲学，不同实现。**

### 吸收记录文件

- `references/absorption-claude-code-skills-2026-06-05.md` — 完整吸收记录 (5 层提取 + 关键教训)

## 吸收方法论清单

> 所有吸收遵循 Synthos 吸收标准 (P7: 拒绝搬运，只取方法论)。每次吸收完成:
> 1. 读文档/代码 → 理解核心方法论
> 2. 五维评分 → 决定是否吸收
> 3. 方法论提取 → 剥离具体实现，提取可移植原理
> 4. 文言提炼 → 压缩为 3-5 条文言格言
> 5. 注入融合 → 进入 Synthos 现有技能协议
> 6. 记录 → evolution-log 记录吸收过程

### 历史吸收 (按时间排序)

| 项目 | 分数 | 状态 | 注入点 | 日期 |
|:-----|:----:|:-----|:-------|:-----|
| autocontext (3.9) | absorbed | improvement-loop + knowledge-inheritance + trace-continuity | evolution protocol | 2026-06-05 |
| PaperDebugger (3.3) | absorbed_methodology | Research→Critique→Revision + conference-style review | quality-gate + P0 + paper-pipeline | 2026-06-05 |
| 724-office (3.8) | absorbed_methodology | Nudge Registry + Trigger Functions + Auto-Inject Hints | evolution + quality-gate | 2026-06-05 |
| Claude Code (4.5) | absorbed_methodology | Hooks + Confidence Scoring + Parallel Agents + Session Start Context | evolution + quality-gate + task-router | 2026-06-05 |

## 核心流程

```
DIAGNOSE → 结构探查 + 功能基准 + Pareto多维优化
  ↓
OPTIMIZE → GEPA反射式分析 + 自动数据集
  ↓
VERIFY → 黄金验证 + 收敛检查
  ↓
CRYSTALLIZE → 技能结晶 + 教训学习
  ↓
BENCHMARK → 更新基准 + 自扩关键词
  ↓
SELF_REFLECT → 漂移检测 + 宪法集成
  ↓
→ 下一周期
```

## 四态决策

| 状态 | 触发条件 | 执行 |
|:-----|:---------|:-----|
| OPTIMIZE | 基线+改进方向清晰 | GEPA分析→技能建议 |
| DIAGNOSE | 指标未达标 | Pareto扫描→薄弱维度定位 |
| CRYSTALLIZE | 技能结晶点 | 事后分析→SKILL.md |
| EXPLORE | 方向不明确 | 自扩关键词→新方向 |

## 硬收敛护栏

- `EDIT_BUDGET`: 每次最多修改3个文件
- `rejected_buffer`: 被驳回的技能建议存入buffer，同方向不再提
- 连续3轮无进展 → 降级至探索模式
- 相同目标连续2次 → 自动切换到其他维度

## 查询命令

```bash
# 状态查询
cat evolution-state.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'Cycles: {d[\"evolution_count\"]}, Score: {d[\"composite_score\"]}')"

# 最新日志
tail -50 evolution-log.md

# 基准测试
cat BENCHMARKS.md | grep -E "Pass|Fail|Score"
```

## 输出

- `evolution-state.json` — 状态持久化
- `evolution-log.md` — 操作日志
- `BENCHMARKS.md` — 自动数据集基准
- `skill_registry.json` — 技能注册表更新

## v2.19 注入 (autocontext absorption)

### improvement-loop auto-crystallize
CRYSTALLIZE 步骤新增自动检测：同一任务模式成功执行 ≥3 次 → 输出 pending_review SKILL.md 草稿。
文言：去芜存菁，留真去伪。

### knowledge-inheritance contract
evolution-state.json 新增 `inherited_knowledge` 字段，记录跨轮知识传递。
文言：前鉴不丢，后事之师。

### trace-continuity markers
evolution-log.md 新增 `kept` / `discarded` 标记，区分成功/失败迭代。
文言：迭代有约，出必有痕。

详见: references/evolution_protocol_v2.19.md (11步完整流程) 和 references/absorption-autocontext-2026-06-05.md

## 自动持续迭代协议 (v2.20)

> 用户指令: "自动持续迭代，判断用户回答，超过阈值自动执行"
> 条件: score≥0.85 + status=healthy + 无rejected buffer + 连续健康<20轮

当上述条件全部满足时，自动进入下一进化周期，无需人工干预。
每次自动迭代记录到 evolution-log.md，追加 lesson 到 lessons.jsonl。

### 阈值矩阵

| 场景 | 行为 |
|:-----|:-----|
| score≥0.85 + healthy + 无rejected + 连续<20 | ⚡ 自动继续下一周期 |
| score<0.85 OR degraded OR rejected>0 OR 连续≥20 | 🔴 停止，人工审查 |

## 参考文件

- `references/evolution-cycle-detail.md` — 完整周期流程Deep Dive
- `references/evolution_protocol.md` — 11步执行协议 (v2.17)
- `references/evolution_protocol_v2.19.md` — 11步执行协议 (v2.19完整注入)
- `references/absorption-standard.md` — 吸收标准体系（五维比较+质量门）
- `references/absorption-autocontext-2026-06-05.md` — autocontext方法论吸收记录
- `references/absorption-paperdebugger-2026-06-05.md` — PaperDebugger方法论吸收记录
- `references/absorption-724-office-2026-06-05.md` — 724-office Nudge System吸收记录
- `references/auto-continuation-protocol.md` — 自动持续迭代协议（阈值+条件）

### Nudge 系统注入 (724-office absorption)

> 吸收自: wangziqi06/724-office (MIT)
> 文言: 用结构使错误不可能 | 检测有工具不用，自动注入提示继续

## 已知陷阱 · 多Agent进化

> **陷阱：多 Agent 运行进化循环时，state.json 必须每周期后更新。**
>
> Cycle 65 发现：git 已有 cycle-64 commit，但 state.json 仍显示 cycle 63。
> 状态滞后导致后续 cycle 的 PROBE 和 DIAGNOSE 基于过时数据，产生错误评分。
>
> **修复规则**: LOAD_STATE 步骤必须检查 `git log --oneline | grep "evolution" | head -1`，
> 若 state.json 的 cycle 数落后于 git 中的最大 evolution commit，先同步再执行后续步骤。
>
> 文言: 心随境转，先对齐后行动

## 参考文件

- `references/multi-agent-state-sync.md` — 多 Agent 进化状态同步完整记录

### Benchmark 计算陷阱

> **陷阱：benchmark 分数不应基于 state.json 的旧值，必须每次重新计算。**
>
> Cycle 67 发现：state.json 的 benchmark=0.95，但实际重新计算为 0.77。
> 差值来源：55 技能缺少 signature（实际 50%），89 缺少 IO_CONTRACT（80.9%），
> 26 个 untracked reference 文件影响 git_clean 分数。
>
> **修复规则**: BENCHMARK 步骤必须从零计算所有子分数（YAML、version、signature、
> IO_CONTRACT、git_tracked、encoding、git_clean），不可信任 state.json 的历史值。
> 每次改进后必须 VERIFY 时重算基准，不可沿用旧分。
>
> 文言: 数必重算，不可袭旧

### Probe 原子路径陷阱

> **陷阱：research-ideation 不在 `skills/research-ideation/`，而在 `skills/research/research-ideation/SKILL.md`。**
>
> Cycle 68 发现：7个核心原子中，6个位于 `skills/<atom>/SKILL.md`，但 research-ideation 是嵌套在 research/ 子目录下的。
> 直接按 `skills/<atom_name>/SKILL.md` 路径检查会漏掉这个原子，导致结构评分错误（0.00 而非 0.29）。
>
> **修复规则**: PROBE 步骤中对每个原子检查前，必须用 `os.path.exists()` 确认路径，不要假设所有原子都在同一层级。
> 对于不确定路径的原子，先在 `skills/` 下递归查找 `SKILL.md` 文件。
>
> 文言: 路径不一，先探后行

### Frontmatter 嵌套版本陷阱

> **陷阱：version 字段可能在 `metadata.synthos.version`（嵌套），也可能在 frontmatter 顶层。**
>
> Cycle 68 发现：7个核心原子的 version 全部在 `metadata.synthos.version` 下，不在顶层。
> 如果只检查顶层 `version:` 键，会错误地判定所有原子缺少 version。
>
> **修复规则**: 检查 version 时必须同时检查顶层和 `metadata.synthos.version` 两个位置。
>
> 文言: 名虽一也，位各不同

### Research→Critique→Revision 流水线注入 (PaperDebugger)

> 吸收自: PaperDebugger/paperdebugger (AGPL-3.0, 方法论)
> 文言: 格物通理，立言成章 | 分段审核，逐段精进 | 引用可溯，证据可验

注入点: paper-pipeline + quality-gate。三个子门:
1. **Researcher** — 文献定位与上下文分析
2. **Reviewer** — 会议审稿人风格的分段结构化评审
3. **Enhancer** — 上下文感知的精修改写

详见: references/absorption-paperdebugger-2026-06-05.md

Nudge 系统 = 结构行为校正 (Structural Behavior Correction)。核心机制：

1. **Nudge Registry** — 注册行为触发规则（trigger_fn: ctx → bool）
2. **Trigger Functions** — 检测 LLM 有工具但未使用的场景
3. **Auto-Inject Hints** — 自动注入提示让 LLM 继续执行
4. **Max Fires Limit** — 防止循环触发（每会话 max_fires=1）

内建规则:
| 规则 | 触发条件 | 效果 |
|:-----|:---------|:-----|
| search_nearby_no_location | 搜索返回结果但未发位置卡 | 提示发送位置 |
| said_recorded_no_write | 说"已记录"但未写文件 | 提示写入文件 |
| said_scheduled_no_schedule | 说"已安排"但未调用调度 | 提示调用 schedule |
| structured_data_no_render | 回复含结构化数据但未渲染 | 提示调用 render_page |
| self_reflect_no_report | 给出行为分析但未用 soul_report | 提示生成行为报告 |

注入点: evolution protocol OPTIMIZE 步骤 → LLM 行为监测 + 自动提示注入。

## 参考文件

- `references/evolution-cycle-detail.md` — 完整周期流程Deep Dive
- `references/pareto-optimization.md` — Pareto多维优化策略
- `references/gepa-reflection.md` — GEPA反射式分析协议
- `references/benchmark-automation.md` — 自动基准测试
- `references/drift-detection.md` — 漂移检测和宪法集成
- `references/absorption-standard.md` — 吸收标准体系（五维比较+质量门）
- `references/absorption-paperdebugger-2026-06-05.md` — PaperDebugger方法论吸收记录（XtraMCP流水线、conference-style review、citation verification）
- `references/absorption-autocontext-2026-06-05.md` — autocontext方法论吸收记录（improvement-loop、knowledge-inheritance、trace-continuity）
- `references/absorption-autocontext-2026-06-05.md` — autocontext方法论吸收记录
- `references/IO_CONTRACT.md` — IO契约格式
- `references/EVIDENCE_SCHEMA.md` — 证据schema
- `references/BOUNDARY.md` — 边界声明
- `references/LESSONS.md` — 历史教训集
- `references/project-health-assessment.md` — 手动健康评估
- `references/SKILL_TREE.md` — 技能树结构
- `references/QUALITY_CRITERIA.md` — 质量评分标准
- `references/CHANGE_LOG.md` — 变更日志
- `references/ABSORPTION.md` — 吸收通用流程