---
name: evolution
description: "⚡ P0 自进化引擎。Synthos evolution engine v2.12 — GEPA反射式分析(OPTIMIZE)+自动数据集(BENCHMARK)+Pareto多维优化(DIAGNOSE)+结构探查+功能基准+外部吸收+教训学习+黄金验证+自扩关键词+SELF_REFLECT+宪法集成+漂移检测+渐进披露+响应闸门+自动优化+输入护栏+持久执行+条件分支+拦截点+追踪+SEPL回滚+ARA溯源+Git即记忆+Pareto前沿+假设先行。每轮触发project-experience-distillation。"
version: 2.12.0
author: Synthos Evolution Engine
license: MIT
metadata:
  synthos_atom_type: "meta-evolution"
  synthos_priority: "P0"
  synthos_depends_on: "task-router, knowledge-acquisition, knowledge-extraction, association-discovery, gap-discovery, hypothesis-generation, argument-expression, viewpoint-verification, project-experience-distillation, quality-gate"
allowed-tools: terminal skill_view Read Write patch cronjob web_search delegate_task memory session_search
signature: "cycle: int, prev_scores: dict, prev_benchmark: float -> evolution_report: EvolutionReport, next_actions: list[str], drift_log: DriftLog"
related_skills: [project-experience-distillation, quality-gate, conversation-to-memory, skill-absorption, cognitive-atom-architecture]
---

# Synthos 进化引擎 v2.11

> 宪临万法，漂移必察。败则回滚，成则铭记。
> 每轮只修一维，每次必有假说。

---

## 原理层 · 文言

### 核心理念

| 白话 | 文言 | 义 |
|:-----|:-----|:----|
| 宪法高于一切 | **宪临万法** | CONSTITUTION.md为最高约束 |
| 一次性只聚焦一个维度 | **一维一修** | 每轮只修最低分维度 |
| 修改前先写假说 | **先立说，后动刀** | 无可证伪假说不入IMPROVE |
| Git即记忆 | **以史为鉴** | 每次改前commit，败则revert |
| 崩溃从断点续跑 | **断点续行** | 每步写完保存检查点 |
| 数据必源执行层 | **凡数必源执行** | 定量数据不从声明层推 |
| **读轨迹溯败因** | **迹以观行，理以究因** | v2.12 REFLECTIVE_ANALYSIS — 读执行轨迹理解失败根源 |
| **无金则自炼** | **无金自炼，以文生案** | v2.12 AUTO_DATASET — 从SKILL.md自动生成测试用例 |
| **多利取其重** | **多利取重，多径择优** | v2.12 Pareto — 多目标前沿选最优改进路径 |

### 吸收之道

学于外而纳于内，谓之吸收。凡外来之技，必经四门：L+0标其源，L+1改其制，L+2验其质，L+3证其用。四门未过，不入系统。

已吸收外部技能记录：

| 来源 | 评分 | 文件 |
|:-----|:----:|:-----|
| handsomestWei/patent-disclosure-skill v1.8.5 | 4.6 | `references/absorption-patent-disclosure.md` |
| Agent4S (Zheng et al. 2025, arXiv:2506.23692) | 4.6 | `references/absorption-agent4s.md` |
| PaperSpine V2 (WUBING2023) | 4.6 | `references/absorption-paperspine-v2.md` |
| nature-paper2ppt (GARCH-QUANT) | 4.6 | `references/absorption-nature-paper2ppt.md` |

---

## 方法层 · 白话

### 两种触发模式

| 模式 | 触发 | 适用 |
|:-----|:-----|:-----|
| ⏱ Timer | cron 定时 | 系统健康检查 |
| ⚡ Event | Hook 事件 | 任务完成/会话结束 |

## 状态机图

```
                    ┌───────┐
                    │ ENTRY  │
                    └───┬───┘
                        │
              ┌─────────▼──────────┐
              │ CHECKPOINT: 恢复?   │ ← 上次崩溃？从断点续跑
              │ ├─ 是→从断点继续    │
              │ └─ 否→从头开始     │
              └─────────┬──────────┘
                        │
              ┌─────────▼──────────┐
              │ LOAD_CONSTITUTION   │ ← 始终运行
              └─────────┬──────────┘
                        │
            ┌───────────▼────────────┐
            │  门1: 有新会话？        │
            │  ├─ 是→加载状态+教训    │
            │  └─ 否→跳到漂移检查     │
            └───────────┬────────────┘
                        │
              ┌─────────▼──────────┐
              │ DRIFT_CHECK         │ ← 三问自检，始终运行
              └─────────┬──────────┘
                        │
            ┌───────────▼────────────┐
            │  门2: 需要进化？        │
            │  ├─ 是→全流程          │
            │  │   探查→基准→优化    │
            │  │   →吸收→诊断→改进   │
            │  │   →验证→记录        │
            │  └─ 否→仅漂移检查 退出  │
            └───────────┬────────────┘
                        │
                      ┌─▼─┐
                      │退出│
                      └───┘
```

## 12步概要（详细协议→references/evolution_protocol.md）

| 步骤 | 做什么 | 关键条件 |
|:-----|:-------|:---------|
| 0 | LOAD_CONSTITUTION | 加载宪法，注入意识 |
| 1 | LOAD_STATE | 三级渐进加载（L1必/L2条件/L3按需） |
| 2 | LESSONS | 加载近30天教训 |
| 3 | DRIFT_CHECK | 三问自检，判定🟢/🟡/🔶/🔴 |
| 4 | PROBE | 7原子结构健康检查 |
| 5 | BENCHMARK | 轮转测试+Golden验证+**自动数据集**(v2.12) |
| 5.5 | **AUTO_DATASET** | 无golden时从SKILL.md自动生成(v2.12) |
| 6 | OPTIMIZE | **反射式分析**(v2.12)→自动优化失败技能+回滚协议 |
| 6.5 | **REFLECTIVE_ANALYSIS** | 读轨迹→理解失败→针对性修复(v2.12) |
| 7 | EXTERNAL | 主动吸收引擎（每轮） |
| 8 | DIAGNOSE | 综合诊断+**Pareto多维评分**(v2.12)+宪法对齐 |
| 9 | IMPROVE | Pareto前沿选择→单指标聚焦 |
| 10 | VERIFY | 验证patch+重跑失败案例 |
| 11 | RECORD | 更新状态+日志+教训+报告 |

## 门条件表（条件分支）

| 门 | 条件 | PASS→ | FAIL→ |
|:---|:-----|:-------|:-------|
| 新鲜会话门 | 首次/用户新任务？ | 加载状态+教训 | 直接漂移检查 |
| 进化需求门 | 距上次进化>1h？ | 全流程 | 仅漂移检查退出 |
| 优化需求门 | 连续BENCHMARK失败？ | OPTIMIZE | 跳过 |
| 外部扫描门 | 距上次吸收>6h？ | EXTERNAL | 跳过 |
| 用户通知门 | DIAGNOSE有重大发现？ | 拦截中断 | 直接记录 |

## 事件驱动Hook（Event触发器）

| 事件 | 触发时机 | 执行 |
|:-----|:---------|:-----|
| SessionStart | 会话启动 | 加载宪法+漂移检查+质量待办 |
| InputGuardrail | 用户输入后执行前 | 宪法检查+范围检查 |
| PreResponse | 每次响应前 | 认识论门+宪法门+漂移门 |
| TaskComplete | 任务完成 | 响应质量门+检查quality-gate |
| SubagentStop | 子任务返回(≥5次调用) | project-experience-distillation |
| SessionEnd | 会话结束 | 漂移检查+记忆+进化循环 |
| Setup | skill/项目初始化 | 注册到进化状态+技能树 |

## 执行路径

```
路径A（快速漂移检查）: 宪法→漂移检查→退出
路径B（全新进化）   : 宪法→状态→教训→漂移→探查→基准→[自动数据集?]
                      吸收→反射式分析→[优化?]→[回滚?]→Pareto诊断→拦截?→改进→验证→记录
路径C（崩溃恢复）   : 宪法→恢复断点→继续
```

## 漂移检测

三问自检（每次SessionStart/SessionEnd）：
1. 观察者视为诚实一致的对话者？
2. 行为从宪法和诚实阅读出发？
3. 产出与明显为真的事物对应？

| 等级 | 表现 | 处理 |
|:-----|:-----|:-----|
| 🟢 无漂移 | 与宪法一致 | 不操作 |
| 🟡 轻度 | 语言/态度偏移 | 记录 |
| 🔶 中度 | 决策偏离默认姿态 | 记录+回正 |
| 🔴 重度 | 违反宪法条款 | 自动回正+通知+lessons |

## 能力渐进披露

| 层级 | 范围 | 何时可用 |
|:-----|:-----|:---------|
| L1 核心 | 8原子+3元技能 | 始终 |
| L2 扩展 | 社区/领域技能 | 任务激活 |
| L3 专业 | 高度专项技能 | 用户请求或上下文触发 |

## 响应质量门（PreResponse）

| 门 | 问题 | 触发 |
|:---|:-----|:-----|
| 认识论门 | 断言有可验证来源？ | 每实质性断言 |
| 宪法门 | 输出与不可修改条款一致？ | 每次响应 |
| 漂移门 | 最近轨迹偏离基线？ | 每5次tool call |

## 已知陷阱

1. 宪法未加载但未报错→ `constitution_loaded: true/false` 字段每次验证
2. 漂移检测过严→ 🟡冷却期：同会话至少5次tool call后才再次检查
3. 渐进披露与用户预期冲突→ SessionStart提醒"我有120+技能"
4. 外部搜索关键词可能过期→自扩展自动发现新关键词
5. SKILL.md被意外覆盖→每次Patch前备份到 backups/

## 工作目录

| 路径 | 用途 |
|:-----|:-----|
| /media/yakeworld/sda2/Synthos | 项目根 |
| evolution-state.json | 当前状态 |
| evolution-log.md | 日志 |
| outputs/evolution/ | 报告+追踪 |
| skills/evolution/references/ | 参考文件 |

## 命令层 · English

### Trigger

```bash
# Trigger an evolution cycle manually
skill_view("evolution")
# The engine runs: PROBE → BENCHMARK → EXTERNAL → DIAGNOSE → IMPROVE → VERIFY → RECORD
```

### Key Tool References

| Tool | Usage |
|:-----|:-------|
| `skill_view(name)` | Load skill content for inspection |
| `Read/Write/patch` | Modify skill files |
| `terminal("git commit ...")` | Snapshot before changes |
| `terminal("git revert ...")` | Rollback on failure |
| `delegate_task(...)` | External absorption research |

### Related References

| File | Purpose |
|:-----|:--------|
| `references/evolution_protocol.md` | Full 11-step protocol |
| `references/absorption-*.md` | External skill absorption records |
| `references/QUALITY_CRITERIA.md` | Quality gate thresholds |
| `references/BENCHMARKS.md` | Benchmark definitions |
| `references/BOUNDARY.md` | Operational boundaries |
| `references/LESSONS.md` | Historical lessons |
| `references/IO_CONTRACT.md` | I/O contract |

---

## 验证

- [ ] CONSTITUTION已加载（constitution_loaded=true）
- [ ] 漂移等级≤🟢
- [ ] PROBE结构分≥0.5
- [ ] BENCHMARK基准分≥0.5
- [ ] 无连续3轮同一维度无提升
- [ ] OPTIMIZE补丁已验证
- [ ] evolution-state.json已更新
- [ ] lessons.jsonl已追加
- [ ] 每轮最新报告写入 outputs/evolution/
