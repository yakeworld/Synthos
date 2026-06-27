# HCS-3WT Figure 1 QA 完整报告

> 日期: 2026-06-26
> 来源脚本: generate_figures_v2.py

## 审计结果

所有 6 项检查通过。

### 箭头终点精确坐标（axes 坐标）

| 箭头 | 终点 | 目标框 | 判定 |
|------|------|--------|------|
| arrow1 | (4.35, 6.68) | expert_b [0.22,5.22,4.36,1.56] | ✅ x=4.35 in [0.22,4.58], y=6.68 in [5.22,6.78] |
| arrow2 | (5.3, 5.97) | clear_negative [5.24,5.49,3.32,0.97] | ✅ x=5.30 in [5.24,8.56], y=5.97 in [5.49,6.46] |
| arrow3 | (5.3, 3.47) | clear_positive [5.24,2.99,3.32,0.97] | ✅ x=5.30 in [5.24,8.56], y=3.47 in [2.99,3.96] |
| arrow4 | (2.4, 1.62) | expert_c [0.22,0.12,4.36,1.61] | ✅ x=2.40 in [0.22,4.58], y=1.62 in [0.12,1.73] |
| arrow5 | (2.4, 1.62) | expert_c | ✅ 同上 |
| arrow6 | (5.3, 0.92) | gray_zone [5.24,0.49,3.32,0.97] | ✅ x=5.30 in [5.24,8.56], y=0.92 in [0.49,1.46] |

### 文字检查结果

全部文字均在框内。最紧凑: `PowerTransformer + SelectKBest` (fs=7.5) 在 Input Box: 2.81/3.40in width, 0.14/0.60in height.

## QA 脚本

`scripts/fig-generation-qa.py` — 使用方法: `python3 fig-generation-qa.py`