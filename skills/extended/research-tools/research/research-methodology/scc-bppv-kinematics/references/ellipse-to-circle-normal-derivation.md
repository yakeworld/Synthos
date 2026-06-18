# 椭圆反求3D圆法向量

3D空间中圆的正交投影必为椭圆。给定椭圆几何参数，可唯一确定原圆的法向量（至多前后颠倒二义性）。

## 核心结论

半轴长与法向量的关系：

$$a = R, \quad b = R|n_z|$$

其中 $R$ 为圆的半径，$n_z$ 为法向量与 $z$ 轴（投影方向）夹角的余弦。

## 求解公式

已知椭圆参数：半长轴 $a$、半短轴 $b$、长轴方向角 $\varphi$（xy平面内从x轴逆时针旋转）：

$$R = a$$

$$n_z = \pm\frac{b}{a}$$

长轴方向 $\mathbf{m} = (\cos\varphi, \sin\varphi, 0)$ 在圆平面内，故 $\mathbf{n}\cdot\mathbf{m} = 0$：

$$n_x = \mp\frac{\sqrt{a^2-b^2}}{a}\sin\varphi$$
$$n_y = \pm\frac{\sqrt{a^2-b^2}}{a}\cos\varphi$$
$$n_z = \frac{b}{a}$$

**两解**（互为反向，对应无向平面的两种定向）：

$$\mathbf{n}_{1,2} = \frac{1}{a}\left(\mp\sqrt{a^2-b^2}\sin\varphi,\ \pm\sqrt{a^2-b^2}\cos\varphi,\ b\right)$$

## 几何解释

| 椭圆特征 | 几何含义 |
|---------|---------|
| 扁率 $b/a$ | $=|n_z|$，法向量与z轴夹角余弦 |
| 长轴角 $\varphi$ | 圆平面与xy平面交线方向；法向量水平分量垂直于此 |
| $b=a$（圆） | $n_z=\pm1$，圆平行于xy平面 |
| $b=0$（线段） | $n_z=0$，圆垂直于xy平面 |

## 应用：SCC半规管

SCC（半规管）在解剖学上近似为空间圆。CT扫描为正交投影，SCC投影为椭圆。此公式用于从2D投影椭圆反推SCC空间法向量，进而分析SCC空间姿态与BPPV易感性的关系。

## 验证代码

```python
import numpy as np

def ellipse_to_normal(a, b, phi):
    """椭圆参数 → 3D圆法向量"""
    sin_phi, cos_phi = np.sin(phi), np.cos(phi)
    tilt = np.sqrt(a**2 - b**2) / a
    n1 = np.array([-tilt*sin_phi,  tilt*cos_phi, b/a])
    n2 = -n1
    return n1, n2

# 验证：正向+反向
R = 5.0
n_true = np.array([0.3, 0.4, 0.8])
n_true = n_true / np.linalg.norm(n_true)
# 生成圆、投影、拟合椭圆 → 反推法向量
# 验证 dot(n_true, n_recovered) = ±1
```

## 推导要点

1. 圆参数化：$\mathbf{r}(\theta) = \mathbf{C} + R\cos\theta\,\mathbf{u} + R\sin\theta\,\mathbf{v}$
2. 正交投影到xy平面：$\mathbf{r}_{\text{proj}}(\theta) = \mathbf{c} + R\cos\theta\,\mathbf{u}_{2d} + R\sin\theta\,\mathbf{v}_{2d}$
3. 形状矩阵 $M^\top M$ 的特征值为 $R^2$ 和 $R^2 n_z^2$
4. 特征值分解来自：$\det(M^\top M - \lambda I) = \lambda^2 - R^2(1+n_z^2)\lambda + R^4 n_z^2 = 0$
