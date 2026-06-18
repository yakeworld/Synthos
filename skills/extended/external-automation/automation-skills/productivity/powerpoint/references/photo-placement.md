# 照片替换模式

## 从占位框到真实照片

```python
# 1. 读取原始尺寸
from PIL import Image
img = Image.open(photo_path)
iw, ih = img.size

# 2. 计算可用区域
area_w, area_h = 4.5, 3.2  # 英寸
area_ratio = area_w / area_h
img_ratio = iw / ih

# 3. 等比缩放（不变形）
if img_ratio > area_ratio:
    w, h = area_w, area_w / img_ratio  # 宽度填满
else:
    h, h = area_h, area_h * img_ratio  # 高度填满

# 4. 居中放置
left = area_left + (area_w - w) / 2
top = area_top + (area_h - h) / 2

s.shapes.add_picture(photo_path, Inches(left), Inches(top), Inches(w), Inches(h))
```

## 常见图片尺寸

| 图片类型 | 典型比例 | 缩放策略 |
|:---------|:---------|:---------|
| 证件照 | 2:3 竖版 | 高度填满，左右留白 |
| 系统封面 | 16:9 横版 | 宽度填满 |
| 设备实物 | 4:3 或 3:4 | 按比例缩放 |
| 论文图表 | 16:9 或自定义 | 宽度填满，高度自适应 |

## 陷阱

- 直接设 `Inches(4.5)` 宽 + `Inches(3.2)` 高 → 强制拉伸变形
- 必须先用 PIL 读取原图尺寸再计算等比尺寸
