---



name: remote-gpu-training
description: "Directory index for remote-gpu-training: remote-gpu-training"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "model_config: dict, dataset: str, budget: float -> training_job: dict (gpu_config, schedule, estimated_cost, checkpoints)"
    atom_type: skill
    priority: P1
    related_skills: []
---




## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`


## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

> 对应原则：P2（机械原子暴露输入输出规范）



# Remote Gpu Training

远程GPU训练工作流 — SSH连接, env setup, scp脚本, tmux后台训练。

详细内容请加载对应 references/ 目录下的参考文件。
