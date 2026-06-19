# BOUNDARY.md — toulmin-argument (Toulmin 论证模型)

> 对应原则：P2
> 依赖：Toulmin (1958)

## 边界陈述

本模块的唯一职责：分析论文中单个论点/主张的 Toulmin 结构完整性（Claim-Data-Warrant-Backing-Qualifier-Reservation）。

## 与其他原子的边界

| vs 原子 | 边界 |
|---------|------|
| CARS 模型 | CARS 分析 Introduction 整体结构；Toulmin 分析论点内部结构 |
| Gap Type 分类 | Gap Type 分类空白类型；Toulmin 验证论证结构完整性 |
| 引用功能分类 | 引用功能标注每篇文献的角色；Toulmin 分析论证逻辑链 |
| 4D 质量门控 | 4D 质量门做整体评分；Toulmin 是"解决方案"维度的输入源 |
| 假设生成原子 | 假设生成产生 Hypothesis；Toulmin 验证假设的论证结构 |
| 观点验证原子 | 观点验证做全面评估；Toulmin 是其中"论证质量"子项 |

## 不包含

- 不做假设/研究问题的生成
- 不做文献检索或综述
- 不做论文整体质量评分
- 不做引文数量/引用质量评估

## 输入/输出

- 输入：论文的论点/主张文本（从 ARG 原子或论文草稿提取）
- 输出：JSON 格式的 Toulmin 结构分析 + 完整度/有效性评分
