# PDF 末页替换为盖章扫描件

## 场景
证明材料已打印盖章后，需要将最后一页替换为含公章的扫描件（图片/PDF）。

## 前置检查
```bash
# 原PDF页数
pdfinfo Synthos_证明材料.pdf | grep Pages

# 盖章扫描件信息
file 盖章页.jpg
# 预期：JPEG, A4比例, 150dpi+
```

## 工作流

### 1. 扫描件是图片 → 转换为A4 PDF
```bash
# 方法A：ImageMagick（推荐，可控尺寸）
convert 盖章页.jpg -resize 2480x3508 \
  -background white -gravity center -extent 2480x3508 \
  stamp_fixed.png
convert stamp_fixed.png -page A4 stamp_page.pdf

# 方法B：直接img2pdf（保持原尺寸）
img2pdf 盖章页.jpg -o stamp_page.pdf
```

### 2. 替换末页（pdftk）
```bash
# 原PDF保留前N-1页 + 盖章页
pdftk A=原材料.pdf B=stamp_page.pdf \
  cat A1-$(N-1) B1 \
  output 新材料_带章.pdf
```

### 3. 验证
```bash
pdfinfo 新材料_带章.pdf | grep -E "Pages|Page size"
# Pages应为N（与原著相同）
# Page size应为A4（595.28 x 841.89 pts）
```

## 典型案例
```
原：Synthos_证明材料.pdf（5页）
盖章页：用户发送的扫描图片
命令：pdftk A=原.pdf B=盖章.pdf cat A1-4 B1 output 带章.pdf
结果：5页，第5页替换为盖章扫描件
```

## 注意事项
- 扫描件分辨率至少150dpi，200dpi更安全
- ImageMagick `convert` 的 `-extent` 保证A4比例，防止打印错位
- 盖章页和原PDF页面大小必须一致（均为A4），否则打印时会错位
- pdftk会丢弃原PDF的元数据（创建时间等），不影响内容
- 如果盖章扫描件本身是多页PDF（如2页签章），选择正确的页码替换
