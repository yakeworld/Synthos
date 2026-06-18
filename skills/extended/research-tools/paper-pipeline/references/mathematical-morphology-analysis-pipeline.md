# Mathematical Morphology Analysis Pipeline

> 3D解剖结构中心线的数学建模——适用于半规管、血管、气道等管状结构。
> 2026-05-28 实战：SCC 3D对数螺旋模型，160例CT (475条中心线)。

## 问题类型

什么结构适用：**管状/环状3D中心线**，需要参数化数学模型描述其空间形态。

典型问题："XX结构（半规管/冠状动脉/气管）的空间形态符合什么数学模型？"

## 流程概要

```
1. 中心线获取（.mrk.json / NPZ / CSV）
2. 最佳平面拟合（SVD）
3. 多候选模型拟合（6种）
4. AIC/BIC 模型选择
5. 骨vs膜对比（如果有）
6. Frenet-Serret 曲率/挠率分析
7. 流体动力学理论推导（可选）
```

## 候选模型层级

| Level | 模型 | 参数 | 方程 |
|:------|:-----|:----:|:-----|
| 0 | 平面圆 | 6 | r(θ) = (R·cosθ, R·sinθ, 0) |
| 1 | 平面椭圆 | 8 | r(θ) = (a·cosθ, b·sinθ, 0) |
| **2** | **3D对数螺旋** | **7** | **r(θ) = O + R·(a·e^(bθ)·cosθ, a·e^(bθ)·sinθ, A·sin(ωθ+φ))ᵀ** |
| 2' | 非平面正弦椭圆 | 10 | r(θ) = R·(a·cosθ, b·sinθ, A·sin(ωθ+φ)) + c |
| 3 | Fourier级数 | 27-39 | x_i(t) = A0_i + Σ[Ak_i·cos(kt) + Bk_i·sin(kt)] |
| — | 螺旋线 | 7 | r(t) = (R·cos t, R·sin t, h·t) |

## 拟合方法

两步法：

**Step 1：平面对数螺旋**
- SVD 最佳平面投影 → 2D坐标
- 半对数线性化：ln(r) = ln(a) + b·θ → 最小二乘初始值
- Nelder-Mead 非线性精化

**Step 2：面外正弦项**
- 面外偏差 = signed distance from plane
- 非线性最小二乘拟合：z = A·sin(ωθ+φ)
- 多初值（4种ω × 3种φ）避免局部极小

## 模型选择

AIC = N·ln(RMSE²) + 2k
BIC = N·ln(RMSE²) + k·ln(N)

使用 AIC/BIC 而非单纯 RMSE 比较，避免过拟合。

## 关键陷阱

1. **坐标单位一致性**：.mrk.json 是 LPS (mm)；NPZ 可能是 voxel（需spacing转换）
2. **初值敏感性**：对数螺旋的 b 参数对初值敏感。先用线性化 + 半对数回归得到初始值，再做非线性精化
3. **面外正弦的相位折叠**：A 的符号 + φ 的 2π 模糊性。统一约定 A ≥ 0，φ ∈ [0, 2π)
4. **半规管的非封闭性**：中心线不是闭合环，注意端点处理
5. **自动化中心线质量**：UNet提取的中心线（.npz smooth_mm）有自动插值和降噪，RMSE因此偏大(0.6mm vs 手动分割0.07mm)。应以手动分割为ground truth
6. **左右耳不对称性检查**：对双侧数据必须检查左右对称性。若Cohen's d<0.25则确认参数稳定性。论文中应报告L/R分析结果，这是方法稳健性的重要证据
7. **分割不完整导致的样本差异**：三管数据量可能不等（后管最难分割，常缺2-4例）。不必剔除——在论文中透明标注各管N值即可

## SCC对数螺旋参数参考（160例CT，n=475）

| 参数 | 均值 | 中位数 | 标准差 | 范围 |
|:-----|:----:|:------:|:------:|:----:|
| b（增长率） | 0.059 | 0.047 | 0.049 | [0.0002, 0.158] |
| a（尺度mm） | 2.02 | 2.01 | — | — |
| A（扭转mm） | 0.15-0.34 | — | — | — |

### 各管分类

| 半规管 | n | b均值 | b中位数 | 功能含义 |
|:-------|:-:|:-----:|:-------:|:---------|
| Superior (AC) | 160 | 0.096 | 0.109 | 最紧螺旋，垂直面角速度编码 |
| Posterior (PC) | 156 | 0.032 | 0.017 | 近圆环，斜平面 |
| Lateral (LC) | 159 | 0.048 | 0.033 | 35.2%与耳蜗重叠，水平面 |

### 左右对称性（Cohen's d）
| 半规管 | L均值 | R均值 | d | 判定 |
|:-------|:-----:|:-----:|:-:|:-----|
| Superior | 0.092 | 0.101 | -0.250 | 小差异 |
| Posterior | 0.037 | 0.028 | 0.217 | 小差异 |
| Lateral | 0.046 | 0.049 | -0.071 | 可忽略 |

## 耳蜗对比注意

SCC b值与耳蜗b值（文献~0.02-0.08）的重叠是论文核心卖点。但：
- LC(b≈0.03-0.05) 最接近耳蜗 → 35.2%重叠率
- AC(b≈0.10) 偏差大 → 仅11.9%重叠率
- 需用Bootstrap给置信区间（10,000次重采样, 95%CI = [0.039, 0.085]）
- 当前版本引用文献数据而非直接测量——标注为limitation
- 若需加强论证：在Discussion中可补充"Direct within-specimen cochlear comparison is underway"

## 批量处理性能参考

160例CT (480中心线)的对数螺旋拟合：
- 总耗时：48秒（单中心线~0.1秒）
- 成功率：475/480 = 99%
- 5例失败均因UNet分割阶段后管未提取出，非拟合失败
- Python实现（scipy.optimize.curve_fit + Nelder-Mead）

## 流体动力学理论（可选扩展）

椭圆截面在Stokes流中的阻尼-灵敏度解耦：
- 圆管：S ∝ r², C ∝ 1/r⁴（耦合——阻尼增则灵敏度降）
- 椭圆管：S ∝ ε, C ∝ (1+ε²)/(2ε)（解耦——两者可同步增）
- 当ε=1.6（AC典型值）：S增60%, C仅增15%
- 对应论文中Theory章节，若期刊接受理论文章可保留，否则移至Supplementary

## 论文写作流程（NotebookLM Q&A驱动）

```
╔══════════════════════════════════════════════════════════════╗
║  不要直接写论文。所有章节必须通过NotebookLM Q&A逐节生成。     ║
║  铁律：notebooklm ask → extract → compile, 跳过此步=违规   ║
╚══════════════════════════════════════════════════════════════╝

Step 1: 文献检索（add-research）
Step 2: Q&A知识提取（逐问法4轮）
Step 3: NotbookLM逐节生成（先Results→Methods→Discussion）
Step 4: 提取→组合为LaTeX
Step 5: 编译（2x pdflatex）
Step 6: 双质检（L0.5 + Layer A + Layer B）
Step 7: 投稿文件包（manuscript + cover letter + declarations + figures）

详见 paper-pipeline SKILL.md 中 P2 节 NotebookLM Q&A 铁律。
```

## 输出产物

- `{paper_dir}/paper.tex` — 完整 LaTeX 论文
- `{paper_dir}/tmp/qa_r*.txt` — 每轮Q&A记录
- `{paper_dir}/figures/` — model_comparison.pdf, centerline_3d.pdf, scc_cochlea_comparison.pdf
- `{paper_dir}/quality-report.md` — D1-D10双质检报告
- `{paper_dir}/scc-mathematical-morphology-v{N}.pdf` — 编译后PDF，版本递增
- `{paper_dir}/submission/` — 投稿文件包（含cover-letter.pdf, declarations.pdf）
