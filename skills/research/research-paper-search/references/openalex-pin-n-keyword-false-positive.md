# OpenAlex PINN/ODE 关键词假阳性 — 2026-06-07

## 现象

当使用 OpenAlex 搜索 `PINN` 或 `NeuralODE` 相关关键词时，偶尔会返回**数量极少但高度相关标题**的论文。这些论文在标题/关键词中包含 "PINN" 作为词组的一部分，但实际方法是完全不同的经典研究。

## 案例：Paper 76 (saccade-kinematic-ODE)

**查询**：`saccade+kinematic+PINN` → OpenAlex 返回 1 篇论文：

```
Title: "Subsets of extraocular motoneurons produce kinematically distinct saccades during hunting and exploration"
Journal: Current Biology
Authors: Charles K. Dowell, Thomas Hawkins, Isaac H. Bianco
```

**为什么匹配**：
- "saccade" 出现在标题
- "kinematically" 出现在摘要中  
- "PINN" 出现在摘要文本（不是指 Physics-Informed Neural Network，而是出现在某个专业术语或缩写中）

**实际内容**：关于鱼（medaka）捕食行为中的眼球运动神经科学的经典神经生物学论文。与 PINN 完全无关。

## 教训

**OpenAlex 的 `search` 参数是关键词匹配，不是语义匹配**。当查询包含 "PINN" 时：

1. **如果返回 0 个结果**：可以高度确信是白空间（仍需交叉验证 PubMed）
2. **如果返回 1-2 个结果**：**必须**逐条阅读摘要，确认：
   - "PINN" 是否指 Physics-Informed Neural Network
   - 还是出现在其他上下文（如作者名缩写、机构缩写、不同领域的 PINN）
   - 实际方法论是什么
3. **如果返回 >3 个结果**：通常是有真实竞争，但仍需检查相关性

## 判定规则

| OpenAlex 返回数 | 判定 | 行动 |
|-----------------|------|------|
| 0 | 绝对白空间 | 继续 PubMed 验证 |
| 1 | **必须检查摘要** | 阅读摘要，确认是否真正使用 PINN/NeuralODE 方法 |
| 2 | **必须检查摘要** | 同上 |
| 3+ | 可能竞争 | 检查 top-3 标题和相关性 |

## 已确认的案例

| 查询 | OpenAlex 返回 | 实际相关性 | 结论 |
|------|--------------|-----------|------|
| saccade+kinematic+PINN | 1 | 经典神经科学（Current Biology） | 假阳性 |
| saccade+kinematic+ODE | 47 | 昆虫飞行器、梁振动 | 全部不相关 |
| saccade+velocity+profile+ODE | 64 | 运动学、脑成像、视觉神经元 | 全部不相关 |
| saccade+dynamics+NeuralODE | 0 | — | 白空间 |
| saccade+kinematic+NeuralODE | 0 | — | 白空间 |
| saccade+dynamics+PINN | 0 | — | 白空间 |
