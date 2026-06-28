---



name: computational-ode-modeling
description: "Directory index for computational-ode-modeling: computational-ode-modeling"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "model_spec: dict, solver: str, parameters: dict -> solution: dict (trajectories, stability, sensitivity)"
    atom_type: skill
    priority: P1
    related_skills: []
---




## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）



# Computational ODE Modeling for SCI Papers

> 建座山不如先量一量。ODE 参数校准是论文管线中最耗时的调试环节。

## 原理

当为 SCI 论文构建 2-ODE 计算模型时，最常见的失败模式是**动力学不稳定**：
- S 值超出 [0,1] 物理范围
- 平衡态不是稳态（微小扰动导致 runaway）
- 所有轨迹收敛到同一个 attractor（无 bifurcation）
- 求解器 hang（stiff ODE）

## 核心原则

### 1. 先校准平衡态，再加非线性

**错误做法**：直接写完整 ODE 系统 → 调试 20+ 轮 → 放弃
**正确做法**：
1. 定义平衡态：`dS/dt = 0` 在 S=S_eq, A=0 时成立
2. 验证：`ode(0, [S_eq, 0], params)` → dSdt ≈ 0
3. 加非线性项（MMP、mechanotransduction 等），逐步验证稳定性
4. 最后调时间尺度

### 2. 使用 cubic 双稳态结构

```
dS/dt = k * (S_high - S) * (S - S_unstable) * (S - S_low)
```

三个根：S_high（健康平衡）、S_unstable（鞍点/阈值）、S_low（病理平衡）。

**优势**：
- 自然双稳态：S > S_unstable → 健康，S < S_unstable → 病理
- S_high 是绝对上限：`S > S_high` 时 `(S_high - S) < 0` → dSdt < 0 ✓
- 鞍点位置决定临床阈值（可调参数）
- 无奇异点，求解器稳定

**对应生物**：
- S_high ≈ 0.92：健康组织完整性
- S_unstable ≈ 0.65：病理触发阈值（saddle）
- S_low ≈ 0.40：病理状态
- k：动力学速度（控制进展快慢）

### 3. A 方程与 S 解耦

```
dA/dt = lam * max(0, S_high - S) - mu * A + growth(A)
```

- `lam * max(0, S_high - S)`：S 偏离健康 → IOP 驱动扩张
- `-mu * A`：视觉反馈稳定（emmetropization）
- `growth(A)`：饱和生长因子

### 4. 校准流程

```
Step 1: 设 S_eq, 验证 ode(0, [S_eq, 0], p) → [~0, ~0]
Step 2: 加 MMP → 验证 S < S_unstable 时 dSdt < 0
Step 3: 加 mech_feedback → 验证 A > A0 时 S 下降加速
Step 4: 调 k → 控制进展时间尺度（年 vs 月）
Step 5: 调 lam/mu → 控制 A 的稳态值
Step 6: 扫 S0  across saddle → 确认 bifurcation 存在
```

## 常见陷阱

### 陷阱 1：平衡态校准错误

```python
# WRONG — equilibrium doesn't hold
dSdt = -alpha*S + eta*(1-S) + delta*D*S*(1-H)
# At S=0.92: -0.02*0.92 + 0.015*0.08 + 0.03*1*0.92*1 = +0.0105
# S increases → S > 1 → crash

# RIGHT — balance at equilibrium
# -alpha*S_eq + eta*(1-S_eq) + delta*D*S_eq = 0
```

**检测**：`ode(0, [S_eq, 0], p)` 的 dSdt 应该在 1e-5 以内。

### 陷阱 2：MMP autocatalysis 范围错误

```python
# WRONG — MMP active at ALL S values
H = S**n / (K**n + S**n)  # MMP high when S is HIGH

# RIGHT — MMP only when damaged
H = ((Sc - S)/Sc)**n / (K**n + ((Sc-S)/Sc)**n) if S < Sc else 0
```

### 陷阱 3：cubic 根顺序错误

```python
# WRONG: dSdt = k*(S-S_high)*(S-S_unstable)*(S-S_low)
# At S > S_high: all positive → dSdt > 0 → S runs away

# RIGHT: dSdt = k*(S_high-S)*(S-S_unstable)*(S-S_low)
# At S > S_high: (S_high-S) < 0 → dSdt < 0 → S pushed back ✓
```

### 陷阱 4：求解器 hang

当 ODE 出现奇点（如 division by zero at A=0, S=Sc）时，求解器会 hang。

**防御**：
```python
S = np.clip(S, 0.01, 0.99)  # Never hit exact boundaries
A = max(0.0, A)              # Never negative
dSdt = np.clip(dSdt, -0.5, 0.5)  # Cap rates to prevent overshoot
```

### 陷阱 5：A 方程无恢复力

```python
# WRONG — no visual feedback → A grows unbounded
dAdt = lam * max(0, S_high - S)  # Only positive expansion

# RIGHT — balanced expansion/contraction
dAdt = lam*max(0, S_high-S) - mu*A + growth  # Has negative term proportional to A
```

## 验证清单

每次 ODE 模型完成后，检查：

1. **平衡态**：`ode(0, [S_eq, 0], p)` → [~0, ~0]
2. **健康轨迹**：S0 > S_unstable → S → S_high, A → 0
3. **病理轨迹**：S0 < S_unstable → S → S_low, A → high
4. **bifurcation**：S0 just above vs just below S_unstable → different attractors
5. **物理约束**：S ∈ [0,1], A ≥ 0 at all times
6. **参数敏感性**：±50% 变化 → 定性行为不变（结构稳定性）

## 与 Paper Pipeline 集成

1. ODE 系统稳定后，`generate_results.py` 输出 JSON
2. 用该 JSON 填充论文 Methods/Results 部分
3. 通过 quality-gate 门：MAPE < 10%, R² > 0.90, AUC > 0.85
4. 装配 paper.tex → PDF

## 历史教训

- Paper 113 (scleral remodeling) 用了 15+ 轮调试才稳定。教训：**先 cubic 再复杂化**。
- 每次 `ode(0, [S_eq, 0], p)` 不接近零 → 必须改参数，不能改算法。
- 用 `solve_ivp` 的 `rtol=1e-10, atol=1e-12` 保证数值精度，否则 bifurcation 点漂移。


## 示例 · EXAMPLES

1. **基本用法**: 标准输入 → 标准输出
2. **边界用例**: 空输入、特殊字符、异常路径
3. **错误场景**: 缺失依赖、权限不足、网络异常


## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态


## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每个示例必须可独立运行、有明确输入输出、包含错误处理。
