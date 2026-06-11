# Photo Placeholder Replacement in PPTX

## Pattern

When a PPT design spec includes a photo placeholder (e.g., "彩色职业正装照"), replace it with the actual image file using `shapes.add_picture()`.

## Code

```python
# BEFORE (placeholder):
rc(s, Inches(x), Inches(y), Inches(w), Inches(h), CARD_BG, BORDER, 1)
tx(s, Inches(x+0.5), Inches(y+1.0), Inches(w-1), Inches(0.4),
   "[ 彩色职业正装照 ]", sz=14, cl=DIM, al=PP_ALIGN.CENTER)

# AFTER (real photo):
s.shapes.add_picture("/path/to/photo.jpg", Inches(x), Inches(y), Inches(w), Inches(h))
```

## Verification

After generation, check the PPTX zip structure:

```python
import zipfile, re
with zipfile.ZipFile('output.pptx', 'r') as z:
    imgs = [f for f in z.namelist() if 'image' in f.lower()]
    print(f"Images embedded: {len(imgs)}")  # should be > 0
    # Verify slide references the image
    rels = z.read('ppt/slides/_rels/slideN.xml.rels').decode()
    print(f"Has image ref: {'image' in rels}")
```

## Pitfalls

- Photo must be a real file accessible from the Python runtime
- `add_picture` position/size uses same `Inches()` coordinate system as shapes
- **⚡ 等比缩放（P0）**: `add_picture(w, h)` 直接拉伸会变形。必须先用 PIL 读原始尺寸，按占位区宽高计算等比 fit，居中放置：
  ```python
  from PIL import Image
  img = Image.open(photo_path)
  img_ratio = img.size[0] / img.size[1]
  area_w, area_h = 4.5, 3.2  # 占位区
  if img_ratio > area_w / area_h:  # 宽幅：fit width
      w, h = area_w, area_w / img_ratio
  else:  # 竖幅：fit height
      h, area_h; w = area_h * img_ratio
  left = area_left + (area_w - w) / 2  # 水平居中
  top = area_top + (area_h - h) / 2
  s.shapes.add_picture(photo_path, Inches(left), Inches(top), Inches(w), Inches(h))
  ```
- Remove both the placeholder rect AND the placeholder text when replacing
