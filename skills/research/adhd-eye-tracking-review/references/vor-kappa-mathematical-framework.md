# VOR-Kappa 角标定：数学框架参考

## 1. 核心概念

**Kappa角（$\omega$）**：光轴与视轴之间的空间角。
- 光轴（Optical Axis）：通过瞳孔中心、垂直于虹膜平面的直线，可由3D眼动追踪测量
- 视轴（Visual Axis）：角膜中心与黄斑（中央凹）的连线，不可直接观测

**VOR（前庭眼反射）**：头动时眼球的补偿性旋转反射，增益≈1，目的是维持固视。

## 2. 坐标系定义（世界坐标系 $W$）

光轴方向向量：
$$\mathbf O_W = [0, 0, 1]^T$$

视轴方向向量（由Kappa角 $\omega$ 和方位角 $\phi$ 参数化）：
$$\mathbf V_W = [\sin\omega\cos\phi,\ \sin\omega\sin\phi,\ \cos\omega]^T$$

偏差矢量：
$$\mathbf D_W = \mathbf O_W - \mathbf V_W = [-\sin\omega\cos\phi,\ -\sin\omega\sin\phi,\ 1-\cos\omega]^T$$

## 3. 罗德里格斯旋转变换

当头动诱发VOR时，眼球绕旋转轴 $\hat{\mathbf n}$ 旋转 $\theta$ 角。偏差矢量变换到头部坐标系 $H$：

$$\mathbf D_H = R(\hat{\mathbf n},-\theta)\mathbf D_W$$

由Rodrigues公式展开：
$$\mathbf D_H = \mathbf D_W\cos\theta + (\hat{\mathbf n}\times\mathbf D_W)\sin\theta + \hat{\mathbf n}(\hat{\mathbf n}\cdot\mathbf D_W)(1-\cos\theta)$$

## 4. 观测角与旋转角的关系

观测角 $\gamma$ 为偏差矢量旋转前后的夹角：

$$\cos\gamma = \frac{\mathbf D_W\cdot\mathbf D_H}{|\mathbf D_W||\mathbf D_H|}$$

利用旋转不改变向量长度 $|\mathbf D_H|=|\mathbf D_W|$，以及正交特性 $\mathbf D_W\cdot(\hat{\mathbf n}\times\mathbf D_W)=0$：

$$1-\cos\gamma = \left(1-\frac{(\hat{\mathbf n}\cdot\mathbf D_W)^2}{|\mathbf D_W|^2}\right)(1-\cos\theta)$$

定义能量占比系数：
$$K = 1-\frac{(\hat{\mathbf n}\cdot\mathbf D_W)^2}{|\mathbf D_W|^2}$$

得到核心关系式：
$$\boxed{1-\cos\gamma = K(1-\cos\theta)}$$

## 5. 正交方向分离

**绕X轴旋转**（Pitch，低头/抬头，$\hat{\mathbf n}=[1,0,0]^T$）：
$$1-K_x = \frac{1+\cos\omega}{2}\cos^2\phi$$

**绕Y轴旋转**（Yaw，左右摇头，$\hat{\mathbf n}=[0,1,0]^T$）：
$$1-K_y = \frac{1+\cos\omega}{2}\sin^2\phi$$

## 6. 闭式解

**两式相加**消去方位角 $\phi$：
$$\boxed{\omega = \arccos(3 - 2(K_x + K_y))}$$

**两式相除**得方位角：
$$\boxed{\phi = \operatorname{atan2}\left(\sqrt{1-K_y},\ \sqrt{1-K_x}\right)}$$

## 7. 实现要点

### K_x, K_y 的获取
1. 从3D眼动追踪数据提取VOR慢相段
2. 对每帧数据：四元数 $\to$ 轴角分解 $(\hat{\mathbf n}, \theta, \gamma)$
3. 按 $\hat{\mathbf n}$ 方向分类：
   - $\hat{\mathbf n} \approx [1,0,0]^T$ → Pitch数据集
   - $\hat{\mathbf n} \approx [0,1,0]^T$ → Yaw数据集
4. 过原点线性回归：$x=1-\cos\theta$, $y=1-\cos\gamma$, 斜率 = $K$

### 验证建议
- 仿真验证：用已知 $\omega,\phi$ 生成模拟数据，验证闭式解复现精度
- 实测验证：与iTrace测量值对比（Pearson相关性>0.90为目标）
- 鲁棒性测试：不同头动幅度（$\theta=5^\circ, 10^\circ, 20^\circ, 30^\circ$）下Kappa角估计的稳定性

## 8. 与现有方法的对比优势

| 方法 | 需视轴 | 需头动传感器 | 需标定点 | 解算方式 | 头动限制 |
|:-----|:------:|:-----------:|:--------:|:---------|:---------|
| 传统多点标定法 | ✅ | ❌ | ≥9个 | 非线性优化 | 头托固定 |
| iTrace直接测量 | ✅ | ❌ | 0 | 角膜地形图 | 头托固定 |
| 双目约束法 | ✅ | ❌ | 1-2个 | 双目视差 | 自由 |
| 回归法 | ❌ | ❌ | 训练集 | 数据驱动 | 自由 |
| **本方法(VOR闭式解)** | **❌** | **❌** | **0** | **闭式解析解** | **自由** |

## 9. 关键研究笔记

### 固视本质
> "VOR的本质也是固视" — 用户纠正（2026-05-21）
> 固视是统一生理过程，VOR是其头动条件下的执行机制。因此动态固视（VOR下的固视）与静态固视的信息格式相同。

### 不需要头动数据
> "不需要头动数据。三维眼动可测旋转轴" — 用户纠正（2026-05-21）
> 3D眼动追踪系统可以直接测量眼球的完整三维旋转（旋转轴 + 旋转角），利用VOR增益≈1，眼球旋转轴等价于头动旋转轴。

### 不需要视轴信息
> "我们通过2组X，Y方向的Vor就可以推算kappa,不需要知道视轴" — 用户陈述（2026-05-21）
> 两组正交VOR（Pitch + Yaw）提供两个独立几何约束，可直接闭式解算Kappa角。
