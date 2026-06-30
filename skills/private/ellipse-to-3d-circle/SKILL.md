---
name: ellipse-to-3d-circle
category: mlops
description: 椭圆逆投影为三维空间圆 — 核心为眼动追踪中瞳孔椭圆→3D角膜面法向量反推。覆盖正交/透视投影、法向量参数化、深度歧义消除、正交基构建。
signature: "ellipse-to-3d-circle -> processed_result"
---
version: 2.0.0

# ellipse-to-3d-circle: 椭圆逆投影为三维空间圆

## 边界 (Boundary)

将二维图像平面上的椭圆参数反推为三维空间圆的几何参数（圆心、半径、法向量）。
核心应用场景：眼动追踪中瞳孔椭圆→3D角膜面法向量、虹膜椭圆→3D眼球姿态。

**输入**：椭圆参数（中心、长半轴、短半轴、旋转角）+ 相机内参 + 先验约束（如眼球半径）
**输出**：3D圆心、3D法向量、倾斜角、方位角

**不适用**：透视畸变严重的广角镜头、多椭圆联合求解（需扩展）、无相机标定的纯形状反推


## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。
## 输入输出契约 (IO Contract)

### 输入
```python
{
    "ellipse": {
        "center": (u0, v0),           # 像素坐标
        "major_axis": a,              # 长半轴（像素）
        "minor_axis": b,              # 短半轴（像素）
        "rotation_angle": theta       # 椭圆长轴与u轴夹角（弧度）
    },
    "camera": {
        "intrinsic_matrix": K,        # 3x3相机内参矩阵
        "principal_point": (cx, cy),  # 光心
        "focal_length": f            # 焦距（像素）
    },
    "prior": {
        "circle_radius": R,           # 已知圆半径（像素或mm）
        "sphere_center_prior": C     # 可选：球心先验（mm）
    }
}
```

### 输出
```python
{
    "circle_3d": {
        "center": (cx, cy, cz),      # 3D圆心（与prior单位一致）
        "radius": R,                  # 圆半径
        "normal": (nx, ny, nz),      # 单位法向量
        "tilt_angle": alpha,         # 倾斜角（弧度），cos(alpha)=b/a
        "azimuth_angle": phi         # 方位角（弧度）
    },
    "confidence": {
        "well_determined": True/False,  # 是否唯一确定
        "ambiguity": "none" | "azimuth" | "depth"  # 模糊类型
    }
}
```

## 核心步骤

### Step 1: 椭圆→基本几何量

1. **圆半径**：`R = a`（长半轴 = 原圆半径，假设正交投影或已知深度）
2. **倾斜角**：`alpha = arccos(b/a)`，其中 `cos(alpha) = b/a = n·k`（法向量与光轴夹角）
3. **椭圆长轴方向**：给出法向量在图像平面上的投影方向

### Step 2: 法向量参数化

法向量用球坐标参数化（2个自由度）：

$$\mathbf{n} = (\sin\alpha\cos\phi,\; \sin\alpha\sin\phi,\; \cos\alpha)^\top$$

其中：
- $\alpha$ 由 $b/a$ 唯一确定（1个约束）
- $\phi$（方位角）由椭圆长轴方向确定（第2个约束）

**关键约束方程**：
$$\mathbf{n} \cdot \mathbf{k} = \frac{b}{R} = \frac{b}{a}$$
其中 $\mathbf{k} = (0, 0, 1)^\top$ 是相机光轴方向。

### Step 3: 求解方位角

椭圆长轴方向 $\mathbf{d}_{major}$（在图像平面内）给出了法向量的方位：

1. 将椭圆长轴方向映射为3D平面内的方向向量
2. 法向量绕光轴旋转 $\phi$ 后，其投影与 $\mathbf{d}_{major}$ 对齐
3. 由椭圆旋转角 $\theta$ 解出 $\phi = \theta + \pi/2$（或 $\theta - \pi/2$，需根据右手定则确定符号）

### Step 4: 深度求解（歧义消除）

**仅有椭圆参数时**，法向量确定但圆心深度 $z_c$ 不唯一——这是**深度模糊**。

**消除方法**（按你的场景优先级）：
1. **眼球模型约束**：瞳孔中心在眼球球面上，已知球心位置和半径 → 深度可解
2. **双目/多视角**：另一视角产生第二个椭圆，两圆锥交线唯一确定
3. **深度传感器**：结构光/ToF直接提供深度
4. **运动连续性**：时间序列上的平滑假设

### Step 5: 构建正交基

得到法向量 $\mathbf{n}$ 后，构建圆平面正交基：

1. 任选不与 $\mathbf{n}$ 平行的参考向量 $\mathbf{w}$（如 $\mathbf{w}=(1,0,0)^\top$，若 $\mathbf{n}$ 接近平行则改用 $(0,1,0)^\top$）
2. $\mathbf{u} = \frac{\mathbf{w} \times \mathbf{n}}{\|\mathbf{w} \times \mathbf{n}\|}$
3. $\mathbf{v} = \mathbf{n} \times \mathbf{u}$
4. 圆参数化：$\mathbf{r}(\theta) = \mathbf{c} + R\cos\theta\,\mathbf{u} + R\sin\theta\,\mathbf{v}$

## 常见陷阱 (Pitfalls)

### 陷阱1：长半轴≠圆半径
当椭圆来自**透视投影**而非正交投影时，$a \neq R$。透视投影下椭圆参数与圆半径的关系更复杂，需知道圆心深度 $z_c$ 才能正确反推。

**修复**：使用完整相机投影模型 $u = K [R|t] \mathbf{r}(\theta)$，而非简单的正交假设。

### 陷阱2：法向量锥面歧义
仅知 $b/a$ 时，法向量位于以光轴为轴、半角 $\alpha = \arccos(b/a)$ 的**圆锥面**上。必须用椭圆长轴方向确定方位角 $\phi$，否则有无限多解。

### 陷阱3：奇异情况 — 正对相机
当圆正对相机时，$a = b = R$，$\alpha = 0$，椭圆退化为圆。此时无法从单个椭圆判断旋转状态（任何绕光轴的旋转产生相同的投影）。

**修复**：需要圆上纹理特征点或第二视角。

### 陷阱4：单位混淆
椭圆参数是**像素**，法向量/圆心是**物理单位**（mm）。转换时需要相机焦距 $f$：
$$R_{\text{mm}} = \frac{R_{\text{px}} \cdot d_{\text{mm}}}{f_{\text{px}}}$$
其中 $d_{\text{mm}}$ 是圆心到相机距离。

### 陷阱5：Kruppes方程的适用性
经典计算机视觉中的 Kruppes 方程处理的是**一般二次曲面**（非球面）的椭圆投影。对于**球面→椭圆**的特殊情况，有更简洁的解析解（上述推导），不需要迭代求解 Kruppes 方程。

## 用户特异性方法：解剖约束法

对于**眼动追踪场景**（瞳孔/虹膜→角膜/虹膜面），用户推导了一套完整的解剖约束方法，将自由度从2压缩到0：

- `references/anatomy-constrained-derivation.md` — 完整推导：法向量公式、光轴平面、Rodrigues旋转、多帧眼球中心求解
- 核心约束：R_eyeball = 2*R_iris, d = √3*R_iris
- 关键优势：单帧椭圆→法向量，多帧椭圆→眼球中心，无需迭代

详见 `mlops/ellipse-3d-anatomy-constrained` skill。

## 相关资源

- `references/eye-tracking-constraints.md` — 眼动追踪场景中的具体解剖约束、典型精度、VOR关联
- `references/kruppes-ellipse-theory.md` — Kruppes方程、对偶圆锥、球面→椭圆解析解
- `references/anatomy-constrained-derivation.md` — 用户特异性解剖约束推导（AKNE笔记来源）
- `scripts/ellipse_to_3d_circle.py` — 可独立运行的命令行工具（python3 ellipse_to_3d_circle.py --help）

## 质量门

- [ ] 法向量 $\mathbf{n}$ 是单位向量（$\|\mathbf{n}\| \approx 1$）
- [ ] 倾斜角 $\alpha \in [0, \pi/2]$（只取非负）
- [ ] $b/a \in (0, 1]$（否则输入无效）
- [ ] 正交基 $\mathbf{u}, \mathbf{v}, \mathbf{n}$ 构成右手坐标系
- [ ] 输出中明确标注是否有深度模糊

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引


## 核心原则 · PRINCIPLES

1. **准确为先**: 所有输出必须经过事实核查，不编造数据
2. **证据驱动**: 每个结论必须可追溯到具体证据或数据源
3. **可复现性**: 每一步操作必须可重复，结果可验证


## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态


## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。



# Ellipse To 3D Circle

