# PDF 编译流程 — step_*.md → .tex → .pdf

## 前提条件
- paper_dir: 论文目录下的 01-manuscript/ 目录
- 所有 step_*.md 文件已存在
- MiKTeX 已安装（`pdflatex` 在 PATH 中）

## 流程

### 步骤 1: 组装 .tex
```bash
python3 /media/yakeworld/sda2/Synthos/skills/writing/latex-output/scripts/assemble_pdf_from_steps.py <paper_dir>
```

或手动：
```bash
cd <paper_dir>
python3 -c "
import os, glob
tex = r'\documentclass[11pt]{article}\\usepackage{amsmath,amssymb,graphicx,url,hyperref,booktabs,geometry}\\geometry{margin=1in}\\begin{document}\n'
for f in sorted(glob.glob('step_*.md')):
    in_latex = False
    with open(f) as fh:
        for line in fh:
            if '```latex' in line: in_latex = True; continue
            if '```' in line: in_latex = False; continue
            if in_latex: tex += line + '\n'
tex += '\\end{document}'
open('paper.tex','w').write(tex)
print(f'Wrote {len(tex)} chars')
"
```

### 步骤 2: 编译 PDF
```bash
cd <paper_dir>
pdflatex -interaction nonstopmode paper.tex  # ← 注意：nonstopmode 无下划线
pdflatex -interaction nonstopmode paper.tex  # 第二次消除 cross-reference warnings
```

### 步骤 3: 验证
```bash
ls -la paper.pdf  # 确认输出
file paper.pdf    # 确认 PDF 格式
```

## 已知问题
- MiKTeX 22.1 使用 `nonstopmode`（无下划线），不是 `nonstop_mode`
- 首次编译可能有 warning，第二次消除
- 若 PDF 为空或 0 页，检查 step_*.md 中 LaTeX 块是否正确闭合（```latex ... ```）
