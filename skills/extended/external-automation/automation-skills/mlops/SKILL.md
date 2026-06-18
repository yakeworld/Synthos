---

name: mlops
description: 机器学习运维 — ODE建模、实验管理、模型训练、推理部署、模型架构。
version: 1.0.0
triggers:
  - 需要执行mlops下的子技能
metadata:
  synthos:
    priority: P2
    atom_type: parent-skill
    description: "父级技能 — 机器学习运维 — ODE建模、实验管理、模型训练、推理部署、模型架构。"
    signature: 'mlops -> sub-skills: [biomechanical-regulation-ode, computational-ode-modeling, crispdm-helix-experiment]'
    related_skills: ["biomechanical-regulation-ode", "computational-ode-modeling", "crispdm-helix-experiment", "evaluation", "experiment-recipes"]

---

## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）

> 对应原则：P2（机械原子暴露输入输出规范）



# mlops

> 父级技能目录，包含 15 个子技能。
> 子技能通过Hermes技能加载机制自动发现，无需显式调用。

## 子技能

- `biomechanical-regulation-ode`
- `computational-ode-modeling`
- `crispdm-helix-experiment`
- `evaluation`
- `experiment-recipes`
- `huggingface-hub`
- `inference`
- `medical-image-centerline`
- `models`
- `remote-gpu-training`
- `research`
- `serving-llms-vllm`
- `sklearn-benchmark`
- `training`
- `training-pipeline-principles`

## 使用方式

直接调用子技能名称即可：

```
skill_view(name='biomechanical-regulation-ode')  # 加载第一个子技能
```

父级SKILL.md仅作为目录索引，实际执行由子技能完成。
