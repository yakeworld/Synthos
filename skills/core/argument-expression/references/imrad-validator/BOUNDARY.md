# BOUNDARY.md — imrad-validator (IMRaD 结构验证)

> 对应原则：P2

## 边界陈述

本模块的唯一职责：验证论文各章节的结构是否符合 IMRaD 标准格式。

## 与其他原子的边界

| vs 原子 | 边界 |
|---------|------|
| 系统论文结构 | system-description-paper-structure.md 定义系统论文映射；本模块验证实际结构 |
| Pre-writing Gap | Pre-writing 在写作前规划；本模块在写作后验证 |
| CARS 模型 | CARS 分析 Introduction 逻辑；本模块检查 Introduction 结构完整性 |
| 论文管线 (paper-pipeline) | paper-pipeline 是编排层；本模块是其中的质量检查器 |
| Litreview 质量门 | 6 轴门评估文献综述质量；本模块评估整体论文结构 |

## 不包含

- 不做论文内容的质量评估 (这是 4D 门控的职责)
- 不做文献检索或综述
- 不做假设/论证分析
- 不做写作执行

## 输入/输出

- 输入：论文完整文本
- 输出：JSON 格式的章节结构检查 + 评分 + 不合格项
