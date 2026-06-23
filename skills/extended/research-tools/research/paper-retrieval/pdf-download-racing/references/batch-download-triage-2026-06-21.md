# 批量下载失败DOI重要性分级法 (2026-06-21)

## 场景

Pima-CRISP-DM 论文41个DOI中14篇下载失败。需区分哪些值得追、哪些可放弃。

## 分级标准

### 【核心】— 必须补
- PIMA数据集直接相关（缺失值/泄漏/预处理）
- 方法论基线或同类审计工作
- 论文核心论据或立场引用

### 【重要】— 尽量补
- 方法学参考（不平衡/质量评估/报告规范）
- 被审计论文案例
- 讨论部分对比引用（SHAP等）

### 【可弃】— 直接放弃
- 低影响力期刊/会议（Procedia, Telematika）
- 观点/评论文章（非技术）
- 数据集描述（非论文，在线可查）
- 无独特贡献的综述

## 2026-06-21 Pima实测

| 分级 | 数量 | 代表DOI |
|:-----|:----:|:---------|
| 核心 | 4 | Stiglic2012Missing, Mehta2024, Kapoor2023Leakage, Wen2024Leakage |
| 重要 | 6 | Wu2024BRFSS, Chang2024, Norgeot2020MI-CLAIM等 |
| 可弃 | 4 | Char/NEJM, Deepalakshmi/Procedia, UCI数据集, Akbar/Telematika |
