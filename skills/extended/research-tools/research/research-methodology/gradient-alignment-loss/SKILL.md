---

## IO_CONTRACT

- **input**: `model_arch: str, training_data: str` — 用户请求描述、上下文信息
- **output**: `loss_spec: dict — 梯度对齐损失`

> 对应原则：P2（机械原子暴露输入输出规范）

> 对应原则：P2（机械原子暴露输入输出规范）
name: gradient-alignment-loss
related_skills: ["knowledge-extraction", "hypothesis-generation"]
description: >-
version: 1.0.0
  梯度对齐损失(GAL) — 边界感知辅助损失用于医学图像分割。
metadata:
  synthos:
    version: 1.0.0
    author: Synthos

---


# Gradient Alignment Loss

梯度对齐损失(GAL) — 边界感知辅助损失用于医学图像分割。
