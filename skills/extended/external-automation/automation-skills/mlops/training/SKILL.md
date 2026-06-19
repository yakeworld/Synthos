---
name: training
description: "Directory index for training — mlops/training   模型训练与微调"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    atom_type: directory-index
    description: "Directory index for training"
    signature: "task_desc: str, context: dict -> result: dict"
    related_skills: []
    priority: P2

---
# mlops/training — 模型训练与微调

## IO_CONTRACT

- **input**: `dataset: list, model_config: dict, hyperparameters: dict` — 任务描述、参数配置
- **output**: `trained_model: dict (weights, metadata, metrics)` — 执行结果

> 对应原则：P2（机械原子暴露输入输出规范）

## 子技能

| 技能 | 描述 | 调用类别 |
|------|------|----------|
| axolotl | Axolotl: YAML LLM fine-tuning (LoRA, DPO, GRPO) | quick |
| trl-fine-tuning | TRL: SFT, DPO, PPO, GRPO, reward modeling for LLM RLHF | ultrabrain |
| unsloth | Unsloth: 2-5x faster LoRA/QLoRA fine-tuning, less VRAM | quick |

## 使用场景

- LoRA/QLoRA 微调：2-5倍加速，降低显存需求
- RLHF/DPO/GRPO：人类反馈强化学习、直接偏好优化
- SFT 监督微调：标准指令微调
- 奖励建模：训练奖励模型
