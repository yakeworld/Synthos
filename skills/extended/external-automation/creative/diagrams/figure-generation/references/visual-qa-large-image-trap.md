# Visual QA Large Image Trap (2026-06-27)

vision_analyze returns Qwen3VLProcessor 400 error for images wider than 2000px.

## Example

Breast cancer paper hcs3wt-breast-cancer 05-figures/:

| Image | Original Size | Error |
|-------|--------------|-------|
| fig2_roc_curves.png | 2658x2208 | 400 |
| fig3_confusion_matrices.png | 4406x2562 | 400 |
| fig4_feature_importance.png | 3257x2210 | 400 |

## Fix

Resize to <=1200px width before vision_analyze:

```python
from PIL import Image
img = Image.open(path)
if img.width > 1200:
    ratio = 1200 / img.width
    img = img.resize((1200, max(1, int(img.height * ratio))), Image.LANCZOS)
    img.save('/tmp/resized.png', 'PNG')
    path = '/tmp/resized.png'
```

## Consequence

Without resizing, vision_analyze fails completely and visual QA cannot proceed.