# Gap-Hypothesis Congruence Protocol（空假一致性协议）

> 在双质检（Layer B）阶段，对每篇关键参考文献回溯它填了什么gap/提了什么假设 → 对比我方论文的gap/hypothesis → 验证定位正确性。
>
> **核心原则**：研究空白不是起点专利。起点找出空白，终点验空白是否还站得住。

## 为什么要双向验证

```
文献阅读阶段：空白识别（找方向）
        ↓
论文写作阶段：空白-假设-论证（建逻辑）
        ↓
论文完成阶段：空假一致性检查（验定位） ← 新增的G5d
```

可能的漂移：
- **gap膨胀**：少量空白写成了领域空白
- **gap漂移**：引言的gap与结论的贡献不一致
- **假设竞争**：已有论文提出了类似假设但未被讨论
- **gap已填**：写作期间有新文献填补了你的空白

## 执行流程

### Step 1: 提取我方论文的Gap-Hypothesis声明

摘录：
- **Gap声明句**（通常Introduction末段）
- **Hypothesis声明句**（Introduction末段/Methods开头）
- **Contribution声明句**（Abstract/Conclusion）

### Step 2: 对关键参考文献逐篇提取

选取5-15篇核心引用文献。对每篇：

| 字段 | 内容 |
|:-----|:-----|
| Bibkey | — |
| 他们识别的gap | 该文献声称填补了什么空白 |
| 他们的核心发现 | 主要结果/结论 |
| 他们的假设 | 测试了什么假设 |
| 与我方关系 | 支持/对立/无关/部分重叠 |

### Step 3: 构建Congruence矩阵

```
| 文献 | 其gap | 其发现 | 我方gap相对于它 | 定位正确性 |
|:-----|:------|:-------|:---------------|:-----------|
| Smith2021 | 缺SCC曲率数据 | 首次报告曲率 | 我们延伸至膜性SCC | ✅ 正确延伸 |
| Patel2022 | 已做膜重建 | 报告了偏差 | 我方贡献"首次"失效 | ❌ gap已填 |
```

### Step 4: 判定与行动

| 判定 | 行动 |
|:-----|:-----|
| ✅ 所有文献定位正确 | 通过，进入Layer B |
| 🟡 1-2篇贡献声明略强 | 降级措辞 |
| 🔴 gap已填/contribution冲突 | 根本性重新定位 |

### 措辞分级

| 证据强度 | 允许措辞 | 禁止措辞 |
|:---------|:---------|:---------|
| 全领域空白 | "first comprehensive analysis" | — |
| 有相关研究但维度不同 | "has not been examined in context of Z" | "first study" |
| 延伸已有工作 | "building on methodology of X" | "no prior work" |
| 独立验证 | "independently validate using different approach" | "first demonstration" |
