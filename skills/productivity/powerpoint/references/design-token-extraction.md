# Design Token Extraction from Existing PPTX

When the user has an existing PPTX they consider "beautiful" and wants new slides in the same style, extract the design tokens programmatically rather than guessing colors.

## Workflow

```
Existing PPTX → Extract tokens → python-pptx recreate → QA
```

## Step 1: Extract Design Tokens from XML

```python
from pptx import Presentation
from lxml import etree

prs = Presentation("existing.pptx")
slide = prs.slides[0]  # Cover slide

# Get full XML to find color values
xml_str = etree.tostring(slide._element, pretty_print=True).decode()
# Search for <a:srgbClr val="XXXXXX"/> patterns
```

### Key tokens to extract

| Token | XML Attribute | Example |
|-------|--------------|---------|
| Background fill | `p:bg > p:bgPr > a:solidFill > a:srgbClr val` | `0F172A` |
| Card fill | `a:solidFill > a:srgbClr val` on rounded rectangles | `1E293B` |
| Card border | `a:ln > a:solidFill > a:srgbClr val` | `334155` |
| Accent color | Colored rectangle/shape fills | `3B82F6` |
| Title text | `a:r > a:t` with `a:defRPr sz` and `a:srgbClr` | `F8FAFC` |
| Subtitle text | Secondary text fills | `06B6D4` |
| Secondary text | Muted text fills | `94A3B8` |
| Font family | `a:latin typeface` | `Arial` |
| Font sizes | `sz` in hundredths of a point | `5400` = 54pt |
| Slide dimensions | `prs.slide_width` / `prs.slide_height` | 13.33×7.5" (1280×720) |

## Step 2: python-pptx Design System

```python
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# Slide dimensions (16:9 standard)
SLIDE_W = Emu(12800000)  # 13.33 inches
SLIDE_H = Emu(7200000)   # 7.5 inches

# Design tokens (from extraction)
BG_DARK = RGBColor(0x0F, 0x17, 0x2A)
CARD_FILL = RGBColor(0x1E, 0x29, 0x3B)
CARD_BORDER = RGBColor(0x33, 0x41, 0x55)
ACCENT = RGBColor(0x3B, 0x82, 0xF6)       # Blue accent
ACCENT_CYAN = RGBColor(0x06, 0xB6, 0xD4)  # Cyan for secondary titles
TEXT_MAIN = RGBColor(0xF8, 0xFA, 0xFC)    # Near-white
TEXT_SECONDARY = RGBColor(0x94, 0xA3, 0xB8)  # Slate-400
TEXT_MUTED = RGBColor(0x64, 0x74, 0x8B)   # Slate-500
```

### Common shapes

```python
# Accent bar (vertical left strip on each slide)
add_rect(slide, Emu(0), Emu(0), Emu(80000), SLIDE_H, ACCENT)

# Card with border
shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, 
                                left, top, width, height)
shape.fill.solid()
shape.fill.fore_color.rgb = CARD_FILL
shape.line.color.rgb = CARD_BORDER
shape.line.width = Pt(1.5)

# Colored left accent bar on a card
add_rect(slide, card_x, card_y, Emu(60000), card_height, accent_color)
```

## Step 3: NotebookLM → PPT Pipeline

For competition presentations where NotebookLM generates the content:

1. **Prepare Notebook**: Upload all relevant source docs to a Synthos NotebookLM project
2. **Generate slide-deck content**: `notebooklm generate slide-deck "10页以内的描述"`
3. **Extract content via QA**: `notebooklm ask "逐页列出幻灯片内容"`
4. **Recreate with python-pptx**: Use the extracted design tokens and the QA content to build slides
5. **QA**: Convert to PDF → images → visual inspection with `pdftoppm`

### Typical slide structure for competition PPTs

| Slide | Content |
|-------|---------|
| 1 | Cover: SYNTHOS title + subtitle + competition name |
| 2 | What is it? Philosophy frame + architecture overview |
| 3 | 7 Cognitive Atoms + TR Router (grid layout) |
| 4 | Architecture innovation (Zero-Python vs Traditional side-by-side) |
| 5 | Self-evolving engine (big metrics cards) |
| 6 | Core capabilities (3-column cards) |
| 7 | Education + Research dual drive |
| 8 | Use cases (domain-specific examples) |
| 9 | Competition fit (checklist/cards) |
| 10 | Thank you / Contact |

## Pitfalls

- **LibreOffice renders differ from WPS/MS Office**: Test the final PPTX in the user's target application (WPS in this case).
- **Accent bars under titles**: The `powerpoint` SKILL.md warns about this being an "AI hallmark" — but the user's original PPT actually uses this pattern. Always match the user's existing design language, not generic best-practices.
- **Font embedding**: System fonts (Arial) are safe; custom fonts may not render in LibreOffice headless conversion.
