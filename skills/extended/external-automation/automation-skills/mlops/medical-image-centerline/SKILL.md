---



name: medical-image-centerline
description: "Directory index for medical-image-centerline: medical-image-centerline"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "image_data: str, vessel_type: str -> centerline: dict (points, confidence, quality_metrics)"
    atom_type: skill
    priority: P1
    related_skills: []
---




## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）



# Medical Image Centerline

从3D分割标签提取中心线 — 图论环基法/中位切+图直径法。

详细内容请加载对应 references/ 目录下的参考文件。
