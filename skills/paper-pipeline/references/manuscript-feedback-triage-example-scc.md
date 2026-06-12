# SCC 论文反馈分类实战案例 (2026-05-31)

> 配套 `paper-pipeline` 的 P5 手稿反馈分类。本案例完整展示如何对审稿人/同事的书面反馈做逐条溯源验证。

## 背景

论文: SCC Mathematical Morphology (v4)
反馈来源: "文章存在的问题.docx"（同事评审文档）
反馈条数: 6条

---

## 逐条溯源详情

### 🟢 Issue 1: 拟合可靠性（P0）

**反馈原文**: "检查是否存在两套互斥的拟合——1套好（Fig 1/centerline_3d_fits，RMSE 0.11–0.27）、1套失败（sp1/sp2/sp3的图，RMSE 高到 7 mm、|b| 到 0.9）。Table 2 把'失败那套的 b'和'好那套的 RMSE'拼在一起。"

**溯源路径**:
```
Ref: /media/yakeworld/sda2/Synthos/outputs/papers/scc-mathematical-morphology/
```

| 检查项 | 文件 | 命令/操作 | 结果 |
|:-------|:-----|:----------|:-----|
| Table 2 b/RMSE 同源？ | `01-manuscript/v4-paper.tex` | 查 Table 2 Tab:spiral_params | RMSE 0.07-0.17, b -0.109~0.242 ✅同源 |
| CT 475条有失败拟合？ | `04-data/batch_logspiral_params_A_manual.csv` | `python3 -c "check |b|>0.8 or RMSE>1"` | 0条 RMSE>1mm, 32条 \|b\|>0.8 (均短弧) |
| uCT 186条有失败拟合？ | `04-data/batch_logspiral_params_HBL_uCT_v5.csv` | 同上 | 0条 RMSE>2mm ✅ |
| 个体图 sp1/sp2/sp3 用不同管线？ | `03-code/fit_logspiral_aligned.py` | 查看代码 → 主图与补充图同一函数 | 同一 `fit_logspiral_3d()` ✅ |

**判定**: ❌ 未复现"两套拟合"。v4 管线同源，但需肉眼验图确认 sp1/sp2/sp3.pdf 确实来自同一导管。

**修复**: `python3 regenerate_all.py` 全管线重跑 → 输出同源主表 → 人工验图。

---

### 🟢 Issue 2: Fig 1 标注"six models"但实际仅展示4种

**溯源路径**:

```
01-manuscript/v4-paper.tex line 154:
  "Figure~1 shows a quantitative comparison of fitting errors across all six models."
  
Fig 1 caption line 201-203 列出:
  "Logarithmic Spiral, HSMM-2, planar (circle, ellipse), helical models, B-spline"
→ 计数: Circle + Ellipse + Log Spiral + HSMM-2 + Helix + B-spline = 6种 ✅
```

**但**: Fourier(4) 和 Fourier(6) 未在 Fig 1 中出现（只在 Table 3 model selection 对比）。

**判定**: 🟡 文本说"six models"是对的，但可能引起读者困惑——Fourier models在哪？

**修复**: Fig 1 caption 末尾加：
```latex
Fourier series models are excluded from the figure due to their substantially 
higher number of parameters (27/39) and poorer AIC/BIC performance (see Table~3).
```

---

### 🔴 Issue 3: 参考文献[6]不可引用（"in preparation"）

**溯源路径**:

```
01-manuscript/v4-paper.tex: grep -n "6\]\|our previous\|our prior\|from \["
  Line 111: "This model (from our prior work)" — 无引用号
  Line 58/70: 无 [6] 引用
  
01-manuscript/references.bib: 无 "in preparation" 条目
```

**判定**: ✅ v4 已修复。引言 §2.1 已改写为无引用陈述，`references.bib` 中无 "in preparation" 条目。

**但**: 仍遗留问题——§2.1 缺少 Dataset 1 的完整方法描述（标本来源、PTA染色参数、成像参数、分割软件）。需补入 1-2 句话。

**修复**:
```latex
// 在 §2.1 末尾加：
Three human cadaveric temporal bone specimens (obtained from [institution]) 
were imaged as follows: Specimen 1 by PTA-enhanced micro-CT at [X] keV / [Y] μA 
with [Z] μm isotropic voxel size; Specimen 2 by 7T MRM with [parameters]; 
Specimen 3 by industrial CT at [parameters]. Bony and membranous labyrinth 
segmentation was performed using [software/tool] following [protocol reference].
```

---

### 🟡 Issue 4: "micro-CT"称呼混乱

**溯源路径**:

全文 grep "micro-CT\|µCT\|uCT\|high-resolution micro-CT":

| 数据集 | 文章称呼 | 出现位置 |
|:-------|:---------|:---------|
| Dataset 1 (n=3) | "micro-CT", "high-resolution multi-modal" | §2.1, §3.1 (line 154) |
| Dataset 2 (n=160) | "clinical CT" | §2.2 (清晰✅) |
| Dataset 3 (n=31) | "micro-CT (µCT)", "uCT", "high-resolution uCT" | §2.3, §3.3 |

**问题**: §3.1 的 "On the high-resolution micro-CT data" — 指的是 Dataset 1 还是 Dataset 3？下文 §3.3 分开了（"Micro-CT reference specimens (n=3)" vs "High-resolution uCT dataset (n=62 ears)"），但 §3.1 不明确。

**Dataset 1 模态关系**: 从代码目录结构 (sp1=microct, sp2=mrn, sp3=ict) 确认——**3标本各用1种模态，非每例3种**。

**修复方案**:

| 原文 | 改为 |
|:-----|:-----|
| §2.1 "micro-CT, ICT, and 7T MRM" | 改为 "micro-CT (n=1), ICT (n=1), and 7T MRM (n=1)" |
| §3.1 "On the high-resolution micro-CT data" | "On the three benchmark specimens (micro-CT, 7T MRI, ICT)" |
| §2.3 "micro-CT (µCT)" | 统一用 "uCT validation set (n=62 ears)" |
| §3.3 "High-resolution uCT dataset" | 保留，但首次出现时加 "（§2.3）" 指回方法 |

---

### 🟡 Issue 5: RMSE 数值不一致

**原始**: Abstract 说 "RMSE of 0.07-0.17mm"，Fig 1 标注有 0.271。

**溯源**:

```
Abstract line 37: "The proposed 3D Logarithmic Spiral model...RMSE of 0.07-0.17mm"
  → 明确指 Log Spiral 模型 ✅

Fig 1 caption: "The 3D Logarithmic Spiral (blue) consistently achieves RMSE below 0.17mm"
  → 也指 Log Spiral ✅
  
若 Fig 1 中 0.271 条柱子标在 Planar Circle / Helix / 其他模型上
  → 完全正常（其他模型 RMSE 更高）
```

**判定**: ✅ 无矛盾。但读者阅读时可能误解 0.271 为 Log Spiral 的 RMSE。

**修复**（可选）:
```latex
// §3.1 line 154 改为：
"The 3D Logarithmic Spiral achieved RMSE of 0.07–0.17 mm, substantially 
outperforming the planar circle (RMSE up to 0.27 mm) and helical models."
```

---

### 🟡 Issue 6: Fig 4C 数据来源不明

**原始**: Fig 4C 的 `ln r vs θ` 半对数图，caption 未说明 SCC 数据和 Cochlea 数据各来自哪里。

**溯源**:

```
Fig 4 (scc_cochlea_comparison.pdf):
  Panel A: 本文 SCC 数据（AC bony centerline + 拟合曲线）✅
  Panel B: 耳蜗对数螺旋示意图（来自 Manoussaki 文献）
  Panel C: ln(r) vs θ 图 — 同时展示 SCC 和 Cochlea 的线性关系
```

**判定**: Panel C 很可能是**混合图**（SCC 数据来自本文拟合结果，耳蜗数据引用 Manoussaki 文献），但 caption 未做区分。

**修复**:
```latex
// Fig 4 caption 段尾改为：
"SCC data in panels (A) and (C) are from this study (Specimen 1, anterior 
superior canal, micro-CT). Cochlear spiral in panels (B) and (C) is 
reproduced from Manoussaki et al. (2006) \[22\] for visual comparison."
```

---

## 优先级排序与执行

| 优先级 | 问题 | 判定 | 工作量 | 优先级依据 |
|:------:|:-----|:----:|:------:|:-----------|
| 🔴 P0 | 拟合可靠性 | 未复现，需验图 | 1h | 数据完整性，投稿最大风险 |
| 🔴 P0 | Dataset 1 模态关系 | 确认问题 | 0.5h | 方法学误导 |
| 🟡 P1 | micro-CT 术语 | 确认问题 | 1h | 全文3处需改 |
| 🟡 P1 | Fig 1 caption | 可改可不改 | 0.3h | 防审稿人困惑 |
| 🟡 P1 | Fig 4C 数据来源 | 确认问题 | 0.3h | 学术诚信 |
| 🟢 P2 | RMSE 澄清 | 无矛盾 | 0.2h | 可选 |
| 🟢 P3 | [6]引用 | 已修复 | — | 最后验证 |
