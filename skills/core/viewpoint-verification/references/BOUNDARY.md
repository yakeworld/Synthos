# BOUNDARY.md — viewpoint-verification

> 对应原则：P2

## 边界陈述

本原子的唯一职责：对假设和论证进行多角度验证（反方观点、证伪条件、鲁棒性）。不做假设生成、不做论证表达。

## 与其他原子的边界

| vs 原子 | 边界 |
|---------|------|
| hypothesis-generation (4) | 原子4正向构建；本原子反向证伪 |
| argument-expression (5) | 原子5构建论证；本原子拆解论证 |
| association-discovery (3) | 原子3发现关联；本原子评估关联的可靠性 |
| **pwbench Citation F1** | 引用质量验证(P0/P1)是"论证证据充分性"的子维度，属于验证范畴。不改变"反向证伪"核心定义。与ARG的6轴引用严谨性自检形成互补（ARG=生产自检，VER=独立验证） |
