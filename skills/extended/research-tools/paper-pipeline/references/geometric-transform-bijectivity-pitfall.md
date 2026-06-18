# 几何变换可逆性陷阱 — 椭圆↔矩形映射的数学直觉误区

## 问题描述

在描述几何变换（如椭圆→矩形归一化）时，容易无意识地做出「逆向变换也存在且唯一」的错误假设。实际上：

| 变换方向 | 是否唯一 | 原因 |
|:---------|:--------|:-----|
| **椭圆→矩形(正向)** | ✅ **唯一** | 给定椭圆参数(a,b,θ,xc,yc)+3D眼球参数 → 归一化矩形确定 |
| **矩形→椭圆(逆向)** | ❌ **不唯一** | 同一个矩形可来自无数个不同的椭圆参数组合（缺少视线方向、瞳孔半径等信息） |

## 实战案例

3D Iris Normalization 论文讨论过程中，提出了「矩形中的水平位移可逆向修正椭圆旋转角」的猜想。

**错误推导**：
```
矩形水平位移 Δx → Δθ = Δx / R（椭圆旋转角修正）
```

**问题**：矩形水平位移只对应环转角（cyclotorsion）Δψ = Δx/R_iris，而环转角与椭圆形态参数(a,b,θ)完全无关。将Δx归因于椭圆旋转角修正是混淆了两个独立自由度。

**正确理解**：
```
矩形水平位移 Δx → Δψ = Δx / R_iris（环转角）
                   椭圆参数(a,b,θ,xc,yc)不变（旋转对称性）
```

## 写入论文时的正确表述

### ✅ 正确（仅做前向映射）

> "We propose a direct ellipse-to-rectangle transformation method" —— 只说前向，不暗示逆向

### ❌ 错误（暗示逆映射）

> "This transformation enables recovery of elliptical parameters from the normalized texture" —— 矩形纹理不包含椭圆参数信息

### ✅ 正确的应用（纹理互相关测环转角）

> "Since cyclotorsion does not affect elliptical morphology but manifests as pure horizontal translation in the normalized rectangle, we recover Δψ = Δx / R_iris via 1D cross-correlation"

## 检查清单

在论文中描述几何变换时，逐项自查：

- [ ] 正向变换的输入参数是否明确列出？
- [ ] 是否暗示了逆向变换的存在？
- [ ] 如果讨论了逆向，逆变换的输入参数是否与正向输出维度匹配？
- [ ] 是否混淆了「纹理位置偏移」和「边界形态变化」？前者是纹理在固定边界内的滑动，后者是边界本身的变形。
- [ ] 应用场景中检测到的偏移量，能否明确归因于唯一的自由度？（如环转角vs椭圆旋转角是两个不同的自由度）
