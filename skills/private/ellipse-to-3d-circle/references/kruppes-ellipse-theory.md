# Kruppes 方程与椭圆对偶性 — 理论速查

## 经典问题设定

已知相机内参矩阵 $K$ 和图像中的椭圆矩阵 $E_i$（3×3 对称矩阵），求解**本质矩阵相关的椭圆对偶约束**。

## 椭圆矩阵表示

图像中椭圆可表示为二次型：
$$E = \begin{pmatrix} A & B/2 & C/2 \\ B/2 & D & E/2 \\ C/2 & E/2 & F \end{pmatrix}$$

满足：对于椭圆上任意点 $\mathbf{x} = (u, v, 1)^\top$，有 $\mathbf{x}^\top E \mathbf{x} = 0$。

## Kruppes 方程

本质矩阵 $E$ 与图像椭圆满足对偶约束：
$$E^\top \Omega^* E = \text{degenerate}(R, t)$$

其中 $\Omega^* = K^{-\top} K^{-1}$ 是**图像绝对二次像 (IAC)** 的对偶。

对每个相机 $i$：
$$E_i^\top \Omega^* E_i = \lambda_i [\mathbf{t}]_\times R + \text{rank-2 约束}$$

## 球面→椭圆的特殊情况

对于**球体**（而非一般二次曲面），椭圆投影有更直接的解析解：

### 球面参数
球心 $\mathbf{C}$，半径 $R$。相机坐标系下球心 $(X_c, Y_c, Z_c)$。

### 椭圆参数与球面参数的关系

**椭圆中心**（精确解）：
$$u_0 = c_x + f_x \frac{X_c}{Z_c}, \quad v_0 = c_y + f_y \frac{Y_c}{Z_c}$$
即椭圆中心 = 球心投影（对透视投影精确成立，对球体而言）。

**椭圆半轴**（近似，需迭代）：
$$a \approx f \sqrt{\frac{R^2 Z_c^2 + R^2(X_c^2+Y_c^2)}{Z_c^2 - R^2}}$$
$$b \approx \frac{fR}{\sqrt{Z_c^2 - R^2}}$$

更精确的解析解需要求解**圆锥-平面交线**，即对偶四元数方法。

## 对偶圆锥 (Dual Cone) 方法

球面的对偶圆锥在相机坐标系下：
$$C^* = \begin{pmatrix} \frac{1}{R^2}I & -\frac{1}{R^2}\mathbf{C} \\ -\frac{1}{R^2}\mathbf{C}^\top & \frac{\|\mathbf{C}\|^2}{R^2} - 1 \end{pmatrix}$$

投影到图像：$E = P C^* P^\top$，其中 $P = K [I|0]$ 是相机投影矩阵。

## 与你的场景的关系

对于眼动追踪（瞳孔→球面）：
- **标准 Kruppes**：处理一般相机-物体关系，计算量大
- **球面特化**：上述简化公式足够，无需迭代
- **你的优势**：眼球半径作为**已知先验**，直接约束 $R$，无需从椭圆中估计

## 参考文献

- Hartley & Zisserman, *Multiple View Geometry*, Ch. 19 (Dual Quadrics)
- Kahl & Heyden, "Algebraic motions for structure and motion estimation" (2001)
- Fitzgibbon, "Simultaneous linear estimation of multiple view geometry and calibration" (2001)
