---



name: gradient-alignment-loss
description: "Skill: gradient-alignment-loss"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "model_arch: str, training_data: dict -> loss_spec: dict (formula, bounds, convergence_criteria)"
    atom_type: skill
    priority: P1
    related_skills: []
---




## IO_CONTRACT

- **input**: `model_arch: str, training_data: str` — 用户请求描述、上下文信息
- **output**: `loss_spec: dict — 梯度对齐损失`


> 对应原则：P2（机械原子暴露输入输出规范）

# Gradient Alignment Loss

梯度对齐损失(GAL) — 边界感知辅助损失用于医学图像分割。
