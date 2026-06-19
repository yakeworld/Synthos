---
name: models
description: "Directory index for models — mlops/models   模型架构"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    atom_type: directory-index
    description: "Directory index for models"
    signature: "task_desc: str, context: dict -> result: dict"
    related_skills: []
    priority: P2

---
# mlops/models — 模型架构

## IO_CONTRACT

- **input**: `model_type: str, task: str, domain: str` — 任务描述、参数配置
- **output**: `model_spec: dict (architecture, hyperparameters, training_config)` — 执行结果

> 对应原则：P2（机械原子暴露输入输出规范）

## 子技能

| 技能 | 描述 | 调用类别 |
|------|------|----------|
| audiocraft | AudioCraft: MusicGen text-to-music, AudioGen text-to-sound | quick |
| segment-anything-model | SAM: zero-shot image segmentation via points, boxes, masks | quick |

## 使用场景

- 音频生成：MusicGen 文本到音乐、AudioGen 文本到声音
- 图像分割：Segment Anything Model (SAM) 零样本分割
