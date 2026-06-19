---


name: remote-gpu-training
related_skills: []
description: >-
version: 1.0.0
license: MIT
author: Synthos
  远程GPU训练工作流 — SSH连接, env setup, scp脚本, tmux后台训练。
metadata:
  synthos:
    version: 1.0.0
    author: Synthos



---



## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）



# Remote Gpu Training

远程GPU训练工作流 — SSH连接, env setup, scp脚本, tmux后台训练。

详细内容请加载对应 references/ 目录下的参考文件。
