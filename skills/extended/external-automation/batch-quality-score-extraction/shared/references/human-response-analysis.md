# 人类响应语言分析框架 — Human Response Linguistic Analysis

## 核心原理（文言）

> **言为意表，辞为信根。**
> 不听其词而察其势，不观其字而究其情。
> 拒则权重加，诺则权重减。
> 疑则阈下探，令则径行之。

## 概述

该框架在 `Predict-Judge-Act` 协议前增加 **Step 0: ANALYZE** 层，对用户输入做实时语言分析，输出动态置信度。置信度不再是固定基线，而是基于实际交互文本计算的结果。

## Step 0: ANALYZE — 语言分析管道

```
用户原始输入
    ↓
[句类检测] → 陈述句/祈使句/疑问句/省略句
    ↓
[信号词提取] → 肯定/否定/犹豫/反问/命令信号
    ↓
[历史模式匹配] → 过去相同场景的纠正记录
    ↓
[动态置信度计算] → 输出 [0.1, 0.99] 的数值
    ↓
进入 Step 1: PREDICT（使用动态置信度而非固定基线）
```

## 信号词库（中英文双语）

### 🟢 肯定信号（提升置信度）

| 分类 | 中文信号 | 英文信号 | 权重 |
|:-----|:---------|:---------|:----:|
| 直接肯定 | 好、对、可以、是的、行、OK、嗯 | yes, ok, good, right, sure, fine | +0.10 |
| 热情肯定 | 太好了、非常棒、完美、厉害 | great, perfect, excellent, awesome | +0.15 |
| 继续指示 | 继续、接着、下一步、然后呢、再说、再来 | continue, next, go on, proceed, more | +0.12 |
| 确认同意 | 同意、批准、通过、就这样、可以了 | agree, approved, looks good, confirmed | +0.10 |
| 无异议默许 | （无否定词+长度<5字） | （简短陈述无否定词） | +0.05 |

### 🔴 否定/纠正信号（降低置信度）

| 分类 | 中文信号 | 英文信号 | 权重 |
|:-----|:---------|:---------|:----:|
| 直接否定 | 不、别、不要、不对、不是、错了 | no, not, wrong, incorrect, stop | -0.20 |
| 纠正重做 | 应该、需要、重新、改、换、重来 | should, need to, redo, change, revise | -0.15 |
| 暂停阻止 | 等一下、等等、停、hold on | wait, hold on, stop, hang on | -0.18 |
| 反问质疑 | 是吗？、对吗？、真的？、为什么？ | really?, are you sure?, why? | -0.12 |
| 否定前缀 | 没、未、无、非、别 | un-, in-, not, without | -0.08 |

### 🟡 犹豫/不确定信号（降低置信度）

| 分类 | 中文信号 | 英文信号 | 权重 |
|:-----|:---------|:---------|:----:|
| 犹豫词 | 嗯…、那个、这个…、怎么说 | um, uh, well, hmm, like | -0.08 |
| 模糊词 | 或许、大概、可能、maybe、也许 | maybe, perhaps, probably, might | -0.10 |
| 条件词 | 如果、要是、假如、除非 | if, unless, depending | -0.05 |
| 间接请求 | 能不能、是否可以、帮我看一下 | could you, can you, would you | -0.03 |

### 🟣 命令信号（高置信度直接执行）

| 分类 | 中文信号 | 英文信号 | 权重 |
|:-----|:---------|:---------|:----:|
| 直接命令 | 把、给我、去、立即、马上 | do, run, execute, implement | +0.15 |
| 祈使句 | （动词开头无提问） | (verb at start + no question mark) | +0.10 |

## 句类检测算法

```python
def detect_sentence_type(text: str) -> str:
    """返回: imperative, interrogative, statement, elliptical"""
    text = text.strip()
    if not text:
        return 'elliptical'
    # 疑问句
    if text.endswith('？') or text.endswith('?') or text.startswith('是不是') or text.startswith('要不要'):
        return 'interrogative'
    # 祈使句（中文动词开头）
    imperative_starts = ['把', '给', '去', '立即', '马上', '给我', '帮我', '要']
    if any(text.startswith(s) for s in imperative_starts):
        return 'imperative'
    # 英文祈使句（动词开头）
    english_imperatives = ['do', 'run', 'execute', 'create', 'build', 'write', 'make', 'implement']
    first_word = text.split()[0].lower() if text.split() else ''
    if first_word in english_imperatives and not text.endswith('?'):
        return 'imperative'
    # 省略句（非常短）
    if len(text) < 6:
        return 'elliptical'
    return 'statement'
```

## 动态置信度计算公式

```python
def calculate_dynamic_confidence(
    user_input: str,
    base_confidence: float = 0.80,
    history_matches: list = None  # 历史纠正记录列表
) -> float:
    """
    动态置信度计算
    
    输入: 用户原始文本
    输出: [0.1, 0.99] 的置信度
    
    公式:
    dynamic_confidence = min(max(
        base_confidence 
        + Σ(signal_weights) / max(len(weighted_signals), 1)  # 信号平均影响
        + sentence_type_modifier                                  # 句类调整
        + history_modifier,                                       # 历史纠正
    0.1), 0.99)
    """
    confidence = base_confidence
    
    # 1. 信号词分析
    signals = extract_signals(user_input)
    if signals:
        net_signal = sum(s['weight'] for s in signals) / len(signals)
        confidence += net_signal
    
    # 2. 句类调整
    s_type = detect_sentence_type(user_input)
    type_modifiers = {
        'imperative': +0.10,     # 命令句→高置信度
        'interrogative': -0.15,  # 疑问句→低置信度
        'elliptical': +0.05,     # 短句→默认略高（"继续"类）
        'statement': 0.0,        # 陈述句→中性
    }
    confidence += type_modifiers.get(s_type, 0.0)
    
    # 3. 历史纠正匹配
    if history_matches:
        for record in history_matches:
            if record['scenario'] in user_input or record['correction'] in user_input:
                # 匹配到历史纠正 → 大幅降置信度
                confidence -= 0.15
                break
    
    return max(0.1, min(0.99, confidence))
```

## 信号提取函数

```python
AFFIRM_SIGNS = {
    '好': 0.10, '对': 0.10, '可以': 0.10, '是的': 0.10, '行': 0.10,
    'OK': 0.10, 'ok': 0.10, '继续': 0.12, '接着': 0.12, '下一步': 0.12,
    '太好了': 0.15, '非常棒': 0.15, '完美': 0.15, '厉害': 0.15,
    'yes': 0.10, 'great': 0.15, 'perfect': 0.15, 'continue': 0.12,
    '同意': 0.10, '批准': 0.10, '通过的': 0.10, '就这样': 0.10,
}

NEGATE_SIGNS = {
    '不': -0.20, '别': -0.20, '不要': -0.20, '不对': -0.20, '不是': -0.20,
    '错了': -0.20, 'no': -0.20, 'wrong': -0.20, 'stop': -0.18,
    '应该': -0.15, '需要': -0.15, '重新': -0.15, '改': -0.15, '换': -0.12,
    '等一下': -0.18, '等等': -0.18, 'wait': -0.18,
    '是吗': -0.12, '真的？': -0.12, 'why': -0.12,
    '没': -0.08, '未': -0.08, '无': -0.08,
}

HESITATE_SIGNS = {
    '嗯': -0.08, '那个': -0.08, '怎么说': -0.08, 'um': -0.08,
    '或许': -0.10, '大概': -0.10, '可能': -0.10, 'maybe': -0.10, 'perhaps': -0.10,
    '如果': -0.05, '要是': -0.05, 'unless': -0.05,
}

COMMAND_SIGNS = {
    '把': 0.15, '给我': 0.15, '去': 0.10, '立即': 0.15, '马上': 0.15,
    'do': 0.15, 'run': 0.15, 'execute': 0.15, 'implement': 0.15,
}

def extract_signals(text: str) -> list:
    signals = []
    # 按优先级：否定>命令>肯定>犹豫
    for word, weight in NEGATE_SIGNS.items():
        if word in text:
            signals.append({'word': word, 'weight': weight, 'type': 'negation'})
    for word, weight in COMMAND_SIGNS.items():
        if text.startswith(word) or text.endswith(word):
            signals.append({'word': word, 'weight': weight, 'type': 'command'})
    for word, weight in AFFIRM_SIGNS.items():
        if word in text:
            signals.append({'word': word, 'weight': weight, 'type': 'affirmation'})
    for word, weight in HESITATE_SIGNS.items():
        if word in text:
            signals.append({'word': word, 'weight': weight, 'type': 'hesitation'})
    return signals
```

## 与 Predict-Judge-Act 协议的集成

### 完整执行流程（v2.0）

```
收到用户消息
    ↓
当前场景分类
    ↓
反模拟检测（不变）
    ↓
[Step 0: ANALYZE] ← 新增
  ├── detect_sentence_type(user_input)
  ├── extract_signals(user_input)
  ├── history_matches = search_memory(scenario)
  └── dynamic_confidence = calculate(..., history_matches)
    ↓
[Step 1: PREDICT]
  └── 使用 dynamic_confidence 而非固定置信度
    ↓
[Step 2: JUDGE]
  ├── ≥80% → ⚡ 直接执行
  ├── 60-80% → 🟡 给选项 + 推荐
  └── <60% → 🔴 等确认
    ↓
[Step 3: ACT]
  ├── 执行动作
  └── 附推理链（含分析摘要）
```

### 输出格式扩展

```yaml
[场景: 常规任务]
🔍 [分析: 句类=祈使句, 信号=肯定(+0.10), 历史=无匹配]
   -> 动态置信度: 0.90
🟢 [推测: 直接执行, 置信度90%]
⚡ 开始自主执行: ...
```

```yaml
[场景: 复杂决策]
🔍 [分析: 句类=疑问句, 信号=犹豫(-0.08)+否定(-0.15), 历史=纠正:选择目标期刊(1)]
   -> 动态置信度: 0.57
🟡 [推测: 用户可能想换方案, 置信度57%]
  推荐: 方案A > 方案B > 方案C
```

## 历史匹配

当历史中有纠正记录时，将该记录的场景描述文本与当前用户输入做模糊匹配。匹配规则：

1. 若用户输入包含历史纠正中的关键词（如"不对"+"应该用PubMed"），则匹配
2. 若当前场景与历史记录的场景相同，且用户输入包含"不"或"改"类信号词，则匹配
3. 匹配到历史纠正 → 置信度额外 -0.15

## 验证清单

- [ ] 句类检测：正确区分祈使句/疑问句/陈述句/省略句
- [ ] 信号提取：正确识别肯定/否定/犹豫/命令信号
- [ ] 历史匹配：正确回忆过去类似的纠正场景
- [ ] 置信度计算：输出在[0.1, 0.99]范围内
- [ ] 错误案例：当用户说"不是这个意思"时，置信度降至<60%
- [ ] 正确案例：当用户说"对，继续"时，置信度升至≥90%

## 已知局限

1. **单语言优先** — 当前信号词以中文为主+基础英文，其他语言不支持
2. **表面匹配** — 信号词是字面匹配，未使用NLP语义分析
3. **线性权重** — 信号权重相加取平均，非线性模型
4. **无增量学习** — 历史权重不会自动调整，需手动patch
