# uCT vs CT 多模态比较（2026-05-30 最终版）

> 基于 **v5管线** 的最终分析结果，已整合入 `scc-mathematical-morphology` 论文。

## 数据

- **CT**: 160临床CT（80例×2耳），475条中心线，来自 `A_manual/`，参数 `batch_logspiral_params_A_manual.csv`
- **uCT**: 31标本×2侧=62耳 Human Bony Labyrinth，中心线由 v5管线（rejection_ratio=0.40）提取，参数 `batch_logspiral_params_HBL_uCT_v5.csv`

## 拟合

`clean_centerline.py` 自带拟合（`fit_logspiral()`）。坐标变换：NPZ ZYX → XYZ → LPS。

## 统计方法

Mann-Whitney U 检验（双尾），因参数呈非正态分布（Shapiro-Wilk p<0.05）。

## 关键结果

### |b|（螺旋增长率）— 主发现 ✅

| 管型 | uCT 均值 | CT 均值 | p值 | 结论 |
|:----|:--------:|:-------:|:---:|:-----|
| AC | 0.194 | 0.186 | 0.26 | **无显著差异** |
| PC | 0.188 | 0.199 | 0.20 | **无显著差异** |
| LC | 0.260 | 0.213 | 0.08 | **无显著差异** |

→ **螺旋参数跨模态一致**，论文核心支撑。

### 弧长

| 管型 | uCT (mm) | CT (mm) | p值 | 解读 |
|:----|:--------:|:-------:|:---:|:-----|
| AC | 8.30±2.70 | 10.45±2.97 | 0.000 | 标本片段提取 vs 全骨扫描 |
| PC | 7.59±2.45 | 9.74±4.57 | 0.013 | 同上 |
| LC | 6.42±1.78 | 7.48±2.28 | 0.000 | 同上 |

弧长差异由标本制备差异（uCT为干骨碎片，临床CT为完整颞骨）导致，不影响螺旋参数可比性。

### RMSE

| 管型 | uCT (mm) | CT (mm) | p值 | 解读 |
|:----|:--------:|:-------:|:---:|:-----|
| AC | 0.052 | 0.089 | **0.000** | uCT 8×更高分辨率→拟合更优 |
| PC | 0.047 | 0.072 | **0.000** | |
| LC | 0.035 | 0.050 | **0.000** | |

## 论文结构

```
§2.3 High-Resolution Micro-CT Validation Dataset（Methods）
  → 描述31标本62耳uCT、0.061mm体素、186/186 100%提取成功

§3.3 Cross-Modality Validation（Results + Figure 2）
  → Micro-CT参考标本（n=3）→ 保持原内容
  → 高分辨uCT（n=62耳）→ |b|不显著p=0.08-0.26、弧长差异解释、RMSE更低

Figure 2: uCT vs CT |b| 箱线图（三管分面，p值标注）
  → figures/uct_vs_ct_b.pdf
```

## 数据路径

参考论文目录下的 `DATA_MAP.md`。

## 相关脚本

- `figure-generation` 技能的 `references/python-recipes.md` — matplotlib PDF 生成最佳实践
- `medical-image-centerline` 技能 — v5管线 + rejection_ratio调参
