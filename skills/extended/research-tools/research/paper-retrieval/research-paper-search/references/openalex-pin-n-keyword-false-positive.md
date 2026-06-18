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

## v91 扩展案例 — 2026-06-08

以下案例来自 Paper 84 (cochlear-vestibular-coupling-PINN) 及 v88-v90 扫描循环:

| 查询 | OpenAlex 返回 | 实际相关性 | 领域 |
|------|--------------|-----------|------|
| cochlear+vestibular+coupling+PINN | 2 | 神经纤维瘤病(NF1/NF2)综述、听神经细胞生物学 | 临床综述 |
| cochlear+vestibular+differential+equation+model | 3 | 浸没边界法、恒星核合成、微生物群 | 完全无关 |
| cochlear-vestibular+PDE | 3 | 颅脑MRI去毛皮、晕动症、儿童重度聋综述 | 临床综述 |
| inner+ear+coupling+dynamics | 3 | Meniere诊断标准、视网膜色素变性、粘附G蛋白偶联受体综述 | 临床综述 |
| meniere+disease+mathematical+model | 3 | 颅脑MRI去毛皮、晕动症、儿童重度聋综述 | 完全无关 |
| fixation+PINN | 71+ | 分子运输、植物学、等离子体建模、融合反应 | 完全无关 |
| smooth-pursuit+NeuralODE | 542 | 热力学整流、交通预测、Hirschsprung病 | 完全无关（0 smooth pursuit） |
| VOR+cancellation | 214 | 光学、恒星成像 | 完全无关 |
| binaural+vestibular+ODE | 16 | 脑成像、球面谐波、自旋转感知 | 0 ODE |
| vestibular+spinal | 5227 | 神经界面电子学 | 完全无关 |
| smooth-pursuit+PINN | 1 | hp-VPINNs变分方法 | 完全无关（数学，非眼动） |
| cochlear+vestibular | 1 | ribbon synapse生物物理 | 非PINN |
| VEMP+PINN | 1 | 奥地利会议摘要 | 0 relevant |
| vestibular+paroxysmia | 43 | 三叉神经临床+计算轴突建模 | 无PINN |
| concussion+oculomotor | 227 | 临床综述+硬件+临床 | 0 computational |
| ACL+CrossPin+PINN | 1 | ACL重建CrossPin手术 | 完全无关 |
| neurofibromatosis+review | 大量 | NF1/NF2/schwannomatosis综述 | 非PINN |
| MRI+skull+stripping | 多个 | 颅脑MRI算法 | 完全无关 |

**v91 总结**：OpenAlex PINN/ODE 假阳性已确认发生在至少8个不同领域：临床综述(NF1/NF2)、天文物理学(恒星核合成)、植物学/生物化学、医学成像(MRI/PET)、材料科学、重建手术、神经界面电子学、变分数学。每次返回0-3个结果都需要手动检查摘要。返回>3个时大概率是竞争领域。

**判定规则 v3**（更新 v91）：

| OpenAlex 返回数 | 判定 | 行动 |
|-----------------|------|------|
| 0 | 绝对白空间 | 继续 PubMed 交叉验证 |
| 1 | **必须检查摘要** | 阅读摘要，确认是否真正使用 PINN/NeuralODE 方法。检查：是否出现在不同领域上下文（天文、植物、手术、材料） |
| 2-3 | **必须检查摘要** | 同上。v91确认：1-3个结果95%+是假阳性，必须阅读摘要 |
| 4-10 | **检查top-3标题** | v91确认：此范围内仍可能全是假阳性，需逐条检查 |
| 10+ | 可能竞争 | 但仍需检查相关性，v91中fixation+PINN=85全是假阳性 |
