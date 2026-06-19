# BOUNDARY.md — spice-framework (SPICE/SPIRIT 研究问题框架)

> 对应原则：P2

## 边界陈述

本模块的唯一职责：将研究空白 (Gap) 转化为结构化的研究问题 (Research Question)，使用 SPICE/SPIRIT 框架。

## 与其他原子的边界

| vs 原子 | 边界 |
|---------|------|
| association-discovery (3) | 原子3发现空白；SPICE 将空白转化为研究问题 |
| hypothesis-generation (4) | SPICE 产生研究问题；原子4基于研究问题生成假设 |
| gap-type-classifier | GAP-TYPE 分类空白类型；SPICE 填充空白为具体研究问题 |
| CARS Model | CARS Move2 定位空白；SPICE 将空白形式化为研究问题 |

## 不包含

- 不做空白的发现 (这是 association-discovery 的职责)
- 不做假设的生成 (这是 hypothesis-generation 的职责)
- 不做文献检索或综述
- 不做实验设计

## 输入/输出

- 输入：研究空白 (来自 association-discovery 或 gap-type-classifier)
- 输出：JSON 格式的结构化研究问题 (SPICE/SPIRIT 模板)
