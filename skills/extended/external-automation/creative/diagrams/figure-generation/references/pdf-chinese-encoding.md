# PDF 中文编码修复 — pandoc + xelatex + ctex header

## 核心问题

pandoc 生成 PDF 时，中文默认用 LaTeX Latin 字体（lmroman10-regular），不支援 CJK 字符 → 输出 PDF 中文乱码（方框/乱码）。

## 解决方案

### 方法：pandoc + xelatex + ctex header（唯一可靠方法）

```bash
# 步骤 1：创建包含 ctex 包的 header 文件
cat > /tmp/chinese-header.tex << 'EOF'
\usepackage{ctex}
\setCJKmainfont{Noto Sans CJK SC}
\setCJKsansfont{Noto Sans CJK SC}
EOF

# 步骤 2：用 header 生成 PDF
pandoc input.md -o output.pdf \
  --pdf-engine=xelatex \
  -H /tmp/chinese-header.tex \
  2>&1 | grep -v "Missing character" | tail -5

# 步骤 3：验证中文
pdftotext output.pdf output.txt
python3 -c "
with open('output.txt', 'r', encoding='utf-8') as f:
    t = f.read()
print('中文正常:', '关键词' in t)
"
```

### 为什么这个方法有效

- `-H` 指定 LaTeX header，`ctex` 包自动处理 CJK 字体加载
- `--pdf-engine=xelatex` 使用 XeLaTeX（原生 Unicode 支持）
- `setCJKmainfont` 指定中文字体（Noto Sans CJK SC 在系统中）

### 常见错误

1. **不加 `-H` header** → PDF 中文乱码（最常见错误）
2. **使用 `pdflatex` 而不是 `xelatex`** → 需要额外配置 CJK 包
3. **加了 `-V documentclass=ctexart`** → 会导致 `\ifXeTeX` 错误（MiKTeX 兼容性问题）
4. **使用 `wkhtmltopdf`** → 不支持中文（安装失败）

### 验证中文正常

用 `pdftotext` 读取 PDF 提取中文，检查关键词：

```bash
pdftotext output.pdf -  # 输出到 stdout
# 或用 python3 读取文件检查
```

如果 `pdftotext` 读取中文正常（如"瞳孔""温州""技术"等关键词存在），则 PDF 中文编码正确。

### 已知警告（可忽略）

```
[WARNING] Missing character: There is no ✅ (U+2705) in font [lmroman10-regular]
[WARNING] Missing character: There is no ≥ (U+2265) in font [lmroman10-regular]
```

这些是 LaTeX 默认拉丁字体不支持 emoji 和数学符号的警告，不影响中文。可以 `grep -v "Missing character"` 过滤。

## 参考

- 来源：本 session 中为瞳孔形态检测技术综述生成中文 PDF 时的经验
- 中文字体路径：`/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc`
- MiKTeX 版本：4.10 (MiKTeX 22.1)
- pandoc 版本：系统自带
