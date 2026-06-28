# MD→PDF 编译管线（xelatex + 中文字体）

## 背景
质量检查报告以 Markdown 格式存储在 `07-quality/` 目录。需转换为 PDF 交付给用户。

## 坑

1. **emoji 不可见** — xelatex 的 LaTeX 字体不含 emoji，渲染为空白。必须先替换：
   - `✅` → `[PASS]`
   - `❌` → `[FAIL]`
   - `⚠️` → `[WARN]`
   - `🟡` → `[P1]`
   - `🟢` → `[P2]`

2. **LaTeX 特殊字符** — `|`、`_`、`&`、`%`、`#`、`{}`、`~`、`^`、`\` 在 md 中正常，在 tex 中需转义。但表格分隔线（`|---|`）行不转义，否则表格损坏。

3. **文件太大** — PPTX 转 PDF 可能 30-80MB。飞书 MEDIA 附件 >10MB 静默失败。必须用 Ghostscript 压缩到 ≤10MB。

## 流程

### Step 1: 清理 Markdown
```python
# Read MD
content = open('report.md', 'r', encoding='utf-8').read()

# Replace emoji with text markers
content = content.replace('\u2705', '[PASS]')
content = content.replace('\u274c', '[FAIL]')
content = content.replace('\u26a0\ufe0f', '[WARN]')

# Escape LaTeX special chars (but NOT table delimiter lines)
escape_chars = [('_', r'\_'), ('&', r'\&'), ('%', r'\%'),
                ('#', r'\#'), ('{', r'\{'), ('}', r'\}'),
                ('~', r'\~{}'), ('^', r'\^{}')]

for line in content.split('\n'):
    if line.strip().startswith('|---') or line.strip().startswith('|--'):
        # Skip table delimiters
        continue
    elif line.startswith('|'):
        # Light escape for table content
        escaped = line.replace('&', r'\&').replace('_', r'\_')
    else:
        escaped = line
        for ch, esc in escape_chars:
            escaped = escaped.replace(ch, esc)
```

### Step 2: Generate TeX wrapper
```latex
\documentclass[10pt]{article}
\usepackage[margin=1.5cm]{geometry}
\usepackage{fontspec}
\usepackage{ctex}
\usepackage{xcolor}
\usepackage{longtable}
\usepackage{booktabs}
\usepackage{hyperref}
\setCJKmainfont{Noto Sans CJK SC}
\hypersetup{colorlinks=false}
\renewcommand{\arraystretch}{1.1}
\setlength{\tabcolsep}{3pt}
\pagestyle{empty}
\begin{document}
\input{/tmp/report_clean.md}
\end{document}
```

### Step 3: Compile
```bash
xelatex -interaction=nonstopmode report.tex 2>&1 | tail -5
# Output: "Output written on report.pdf (N pages)."
```

### Step 4: Compress (if needed)
```bash
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/screen \
   -dNOPAUSE -dQUIET -dBATCH \
   -sOutputFile=report_compressed.pdf report.pdf
# Typical: 33MB → 2.4MB
```

### Step 5: Copy to stable path
```bash
cp report_compressed.pdf ~/report.pdf
# Send via MEDIA:/home/yakeworld/report.pdf
```

## 文件路径规范
- 中间文件放 `/tmp/`（session 临时）
- 最终文件放 `~/` 或 `/media/`（稳定路径，MEDIA 可访问）
- 绝不放 `/tmp/` 给用户发送 MEDIA — Hermes MEDIA 处理器可能无法访问

## 替代方案
- `pandoc` 可能缺少中文字体支持
- `pdflatex` 不支持 Unicode/CJK
- `xelatex` 是最佳选择：原生 Unicode + CJK 支持
