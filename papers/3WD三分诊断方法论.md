---
tags: [paper, 3wd, methodology]
aliases: [3WD三分诊断方法论, Three-Way Triage]
---

# 3WD: Three-Way Triage 三分诊断方法论

> B+C 整合：定理 + 算法 + PIMA/WDBC 实证

## 基本信息

- **状态**: 🔄 进行中
- **类型**: 方法论论文
- **相关技能**: [[skills/hypothesis-generation/SKILL|HYP]], [[skills/argument-expression/SKILL|ARG]]
- **实验证据**: [[experiments/三文证漏实验|三文证漏实验]]
- **源 TeX**: `~/桌面/article_todo/` (待定位)

## 核心贡献

1. **三分诊断框架** — 将传统二分类扩展到三路决策（正/负/待定）
2. **定理证明** — 形式化三分边界条件
3. **实证验证** — PIMA/WDBC 数据集消融实验

## 关键结果

| 数据集 | 漏诊 F1 提升 | 说明 |
|:-------|:------------|:-----|
| PIMA | +6.71% | 漏类显著改善 |
| WDBC | -0.10% | 持平（无显著退化） |
| Heart | +14.17% | 大幅提升 |

## 相关文档

- [[paper-pipeline|论文管线流程]]
- [[experiments/_INDEX|🔬 实验记录]]

## 参照

- [[papers/_INDEX|← 论文目录]]
- [[_INDEX|← 返回根 MOC]]
