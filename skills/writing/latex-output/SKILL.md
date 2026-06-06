---
name: latex-output
description: >-
  Synthos assembled_output.json → 会议级LaTeX (.tex/.bib/figures)。
metadata:
  synthos:
    version: 1.1.0
    author: Synthos
---

# Latex Output

详细内容请加载此skill后按需执行。核心流程和命令已提炼如下：

## 快速参考

详细文档和完整命令列表已被移至 `references/` 目录以保持简洁。

## Pitfalls

### MiKTeX interaction mode
- 此环境使用 MiKTeX 22.1（路径 `/usr/local/bin/pdflatex`），参数为 `-interaction nonstopmode`（无下划线）
- 错误写法：`pdflatex -interaction nonstop_mode paper.tex` → FATAL exit code 1
- 正确写法：`pdflatex -interaction nonstopmode paper.tex`

### 步骤组装顺序
- 从 step_*.md 组装 .tex 时，按 IMRaD 顺序提取 LaTeX 内容：
  gap_analysis → abstract → intro → method → results → discussion
- 使用 `pdflatex` 编译一次后检查 `.log`，有 warning 可再跑一次消除 cross-reference 问题
- 可选步骤（ref_check、quality_check）在讨论之后添加，用 `\\section{}` 包裹纯文本

### 文件名约定与原始 LaTeX
- 脚本 `assemble_pdf_from_steps.py` 期望短文件名（`step_intro.md`）和 fenced LaTeX 代码块（```latex ... ```）
- 手动 cron 写作常产生长文件名（`step_introduction.md`）和原始 LaTeX 数学符号（`$$...$$`）
- 格式不匹配时，脚本产生空 .tex。使用 `references/manual-assembly-workflow.md` 中的手动组装模式
- 或创建符号链接：`ln -s step_introduction.md step_intro.md`

## 支持文件

- `references/BIBTEX_FORMAT.md` — BibTeX citation format standard
- `references/CONFERENCE_TEMPLATES.md` — Conference-specific LaTeX templates
- `scripts/assemble_pdf_from_steps.py` — 从 step_*.md 自动组装 .tex 并编译 PDF
- `references/manual-assembly-workflow.md` — 手动组装：长文件名（step_introduction.md）和原始 LaTeX 数学的替代方案