# Synthos 8 篇论文 Markdown 转换记录 (2026-05-27)

## 源文件位置

- **源论文**: `~/桌面/article_todo/` (8 篇子目录)
- **原始文件 (TeX/PDF)**: `~/Synthos/outputs/papers/` (符号链接到 article_todo)
- **纯 Markdown**: `~/Synthos/outputs/papers-md/` (中文名，干净无噪音)

## 转换策略

每篇论文按源文件类型选择工具：

| 类型 | 工具 | 命令 |
|:-----|:-----|:-----|
| 有主 PDF | MarkItDown | `uvx markitdown paper.pdf > paper.md` |
| 仅有 TeX | pandoc | `cd src && pandoc paper.tex -f latex -t markdown > paper.md` |
| 无源文件 | 手动笔记 | 30-40行摘要 + frontmatter |

## 转换结果

| # | 论文 | 格式 | 行数 | 工具 |
|:-:|:-----|:-----|:----:|:-----|
| 1 | 3D Eyeball Model Iris Segmentation | PDF->MD | 505 | MarkItDown |
| 2 | Dual-Ellipse Pupil Boundary Estimation | PDF->MD | 505 | MarkItDown |
| 3 | Precise 3D Iris Normalization | TeX->MD | 432 | pandoc |
| 4 | Off-Axis Iris Normalization | TeX->MD | 282 | pandoc |
| 5 | Dual-Ellipse Pupil Localization | PDF->MD | 505 | MarkItDown |
| 6 | YOLOv8 Iris Segmentation | 手写 | 30 | - |
| 7 | BPPV Virtual Simulation | 手写 | 33 | - |
| 8 | Semicircular Canals 3D | PDF->MD | 505 | MarkItDown |

## 引用PDF过滤清单

以下作者/模式应排除在"主论文"检测之外：
benalc, liu, he20, bradshaw, david, rajguru, iversen,
takagi, chacko, santina, hao, javadi, kothari, moreno,
stampe, fuhl, rabbitt, ji, wu, rh, hashimoto, highstein,
ifediba, lane, eliezer, hisaya

## Obsidian 集成

- frontmatter 含 tags + aliases + source 链接
- papers-md/_INDEX.md 为 MOC 入口
- 根 _INDEX.md 链接到 outputs/papers-md/_INDEX.md
