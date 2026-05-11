# 会议模板参考 — LaTeX 宏包配置

> 吸收自 AutoResearchClaw `researchclaw/templates/conference.py`

## 支持的会议模板

### NeurIPS 2025

| 属性 | 值 |
|------|-----|
| documentclass | `article` |
| style package | `neurips_2025` |
| style options | `preprint,nonatbib` 或 `final` |
| 额外宏包 | `natbib`, `graphicx`, `hyperref`, `amsmath`, `amssymb` |
| 作者格式 | `\author{...}` (preamble) |
| 参考文献格式 | `plainnat` |
| 栏数 | 1 (preprint) / 2 (final) |
| 下载URL | `https://media.neurips.cc/Conferences/NeurIPS2025/Styles.zip` |

### ICLR 2026

| 属性 | 值 |
|------|-----|
| documentclass | `article` |
| style package | `iclr_2026` |
| style options | `preprint` 或 `final` |
| 额外宏包 | `natbib`, `graphicx`, `hyperref`, `amsmath`, `amssymb` |
| 作者格式 | `\author{...}` (preamble) |
| 参考文献格式 | `plainnat` |
| 栏数 | 2 |
| 下载URL | `https://media.iclr.cc/Conferences/ICLR2026/Styles.zip` |

### ICML 2026

| 属性 | 值 |
|------|-----|
| documentclass | `article` |
| style package | `icml_2026` |
| style options | `accepted` 或 `preprint` |
| 额外宏包 | `natbib`, `graphicx`, `hyperref`, `amsmath`, `amssymb` |
| 作者格式 | `\begin{icmlauthorlist}...\end{icmlauthorlist}` (post-\begin{document}) |
| 参考文献格式 | `icml2026` |
| 栏数 | 2 |
| 下载URL | `https://media.icml.cc/Conferences/ICML2026/Styles.zip` |

### 中文期刊通用格式

```latex
\documentclass[UTF8]{ctexart}
\usepackage{cite}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{amsmath,amssymb}
\usepackage{booktabs}
\usepackage[top=2.5cm,bottom=2.5cm,left=2.5cm,right=2.5cm]{geometry}

\title{中文论文标题}
\author{作者姓名$^{1}$\thanks{通讯作者: email@example.com} \\
$^{1}$单位名称, 城市, 邮编}

\begin{document}
\maketitle

\begin{abstract}
中文摘要内容...
\end{abstract}

\section{引言}
...

\bibliographystyle{unsrt}
\bibliography{references}

\end{document}
```

## 使用方式

在 `latex-output` SKILL.md 的执行步骤中，根据用户选择的格式确定：
- 国际会议: 从 AutoResearchClaw 的 `styles/` 目录获取 `.sty` 文件
- 中文期刊: 直接使用 `ctexart` + `unsrt` BibTeX 格式
