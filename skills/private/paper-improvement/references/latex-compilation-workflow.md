# LaTeX 编译工作流

## 标准 5 轮编译

```bash
cd /path/to/paper/directory

# 1. 清理辅助文件
rm -f *.aux *.bbl *.blg *.log *.out *.toc

# 2. 第 1 轮：pdflatex（生成 .aux）
pdflatex -interaction=nonstopmode paper.tex

# 3. 第 2 轮：bibtex（生成 .bbl）
bibtex paper.aux

# 4. 第 3-5 轮：pdflatex（解析引用，稳定）
pdflatex -interaction=nonstopmode paper.tex
pdflatex -interaction=nonstopmode paper.tex
pdflatex -interaction=nonstopmode paper.tex
```

## 质量检查

```bash
# 检查错误
grep -i 'Error' paper.log          # 应为 0
grep -i 'undefined' paper.log      # 引用警告，应为 0

# 检查 PDF
ls -lh paper.pdf                   # 通常 8-15 页
```

## Python 自动化

```python
import subprocess, os, glob

paper_dir = "/path/to/paper"
os.chdir(paper_dir)

# 清理
for f in glob.glob("paper.*"):
    if f != "paper.tex": os.remove(f)

# 5 轮编译
for i, cmd in enumerate([
    ["pdflatex", "-interaction=nonstopmode", "paper.tex"],
    ["bibtex", "paper.aux"],
    ["pdflatex", "-interaction=nonstopmode", "paper.tex"],
    ["pdflatex", "-interaction=nonstopmode", "paper.tex"],
    ["pdflatex", "-interaction=nonstopmode", "paper.tex"],
]):
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(f"Round {i}: exit={r.returncode}")
```

## 常见错误速查

| 错误 | 原因 | 修复 |
|------|------|------|
| `! Undefined control sequence` | 反斜杠污染 | 全局替换 `\\\\` → `\` |
| `Package natbib Warning: Citation undefined` | .bbl 未生成 | 先跑 bibtex |
| `File 'xxx.sty' not found` | 缺少 LaTeX 包 | `tlmgr install xxx` |
| `LaTeX Error: Too many unprocessed floats` | 图片过多 | 调整 float 位置 |
| `Overfull \hbox` | 行溢出 | 调整排版或换行 |