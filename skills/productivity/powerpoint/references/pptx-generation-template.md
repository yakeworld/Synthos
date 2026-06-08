# PPTX Generation — 结构化多页PPTX模板模式

**Date discovered:** 2026-06-08  
**Class of tasks:** 结构化PPTX生成（竞赛答辩、项目申报、汇报）

## 模式

适用于需要统一风格、多页、中文内容的PPTX生成。比 `nature-paper2ppt` 更灵活（不依赖论文，面向自定义内容）。

### 核心模板

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

prs = Presentation()
prs.slide_width = Inches(13.33)
prs.slide_height = Inches(7.5)

# 1. 定义配色 palette
NAVY = RGBColor(0x0A, 0x16, 0x28)
DARK_BLUE = RGBColor(0x10, 0x2A, 0x5C)
TEAL = RGBColor(0x00, 0x96, 0x88)
GREEN = RGBColor(0x2E, 0x7D, 0x32)
BLUE = RGBColor(0x15, 0x65, 0xC0)
GOLD = RGBColor(0xFF, 0xB3, 0x00)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY = RGBColor(0xF5, 0xF5, 0xF5)
MID_GRAY = RGBColor(0xE0, 0xE0, 0xE0)
DARK_GRAY = RGBColor(0x33, 0x33, 0x33)
TOTAL = 14
FN = 'Microsoft YaHei'

# 2. 定义 helper 函数（复用）
def add_bg(slide, color):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color

def shp(slide, l, t, w, h, fc, lc=None):
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, l, t, w, h)
    s.fill.solid()
    s.fill.fore_color.rgb = fc
    if lc: s.line.color.rgb = lc; s.line.width = Pt(1)
    else: s.line.fill.background()
    return s

def tb(slide, l, t, w, h, text, sz=14, c=WHITE, b=False, a=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(l, t, w, h)
    tf = box.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text; p.font.size = Pt(sz); p.font.color.rgb = c
    p.font.bold = b; p.font.name = FN; p.alignment = a
    return box

def mkcard(slide, l, t, w, h, title, items, tc=TEAL, bg=WHITE):
    c = shp(slide, l, t, w, h, bg, MID_GRAY)
    tf = c.text_frame; tf.word_wrap = True
    tf.margin_left = Emu(91440); tf.margin_top = Emu(45720)
    tf.margin_right = Emu(45720); tf.margin_bottom = Emu(45720)
    p = tf.paragraphs[0]; p.text = title; p.font.size = Pt(14)
    p.font.color.rgb = tc; p.font.bold = True; p.font.name = FN; p.space_after = Pt(6)
    for i, item in enumerate(items):
        p = tf.add_paragraph() if i > 0 else tf.paragraphs[0]
        p.text = item; p.font.size = Pt(11); p.font.color.rgb = DARK_GRAY
        p.font.name = FN; p.space_before = Pt(3); p.space_after = Pt(3)
    return c

def footer(slide):
    tb(slide, Inches(0.5), Inches(7.0), Inches(12), Inches(0.4),
       "INSTITUTION_NAME_PLACEHOLDER | 神内团队", 9, RGBColor(0x88,0x88,0x88), a=PP_ALIGN.LEFT)
def snum(slide, n):
    tb(slide, Inches(12.3), Inches(7.0), Inches(0.8), Inches(0.4),
       "%d/%d" % (n, TOTAL), 9, RGBColor(0x88,0x88,0x88), a=PP_ALIGN.RIGHT)
def header(slide):
    shp(slide, Inches(0), Inches(0), Inches(13.33), Inches(0.06), TEAL)
```

### 执行

```bash
# 写文件 → 用系统Python执行（sandbox venv无python-pptx）
/usr/bin/python3 /home/yakeworld/gen_pptx.py
```

### 新增幻灯片布局陷阱

**`prs.slides.add_slide()` 必须有 layout 参数**。空 presentation 使用 `prs.slide_layouts[6]`（BLANK 布局）：

```python
prs = Presentation()  # 全新PPT，无预设layout
slide = prs.slides.add_slide(prs.slide_layouts[6])  # [6] = BLANK
```

已有PPT打开后用 `prs.slide_layouts[0]`（TITLE_SLIDE）或 `[1]`（CONTENT）：

```python
prs = Presentation('existing.pptx')  # 已有layout定义
slide = prs.slides.add_slide(prs.slide_layouts[1])  # CONTENT布局
```

**`add_slide()` 无参会报错**：`TypeError: Slides.add_slide() missing 1 required positional argument: 'slide_layout'`

### 箭头形状填充陷阱

`MSO_SHAPE.RIGHT_ARROW` 返回的形状默认 `fill.type` 为 `_NoneFill`，直接设置 `fill.fore_color.rgb` 会报错：

```
TypeError: fill type _NoneFill has no foreground color, call .solid() or .patterned() first
```

**修复**：必须先调用 `.fill.solid()`：

```python
arrow = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, x, y, w, h)
arrow.fill.solid()  # ← 必须先调用
arrow.fill.fore_color.rgb = TEAL
```

### 关键要点

- 函数名避免与变量名冲突（如 `card` vs `mkcard`）
- 所有 `text_frame` 访问必须用 `.text_frame.paragraphs`（非 `.paragraphs`）
- `word_wrap = True` 必须显式设置
- 每页结构：背景色 → header → 标题 → 内容 → footer → snum
- 表格行交替背景用 `i % 2`
- 中文字体统一 `Microsoft YaHei`
- 全新PPT add_slide 用 `prs.slide_layouts[6]`（BLANK）
- 箭头/形状填充前必须先 `.fill.solid()`
