---
name: markitdown-convert
description: Convert PDF/Office files to Markdown using Microsoft MarkItDown
version: 1.0.0
allowed-tools:
- terminal
- read_file
- write_file
- search_files
platforms:
- linux
- macos
metadata:
  synthos:
    signature: 'file_path: str -> md_path: str'
    related_skills:
    - airtable
    - chinese-form-automation
    - google-workspace
    - jupyter-live-kernel
    - linear

---



# MarkItDown → Markdown 转换

> 微软开源文档转 Markdown 工具。支持 PDF、DOCX、PPTX、Excel、图片。
> 安装: `uv tool install markitdown --with markitdown[pdf]`

## ⚠️ 强制前置：PDF→MD 是下载后的标准步骤，非可选

2026-05-31 确认：所有论文管线必须将 **PDF→Markdown 转换** 作为下载后的强制步骤。

**原因**：
- Layer B 双质检需要全文文本，仅 PDF 不可靠（NotebookLM 索引 PDF 经常 error）
- Markdown 格式在 NotebookLM 中 100% 索引成功
- `markitdown` 优于 `pdftotext`：保留数学公式（LaTeX内联）、表格结构、章节标题

**标准目录结构**：PDF 和 MD 共存，MD 放在 `pdfs_md/` 子目录：
```
06-references/
├── pdfs/           # 原始 PDF（用于 D9 验证）
│   ├── Smith1988.pdf
│   └── ...
└── pdfs_md/        # 转换后的 Markdown（用于质检 & NotebookLM）
    ├── Smith1988.md
    └── ...
```

## 批量转换参考文献 PDF（推荐脚本）

```bash
python3 << 'PYEOF'
import subprocess, os

pdf_dir = "06-references/pdfs"
md_dir = "06-references/pdfs_md"
os.makedirs(md_dir, exist_ok=True)

for f in sorted(os.listdir(pdf_dir)):
    if not f.endswith('.pdf'): continue
    bibkey = f.replace('.pdf', '')
    out = f'{md_dir}/{bibkey}.md'
    if os.path.exists(out) and os.path.getsize(out) > 100:
        continue  # 跳过已有缓存
    r = subprocess.run(['uvx', 'markitdown', f'{pdf_dir}/{f}'],
                      capture_output=True, text=True, timeout=120)
    if r.returncode == 0 and len(r.stdout) > 50:
        with open(out, 'w') as fh: fh.write(r.stdout)
        print(f'{bibkey} — {len(r.stdout):,} chars ✅')
    else:
        # Fallback: pdftotext
        r2 = subprocess.run(['pdftotext', f'{pdf_dir}/{f}', '-'],
                          capture_output=True, text=True)
        if len(r2.stdout) > 100:
            with open(out, 'w') as fh: fh.write(r2.stdout)
            print(f'{bibkey} — pdftotext ⚠️ ({len(r2.stdout):,} chars)')
        else:
            print(f'{bibkey} — ❌ 无可提取文本')
            with open(out, 'w') as fh:
                fh.write(f'# {bibkey}\n\n[PDF无法提取文本 — 需手动补摘要或走OCR]\n')
PYEOF
```

## 单文件转换

```bash
uvx markitdown input.pdf > output.md
```

## 实战成功率

| 类型 | 比例 | 说明 |
|:-----|:----:|:-----|
| 正常学术PDF | ~35/40 (87.5%) | MarkItDown 直转成功 ✅ |
| 无文本层/损坏PDF | ~5/40 (12.5%) | 需手动补摘要或走 OCR |
| arXiv PDF (旧版) | 多数 OK | 少数 2016前 PDF 无文本层 |

## 损坏PDF检测

部分下载PDF虽报告 %PDF- 头，但 xref 表破损/catalog 缺失，所有工具均无法提取文本：

```bash
# 检测方法
python3 -c "
import re
with open('file.pdf', 'rb') as f:
    content = f.read()
text_chars = sum(1 for b in content if 32 <= b < 127)
strings = re.findall(rb'[ -~]{10,}', content)
print(f'Readable chars: {text_chars}/{len(content)} ({text_chars/len(content)*100:.1f}%)')
for s in strings[:5]: print(s.decode(errors='ignore')[:80])
"

# 损坏PDF典型表现：
# - pdftotext 返回 0 字符
# - pymupdf.get_text() 返回 0 字符
# - mutool 报 "cannot find page tree"
# - file 命令报 "PDF document" 但 ImageMagick 报 "Catalog dictionary not located"
```

**处理策略**：
1. 寻找 arXiv/PMC 替代版本（多数经典论文有线上全文）
2. 手动写摘要（知名论文如 SMOTE、LIME、CRISP-DM）
3. 走 OCR 管线（`ocr-and-documents` skill）

## OCR 替代（MarkItDown 不做 OCR）

扫描版/纯图像 PDF 需走 `ocr-and-documents` skill 的 Tesseract 或 marker-pdf 管线：

```bash
# Tesseract OCR（英文）
pdftoppm -png -r 200 input.pdf /tmp/page
for f in /tmp/page-*.png; do
    tesseract "$f" "${f%.png}" -l eng
done
cat /tmp/page-*.txt > full_text.txt
```

## 论文批量转换（含引用PDF过滤）

科学论文目录常混有**自己的论文**与**参考文献PDF**。转换时必须过滤引用，否则会转错目标。

### 找主论文 PDF 的策略

按优先级：
1. **最大 PDF**（排除明显引用：`*reference*`, `*template*`, `*graphical*`）
2. **最新修改的 PDF**（revision 日期最新的）
3. **与目录名匹配的 PDF**

```bash
OUTPUTS="outputs/papers"
for paper_dir in "$OUTPUTS"/*/; do
    main_pdf=$(find "$paper_dir" -maxdepth 2 -name "*.pdf" \
        -not -iname "*graphical*" -not -iname "*template*" \
        -printf '%s\t%p\n' 2>/dev/null | sort -rn | head -1 | cut -f2)
    if [ -n "$main_pdf" ]; then
        uvx markitdown "$main_pdf" > "$paper_dir/paper.md" 2>/dev/null
    fi
done
```

**陷阱**：引用PDF命名为 `hooge2021pupil.pdf` 等作者年格式，容易被当作主论文。始终用 `-not -name` 排除已知引用模式。

### TeX 替代方案（无可用 PDF 时）

```bash
cd "$tex_source_dir"
pandoc paper.tex -f latex -t markdown --wrap=none --mathjax -o paper.md
```

⚠️ 从源文件目录执行 pandoc，否则 `.bib` 引用解析失败。

## 依赖

- Python 3.10+, uv
- `uv tool install markitdown --with markitdown[pdf]`
- 不加 `[pdf]` extra 会报 `MissingDependencyException`

## 转换后处理：添加 Obsidian frontmatter

生成的 `paper.md` 缺少 YAML frontmatter，Obsidian 无法识别标签/别名。转换完成后补充：

```bash
python3 -c "
import os
path = 'paper.md'
with open(path) as f: content = f.read()
if not content.startswith('---'):
    fm = '''---
tags: [paper, your-tags-here]
aliases: [Paper Title]
---

'''
    with open(path, 'w') as f: f.write(fm + content)
"
```

## 已知限制

- 数学公式 → LaTeX 内联文本，非渲染格式
- 表格可能展平
- 多栏 PDF 需额外处理
- **MarkItDown 无 OCR** — 扫描版 PDF 走 `ocr-and-documents` skill

## 相关文件

- `references/synthos-paper-conversion-2026-05-27.md` — 本会话的 8 篇论文转换记录
