---
name: ellipse-3d-anatomy-constrained
category: mlops
description: 用户特异性推导：椭圆→3D圆通过解剖约束（R=2r, d=√3r）消除方位角模糊。覆盖法向量公式、光轴平面、Rodrigues旋转、多帧眼球中心求解。源自AKNE眼动研究笔记。
signature: "ellipse-3d-anatomy-constrained -> processed_result"
---
version: 1.0.0

# ellipse-3d-anatomy-constrained: 椭圆→3D圆解剖约束法

## 边界

将二维椭圆参数反推为三维空间圆几何参数，通过解剖约束消除方位角模糊。

核心创新：用户方法通过 R_eyeball = 2*R_iris、d = √3*R_iris 将自由度从2压缩到0。

输入：椭圆参数 + 旋转角 + （可选）多帧
输出：3D法向量（光轴）、虹膜中心3D、眼球中心、旋转矩阵

## 核心推导

### 法向量
n = [sin(alpha)*sin(beta), -sin(alpha)*cos(beta), cos(alpha)]
cos(alpha) = b/a, beta = 椭圆旋转角。

### 光轴投影直线
cos(beta)*(x - x1) + sin(beta)*(y - y1) = 0

### 多帧确定眼球中心
至少两帧椭圆 → 光轴直线交点 = 眼球中心。

### 解剖约束
R_eyeball = 2*R_iris, d = √3*R_iris
z1 = sqrt(3*R_iris^2 - (x1-x0)^2 - (y1-y0)^2)

### Rodrigues 旋转
M = I + [v]_x + [v]_x^2 / (1 + O·O')

## Pitfalls
1. 单帧无法确定眼球中心
2. z1 为虚数时：椭圆参数与解剖约束矛盾
3. 用户设定 Center_eye 在 XY 平面 (z=0)
4. 多帧需迭代：先估计 → 计算 → 收敛

## Related
- ellipse-to-3d-circle — 通用椭圆→3D圆方法（正交投影基础）
- eye-tracking-platform — K230嵌入式眼动平台

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。