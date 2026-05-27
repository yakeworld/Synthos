# Auto-Execution Engine — 自动执行引擎

## 核心原理（文言）

> **行不需问，续不需请。**
> 迹在则行，门通则续。
> 不待言而自进，不俟令而自前。
> 错则后改，不因怕错而止步。

## 问题

当前自动执行虽在概念上实现了 ANALYZE→PJA→CONSISTENCY GATE，但实际运行时：

1. **置信度是手算的** — 我在文本里写"P(继续)=0.80+0.10+...=0.99"，但没有真的跑函数
2. **pipeline-trace是旁观者** — 它记录但不驱动，下一步是我手动选择的
3. **每步之间有人工间隙** — 虽然不等用户响应，但中间有我的"思考"

## 解决方案：三条强化

### 强化1: 正式置信度计算函数

每次需要决策时，实际运行以下逻辑（而非手动推算）：

```python
def compute_dynamic_confidence(
    user_input_history: list,      # 最近N条用户消息
    current_step_status: dict,     # 当前步骤状态
    pipeline_trace: dict,          # 整个管线trace
    step_output_quality: float,    # 当前产出质量评分
) -> float:
    """
    真实置信度计算，基于实际可量化指标。
    """
    confidence = 0.80  # 正向基线
    
    # 1. 历史语气分析（基于最近3条消息）
    recent_msgs = user_input_history[-3:] if user_input_history else []
    affirmation_count = sum(1 for m in recent_msgs if any(w in m for w in ['好','继续','对','yes','great','perfect','ok']))
    negation_count = sum(1 for m in recent_msgs if any(w in m for w in ['不','别','不对','错了','stop','wait','等一下']))
    continue_count = sum(1 for m in recent_msgs if '继续' in m)
    
    if continue_count >= 2:
        confidence += 0.15  # 多次"继续"→高确
    elif affirmation_count > negation_count:
        confidence += 0.08
    else:
        confidence -= 0.15
    
    # 2. 步骤依赖链检查
    if pipeline_trace:
        all_preconditions_met = all(
            step['gate']['status'] in ('passed', 'unblocked')
            for step in pipeline_trace.get('steps', [])
            if step['step_id'] in current_step_status.get('depends_on', [])
        )
        if all_preconditions_met:
            confidence += 0.10  # 所有前驱步骤通过→高确
    
    # 3. 产出质量检查
    if step_output_quality >= 0.85:
        confidence += 0.05
    elif step_output_quality < 0.60:
        confidence -= 0.10
    
    # 4. 阻塞检查
    blockers = pipeline_trace.get('blockers', []) if pipeline_trace else []
    if blockers:
        confidence -= 0.10  # 有阻塞→降低
        
    return max(0.1, min(0.99, confidence))
```

### 强化2: pipeline-trace驱动的自动流转

不再"先做完一步→然后手动决策下一步"。改为：

```python
def auto_advance(trace_path: str) -> str:
    """
    读取pipeline-trace，自动找到下一个可执行的步骤。
    """
    with open(trace_path) as f:
        trace = json.load(f)
    
    steps = trace['steps']
    
    # 找到第一个 status 为 'not_started' 且 gate 未阻塞的步骤
    for step in steps:
        if step['status'] == 'not_started':
            gate_status = step.get('gate', {}).get('status', 'blocked')
            if gate_status in ('passed', 'unblocked'):
                return step['step_id']  # 自动推进到此步
    
    # 所有步骤完成 → 返回完成状态
    return 'COMPLETED'
```

**效果**：当 P3 完成且 gate 设为 'passed' 后，auto_advance() 自动返回 'P2' → 我无需人工判断就直接开始 P2。

### 强化3: 多步链式执行

如果一个步骤完成后，日志明确指示"进入下一步"，则连续执行多步不中断：

```python
def chain_execute(start_step: str, trace_path: str, max_steps: int = 3) -> list:
    """
    链式执行：自动执行后续步骤，最多连续执行max_steps步。
    每步之间不输出中间结果，最后汇总报告。
    """
    executed = []
    current = start_step
    
    for _ in range(max_steps):
        # 执行当前步骤
        result = execute_step(current)
        executed.append((current, result))
        
        # 更新trace
        update_trace(trace_path, current, result)
        
        # 找下一步
        next_step = auto_advance(trace_path)
        
        if next_step == 'COMPLETED':
            break
            
        # 检查下一步是否由当前步骤直接触发的（无外部依赖）
        if not is_direct_continuation(current, next_step):
            break  # 需要人类决策
            
        current = next_step
    
    return executed
```

## 集成到现有流程

### autonomous-execution-threshold v2.2.0

```
收到任务
    ↓
[1] ANALYZE (正式置信度函数)
    ↓
[2] Predict-Judge-Act
    ↓
[3] 执行 Step N
    ↓
[4] 更新 pipeline-trace
    ↓
[5] auto_advance() → 找下一步
    ├── 找到下一步 → 检查是否direct_continuation
    │   ├── ✅ 是 → ⚡ 链式执行后续步骤
    │   └── ❌ 否 → 重新进入[1] ANALYZE
    └── COMPLETED → 汇总报告
```

## 验证清单

- [ ] compute_dynamic_confidence() 基于真实数据而非文本模拟
- [ ] auto_advance() 正确找到下一个可执行步骤
- [ ] chain_execute() 连续执行最多3步不中断
- [ ] 阻塞的步骤不会被auto_advance跳过
- [ ] 所有步骤完成后，最终汇总一次报告
