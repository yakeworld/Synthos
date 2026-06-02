# SCC论文L0.5审计案例：2026-05-31

## 审计类型：主动实验驱动审计

## 发现：同名函数静默覆盖

### 问题
`gen_all_figures.py` 中两分同名 `fit_logspiral_3d` 函数：
- 第一份(行73): 使用最近邻路径 → 正确
- 第二份(行176): 使用 `np.argsort(theta)` → 错误

Python使用最后定义的那份(argsort版本)，导致所有补充图的拟合结果错误。

### 影响程度

| Canal | 错误RMSE | 正确RMSE | 错误b | 正确b |
|:------|:--------:|:--------:|:-----:|:-----:|
| AC bony | **2.2700mm** | 0.1330mm | 0.0958 | 0.0958 |
| PC memb | **2.1731mm** | 0.1704mm | -0.0671 | -0.0671 |
| PC bony | **1.1359mm** | 0.2714mm | -0.0463 | -0.0191 |
| LC bony | 0.8548mm | 0.1745mm | 0.0267 | 0.0052 |

### 根因
`gen_all_figures.py` 开发过程中添加了第二版 `fit_logspiral_3d` 但未删除第一版。Python解释器在模块加载时用最后定义的同名函数覆盖之前定义。两份实现的核心差异是：
- 正确版：使用最近邻路径(order by path)展开θ→保持解剖连续性
- 错误版：使用 `np.argsort(theta)` (order by angle)→混排螺旋不同位置的点

### 检测方法

```bash
# 危险信号
grep -n "def fit_logspiral\|def fit(" 03-code/*.py | grep -v "__pycache__"

# 确认管线一致性
for script in gen_all_figures.py gen_composite_figure.py fit_logspiral_aligned.py; do
  python3 03-code/$script 2>&1 | grep -E "AC bony|PC bony|LC bony|RMSE|b="
done
```

### 修复

1. 删除重复函数定义
2. 统一使用最近邻路径排序
3. 验证所有脚本输出一致

### 交叉验证链

| 验证项 | 方法 | 通过? |
|:-------|:-----|:-----:|
| 管线输出 vs Table 2 | `fit_logspiral_aligned.py`输出 vs manuscript | ✅ |
| 管线输出 vs 摘要 | RMSE 0.07-0.17mm范围匹配 | ✅ |
| 跨脚本一致性 | gen_all/ gen_composite/ fit_logspiral_aligned 三者输出 | ✅ |
| CSV极端值 | 所有|b|>0.8对应弧长<6mm(边界案例) | ✅ |
