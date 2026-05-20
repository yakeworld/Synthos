---
name: latex-output
version: 1.1.0
author: Synthos + Nous Research
description: Convert Synthos assembled_output.json into conference-ready LaTeX (.tex, .bib, figures). Supports NeurIPS/ICLR/ICML/AAAI/ACL/COLM templates + Chinese journal formats. Agent-native — reads JSON, writes LaTeX directly, zero Python.
license: MIT
metadata:
  synthos_atom_type: "output"
  synthos_version: "1.1.0"
  synthos_skill_md_hash: "pending"
  synthos_model_tested_on: "2026-05-18T00:00:00Z"
  synthos_depends_on: "argument-expression, knowledge-acquisition"
  synthos_author: "Synthos + AutoResearchClaw absorption + AI-research-SKILLs enhancement"
  synthos_absorbed_from: "AutoResearchClaw (base) + Orchestra Research AI-research-SKILLs (AAAI/ACL/COLM模板, algorithm包, 写作哲学)"
allowed-tools: terminal read_file write_file
---

# LaTeX 输出 — 从 Synthos 到会议论文

> 吸收自 AutoResearchClaw `researchclaw/templates/` (conference.py + converter.py + styles/)

## 概述

读取 argument-expression (atom5) 输出的章节内容和 knowledge-acquisition 的引用列表，
生成完整的 LaTeX 论文包：

```
outputs/runs/<run_id>/latex/
├── paper.tex                    ← 完整论文（含 abstract, intro, method, experiments, results, conclusion）
├── references.bib               ← BibTeX 引用（从检索到的论文生成，经验证）
├── figures/                     ← 图表（如有）
├── neurips_2025.sty             ← 会议模板
├── build.sh                     ← 一键编译
└── paper.pdf                    ← 编译结果（可选，需要 LaTeX 环境）
```

## 支持的输出格式

| 格式 | 目标 | 模板来源 |
|------|------|---------|
| NeurIPS 2025 | 国际 ML 会议 | AutoResearchClaw `styles/neurips_2025.sty` |
| ICLR 2026 | 国际表征学习会议 | AutoResearchClaw `styles/iclr_2026.sty` |
| ICML 2026 | 国际 ML 会议 | AutoResearchClaw `styles/icml_2026.sty` |
| AAAI 2026 | AI 会议（新） | AI-research-SKILLs `templates/aaai2026/` |
| ACL | 计算语言学（新） | AI-research-SKILLs `templates/acl/` |
| COLM 2025 | 语言建模（新） | AI-research-SKILLs `templates/colm2025/` |
| 中文期刊模板 | 中文核心期刊 | Agent 按规范手写 |

## 输入

从 `<run_dir>/` 读取：
1. `argument-expression_output.json` — 论文章节内容（sections[], arguments[], references[]）
2. `knowledge-acquisition_output.json` — 原始论文列表（含 citation_verification）
3. `assembled_output.json` — 汇总数据（标题、摘要、假设）

## 执行步骤

### 1. 读取输出并提取内容

```json
{
  "title": "论文标题",
  "abstract": "摘要内容（来自 hypothesis-generation 或 argument-expression）",
  "sections": [
    {"heading": "Introduction", "content": "...#"},
    {"heading": "Related Work", "content": "...#"},
    {"heading": "Method", "content": "...#"},
    {"heading": "Experiments", "content": "...#"},
    {"heading": "Results", "content": "...#"},
    {"heading": "Conclusion", "content": "...#"}
  ],
  "authors": ["Author A", "Author B"],  // 非必填，默认为空
  "references": [
    {"key": "yoo2024", "title": "...", "authors": ["..."], "year": 2024, "journal": "...", "doi": "10.xxx"}
  ]
}
```

### 2. 生成 LaTeX 正文

Agent 用 `write_file()` 写入 LaTeX 内容。关键转换规则：

| Markdown | LaTeX |
|----------|-------|
| `# Section` | `\section{Section}` |
| `## Subsection` | `\subsection{Subsection}` |
| `**bold**` | `\textbf{bold}` |
| `*italic*` | `\textit{italic}` |
| `$$ formula $$` | `\[ formula \]` |
| `$ inline $` | `\( inline \)` |
| `[citation]` | `\cite{key}` |
| `- item` | `\item item` |
| `` `code` `` | `\texttt{code}` |

**不要使用任何 Python 库**。Agent 直接用 `write_file()` 逐行生成 .tex 内容。

### 3. 生成 BibTeX 引用

对每篇参考文献生成 BibTeX 条目：

```bibtex
@article{yoo2024,
  title={Development of an innovative approach using portable eye tracking to assist ADHD screening},
  author={Yoo, J. H. and Kang, ChangSu and Lim, Joon S. and others},
  journal={Frontiers in Psychiatry},
  year={2024},
  volume={15},
  pages={1337595},
  doi={10.3389/fpsyt.2024.1337595}
}
```

只包含 `citation_verification.status == "verified"` 的论文。

### 4. 编写编译脚本

```bash
#!/bin/bash
# build.sh — 一键编译
pdflatex paper.tex
bibtex paper
pdflatex paper.tex
pdflatex paper.tex
```

## 输出格式

```
outputs/runs/<run_id>/latex/
├── paper.tex
├── references.bib
├── neurips_2025.sty              (若有)
├── build.sh
└── paper.pdf                     (编译后)
```

## 已知陷阱

### 1. 不要手动编写模板 .sty 文件
模板文件需要精确匹配会议格式。用 AutoResearchClaw 的现有样式文件，
或直接从会议官网下载（URL 在注释中提供）。

### 2. 中文期刊的特殊处理
中文期刊需要 `ctex` 宏包和 CJK 支持：
```latex
\documentclass[UTF8]{ctexart}
\usepackage{cite}
\usepackage{hyperref}
```
不需要 `neurips_2025.sty` 等会议模板。

### 3. LaTeX 命令长度限制
某些系统上 `pdflatex` 有命令长度限制。如果遇到 `! TeX capacity exceeded`，
增加 `extra_mem_bot` 或改用 `lualatex`。

### 4. 中文文献的 BibTeX
中文作者名可能含拼音。BibTeX 处理中文作者时用 `{}` 保护：
```bibtex
author = {{杨}晓凯 and {王}小明}
```

### 5. 公式复制
argument-expression 输出的数学公式（LaTeX 格式）直接透传，
不需要额外转换。

## 触发条件

当以下任一条件满足时，应加载本技能：

- 用户要求将论文内容导出为LaTeX格式
- 用户需要生成会议/期刊模板的 .tex 文件（NeurIPS/ICLR/ICML/中文期刊）
- 需要从 assembled_output.json 生成完整的论文包（paper.tex + references.bib + build.sh）
- 用户需要论文编译、格式调整或LaTeX修复
- 需要将 Markdown 内容转换为 LaTeX 语法

**不加载的时机**：
- 仅需要图表生成（使用 figure-generation 技能）
- 仅需要参考文献检索（使用 knowledge-acquisition 技能）
- 需要的是 Word/PPT/HTML 等非 LaTeX 格式输出
- 论文内容尚未完成论证构建（先使用 argument-expression 技能）

## 验证清单

执行前确认：

- [ ] assembled_output.json 已就绪（含 title, abstract, sections, references）
- [ ] 目标输出格式已明确（NeurIPS / ICLR / ICML / 中文期刊 / 自定义）
- [ ] 参考文献引用已验证状态为 "verified"
- [ ] 图表文件（如有）已就绪，路径已确认
- [ ] 会议模板 .sty 文件可用或可从官网获取

执行后确认：

- [ ] paper.tex 已生成，无 LaTeX 语法错误
- [ ] references.bib 已生成，仅包含已验证引用
- [ ] Markdown→LaTeX 转换正确（`#` → `\section`, `##` → `\subsection`, `**` → `\textbf` 等）
- [ ] 数学公式已正确透传（`$$` → `\[ \]`, `$` → `\( \)`）
- [ ] 图表引用已使用 `\includegraphics` 并设置正确路径
- [ ] 中文期刊使用 `ctex` 宏包，非中文会议使用对应 .sty 模板
- [ ] build.sh 已生成，可一键编译
- [ ] 编译脚本不依赖特定用户环境（使用 pdflatex/bibtex/lualatex 标准命令）

## 参考
- AutoResearchClaw `researchclaw/templates/conference.py` — 会议模板定义
- AutoResearchClaw `researchclaw/templates/converter.py` — Markdown→LaTeX 转换
- AutoResearchClaw `researchclaw/overleaf/formatter.py` — Overleaf 兼容格式化
- AutoResearchClaw `researchclaw/templates/styles/` — 模板 .sty 文件
