# 顺序执行一致性门控协议 — Sequential Execution Consistency Gate

## 核心原理（文言）

> **步步为营，节节有闸。**
> 行一步而观其应，应合则进，应悖则止。
> 不应不续，不确不越。

## 问题定义

当前 `autonomous-execution-threshold` 只在**接受新任务时**做一次决策（直接执行 vs 问人类）。
但**任务内的多步顺序执行**，每步走完后、下一步开始前，还需要一个一致性门控：

```
当前状态:                             理想状态:

收到任务                                收到任务
  ↓                                        ↓
一次执行到底 ← 人类无法中间干预           Step 1 执行
                                              ↓
                                          展示结果
                                              ↓
                                          [一致性门] ← 人类反馈分析
                                         /          \
                                      一致          不一致
                                        ↓              ↓
                                      Step 2       调整/重做
```

## 协议定义

### 触发条件

任意多步顺序执行任务（含有 `Step N / Step N+1` 结构的工作流）：

- 论文管线：P-1.1→P-1.2→P-1.3→P2.1→P2.2→...
- 进化流程：PROBE→BENCHMARK→ABSORB→REFINE→...
- 实验流程：实验A→实验B→实验C→...
- 任何"先做A，再做B"的串行工作

### 工作流

```
Step N 执行完毕
    ↓
① 呈现 Step N 的输出摘要给人类
    ↓
② 等待人类响应（或直接追问决策点）
    ↓
③ [一致性检查]
    ├── 人类输入 → 信号分析（同ANALYZE层）
    │
    ├── 一致性评分 = [0.0, 1.0]
    │     ├── 明确肯定 / 继续指示 → 1.0
    │     ├── 无否定词的短句 → 0.85
    │     ├── 轻微犹豫 / "看看" / "嗯" → 0.60
    │     ├── 质疑 / 反问 / 否定 → 0.30
    │     └── 明确纠正 / "不对" / "重新" → 0.0
    │
    ├── ≥0.80 → ✅ 通过 → 自动进入 Step N+1
    ├── 0.40-0.79 → 🟡 半通过 → 附调整建议继续
    └── <0.40 → 🔴 未通过 → 暂停，等待明确指令
```

### 一致性检测函数

```python
def consistency_check(human_input: str, step_context: dict) -> dict:
    """
    输入：人类对当前步骤输出的反应文本
    输出：一致性评分 + 决策建议
    """
    # 1. 信号分析
    signals = extract_signals(human_input)
    
    # 2. 一致性评分
    score = 0.80  # 基线：默认为一致（正向预设）
    
    affirmation_bonus = sum(s['weight'] for s in signals if s['type'] == 'affirmation')
    negation_penalty = abs(sum(s['weight'] for s in signals if s['type'] == 'negation'))
    hesitation_penalty = abs(sum(s['weight'] for s in signals if s['type'] == 'hesitation'))
    command_bonus = sum(s['weight'] for s in signals if s['type'] == 'command')
    
    score += affirmation_bonus + command_bonus
    score -= negation_penalty + hesitation_penalty
    
    # 句类修正
    s_type = detect_sentence_type(human_input)
    if s_type == 'interrogative':
        score -= 0.15
    elif s_type == 'imperative' and negation_penalty == 0:
        score += 0.10  # 命令式但不否定→高一致
    elif s_type == 'elliptical' and negation_penalty == 0:
        score += 0.05  # "继续"类
    
    # 3. 决策
    score = max(0.0, min(1.0, score))
    
    action = 'proceed'
    if score >= 0.80:
        action = 'proceed'      # 直接下一步
    elif score >= 0.40:
        action = 'adjust'       # 调整后继续
    else:
        action = 'pause'        # 暂停等明示
    
    return {
        'consistency_score': score,
        'signals': signals,
        'sentence_type': s_type,
        'action': action,
        'next_step_hint': '继续' if action == 'proceed' else '调整' if action == 'adjust' else '等待'
    }
```

## 与现有协议的整合

### 完整执行流程（v2.1.0）

```
收到任务
    ↓
[Step 0: ANALYZE] — 分析任务类型、人类意图
    ↓ 动态置信度
[是否自主执行?]
  ├── ≥80% → ⚡ 自主执行 Step 1
  └── <80% → 🟡 给选项人类选
    ↓
Step 1 执行完毕
    ↓
[Step 1.5: CONSISTENCY GATE] ← 新流程
  ├── 呈现结果 + 询问"继续/调整/停止?"
  ├── 分析人类响应的一致性
  ├── ≥0.80 → Step 2
  ├── 0.40-0.79 → 调整后 Step 2
  └── <0.40 → 暂停
    ↓
Step 2 执行完毕
    ↓
[Step 2.5: CONSISTENCY GATE] — 同上
    ↓
...
```

### 输出格式

```yaml
[Step 1 完成]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📋 产出: 领域地图已构建 (15个系统)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 [一致性检查]
  句类: 陈述句 | 信号: 肯定(+0.10) | 历史: 无
  一致性评分: 0.90 ✅
⚡ 自动进入 Step 2: 共同盲区分析
```

```yaml
[Step 2 完成]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📋 产出: 4个盲区已识别
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 [一致性检查]
  句类: 疑问句 | 信号: 质疑(-0.12) + 反问(-0.10)
  一致性评分: 0.43 🟡
  调整: 补充盲区5"人类交互分析缺失"后继续
```

## 场景示例

### 场景A: 论文写作管线

```
P-1.1 文献检索 → [展示结果] → 人类:"好，继续"  
    ↓ 一致性=0.95 ✅
P-1.2 空白分析 → [展示结果] → 人类:"等一下，这个gap不对"
    ↓ 一致性=0.30 🔴 暂停 → 人类调整方向
P-1.2 (修订后) → [展示] → 人类:"对，就这样"
    ↓ 一致性=0.95 ✅
P-1.3 假设形成 → ...
```

### 场景B: 进化循环

```
PROBE → [展示结果] → 人类:"继续" → 一致性=0.90 ✅
BENCHMARK → [展示结果] → 人类:"嗯..." → 一致性=0.65 🟡
  → 调整: 重新运行退化的原子
BENCHMARK (修订) → [展示] → 人类:"好了继续" → 一致性=0.95 ✅
ABSORB → ...
```

## 关键设计哲学

1. **正向预设（默认可继续）** — 基线0.80，只有检测到明确的否定/质疑才降至<0.80。不必要每个步骤都问"可以吗"。
2. **展示摘要，非全量** — 每个步骤后只展示关键产出，不dump全部原始数据。人类只需要看"够不够"。
3. **一致性≠盲目服从** — 人类说"继续"但数据有问题 → 一致性是对的，但数据本身需要修正。这是两个不同的问题。
4. **调整 vs 暂停** — 0.40-0.79时"调整后继续"意味着不重来，而是在当前步骤上做微调后自然推进下一步。

## 验证

- [ ] 多步顺序执行时，每步完成后展示摘要
- [ ] 人类肯定/继续 → 一致性≥0.80 → 自动下一步
- [ ] 人类否定/纠正 → 一致性<0.40 → 暂停
- [ ] 人类犹豫/模糊 → 一致性0.40-0.79 → 调整后继续
- [ ] 静默（未响应）→ 默认继续（正向预设）
