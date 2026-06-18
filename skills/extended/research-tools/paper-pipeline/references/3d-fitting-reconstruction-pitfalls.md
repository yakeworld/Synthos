# 3D Parametric Fitting Reconstruction Pitfalls

## 🔴 致命陷阱：重建时遗漏螺旋中心偏移 (cx, cy)

**2026-05-28 SCC论文实战**：`gen_composite_figure.py` 的 `fit()` 函数在重建3D曲线时遗漏了 `cx*u + cy*v`。

### 错误 vs 正确的重建公式

```
错误（曲线锚定在数据质心，非螺旋中心）：
  cf = c0 + r*cos(θ+rt)*u + r*sin(θ+rt)*v + z*nml
  
正确（曲线从螺旋中心开始）：
  cr_fit = cx + r_fit * cos(t_fit + rot)   ← 关键：加 cx！
  cy_fit = cy + r_fit * sin(t_fit + rot)   ← 关键：加 cy！
  cf = c0 + cr_fit*u + cy_fit*v + z*nml
```

### 错误的影响

- 所有曲线被错误锚定在数据质心（centroid）而非拟合的螺旋中心
- 导致曲线与单标本图存在**视觉差异**（用户可感知的偏差）
- RMSE 计算不受影响（RMSE用数据 θ 范围，不依赖重建范围外的点）
- 但**视觉呈现不可信**

### 根因

2D拟合时的坐标系：
```
p2d = [(pts - c0) @ u, (pts - c0) @ v]  # 相对质心的2D坐标
```
螺旋中心 (cx, cy) 是在这个2D空间中找到的。重建时：
```
2D点 = 螺旋中心 + 螺旋形状
     = (cx, cy) + (r*cos(θ+rt), r*sin(θ+rt))
3D点 = c0 + 2D点_x * u + 2D点_y * v + z * nml
     = c0 + (cx + r*cos(θ+rt))*u + (cy + r*sin(θ+rt))*v + z*nml
```

忘记加 `cx, cy` 相当于把螺旋中心移到了原点（数据质心），改变曲线的3D位置。

### 检查方法

对比两个脚本的图：
- 单标本图（`gen_all_figures.py` — 使用了 `cx+` 和 `cy+`，正确）
- 综合图（`gen_composite_figure.py` — 可能缺 `cx, cy`）

如果同一条半规管在两个图中的曲线位置不同 → 重建出错了。

### 预防

在 `fit()` 函数末尾添加显式检查：
```python
# 验证重建偏移
if abs(cx) < 1e-6 and abs(cy) < 1e-6:
    print("WARNING: cx,cy near-zero — reconstruction likely missing center offset!")
```

## 🟡 次要陷阱：Figure 2 被 LaTeX 推到论文末尾

大图（6×3面板）使用 `[t]` placement 时容易被推到文档末尾。

### 修复

```latex
% 错误：[t] 限制太死，大图易漂移
\begin{figure}[t]

% 正确：[htbp] 给 LaTeX 更多浮动选项
\begin{figure}[htbp]
```

### 间距

图标题与下节内容距离不足时：
```latex
\end{figure}

\vspace{12pt}  % 增加间距

\subsection{...}
```

## 🟡 次要陷阱：多列表格超宽

`\small` 表格含多列数学公式和 range 时容易超宽。用 `\setlength{\tabcolsep}{}` 控制列间距：

```latex
\small
\setlength{\tabcolsep}{4pt}  % 默认 6pt → 4pt 缩小列宽
\begin{tabular}{lcccccc}
...
\end{tabular}
```

## 根因总结

所有这些问题都是 **2D→3D 反投影** 时的坐标系错误。核心原则：

> **拟合时减去的偏移（cx, cy），重建时必须加回来。**
> 这是 3D 参数化拟合中最常见的低级错误。
> 类似于：PCA降维后重建时忘记加回均值一样。
