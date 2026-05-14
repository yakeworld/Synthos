# Literature Review 六轴质量门控

**来源**: PaperOrchestra (Song et al., 2026, arXiv:2604.05018, App. F.3)
**吸收类型**: P1 — 论证质量增强（注入 argument-expression 原子）
**原理**: 在论证生成后运行 6 轴自检评分，确保输出的 Introduction/Related Work 章节符合学术出版标准

---

## 动机

argument-expression 原子原有的质量要求（§7）定义了**原则性约束**（逻辑性、完整性、可读性、规范性），但没有**可量化的质量门控**。6 轴评分框架填补了这个缺口，使得输出可以被自动检查而非仅靠人类判断。

## 六轴评分体系（各 0-100）

| 轴 | 名称 | 评估内容 | 硬上限 |
|:--:|:----|:---------|:------|
| 1 | **Coverage & Completeness** | 主要相关领域的宽度 + 基础与前沿工作的平衡 | — |
| 2 | **Relevance & Focus** | 引用与论点的对齐度 + 无离题 | — |
| 3 | **Critical Analysis & Synthesis** | 主题组织和比较 + 权衡/局限/空白讨论 | ≤ 60 if descriptive |
| 4 | **Positioning & Novelty** | 文献驱动的空白陈述 + 与最近工作的区分度 | ≤ 60 if vague |
| 5 | **Organization & Writing** | 逻辑结构、流、学术语言清晰度 | — |
| 6 | **Citation Practices & Rigor** | 关键主张是否有引用支撑 + 来源可信度 | ≤ 60 if sparse |

## 反膨胀规则（Anti-Inflation Rules）

```
默认期望: 总分 45-70
> 85: 六轴全需强证据
> 90: 接近综述级(near-survey-level) — 极罕见
任何一轴 < 50: 总分通常 ≤ 75
仅描述性综述(逐篇摘要式): 轴3 ≤ 60
无对比的创新声明: 轴4 ≤ 60
稀疏或不一致引用: 轴6 ≤ 60
高引用量 ≠ 高质量（需整合和相关性）
```

## 评分量表

| 区间 | 描述 |
|:----:|:----:|
| 0-20 | Unacceptable |
| 21-40 | Weak |
| 41-55 | Adequate but flawed |
| 56-70 | Solid |
| 71-85 | Strong |
| 86-92 | Excellent |
| 93-100 | Exceptional (极罕见) |

## 加权总分公式

```
总分 = Coverage(20%) × 0.20
     + Relevance(15%) × 0.15
     + Critical Analysis(25%) × 0.25
     + Positioning(25%) × 0.25
     + Organization(10%) × 0.10
     + Citation Rigor(5%) × 0.05
     + Penalties(0到-15分)
     + Positive Adjustment(罕见, +3到+7)
```

### 常见扣分项

| 违规 | 扣分 |
|:----|:----:|
| 无对比地夸创新 | -5 ~ -15 |
| 缺失近期关键工作 | -5 ~ -15 |
| 主要是描述性综述 | -5 ~ -10 |
| 空白陈述薄弱或通用 | -5 ~ -10 |
| 引用倾倒或一致性问题 | -5 ~ -10 |

## 在 argument-expression 中的使用

**时机**: Section 3（过程）中的 Step 7（输出）之前，加第 6.5 步——质量自检。

**自检 Prompt 模板**：

> 你是一名严格的学术评审专家。评估以下论文章节的文献综述质量。
> 仅评估 Introduction 和 Related Work 部分（或等效章节）。
> 使用 6 轴评分体系（Coverage, Relevance, Critical Analysis, Positioning, Organization, Citation Rigor），每轴 0-100。
> 遵守反膨胀规则。返回 JSON 输出。

**门控阈值**:
- 总分 ≥ 55 → 直接输出 ✅
- 总分 40-54 → 输出 + 标注改进点 ⚠️
- 总分 < 40 → 标记为"需要重写"，输出改进建议 🔴

---

**变更**: 2026-05-14 — 从 PaperOrchestra/PaperWritingBench 吸收，v1.0
