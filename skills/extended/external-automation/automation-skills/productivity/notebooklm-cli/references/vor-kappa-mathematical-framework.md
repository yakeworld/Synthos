# VOR-Kappa角闭式标定法 — 数学框架

## 概述

利用前庭眼反射（VOR）生理机制，通过两组正交方向的3D眼动追踪数据，无需视轴信息、无需头动传感器，即可用闭式代数解推算三维Kappa角的大小和空间方位角。

## 坐标系与基础矢量

世界坐标系 $W$ 下：

- **光轴方向向量**（由瞳孔/虹膜特征追踪获取）：
  $$\mathbf O_W = \begin{bmatrix} 0 & 0 & 1 \end{bmatrix}^T$$

- **视轴方向向量**（由Kappa角 $\omega$ 和方位角 $\phi$ 定义）：
  $$\mathbf V_W = \begin{bmatrix} \sin\omega\cos\phi & \sin\omega\sin\phi & \cos\omega \end{bmatrix}^T$$

- **偏差矢量**（光轴与视轴之差）：
  $$\mathbf D_W = \mathbf O_W - \mathbf V_W = \begin{bmatrix} -\sin\omega\cos\phi & -\sin\omega\sin\phi & 1-\cos\omega \end{bmatrix}^T$$

## 罗德里格斯变换

当头动诱发VOR时，偏差矢量绕单位旋转轴 $\hat{\mathbf n}$ 旋转 $\theta$ 角：

$$\mathbf D_H = \mathbf D_W\cos\theta + (\hat{\mathbf n}\times\mathbf D_W)\sin\theta + \hat{\mathbf n}(\hat{\mathbf n}\cdot\mathbf D_W)(1-\cos\theta)$$

## 核心代数关系

观测角 $\gamma$（旋转前后偏差矢量的夹角）满足：

$$1-\cos\gamma = K(1-\cos\theta)$$

其中能量占比系数：

$$K = 1-\frac{(\hat{\mathbf n}\cdot\mathbf D_W)^2}{|\mathbf D_W|^2}$$

## 正交方向分离 → 闭式解

| 刺激方向 | 旋转轴 | 拟合系数 | 关系式 |
|:---------|:-------|:---------|:-------|
| 低头/抬头（Pitch） | 绕X轴 $\hat{\mathbf n}=[1,0,0]^T$ | $K_x$ | $1-K_x = \frac{1+\cos\omega}{2}\cos^2\phi$ |
| 左右摇头（Yaw） | 绕Y轴 $\hat{\mathbf n}=[0,1,0]^T$ | $K_y$ | $1-K_y = \frac{1+\cos\omega}{2}\sin^2\phi$ |

**两式相加**（消去 $\phi$）：

$$\boxed{\omega = \arccos\bigl(3 - 2(K_x + K_y)\bigr)}$$

**两式相除**（求方位角）：

$$\boxed{\phi = \operatorname{atan2}\left(\sqrt{1-K_y},\ \sqrt{1-K_x}\right)}$$

## 实现流程

```
1. 受试者注视固定目标
2. 自然头动：低头/抬头 → 3D眼动追踪 → 提取VOR慢相段
   → 瞳孔+虹膜特征追踪 → 三维虹膜平面重构 → 光轴方向
   → 四元数位姿估计 → 轴角分解得(n_x, θ_x, γ_x)
   → 线性回归拟合(1-cosγ)=K(1-cosθ) → K_x
3. 自然头动：左右摇头 → 同流程 → K_y
4. 代入闭式解 → ω = arccos(3-2(K_x+K_y))
```

## 核心创新点

| 对比项 | 传统方法 | 本方法 |
|:-------|:---------|:-------|
| 视轴依赖 | 需要（注视标定点） | **不需要** |
| 头动传感器 | 需要（IMU/转椅） | **不需要** |
| 标定流程 | 多点注视≥9个点 | **自然VOR头动** |
| 解算方式 | 非线性迭代优化 | **闭式解析解** |
| 适用人群 | 配合度高的成人 | 儿童、认知障碍均可 |

## 来源

NotebookLM项目 `571024b4-a9e6-489d-ba46-6`（基于iTrace的人群kappa角分布研究）
