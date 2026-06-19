---



name: scc-bppv-kinematics
description: "Skill: scc-bppv-kinematics"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "clinical_data: str -> kinematics_report: dict (joint_angles, forces, stability_index)"
    atom_type: skill
    priority: P1
    related_skills: []
---




## IO_CONTRACT

- **input**: `clinical_data: str` — 用户请求描述、上下文信息
- **output**: `kinematics_report: dict — 运动学报告`


> 对应原则：P2（机械原子暴露输入输出规范）

# Scc Bppv Kinematics

SCC半规管形态学分析与BPPV复位运动学 — 中心线加载→平面分析→螺旋拟合→Epley仿真。

## 新增模块

### 椭圆反求3D圆法向量

SCC为空间圆，CT投影为椭圆。从椭圆参数反推SCC空间法向量，见 `references/ellipse-to-circle-normal-derivation.md`。