---
name: markitdown-convert
description: markitdown-convert
version: 1.0.0
category: productivity
signature: 'markitdown-convert -> productivity: Convert PDF/Office files to Markdown
  using Microsoft MarkItDown'
author: Synthos
license: MIT
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


## Operational Steps
1. 确认输入参数完整
2. 执行核心操作（参考本目录下的 scripts/ 或 references/）
3. 验证输出符合契约
4. 保存结果并报告

## Pitfalls
- 
- 

## Verification
- 
- 
- 
- 
1. 
2. 
3. 

## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）

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

pdf_dir = "06-ref/pdfs"
md_dir = "06-ref/pdfs_md"
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
|: