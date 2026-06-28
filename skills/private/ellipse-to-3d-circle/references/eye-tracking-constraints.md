# 眼动追踪中的椭圆→3D圆约束

## 场景：瞳孔椭圆 → 角膜面法向量

### 解剖约束

1. **瞳孔是角膜/巩膜交界处的圆**，位于眼球表面
2. **眼球近似球体**，半径约 12mm（个体差异 ±2mm）
3. **瞳孔中心在眼球球面上**，即 `||pupil_center - sphere_center|| = R_eyeball`

### 已知参数（典型眼动仪）

| 参数 | 值 | 来源 |
|------|-----|------|
| 眼球半径 | 12mm | 解剖学先验 |
| 相机焦距 | 1000-5000px | 标定 |
| 瞳孔半径 | 2-5mm (约 50-200px) | 实时检测 |
| 帧率 | 60-500Hz | 设备规格 |

### 求解流程

```
输入: 瞳孔椭圆 (u0, v0, a_px, b_px, theta_deg) + 相机内参 K
    ↓
Step 1: alpha = arccos(b/a)        → 法线倾斜角
    ↓
Step 2: phi from ellipse major axis → 方位角（法线在图像平面的投影）
    ↓
Step 3: n = (sinα·cosφ, sinα·sinφ, cosα)  → 法向量
    ↓
Step 4: 瞳孔中心像素→物理坐标 P_px → P_mm（用相机标定）
    ↓
Step 5: 深度求解 — 瞳孔中心在眼球球面上
    ||P_mm - C_sphere|| = R_eyeball
    其中 C_sphere 是眼球球心先验（通常近似为相机光心前方某处）
    ↓
输出: 角膜面法向量 n（3D），可用于 VOR 分析、眼震分类等
```

### 关键公式

**法向量**（在相机坐标系下）：
$$\mathbf{n}_{cam} = \begin{pmatrix} \sin\alpha\cos\phi \\ \sin\alpha\sin\phi \\ \cos\alpha \end{pmatrix}$$

**眼球球面约束**：
$$\|\mathbf{p}_{pupil} - \mathbf{c}_{sphere}\|^2 = R_{eyeball}^2$$

其中 $\mathbf{p}_{pupil}$ 是瞳孔中心3D坐标，沿法向量方向：
$$\mathbf{p}_{pupil} = \mathbf{p}_{image} \cdot z_{depth} + \text{offset}$$

**VOR相关**：法向量的时间变化率 $\dot{\mathbf{n}}(t)$ 与角速度 $\boldsymbol{\omega}$ 的关系：
$$\dot{\mathbf{n}} = \boldsymbol{\omega} \times \mathbf{n}$$

### 典型精度

| 参数 | 精度 | 说明 |
|------|------|------|
| 法向量角度误差 | 0.5°-2° | 取决于相机标定精度 |
| 瞳孔中心位置 | 0.1-0.5mm | 取决于图像分辨率 |
| 倾斜角 alpha | 1°-3° | 受噪声影响较大 |
| 方位角 phi | 0.5°-2° | 椭圆长轴拟合精度决定 |

### 文献来源

- 你的论文库中：`3d-iris-normalization`, `3d-pupil-localization`, `dual-ellipse-pupil-localization`
- AKNE节点：`sources/眼动研究/椭圆和圆.md`, `sources/眼动研究/瞳孔双椭圆拟合：数学原理和仿真.md`
