# GenericAgent 吸收记录

> **来源**: lsdefine/GenericAgent (⭐12,156, MIT)
> **论文**: arXiv:2604.17091 — *GenericAgent: A Token-Efficient Self-Evolving LLM Agent via Contextual Information Density Maximization*
> **评分**: 3.85/5.0 — 建议吸收方法论
> **吸收日期**: 2026-05-27

---

## 三方法论提取

| # | 方法论 | 来源概念 | Synthos 注入点 | 优先级 |
|:-:|:-------|:---------|:---------------|:------:|
| 1 | **事后技能结晶** | 每次任务执行后自动将路径固化为 Skill | evolution engine RECORD 步骤增强 | P1 |
| 2 | **种子→树增长模式** | ~3K行种子代码 → 生长为完整技能树，不预加载 | evolution engine 起始设计原则强化 | P2 |
| 3 | **信息密度最大化** | <30K上下文窗口，每段信息需有存在理由 | quality-gate 评估标准扩展 | P2 |

---

## 方法论 1: 事后技能结晶 (Post-hoc Skill Crystallization)

### 原始概念

GenericAgent 每次完成一项任务后，自动将**执行路径**转化为可复用的 **Skill**。第一次做某件事时从头探索、安装依赖、编写脚本；成功后所有步骤被压缩为一个"召回即用"的技能。下次遇到相似任务，直接一行调用。

```text
第一次: 探索 → 安装依赖 → 写脚本 → 调试 → 验证 → 固化为 Skill
第二次及以后: 直接调用 Skill
```

### Synthos 映射

Synthos 已有 `project-experience-distillation` (类似机制)，但：
- 当前是**事件驱动**（SubagentStop ≥5次调用触发）→ 可改为**持续内联结晶**
- 当前依赖 `skill_manage` 手动创建 → 可增加自动轨迹→技能管道

### 注入方式

在 evolution engine RECORD 步骤（第十一步）中增加子步骤：

```yaml
RECORD:
  11a. UPDATE_STATE      # 已有
  11b. WRITE_LOG         # 已有
  11c. CRYSTALLIZE_SKILL # 新增 — 如果有新的稳定执行轨迹，自动结晶为 skill
        trigger: "同一任务模式成功执行 ≥3 次"
        action: "自动从执行轨迹提取方法论 → 生成 SKILL.md 草稿 → 标记 pending_review"
        filter: "排除临时/一次性任务，只结晶有复用价值的模式"
  11d. SAVE_REPORT       # 已有
```

---

## 方法论 2: 种子→树增长模式

### 原始概念

> "不预设技能，靠进化获得能力" — Don't preload skills, evolve them.

~3K 行种子代码 → 生长为数万技能的技能树。核心系统极简（~100行事件循环），所有能力在运行时通过任务执行自然获得。

### Synthos 映射

Synthos 的架构演变（从 16 个 Python 文件到 0，从 72 技能到 100+）本就遵循此哲学。但缺少一个**形式化的种子理论**来指导"什么算种子、什么算增长"。

### 注入方式

在 evolution 核心原则中增加一条**种子理论**：

> 种不可大，大则不生。存其核而弃其繁，繁自生焉。

意思是：初始系统必须尽可能小。只保留不可再简的核心（种子），所有扩展通过任务执行自然生长。

---

## 方法论 3: 信息密度最大化 (Contextual Information Density Maximization)

### 原始概念

GenericAgent 通过限制上下文窗口(<30K)强制信息密度最大化——每段文本必须有其存在的理由。低信息密度的内容（长文档、冗余历史、重复指令）被自动过滤或压缩。

### Synthos 映射

Synthos 的 SKILL.md 压缩（451→331行）就是此原则的具体应用。但缺少一个**形式化评估指标**来判断一段 SKILL.md 内容是否"信息密度不足"。

### 注入方式

在 quality-gate 的评估标准中增加信息密度指标：

> 每条 SKILL.md 内容行必须有独立信息价值。可删除而不损失核心方法论的行 → 信息密度不足，应压缩或移除。

---

## 文言提炼

> **事成即录，录即成技。** — 每次执行结晶为技能
> **种不可大，大则不生；存核弃繁，繁自生焉。** — 种子最小化
> **无密则弃，有密则存。** — 信息密度决定内容留存

---

## 吸收验证

- [x] 读 README (全部)
- [x] 方法论提取 (3条)
- [x] 文言提炼 (3条)
- [x] 注入点确定
- [ ] 注入 evolution engine v2.17 (待当前循环执行)
