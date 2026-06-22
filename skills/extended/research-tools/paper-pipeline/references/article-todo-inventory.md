# Article TODO Inventory — 桌面待写论文清单

> 来源：`~/桌面/article_todo/`（2026-05-28 发现）
> 总计：8篇，分两个方向

## 眼动/虹膜方向（6篇）

| # | 论文标题 | 目录名 | 成熟度 | 关键文件 |
|:-:|:---------|:-------|:-------|:---------|
| ① | 3D Eyeball Model-Constrained Iris Segmentation | `3D Eyeball Model-Constrained Iris Segmentation/` | ⭐ 很成熟 | 完整LaTeX + bib + 多轮revision (v1-v4) + 投稿文件包 + 20+篇参考PDF<br>**投稿状态**：Pattern Recognition, 2025-03-25提交, v4 revision 2025-08-30 (article20250830.tex)。截至2026-06-22 (21个月) **无接受/拒绝信号**。未在PubMed索引。 |
| ② | A Dual-Ellipse Fitting Method for High-Accuracy Pupil Boundary Estimation | `A Dual-Ellipse Fitting Method for High-Accuracy.../` | ⭐ 成熟 | 完整投稿文件（Cover Letter、声明、Highlights、审稿人建议） |
| ③ | A Precise 3D Geometric Transform Method for Iris Normalization | `A Precise 3D Geometric Transform Method.../` | 📝 有基础 | 投稿文件包 |
| ④ | Correcting the Off-Axis Iris Normalization Formulas in Daugman's Method | `Correcting the Off-Axis Iris Normalization.../` | 📝 有基础 | paper.md + references.bib + 配图 |
| ⑤ | Dual-Ellipse Modeling for Accurate Pupil Localization | `Dual-Ellipse Modeling for Accurate.../` | ⭐ 很成熟 | 6次revision (v1-v6) + 16张配图 + 投稿文件包 |
| ⑥ | High-Accuracy Iris Segmentation Using Improved YOLOv8 with Anatomical Priors | `High-Accuracy Iris Segmentation.../` | ⭐ 最成熟 | 14张Figure + 完整投稿文件（Abstract/Authors/Cover Letter/Declaration/Highlights/审稿人建议/title_page）|

## 前庭方向（2篇）

| # | 论文标题 | 目录名 | 成熟度 | 关键文件 |
|:-:|:---------|:-------|:-------|:---------|
| ⑦ | Optimizing the Safety and Efficacy of PSC BPPV Repositioning Maneuvers through Virtual Simulation | `Optimizing the Safety and Efficacy.../` | 📝 paper.md阶段 | paper.md + 4个复位手法视频（Epley/Foster/Gans/Modified Foster）|
| ⑧ | Three-Dimensional Reconstruction and Comparative Spatial Orientation of Membranous and Bony Semicircular Canals via Multi-modal High-Resolution Imaging | `Three-Dimensional Reconstruction and Spatial.../` | ⭐ v2已优化 | 22篇参考PDF + articlev1.pdf（原版16页）+ **articlev2.pdf（优化版13页，820KB，零报错）** + 3张数据表 + 19篇参考文献 + 跨组引用SCC对数螺旋论文 |

## 与已有论文的关系

- **⑧ 膜性半规管三维重建** ↔ `scc-mathematical-morphology/`（当前SCC数学形态学论文）：同领域但互补。⑧侧重重建与测量方法（Sage模板），SCC论文侧重数学模型与数据驱动拟合（J Vestibular Res）。可互相引用，不应合并。
- **桌面 `synthos_paper.tex`**（另有一份在 `synthos-system-paper/`）：独立于article_todo，是Synthos系统论文的早期草稿（39KB）。

## 开启一篇todo论文的标准流程

1. `ls ~/桌面/article_todo/` — 列出全部8个论文目录
2. 选择目标论文后，`tree -L 2 ~/桌面/article_todo/"{目录名}"` — 浏览结构
3. 检查 paper.md / .tex / 投稿文件等主文档
4. 参照 `paper-pipeline` skill的P2节启动写作流程（NotebookLM逐问法优先）
