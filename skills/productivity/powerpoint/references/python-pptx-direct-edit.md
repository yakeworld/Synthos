# python-pptx 直接编辑：快速内容替换（无需解包）

当只需修改现有 PPTX 中的文字内容（更新指标、更名章节、修正文案）时，无需解包再打包——直接用 python-pptx 按形状名称修改文本。

## 工作流

### 1. 分析形状结构

```python
from pptx import Presentation
from pptx.util import Pt

prs = Presentation('input.pptx')
for i, slide in enumerate(prs.slides):
    print(f'=== Slide {i+1} ===')
    for s in slide.shapes:
        if s.has_text_frame:
            txt = s.text_frame.text.strip()[:50]
            print(f'  {s.name} @ ({s.left},{s.top}) = "{txt}"')
```

形状名称（`shape.name`）在 WPS/PowerPoint 保存时是稳定的，可以用作标识符。

### 2. 按名称定位并修改

```python
from pptx.dml.color import RGBColor

slide = prs.slides[0]
for s in slide.shapes:
    if s.name == 'TextBox 3':  # 稳定标识符
        tf = s.text_frame
        tf.clear()
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = '新标题'
        r.font.size = Pt(24)
        r.font.color.rgb = RGBColor(0xF8, 0xFA, 0xFC)
        r.font.bold = True
        r.font.name = 'Arial'
```

### 3. 多段文本处理

```python
def set_textbox_content(shape, title, desc, title_color, desc_color):
    tf = shape.text_frame
    tf.clear()
    # 标题行
    p1 = tf.paragraphs[0]
    r1 = p1.add_run()
    r1.text = title
    r1.font.size = Pt(16)
    r1.font.color.rgb = title_color
    r1.font.bold = True
    r1.font.name = 'Arial'
    # 描述行
    p2 = tf.add_paragraph()
    r2 = p2.add_run()
    r2.text = desc
    r2.font.size = Pt(11)
    r2.font.color.rgb = desc_color
    r2.font.name = 'Arial'
```

### 4. 修改形状填充色

```python
from pptx.oxml.ns import qn

def set_fill_color(shape, hex_color):
    """Change solid fill color of a shape (e.g., accent bar)."""
    sp = shape._element
    spPr = sp.find(qn('a:spPr'))
    if spPr is not None:
        sf = spPr.find(qn('a:solidFill'))
        if sf is not None:
            srgb = sf.find(qn('a:srgbClr'))
            if srgb is not None:
                srgb.set('val', hex_color)
```

### 5. 视觉 QA

```bash
libreoffice --headless --convert-to pdf output.pptx
pdftoppm -png -r 150 output.pdf page
```

## 适用场景

| 场景 | 推荐方法 |
|:-----|:---------|
| 改文字、更新指标、修文案 | 直接编辑（本方法） |
| 改布局、换图片、调样式 | 解包 → 编辑 XML → 打包 |
| 完全新建 | pptxgenjs 或 python-pptx 从头创建 |

## 已知陷阱

- **形状名称在不同 PPT 引擎间可能不同**：WPS 生成的 `TextBox 3` 在 PowerPoint 中可能保留。先分析确认。
- **文本框边距**：`text_frame.margin_*` 属性控制内边距。如果文字剪裁，减少边距。
- **`tf.clear()` 会删除所有段落**：之后必须重新创建。不影响形状的其他属性（大小、位置、边框）。
- **字体回退**：如果指定字体不存在，渲染引擎会回退。中文字体优先用 'Arial' 或 'Noto Sans CJK SC'。
