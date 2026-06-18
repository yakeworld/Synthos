---
name: latex-output
related_skills: ["argument-expression"]
description: >-
version: 1.0.0
  Synthos assembled_output.json → 会议级LaTeX (.tex/.bib/figures)。
metadata:
  synthos:
    version: 1.1.0
    author: Synthos

---

## IO_CONTRACT

- **input**: `content: str, format: str` — 用户请求描述、上下文信息
- **output**: `latex_output: str — LaTeX排版`

> 对应原则：P2（机械原子暴露输入输出规范）

> 对应原则：P2（机械原子暴露输入输出规范）



# Latex Output

详细内容请加载此skill后按需执行。核心流程和命令已提炼如下：

## 快速参考

详细文档和完整命令列表已被移至 `references/` 目录以保持简洁。

## Pitfalls

### MiKTeX interaction mode
- 此环境使用 MiKTeX 22.1（路径 `/usr/local/bin/pdflatex`），参数为 `-interaction nonstopmode`（无下划线）
- 错误写法：`pdflatex -interaction nonstop_mode paper.tex` → FATAL exit code 1
- 正确写法：`pdflatex -interaction nonstopmode paper.tex`

### pdflatex Font Expansion Error (Cron Environment)
- **现象**: `pdflatex` 编译失败，报错 `! pdfTeX error (font expansion): auto expansion is only possible with scalable fonts`，当 `paper.tex` 包含 `\usepackage{microtype}` 时。
- **根因**: Cron 环境中的 CM 字体（Computer Modern）不是可缩放字体，microtype 的字体扩展功能不可用。
- **修复**: 从 paper.tex 中移除 `\usepackage{microtype}`。这是所有 cron 环境 LaTeX 编译的已知限制。
- **影响**: 移除 microtype 不影响 PDF 内容质量，仅影响字距调整——对 SCI 论文质量无实质影响。
- **已知**: 2026-06-09 Paper 117 (orthokeratology-corneal-ODE) 首次遭遇此问题，移除后成功编译。

### Citation Counting Convention
- In-text equations: 直接嵌入正文段落中的 `\text{...}` 或行内公式，不计入 displayed equations 计数
- Displayed equations: `equation` 环境中的公式，每行一个计数
- 典型分布: 2-3 个 displayed equations + 0-2 个 in-text equations（paper.tex 中用 text 标注）
- 示例 Paper 117: 2 equations in text, 2 displayed equations, 7 tables, 17 references

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

### Unescaped `$` in Text Mode (2026-06-12)
- **现象**: `LaTeX Error: Command \end{abstract} invalid in math mode`
- **根因**: 文本模式中的 `$`（如 `$15 billion`、`$15B+`）被解释为进入数学模式，导致 `\end{abstract}` 在数学模式下被调用。
- **修复**: 转义所有文本中的货币符号：`\$15 billion` 而非 `$15 billion`。
- **检测方法**: 编辑后扫描 `grep -n '\$[0-9]' paper.tex`，修复所有 `\$数字` 模式。
- **已知**: 2026-06-12 Paper 137 (ciliary-body-ODE) 首次遭遇，abstract 中 `$15 billion` 导致编译失败。

## 支持文件

- `references/BIBTEX_FORMAT.md` — BibTeX citation format standard
- `references/CONFERENCE_TEMPLATES.md` — Conference-specific LaTeX templates
- `scripts/assemble_pdf_from_steps.py` — 从 step_*.md 自动组装 .tex 并编译 PDF
- `references/manual-assembly-workflow.md` — 手动组装：长文件名（step_introduction.md）和原始 LaTeX 数学的替代方案