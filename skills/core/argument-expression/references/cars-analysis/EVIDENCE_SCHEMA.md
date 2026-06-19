# EVIDENCE_SCHEMA.md — CARS Model Analysis

> 对应原则：P0（证据可溯性）
> 理论来源：Swales (1990, 2004) — Create a Research Space model

## CARS 模型三 Move 的量化分析标准

| Move | 目标 | 必须包含的元素 | 缺失即失败 |
|------|------|----------------|------------|
| Move 1 | Establish a territory | (1) 领域重要性声明 (2) 领域研究现状综述 (3) 引用 3+ 篇关键论文 | 缺少关键论文引用 |
| Move 2 | Establish a niche | (1) 指出空白 (2) 空白类型明确 (3) 空白可填补 (4) 使用 "However/Although/Yet/No study has" 等标记 | 无转折词，无明确 gap |
| Move 3 | Occupy the niche | (1) 提出本文目标 (2) 与 gap 对应 (3) 方法简述 | 无明确目标声明 |

## 评分标准

| 维度 | 权重 | 满分 | 说明 |
|------|------|------|------|
| Move 1 完整度 | 30% | 30 | 关键论文引用质量 + 领域范围定义 |
| Move 2 完整性 | 40% | 40 | 空白类型（方法/理论/实证/应用）+ 可填补性 |
| Move 3 明确性 | 30% | 30 | 目标是否直接回应 Move 2 的 gap |

总分 ≥ 70：合格
总分 50-69：需改进
总分 < 50：需重写

## 证据链节点

```json
{"source_type": "cars_analysis", "source_ref": "introduction_text", "note": "Move1_score=24/30, Move2_score=32/40, Move3_score=27/30"}
```
