---


name: 3d-curve-fitting-figures
description: 3D曲线拟合图的生成规范：从点云到拟合曲线到出版级Figure。 覆盖拟合重建陷阱、多标本复合布局、分段数据合并、argsort路径错乱。
version: 1.0.0
license: MIT
author: Synthos
  配合figure-generation skill使用。
allowed-tools:
- terminal
- read_file
- write_file
- search_files
metadata:
  synthos:
    author: Synthos
    signature: 'input: dict -> output: dict'
    related_skills:
    - figure-generation
    version: 1.2.0
    tags:
    - figure-generation
    - 3d-fitting
    - curve-fitting
    - scientific-figures



---



## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）




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

## 🔴 致命陷阱：argsort 路径错乱（2026-05-31 实战验证）

### 问题

用 `np.argsort(theta)` 按角度排序代替最近邻路径来确定点在螺旋上的顺序。这会将螺旋上不同位置但角度相近的点混排，产生荒谬的拟合结果。

### 症状

| 症状 | 错误值 | 正确值 | 比例 |
|:-----|:------:|:------:|:----:|
| AC bony RMSE | **2.2700 mm** | 0.1330 mm | 17× |
| PC memb RMSE | **2.1731 mm** | 0.1704 mm | 13× |
| PC bony b | -0.0463 | **-0.0191** | 方向相反 |
| LC bony b | 0.0267 | **0.0052** | 5× |

**核心教训**：图看起来"拟合得好"（曲线穿过点云）≠ 参数正确。argsort 产的曲线视觉上可能正常，但 RMSE 和 b 都是错的。**必须交叉验证 — 同时检查 RMSE + b + 视觉质量。**

### 根因

螺旋的数学特性：沿路径 θ 单调递增(或递减)，但 `np.arctan2` 返回的值域是 `[-π, π]`。用 `argsort` 将所有点的 θ 按数值排序，实际上将**一个完整螺旋圈的端点与起点排序到一起**，破坏了点的解剖顺序。

### 正确做法

```python
# ❌ 错误：按角度排序（只能用于 grid search 找中心）
it = np.argsort(thetas)
t_sorted, r_sorted = thetas[it], r[it]

# ✅ 正确：沿最近邻路径展开 θ
path = nearest_neighbor_path(pts)
theta_unwrapped = np.unwrap(theta_raw[path])
r_path = r2[path]

# 然后沿路径拟合 log(r) = a + b*theta_unwrapped
```

### 如何检测

```bash
# 快速扫描：找出所有用在最终拟合的 argsort
grep -n "argsort" code/*.py
```

检查每处 argsort:
- 如果在 `refine_2d`（grid search 找中心）→ ✅ 可接受（仅用于粗定位）
- 如果在最终拟合步骤（确定 `a,b` 和 `A` 参数）→ ❌ 必须改为 path-based

### 最近邻路径实现（标准版）

```python
def nearest_neighbor_path(pts):
    """贪心最近邻：从点0开始，每次找最近未访问点"""
    n = len(pts)
    visited = [False] * n
    path = [0]
    visited[0] = True
    current = 0
    while len(path) < n:
        dists = [np.linalg.norm(pts[current] - pts[j]) if not visited[j] else float('inf') for j in range(n)]
        nearest = np.argmin(dists)
        path.append(nearest)
        visited[nearest] = True
        current = nearest
    return path
```

### 修复检查清单

- [ ] 拟合函数的最终步骤使用 `theta_raw[path]` 而非 `argsort(theta)`
- [ ] 螺旋重建使用路径顺序展开的 θ（`np.unwrap` 后的）
- [ ] 图中标注的 RMSE 与独立拟合脚本的输出一致
- [ ] 复合图与单标本图中同一条中心线的 RMSE 相同
- [ ] 脚本中没有重复定义的 `fit_logspiral_3d` 函数（Python 的最后一个定义覆盖前面的）

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

## 数据一致性检查（v1.2.0新增）

### 多脚本输出交叉验证

当项目中有多个拟合脚本（`fit_logspiral_aligned.py`, `gen_all_figures.py`, `gen_composite_figure.py` 等）时，必须验证它们对同一份数据输出一致：

```bash
# 快速一致性检查：对比两个脚本的拟合结果
# 对 sp1 micro-CT 的 AC bony
python3 -c "
import numpy as np
# 从 fit_logspiral_aligned.py 输出中提取
correct_rmse = 0.1326
correct_b = 0.0958
# 从 gen_all_figures.py 的图标题中提取
figure_rmse = 0.133  # 从图标题读取
figure_b = 0.0958

if abs(correct_rmse - figure_rmse) > 0.01:
    print('WARN: RMSE mismatch!')
if abs(abs(correct_b) - abs(figure_b)) > 0.001:
    print('WARN: b mismatch!')
"
```

### 管道完整性检查

- [ ] 每个拟合脚本都有确定的、不冲突的 `fit_logspiral_3d` 函数（无重复定义）
- [ ] 所有图生成脚本使用相同的拟合管线（路径顺序、中心搜索、参数初始化）
- [ ] 图中的 RMSE 标注与独立拟合脚本的控制台输出一致
- [ ] 补充图与主图使用同一管线（而非各自实现不同版本的拟合）
- [ ] 数据源路径指向当前目录结构（非已删除的 `tmp/` 或旧 `figures/` 目录）

## 3D参数计数约定

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

在 Methods 段用 `"8-parameter independent set: ($c_x, c_y, \\theta_0, a, b, A, \\omega, \\phi$)"` 并说明SVD固定平面、质心固定中心的计数约定。
