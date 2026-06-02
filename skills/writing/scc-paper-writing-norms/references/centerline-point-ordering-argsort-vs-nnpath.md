# 中心线点序方法：argsort vs 最近邻路径

## 问题背景

2026-05-31 SCC数学形态学论文L0.5审计发现：`gen_all_figures.py`中同时存在两种点序方法，
导致同一组中心线的拟合RMSE在不同脚本间不一致（AC bony: 2.27mm vs 0.13mm）。

## 两种方法的原理

### argsort(theta) — ❌ 不推荐

```python
theta = np.arctan2(dy, dx)      # 各点角度
idx = np.argsort(theta)          # 按角度排序
```

**问题**：半规管中心线的2D投影不是严格凸的——当管道在平面上有弯曲/回旋时，
按角度排序会将物理上远离的点排在一起（因为角度接近），导致拟合到跨圈跳跃的错误路径。

### 最近邻路径 — ✅ 推荐

```python
def nearest_neighbor_path(pts):
    n = len(pts)
    visited = [False] * n
    path = [0]                    # 从第0点出发
    visited[0] = True
    current = 0
    while len(path) < n:
        dists = [np.linalg.norm(pts[current] - pts[j])
                 if not visited[j] else float('inf') for j in range(n)]
        nearest = np.argmin(dists)
        path.append(nearest)
        visited[nearest] = True
        current = nearest
    return path
```

**优势**：保持沿管道的自然顺序，适用于任意形状的中心线。

## 实战数据

### SCC数学形态学论文（2026-05-31）

| 管道 | 点数 | argsort RMSE | nn_path RMSE | 差异 |
|:-----|:---:|:------------:|:------------:|:----:|
| AC bony | 18 | 2.27 mm | 0.13 mm | 17.5x |
| PC bony | 16 | 0.41 mm | 0.41 mm | 1x |
| LC bony | 14 | 1.21 mm | 0.36 mm | 3.4x |

非凸形状（AC, LC）受影响最大；近似凸的形状（PC）不受影响。

### 膜性SCC重建论文（2026-06-01）

| 管道 | 点数 | 方法 | RMSE |
|:-----|:---:|:------|:----:|
| 18条中心线全量 | 14-22 | nn_path | 0.36-1.73mm |

膜性数据使用nn_path，结果一致。

## 代码库清理建议

| 文件 | 当前方法 | 建议 |
|:-----|:---------|:-----|
| fit_logspiral.py | 最近邻路径（已重写） | ✅ 生产代码（2026-06-02） |
| fit_logspiral_aligned.py | — | 🗑️ 已删除 |
| gen_all_figures.py | nn_path | 保留 |
| regenerate_all.py | nn_path | 保留 |

## 验证命令

```bash
# 检查某脚本是否使用 argsort
grep -n "argsort" 03-code/*.py | grep -v "refine_2d\|#"
# 输出中若出现在"拟合"或"最终"阶段 → 需要修复
```
