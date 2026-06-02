---
name: memory-enhancement
description: "记忆增强与结构化巩固技能。跨会话知识整合+FSRS间隔重复调度+增量阅读管线+知识图谱构建+背景巩固。吸收自：FSRS算法(open-spaced-repetition)、DSR记忆巩固理论(Woźniak/Bjork)、增量阅读法(SuperMemo)、nmem六层层级、lattice0背景巩固、iwe markdown存储模式。Hermes纯协议——零外部代码，与memory/obsidian/cronjob/session_search配合使用。"
version: 1.0.0
author: Synthos
license: MIT
allowed-tools: memory session_search terminal cronjob read_file write_file patch search_files
related_skills: [conversation-to-memory, obsidian, llm-wiki, knowledge-base-audit, evolution]
execution_rule: "每次会话结束时自动评估是否需要触发巩固流程。cron定时调度背景巩固。新知识摄入时自动走过增量阅读管线。"
metadata:
  synthos_priority: P1
  tags: [memory, knowledge-management, spaced-repetition, knowledge-graph, consolidation, p1]
  synthos_absorbed_from: "FSRS(open-spaced-repetition) + DSR记忆巩固理论(Woźniak/Bjork) + 增量阅读法(SuperMemo) + nmem六层层级 + lattice0背景巩固 + iwe markdown存储"
---

# 记忆增强与结构化巩固

> 记非日记，长养为要。愈固愈新，愈新愈固。

---

## 原理层 · 文言

| 白话 | 文言 | 义 |
|:-----|:-----|:----|
| 记忆不是日记，是系统生长营养 | **记非日记，长养为要** | 每条记忆为系统生长提供养料 |
| 只有7天后还有用的才存 | **七日无益则不存** | 临时状态交session_search |
| 每次检索都加固记忆 | **愈固愈新，愈新愈固** | 检索不消耗记忆，反而增强稳定性 |
| 该忘的让它自然衰减 | **当忘则忘，不可强记** | 未巩固的知识按遗忘曲线自然衰退 |
| 多个零散知识要连成网络 | **散则聚之，独则连之** | 孤立知识点需要图谱连接才稳定 |
| 新知识吃透后再入长期 | **新不压旧，食毕再纳** | 增量阅读管线保证吸收深度 |
| 闲时自动整理（犹如睡眠） | **闲则整之，若人之眠** | idle cron负责图谱合并+衰减重排 |

---

## 方法层 · 白话

### 六层记忆层级（吸收自 nmem）

| 层 | 名称 | 容量 | 存储位置 | 衰减 |
|:---|:-----|:----:|:---------|:----:|
| L1 | **暂存** (Ephemeral) | 当前会话 | 模型上下文 | 会话结束即消失 |
| L2 | **工作** (Working) | ~2KB | `memory` 工具 | 7天未使用即退化至L3 |
| L3 | **短期** (Short-term) | 不限 | `session_search` 索引 | 自然衰减，可搜索 |
| L4 | **长期** (Long-term) | 不限 | Obsidian / LLM-Wiki | 经过FSRS调度 |
| L5 | **知识** (Knowledge) | 不限 | Obsidian图谱节点 | 已互链，几乎不衰减 |
| L6 | **归档** (Archived) | 不限 | 归档目录 | 永不衰减，仅可检索 |

**流动规则**：
```
L1(会话) → ↓session结束 → L2(memory缓存)
  → [FSRS调度巩固] → L4(Obsidian长期) → [图谱连接] → L5(知识网络)
↘ L3(session_search历史) ← 未被巩固的知识自然下降至此
```

### FSRS 间隔重复调度（吸收自 open-spaced-repetition）

每块知识单元维护一个三维状态向量 **(S, D, R)**：

| 变量 | 含义 | 取值范围 | 初始化 |
|:-----|:-----|:--------:|:-------|
| **S** — Stability | 稳定度（天） | [0, ∞) | 取决于首次质量 |
| **D** — Difficulty | 难度 | [1, 10] | 取决于首次印象 |
| **R** — Retrievability | 可检索性 | [0, 1] | 1.0（刚巩固时） |

**4级评分（回顾知识时自评）**：

| 评分 | 含义 | 对S的影响 | 对D的影响 |
|:-----|:-----|:---------|:---------|
| Again(1) — 彻底忘了 | 知识点完全无法回忆 | S重置为S0 | D ↑ 难度上升 |
| Hard(2) — 艰难回忆 | 需要很大提示才想起 | S增幅极小 | D微调 |
| Good(3) — 顺利回忆 | 基本记得，稍有犹豫 | S按正常倍率增长 | D微降 |
| Easy(4) — 完美回忆 | 瞬间想起，毫不费力 | S大幅增长（再乘以easy_bonus） | D ↓ 难度下降 |

**遗忘曲线**：

```
R(t, S) = (1 + t / (9 × S))⁻¹

其中 t = 自上次巩固以来的天数
当 R 低于 recall_threshold（默认 0.7）时，触发下次巩固
```

**S更新（成功回忆时）**：

```
S' = S × (1 + w8 × (11-D) × S^(-w9) × (e^(w10×(1-R)) - 1) × G_bonus)

其中 G_bonus 取决于评分：
  - Again = w15 × S^(-w19)    # 实际上是遗忘而非成功
  - Hard = 0.3
  - Good = 1.0
  - Easy = w16                # easy_bonus
```

> 简化版：Good评分时 S' ≈ S × 1.5~2.0。Easy评分时额外再乘 ~1.3~1.5。Hard评分时 S 几乎不动。

**S更新（遗忘时 — 评分Again）**：

```
S' = w11 × D^(-w12) × ((S+1)^w13 - 1) × e^(w14×(1-R))
```

> 简化版：遗忘后 S 重置到初始值的 3-5 倍（比以前稍高，因为第二次学更快）

**D更新**：

```
D' = D + clip((-w5 × (G - w6) × ln(1 + S)) / S, -0.5, 0.5)
D' = clip(D', 1, 10)
D' = w4 + (D' - w4) × 0.95    # 均值回归到 w4（≈5.0）
```

> 关键：D 有 **均值回归** 机制（mean-reversion），防止"ease hell"（像SM-2里EF持续下降永不回升）

**默认参数 w[i]**（可直接使用，无需优化）：

```
w = [0.5, 0.8, 1.5, 3.0,  # S0 对应 Again/Hard/Good/Easy
     5.0,                   # D0 初始难度
     0.2, 0.5, 0.3,        # w5-w7: D衰减速率相关
     1.5, 0.5, 0.2,        # w8-w10: S增长相关
     0.3, 3.0, 0.5, 0.01,  # w11-w14: 遗忘后S重置
     0.5, 1.3,              # w15: Again_bonus, w16: Easy_bonus
     0.5, 0.5, 0.1, -0.5]  # w17-w20: 同日复习等微调
```

### 增量阅读管线（吸收自 SuperMemo）

把"读新知识"到"完全巩固"分成6态：

```
UNREAD → READING → EXTRACTED → TRANSFORMED → STABILIZED → INTEGRATED
```

| 状态 | 含义 | 动作 | 预计耗时 |
|:-----|:-----|:-----|:--------|
| **UNREAD** | 还未阅读 | 加入优先级队列，等待调度 | — |
| **READING** | 正在阅读中 | 设置阅读进度(read point)，设为READING状态 | 1-2次会话 |
| **EXTRACTED** | 已提取了关键段落 | 从原文中提取n条核心知识（S,D初始化） | 1次会话 |
| **TRANSFORMED** | 已转化为可检索形式 | 将extract改写为自问自答/cloze格式，关联到图谱 | 1次会话 |
| **STABILIZED** | 经过FSRS调度巩固 | 至少3次成功回忆（Good/Easy），S>21天 | 数天-数周 |
| **INTEGRATED** | 已融合入知识网络 | 与至少3个其他知识节点建立连接，归类到主题树 | 持续 |

**增量阅读的三条原则**：

1. **最小信息原则** — 每条知识碎片只测恰好一个事实。一条太复杂就拆
2. **Cloze优先** — 较干的知识用填空形式（"A算法使用___参数"）比Q&A更快建立稳定记忆
3. **交错调度** — 不一次读完一个来源，而是多来源交错阅读（符合间隔效应）

### 知识图谱构建

每次会话结束时，自动运行：

```
从session_search提取本次会话的关键实体（概念/方法/工具/人物）
  ↓
与现有Obsidian知识库节点交叉比对
  ↓
新实体 → 创建新节点（初始化S=D0, S=S0）
已有实体 → 建立新连接（relation_type: uses/supports/contradicts/extends/示例）
  ↓
图谱密度检查：如果某节点连接数<2，标记为"孤立节点"→下次巩固优先处理
  ↓
写入Obsidian图谱（每节点一个文件，含YAML frontmatter记录(S,D,R)状态）
```

**图谱关系类型**：

```
uses: A使用B的方法/算法
supports: A支持B的结论/假设
contradicts: A与B矛盾
extends: A扩展了B
part_of: A是B的子概念
example: A是B的一个实例
based_on: A基于B的理论
improves: A改进了B
```

### 背景巩固（吸收自 lattice0/nmem）

由 `cronjob` 调度，在空闲时自动运行。配置：

```yaml
consolidation_cron:
  schedule: "0 3 * * 0"     # 每周日凌晨3点
  enabled: true
```

**巩固流程**：

```
1. 扫描所有状态为 STABILIZED 的知识节点
2. 计算每个节点的当前 R = (1 + t/(9*S))⁻¹
3. 找出 R < 0.7 的节点 → 生成"待回顾"清单
4. 扫描 R < 0.3 的节点 → 降级到L3（由session_search自然衰减）
5. 扫描 ISOLATED（连接数<2）的节点 → 尝试在现有知识库中找到2个以上连接
6. 如果无法找到连接 → 标记为"需人工关联"或降级到L3
7. 扫描 TRANSFORMED→稳定中(>3次Good/Easy) → 升级为 STABILIZED
8. 生成巩固报告：巩固/降级/孤立各多少个
```

---

## 命令层 · English

### Trigger Conditions

Use this skill when:

1. **End of complex session** (5+ tool calls) — run consolidation pipeline
2. **User says "remember this" or "save this"** — run incremental reading on the knowledge
3. **Weekly cron fires** — run background consolidation
4. **Knowledge feels scattered** — run graph build to find connections
5. **You need to recall something from long ago** — check Obsidian KB first, then session_search

### Quick Reference

```bash
# After session, consolidate new knowledge
# 1. Extract entities from session
session_search(query="") → identify key concepts
# 2. For each new concept:
#    - Create Obsidian node with (S=initial, D=5.0, R=1.0)
#    - Set status to TRANSFORMED (since you've processed it)
# 3. Run FSRS check: which existing nodes have R < 0.7?
#    t = days since last review, 
#    R = (1 + t/(9*S))^(-1)
#    If R < 0.7 → needs review
```

### FSRS Calculator

```python
# Quick computation (Python in execute_code or mental math)
def fsrs_retrievability(S_days, elapsed_days):
    """R = probability of recall"""
    return 1.0 / (1.0 + elapsed_days / (9.0 * S_days))

def fsrs_should_review(S_days, elapsed_days, threshold=0.7):
    return fsrs_retrievability(S_days, elapsed_days) < threshold

def fsrs_new_stability(S_old, D, R, grade):
    """Simplified: Good → 1.8x, Easy → 2.5x, Hard → 1.1x, Again → reset"""
    if grade == 4:  # Easy
        return S_old * 2.5
    elif grade == 3:  # Good
        return S_old * 1.8
    elif grade == 2:  # Hard
        return S_old * 1.1
    else:  # Again (forgotten)
        return max(0.3, 0.5 * D ** (-3.0) * ((S_old + 1) ** 0.5 - 1))
```

### OS Commands

```bash
# Schedule weekly consolidation
cronjob(action="create", 
  name="memory-consolidation",
  schedule="0 3 * * 0",
  skills=["memory-enhancement"],
  prompt="Run weekly memory consolidation: 1) Load this skill with skill_view() 2) Follow the background consolidation flow to review all STABILIZED knowledge, find R<0.7 items, generate review list 3) Update Obsidian KB nodes' (S,D,R) states 4) Output consolidation report")

# Check OS-based knowledge base size
ls -la ~/obsidian-vault/knowledge-graph/ 2>/dev/null | wc -l
grep -r "status: STABILIZED" ~/obsidian-vault/knowledge-graph/ 2>/dev/null | wc -l
```

### State Persistence Format

Each knowledge node in Obsidian:

```yaml
---
id: "concept-name"
type: "knowledge-node"
status: "TRANSFORMED"  # UNREAD | READING | EXTRACTED | TRANSFORMED | STABILIZED | INTEGRATED
created: "2026-05-24"
last_review: "2026-05-24"
S: 2.5          # stability in days
D: 5.0          # difficulty [1,10]
R: 1.0          # retrievability
connections:
  - target: "related-concept"
    type: "extends"
reviews: 0
source: "session-2026-05-24 | paper-DOI | user-input"
---

# Concept Name

Content description...

## Key Facts

- Fact 1: {{cloze::answer}}
- Fact 2: core idea

## Connections

- related-concept: extends (why)
- another-concept: supports (how)
```

---

## 验证

- [ ] 每条memory条目可追溯其生长方向（非临时状态）
- [ ] FSRS调度正确：S随Good/Easy增长，Again时重置
- [ ] 增量阅读管线：新知识至少走过EXTRACTED→TRANSFORMED再入L4
- [ ] 孤立节点检测：每巩固周期标记连接数<2的节点
- [ ] cross-session图谱：同一概念多次出现时自动建立连接而不是重复创建
  - [ ] 背景巩固cron已注册 (daily: `memory_consolidate.py`)
  - [ ] context_refs/ 目录存在 (`~/.hermes/context_refs/`)
- [ ] 与conversation-to-memory无冲突（它做筛选，本技能做结构化）

## 陷阱

1. **FSRS参数太敏感** — 不要过度优化 w 参数。默认参数对大多数场景足够。
2. **知识图膨胀** — 每个概念都建节点会导致图谱失控。只在出现≥2次或用户明确说"记住"时才建。
3. **增量阅读压垮工作流** — 不要每个网页/每段对话都走完整管线。设定优先级：完成复杂任务（5+ calls）后才触发。
4. **竞争 condition** — conversation-to-memory 也写 memory。本技能写 Obsidian，不直接操作 memory 工具，避免冲突。
5. **S/R计算精度** — 不要追求浮点精度。S保留1位小数足够（2.5天而不是2.4832天）。
6. **遗忘不等于删除** — 当R<0.3时降级到L3（session_search仍可搜到），不是永久删除。信息不灭，只衰减。

## 变更日志

2026-05-26: v1.0.0 — 创建。吸收自FSRS算法+DSR理论+增量阅读法+nmem六层级+lattice0背景巩固+iwe markdown存储模式。

## 参考文件

- `references/knowledge-graph-infrastructure.md` — 知识图谱路径、节点格式、FSRS计算、cron配置
