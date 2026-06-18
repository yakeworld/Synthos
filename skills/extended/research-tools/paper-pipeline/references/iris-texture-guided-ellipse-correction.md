# 虹膜归一化双向纹理校正

> 2026-05-26 会话期间产生的洞察。用户提出：矩形域中的水平位移可通过逆向映射作用于椭圆矫正。

## 核心问题

论文《A Precise 3D Geometric Transform Method for Iris Normalization》提出椭圆→矩形的直接变换。用户问：这个逆映射（矩形→椭圆）是否成立？能否通过纹理匹配检测到的矩形水平位移来校正椭圆参数？

## 数学模型

### 正向变换链

椭圆参数方程（Jin et al. 2020）：

$$G(t) = \begin{bmatrix} A\cos t\cos\theta - B\sin t\sin\theta \\ A\cos t\sin\theta + B\sin t\cos\theta \end{bmatrix}$$

其中：
- $t$ = 椭圆边界上的角向参数（0→2π），对应矩形水平轴
- $\theta$ = 椭圆的旋转角
- $A, B$ = 半长轴、半短轴

正向变换：椭圆(image) → 逆透视投影(3D旋转) → 正圆(frontal) → 圆柱展开 → 矩形

### 反向变换

矩形 → 圆柱卷绕 → 正圆 → 透视投影 → 椭圆

### 两种情况的区分

**情况A — Cyclotorsion（真实眼球旋转）**：
- 虹膜绕光轴整体旋转 → 矩形中是纯水平平移
- $\Delta x = R_{iris} \cdot \Delta\psi$，其中 $\Delta\psi$ 为旋转角
- 逆映射：$\Delta\psi = \Delta x / R_{iris}$ → 椭圆旋转角修正 $\Delta\theta = \Delta\psi$（正视角下）
- **成立**，适合连续眼动追踪中的 cyclotorsion 检测

**情况B — 椭圆拟合误差校正**：
- 若椭圆参数 $(\theta, A, B, x_c, y_c)$ 有误差
- 归一化后的纹理偏移不是纯平移，而是随 $t$ 变化的非线性扭曲
- 简单关系 $\Delta\theta = \Delta x / R_{iris}$ **不成立**
- 正确方法：完整5参数雅可比迭代精调

### 形式化验证要点

1. 圆柱展开将角向参数 $t$ 映射到矩形水平轴 $u = R \cdot t$
2. 水平位移 $\Delta u$ 直接对应 $t$ 的偏移 $\Delta t = \Delta u / R$
3. 但 $t$ 是椭圆参数方程中的角向参数，不是椭圆的旋转角 $\theta$
4. $\theta$ 的变化会改变参数方程的整体结构（$\cos t\cos\theta - \sin t\sin\theta$），而不仅仅是 $t$ 的平移
5. 因此：$\Delta u \rightarrow \Delta t$，而非 $\Delta u \rightarrow \Delta\theta$

## 下一步

- [ ] 完整的形式化推导（含投影几何的雅可比矩阵）
- [ ] 迭代精调算法的伪代码
- [ ] 在合成数据上验证收敛性

## 参考

- Jin et al. (2020) eq.4: ellipse parametric equation
- Paper: A Precise 3D Geometric Transform Method for Iris Normalization
- Session: 2026-05-26 用户提出逆向映射问题
