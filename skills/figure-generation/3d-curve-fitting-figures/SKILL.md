---
name: 3d-curve-fitting-figures
description: >-
  3D曲线拟合图的生成规范：从点云到拟合曲线到出版级Figure。
  覆盖拟合重建陷阱、多标本复合布局、分段数据合并。
  配合figure-generation skill使用。
version: 1.1.0
author: Synthos
tags: [figure-generation, 3d-fitting, curve-fitting, scientific-figures]
---

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
|:-----|:-------|:-----|
| `fit_logspiral.py` | `cr_fit = cx + r*cos(t+rot)` | ✅ 正确 |
| `gen_all_figures.py` | `cr_fit = cx + r*cos(t+rot)` | ✅ 正确 |
| `gen_composite_figure.py` | ~~`rf*cos(tf+rt)`~~ 缺cx | ❌ 错误 |

**快速诊断命令**:
```bash
grep -n "cx + r\*cos\|cy + r\*sin" code/*.py
# 输出为空 → 脚本有cx/cy缺失bug
# 输出含cx,cy → 检查是否真的包含(不只是r*cos)
```

## 复合图布局

### 行x列约定

| 场景 | 布局 | 说明 |
|:-----|:------|:------|
| SCC 6种代表 x 3标本 | **6行x3列** | 列=标本(micro-CT, 7T MRI, ICT), 行=代表(AC骨/膜, PC骨/膜, LC骨/膜) |
| 多条件对比 | 行=条件, 列=标本 | 行列主次根据页面长宽比调整 |

### 间距控制

`ax.set_title(pad=15)` — 顶行标题与子图内容拉开
`plt.suptitle(y=0.96)` + `tight_layout(rect=[0,0,1,0.97])` — 总标题与首行间距
`ax.text2D(-0.4, 0.5, label, rotation=90, va='center')` — 左列行标签
LaTeX: `end{figure}` 后加 `vspace{12pt}` — 图与后续正文分隔

## 分段数据合并

当同一管道被分为两段标注(从两端向中点):

```python
merged = np.vstack([seg1, seg2[-2::-1]])  # seg1正向 + seg2反向(去重中点)
```

验证: 合并间隙 <0.2mm。总点数 = len(seg1) + len(seg2) - 1。

**症状**: 短弧段(arc<10mm)拟合出荒谬的螺旋率(b=0.5或-0.9), RMSE虽然小但参数物理意义失真。
合并后b回到正常范围(0.01-0.2), 弧长翻倍。

## 3D参数计数约定 (v1.1新增)

### 问题

论文中的参数计数经常不一致。公式中R(3)+c(3)+shape(5)=11，但拟合仅优化8个。

### 根因

旋转矩阵R和平移向量c并非全部独立：
- 平面法线来自数据SVD → 固定(0自由)
- 3D中心设为数据质心 → 固定(0自由)
- 实际拟合的独立参数仅为面内自由度

### 规则

**只计实际独立调整的参数**，不计公式中可由数据确定的变换。

| 模型 | 参数 | 总计 |
|:-----|:-----|:----:|
| 3D对数螺线 | cx, cy, θ₀, a, b, A, ω, φ | **8** |
| HSMM-2(椭圆+扭转) | cx, cy, θ₀, a, b, A, ω, φ | **8** |

### 写论文时

在 Methods 段用 `"8-parameter independent set: ($c_x, c_y, \theta_0, a, b, A, \omega, \phi$)"` 并说明SVD固定平面、质心固定中心的计数约定。
