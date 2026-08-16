---
name: 3d-curve-fitting-figures
description: 3d-curve-fitting-figures
version: 1.0.0
category: creative
signature: '3d-curve-fitting-figures -> creative: 3D曲线拟合图的生成规范：从点云到拟合曲线到出版级Figure。
  覆盖拟合重建陷阱、多标本复合布局、分段数据合并、argsort路径错乱。'
license: MIT
author: Synthos 配合figure-generation skill使用。
allowed-tools:
- terminal
- read_file
- write_file
- search_files
metadata:
  synthos:
    author: Synthos
    signature: 'input: dict -> output: dict'
    related_skills:
    - figure-generation
    version: 1.2.0
    tags:
    - figure-generation
    - 3d-fitting
    - curve-fitting
    - scientific-figures
---


## Operational Steps
1. 确认输入参数完整
2. 执行核心操作（参考本目录下的 scripts/ 或 references/）
3. 验证输出符合契约
4. 保存结果并报告

## Pitfalls
- 
- 

## Verification
- 
- 
- 
- 
1. 
2. 
3. 

## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）

# 3D曲线拟合图

## 拟合重建陷阱：中心偏移

### 问题

从投影2D坐标拟合3D曲线(如对数螺旋)，重建回3D时**必须包含中心偏移cx,cy**:

```python
# 错误 — 曲线被锚定在数据质心(缺cx,cy)
cf = centroid + r*cos(theta+rot)*u + r*sin(theta+rot)*v + z*normal

# 正确 — 包含螺旋中心偏移
cf = centroid + (cx + r*cos(theta+rot))*u + (cy + r*sin(theta+rot))*v + z*normal
```

### 症状

- RMSE数值合理(<0.2mm)
- 但拟合曲线与数据点在视觉上明显错位
- **复合图与单标本图中同一曲线位置不同**（bug只存在于复合图脚本）

### 根因

2D投影坐标 `(pts-centroid)@u,v` 以数据质心为原点，但螺旋中心 `(cx,cy)` 在2D平面中偏离质心。重建时若直接用 `centroid + r*cos*u` 而非 `centroid + (cx+r*cos)*u`，曲线被错误锚定在质心。

### 代码对比(调试时快速定位)

对比正确 vs 错误版本的重建关键行：

| 脚本 | 重建行 | 状态 |
|: