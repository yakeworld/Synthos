# mlops/training — 模型训练与微调

## IO_CONTRACT

- **input**:  — 任务类型、参数配置
- **output**:  — 执行结果

> 对应原则：P2（机械原子暴露输入输出规范）

> 对应原则：P2（机械原子暴露输入输出规范）

> mlops 子技能目录，提供 LLM 训练、RLHF/DPO/GRPO 训练、分布式训练框架和优化能力。

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
