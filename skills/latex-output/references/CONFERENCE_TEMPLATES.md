# 会议模板参考 — LaTeX 宏包配置

> 吸收自 AutoResearchClaw `researchclaw/templates/conference.py`
> 增强自 Orchestra Research AI-research-SKILLs `ml-paper-writing/templates/`
> (AAAI 2026, ACL, COLM 2025, algorithm.sty 等)

## 支持的会议模板

| 会议 | 支持 | 来源 | 模板位置 |
|------|:----:|:-----|:---------|
| NeurIPS 2025 | ✅ | AutoResearchClaw | `styles/neurips_2025.sty` |
| ICLR 2026 | ✅ | AutoResearchClaw | `styles/iclr_2026.sty` |
| ICML 2026 | ✅ | AutoResearchClaw + AI-research-SKILLs | `styles/icml_2026.sty` + `templates/icml2026/` |
| AAAI 2026 | ✅ **新** | AI-research-SKILLs | `templates/aaai2026/` |
| ACL | ✅ **新** | AI-research-SKILLs | `templates/acl/` |
| COLM 2025 | ✅ **新** | AI-research-SKILLs | `templates/colm2025/` |
| 中文期刊 | ✅ | AutoResearchClaw | 手写 ctexart 模板 |
| 系统会议 (ASPLOS/NSDI/OSDI/SOSP) | 📝 | AI-research-SKILLs | 可下载，见仓库 |

## 模板目录结构

```
references/templates/
├── aaai2026/          ← AI-research-SKILLs 吸收
│   ├── aaai2026.tex   ← 主模板
│   ├── aaai2026.sty   ← 样式
│   └── aaai2026.bst   ← 引用格式文件
├── acl/               ← AI-research-SKILLs 吸收
│   ├── acl.tex        ← 主模板（latex）
│   └── acl.sty        ← 样式
├── colm2025/          ← AI-research-SKILLs 吸收
│   ├── colm2025.tex   ← 主模板
│   └── colm2025.sty   ← 样式
├── icml2026/          ← AI-research-SKILLs 增强
│   ├── algorithm.sty  ← 算法浮动环境
│   └── algorithmic.sty← 算法伪代码排版
```

## 模板使用方式

### 国际会议
从 `references/templates/<conference>/` 获取 `.tex`、`.sty`、`.bst` 文件，复制到输出目录。

**算法格式增强（ICML/NeurIPS）**：使用 `algorithm.sty` + `algorithmic.sty` 排版伪代码：

```latex
\usepackage{algorithm, algorithmic}
\begin{algorithm}
\caption{My Algorithm}
\begin{algorithmic}
\STATE Initialize parameters
\FOR{each iteration}
\STATE Compute gradient
\STATE Update parameters
\ENDFOR
\end{algorithmic}
\end{algorithm}
```

### 中文期刊
直接使用 `ctexart` + `unsrt` BibTeX 格式：

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

## 引用验证（AI-research-SKILLs 吸收）

从 AI-research-SKILLs `ml-paper-writing` 写作哲学吸收的核心规则：

### 永不从记忆生成 BibTeX
- ✅ 用 API 搜索→验证→获取 BibTeX
- ❌ 不要从记忆中写 BibTeX 条目
- ❌ 不确定的文献标记为 `[CITATION NEEDED]` 占位符
- ❌ 找不到的文献不要编造相似的

### 占位符格式
```latex
% TODO: Verify this citation exists
\cite{PLACEHOLDER_author2024_verify_this}
```

向用户报告：*"已标记 [X] 条引用为待验证占位符。"*

## 协作写作哲学

吸收自 Orchestra Research 写作方法（Karpathy, Nanda, Farquhar 等经验）：

1. **主动交付** — 当代码库和结果清晰时，给出完整初稿，不阻塞等待各节反馈
2. **迭代改进** — 提供具体内容让科学家审阅，然后根据响应迭代
3. **反向验证** — 验证每个引用的存在性，不让AI记忆决定论文可信度

## 使用方式

在 `latex-output` SKILL.md 的执行步骤中，根据用户选择的格式确定：
- 国际会议: 从 `references/templates/<conference>/` 获取模板文件
- 中文期刊: 直接使用 `ctexart` + `unsrt` BibTeX 格式
- 需要算法排版: 加入 `\usepackage{algorithm, algorithmic}`
- 引用验证: 对每个 `.bib` 条目，至少验证 DOI 存在性
