# SVG → PNG 转换陷阱

## 问题

cairosvg 在转换含 `<marker>` 节点的 SVG（如带箭头的折线图、流程图）时会报错：

```
libsvg2.Error: svgparser.c:1205: SVG_ATTRIBUTE_START_LINE: unexpected end of tag
```

这是 cairosvg 对 SVG marker 节点解析的已知缺陷。

## 解决方案

使用 ImageMagick `convert` 命令：

```bash
# 高质量转换（300 DPI，适合论文/报告）
convert -density 300 input.svg output.png

# 调整尺寸（小红书封面 1200x1500）
convert -density 300 -resize 1200x1500 input.svg output.png

# 快速预览（72 DPI）
convert -density 72 input.svg output.png
```

## 验证

```bash
# 确认文件存在且可读
file output.png
# 确认尺寸
identify output.png
```

## 注意

- ImageMagick 7 版本命令可能是 `magick convert` 而非 `convert`
- 确保已安装：`sudo apt install imagemagick`
- convert 保留 SVG 原始矢量质量，无 cairosvg 的解析问题
- 适合场景：SVG 箭头/标记、复杂路径、渐变效果
