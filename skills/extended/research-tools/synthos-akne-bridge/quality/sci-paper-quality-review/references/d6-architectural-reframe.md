# D6 叙事重构: 架构级vs指导性防护（理论框架论文专用）

> 适用于无实验数据的理论/架构/教学/框架/范式类论文。
> 当论文的核心洞察是"我们提出了一个框架/架构/方法论"，且D6卡在0.65-0.75时使用。
> 实测（SCF论文，2026-05-25）：D6 0.74→0.78 (+0.04)

## 原始叙事（常见陷阱）

| 元素 | 原文 | 问题 |
|:-----|:-----|:-----|
| Gap | "没有框架解决X问题" | 同行知道X存在，这不算新发现 |
| Abstract | "我们提出了一个框架" | 每个论文都说自己是新框架 |
| 对比 | 列"+"/"-"标记 | 不够突出差异 |
| Contribution | "提供了架构性方案" | 同行可能觉得："不就是安全提示吗？" |
| Conclusion | "有前景的方法" | 缺乏差异化的收束 |

## 重构后叙事

### 核心公式

> 现有方案普遍依赖**指导性**方法（指南/警告/最佳实践），这些依赖用户依从性且效果有限。
> 我们的框架是**第一个**从**架构层面**嵌入安全机制的方案。
> 这不是"又一种方法"，而是从"你应该怎么做"到"系统自动确保你做对了"的范式转换。

---

## 五处修改点

### 1. Gap 第三条（Introduction）

| 原始 | 重构后 |
|:-----|:-------|
| "没有现有框架解决X问题" | "当前方法普遍使用指导性安全机制（指南、警告、最佳实践），依赖用户依从性。研究表明指导性方法不足以预防X。然而没有框架从**架构层面**嵌入安全机制——即内置于学习/工作流结构本身而非外部建议。" |

要点：用"universally"+"advisory"+"compliance"三词建立对比，然后用"however, no existing framework embeds at the architectural level"自然过渡。

### 2. Abstract Conclusion

| 原始 | 重构后 |
|:-----|:-------|
| "我们提出了一个框架" | "与依赖指导性指南的方案不同，本框架在架构层面嵌入安全机制" |
| "框架解决了X风险" | "提供了第一个在架构层面——而非指导层面——操作化Y的框架" |
| 结尾平淡 | "通过设计，而非依从性，解决Y风险" |

要点：在Abstract Results段末尾加一句"Unlike existing frameworks that rely on advisory guidelines, ours embeds safeguards architecturally"。在Abstract Conclusion用"first"+"architectural---rather than advisory---level"的破折号结构。

### 3. 对比表列名

| 原始列名 | 重构后列名 |
|:---------|:----------|
| "Metacognitive Safeguard" | "Safeguard Type" |
| "3 architectural" | "**Architectural**" |
| "Advisory"（如适用） | "Advisory" |

要点：列名从"What kind of safeguard"改为"What TYPE of safeguard"——引导读者关注类别差异而非内容细节。SCF标记为**bold**的"Architectural"，其他框架标记为"None"，有指导性方案的标记为"Advisory"。这使对比从隐式转为显式。

### 4. Discussion / Theoretical Contributions

| 原始 | 重构后 |
|:-----|:-------|
| "提供了架构性方案" | "提供了第一个在架构层面操作化Y的框架——内置于学习过程结构——而非依赖用户依从性的指导性指南" |
| 三条贡献平铺 | 第二条贡献用"First"+"architectural-level"+"embedded within structure"三连强调 |

要点：将第二条贡献从"提供了方案"升级为"提供了第一个框架"。添加破折号解释"architectural level"的具体含义。以"rather than relying on advisory guidelines that depend on user compliance"收尾。

### 5. Conclusion 首句

| 原始 | 重构后 |
|:-----|:-------|
| "提供了理论扎实的方案" | "引入了范式转换：从指导性依从到架构性嵌入" |
| "通过X分解+Y训练+Z安全" | "与现有框架依赖指南/警告不同，本框架将安全嵌入学习过程结构" |

要点：用一个分句定义范式转换：**from advisory compliance to architectural embedding**。然后用"whereas existing frameworks rely on X, ours embeds Y directly within..."对比句。最后用"addresses the central challenge: how to Y without sacrificing Z"收束。

---

## 收益预期

| 维度 | 预期提升 | 实测（SCF） |
|:-----|:--------:|:-----------:|
| D6 新颖性 | +0.03~0.06 | +0.04 |
| D1 科学贡献 | +0.01~0.02 | +0.01 |
| D5 清晰性 | +0.01~0.02 | +0.01 |
| **avg** | **+0.02~0.03** | **+0.008** |

注：avg提升小于D6提升，因为其他维度占比大。SCF论文的D3=0.50硬限制是avg提升有限的主因。

---

## 适用条件

- [ ] 论文类型：理论/架构/框架/教学/范式论文
- [ ] 核心主张：提出新架构/方法/框架
- [ ] 当前D6：0.65-0.75
- [ ] 最大竞争者：使用指导性/建议性安全机制
- [ ] 差异化清晰：你的方案是"架构性"而非"指导性"

## 不适用的论文类型

- 实验/数据驱动论文（应使用现有D6 reframe策略）
- 系统综述/荟萃分析（应使用系统综述D6策略）
- 纯理论论文不做框架对比（无对比表可改）
