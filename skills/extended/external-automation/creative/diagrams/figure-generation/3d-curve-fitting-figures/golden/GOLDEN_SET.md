# GOLDEN_SET.md — 3d-curve-fitting-figures

> 对应原则：P1（认知原子语义可复现：同一输入点云 → 等价拟合参数与重建公式通过金标准测试）
> golden_set_origin: self_defined
> skill_role: external-automation 叶子技能 / 从点云到对数螺旋拟合再到出版级 Figure

## 设计依据

本技能覆盖 3D 曲线拟合的核心陷阱与出版规范：中心偏移重建、argsort 路径错乱、分段数据合并、
多脚本一致性交叉验证、参数计数约定。金标准验证目标：

1. **重建正确性（DC-001）**：重建公式显式含中心偏移 `(cx + r*cos(...))*u + (cy + r*sin(...))*v`，
   `grep -n "cx + r\*cos\|cy + r\*sin" code/*.py` 非空且覆盖所有生成脚本
2. **路径顺序正确性（DC-002）**：最终 a/b/A 拟合沿 `nearest_neighbor_path` + `np.unwrap` 展开的 θ 进行；
   `argsort` 仅允许出现在 grid-search 找中心步骤
3. **交叉验证（DC-003/DC-005）**：RMSE + 螺旋率 b + 视觉质量三者交叉验证；b 落在物理合理范围（约 0.01–0.2）；
   复合图与单标本图同一曲线 RMSE 相同；图标题 RMSE 与控制台输出一致（差 <0.01mm）
4. **分段合并（DC-004）**：`seg1 + seg2[-2::-1]` 合并（中点去重），合并间隙 <0.2mm，总点数 = len(seg1)+len(seg2)-1
5. **参数计数（DC-006）**：只计实际独立参数（8 个：cx, cy, θ₀, a, b, A, ω, φ）

## 金标准覆盖范围

| 维度 | 覆盖 | 说明 |
|------|:--:|------|
| 正常路径 | 1 case | 合法对数螺旋点云，path-based 拟合，参数物理合理 |
| 错误路径 | 1 case | argsort 路径错乱 + 重建缺 cx/cy，参数失真，须被检出 |

## 测试用例 (cases/)

### case_001: 正常路径 — 对数螺旋点云的 path-based 拟合
- **输入**: 单标本 micro-CT 点云（AC bony），平面已 SVD 确定、质心固定
- **期望**: 沿最近邻路径展开 θ 后拟合 `log(r) = a + b*θ_unwrapped`；重建含 cx/cy；
  RMSE < 0.2mm；b 落在 [0.01, 0.2]；独立脚本与图标题 RMSE 一致；独立参数 = 8

### case_002: 错误路径 — argsort 路径错乱 + 重建缺中心偏移
- **输入**: 同一类点云，但拟合脚本用 `np.argsort(theta)` 确定点序、重建公式缺 cx/cy
- **期望**: 检出致命陷阱：b 符号/量级失真（|b| 远超或符号反常）、RMSE 异常放大（10× 量级）、
  曲线视觉错位；诊断须指明 `argsort` 用于最终拟合 与 重建缺 `cx + r*cos` 两处根因，
  并给出 path-based + 含 cx/cy 的修复

## 期望输出 (expected/)

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`。

期望输出采用**语义等价判定**：
- `fitting.method` 必须为 `nearest_neighbor_path + np.unwrap`（正常）/ 检出为 `argsort`（错误）
- `rebuild_contains_center_offset` 必须为 true（正常）/ false（错误）
- 正常路径：`rmse_mm` < 0.2、`b_in_physical_range` 为 true（0.01 ≤ b ≤ 0.2）、`independent_params` = 8
- 错误路径：`diagnosis` 命中 `argsort_final_fit` 与 `missing_center_offset` 两项根因；
  `rmse_mm` 显著大于正确值（>10× 量级或符号反常 b）；`recovery_advice` 非空
- 所有 case：`cross_verified` 为 true（RMSE + b + 视觉三向一致或矛盾被报告）

## 通过标准

- 加权总分 ≥ 0.80
- 所有 critical 检查通过（重建含 cx/cy、path-based 拟合、交叉验证、错误路径不崩溃且给出根因）
- expected 与 cases 数量、命名一一对应

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 重建含中心偏移 / path-based 拟合 / 错误路径检出根因且不崩溃 |
| high | 0.7 | RMSE 阈值 / b 物理范围 / 独立参数=8 / 多脚本 RMSE 一致 |
| medium | 0.4 | 分段合并校验 / 视觉质量 / 恢复建议完备 |

## 验证命令

```bash
# JSON 有效性
for f in golden/cases/*.json golden/expected/*.json; do
  python3 -c "import json; json.load(open('$f'))" || echo "FAIL: $f"
done

# 数量配对
test "$(ls golden/cases/*.json | wc -l)" -eq "$(ls golden/expected/*.json | wc -l)"

# 重建/路径静态检查（对实际拟合代码）
grep -n "cx + r\*cos\|cy + r\*sin" code/*.py   # 非空且覆盖所有生成脚本
grep -n "argsort" code/*.py                      # 仅允许出现在 grid-search 找中心步骤
```
