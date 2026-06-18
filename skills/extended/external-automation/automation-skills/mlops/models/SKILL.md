# mlops/models — 模型架构

## IO_CONTRACT

- **input**:  — 任务类型、参数配置
- **output**:  — 执行结果

> 对应原则：P2（机械原子暴露输入输出规范）

> mlops 子技能目录，提供特定模型架构的操作能力。

## 子技能

| 技能 | 描述 | 调用类别 |
|------|------|----------|
| audiocraft | AudioCraft: MusicGen text-to-music, AudioGen text-to-sound | quick |
| segment-anything-model | SAM: zero-shot image segmentation via points, boxes, masks | quick |

## 使用场景

- 音频生成：MusicGen 文本到音乐、AudioGen 文本到声音
- 图像分割：Segment Anything Model (SAM) 零样本分割
