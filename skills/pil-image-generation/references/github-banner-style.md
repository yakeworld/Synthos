# GitHub README Banner Style (Dark Professional)

Cover technique developed for the Synthos project: a dark-themed, professional GitHub banner with clean typography, decorative rings, and feature badges.

## Palette

| Role | Color | Hex |
|:-----|:------|:----|
| Deepest bg (top) | (10, 12, 28) | #0A0C1C |
| Mid bg | (15, 18, 40) | #0F1228 |
| Lightest bg | (20, 25, 55) | #141937 |
| Accent (bottom) | (30, 20, 50) | #1E1432 |
| Grid lines | (100, 120, 255, alpha=12) | — |
| Primary accent | (80, 180, 255) | #50B4FF |
| Title text | (200, 220, 255) | #C8DCFF |
| Subtitle text | (140, 200, 255) | #8CC8FF |
| Tagline text | (160, 180, 220, alpha=150) | — |
| Dim text | (100, 120, 160) | #6478A0 |

## Layout (1920×1080)

```
┌─────────────────────────────────────────────────────────┐
│                                                          │
│  │  Synthos                                              │
│  │                                                       │
│  │  自主进化学术科研平台            ╭─────╮            │
│  │                                ╱       ╲           │
│  │  Cognitive Operating System   │  rings  │           │
│  │  for Science                   ╲       ╱           │
│  │                                 ╰─────╯            │
│  │  ◇ 7 认知原子       ◇ 自进化引擎                      │
│  │  SKILL.md认知闭环   每日诊断修复吸收                    │
│  │  ◇ 六维评估         ◇ 纯Agent执行                     │
│  │  RCB适配评分        零Python全推理                      │
│  │                                                       │
│  │                                              v4.2.0  │
│  ───────────────────────────────────────────────         │
└─────────────────────────────────────────────────────────┘
```

## Key Elements

### 1. Per-pixel Linear Gradient

```python
colors = [(10, 12, 28), (15, 18, 40), (20, 25, 55), (30, 20, 50)]
for y in range(H):
    t = y / H
    r = int(colors[0][0] * (1-t) + colors[3][0] * t)
    g = int(colors[0][1] * (1-t) + colors[3][1] * t)
    b = int(colors[0][2] * (1-t) + colors[3][2] * t)
    draw.line([(0, y), (W, y)], fill=(r, g, b))
```

This creates a smooth gradient from top to bottom using 4-way linear interpolation. Faster than per-pixel ellipse loops and produces cleaner results.

### 2. Subtle Grid Pattern

```python
for x in range(0, W, 60):
    draw.line([(x, 0), (x, H)], fill=(100, 120, 255, 12), width=1)
for y in range(0, H, 60):
    draw.line([(0, y), (W, y)], fill=(100, 120, 255, 12), width=1)
```

Very low alpha (12) — barely visible, adds texture without distraction.

### 3. Decorative Atomic Rings

```python
cx, cy = W - 280, 250
for r, a in [(200, 20), (160, 30), (130, 15), (100, 25)]:
    ring_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ring_draw = ImageDraw.Draw(ring_img)
    ring_draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=(80, 180, 255, 40), width=2)
    img = Image.alpha_composite(img, ring_img)
```

Place in upper-right quadrant. Slightly rotated ellipses (via different radii) create an orbital effect.

### 4. Left Accent Bar

```python
draw.rectangle([60, 180, 64, 900], fill=(80, 180, 255, 180))
```

Thin vertical bar (4px wide) left of the title. Anchors the eye and gives structure.

### 5. Title with Shadow + Glow

```python
# Shadow
draw.text((title_x+3, title_y+3), title_text, fill=(30, 60, 120, 60), font=font_title)
# Main text
draw.text((title_x, title_y), title_text, fill=(200, 220, 255), font=font_title)

# Glow (Gaussian blur pass)
glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
glow_draw = ImageDraw.Draw(glow_layer)
glow_draw.text((title_x, title_y), title_text, fill=(80, 180, 255, 30), font=font_title)
glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=20))
img = Image.alpha_composite(img, glow_layer)
```

Three-layer technique: dark shadow → bright text → soft blue glow. Gives depth without being gaudy.

### 6. Feature Badges Grid (2×2)

```python
features = [
    ("⚛ 7 认知原子", "SKILL.md 驱动的认知闭环"),
    ("🔄 自进化引擎", "每日自动诊断 + 修复 + 吸收"),
    ("📊 六维评估", "ResearchClawBench 适配评分"),
    ("🧩 纯 Agent 执行", "零 Python 脚本，全推理驱动"),
]
for i, (title, desc) in enumerate(features):
    bx = title_x + (i % 2) * 420
    by = badge_y + (i // 2) * 80
    draw.rectangle([bx, by+6, bx+8, by+14], fill=(80, 200, 255, 180))
    draw.text((bx+22, by-2), title, fill=(200, 220, 255), font=font_small)
    draw.text((bx+22, by+24), desc, fill=(140, 160, 200, 180), font=font_small)
```

Small diamond bullet + title line + description line. Clean, scannable.

### 7. Bottom Separator + Version Badge

```python
draw.line([(100, H-70), (W-100, H-70)], fill=(60, 80, 120, 80), width=1)
draw.text((W - 300, H - 50), "v4.2.0  ·  MIT License", fill=(100, 120, 160, 120), font=font_small)
```

Separator line with fade margins. Version text in bottom-right.

## Font Stack

| Purpose | Font | Size | Color |
|:--------|:-----|:----|:------|
| Main title (English) | Roboto-Bold.ttf | 120-132px | #F0F8FF |
| Chinese subtitle | NotoSansCJK-Bold.ttc | 72px | #8CD2FF |
| English tagline | Roboto-Regular.ttf | 36px | #A0BDE6 |
| Feature titles | NotoSansCJK-Regular.ttc | 24px | #D2E1FF |
| Feature descriptions | NotoSansCJK-Regular.ttc | 18px | #82A5C8 |
| Version badge | NotoSansCJK-Regular.ttc | 18px | #5A6E96 |

**Important**: CJK fonts (NotoSansCJK-*.ttc) may not render Latin characters well at very large sizes (>100px). For the main English title, always use a Latin font like Roboto.

**TrueType Collection**: TTC files can be loaded with `ImageFont.truetype(path, size)` (index defaults to 0). All common weights are in the same file.

## When to Use This Style

- GitHub README banners for AI/ML projects
- Academic competition covers
- Project documentation hero images
- Any situation needing a clean, dark, professional header image

---

## ⚠️ Critical Warnings

### 1. Draw Reference Staleness After Blend

`Image.blend()` returns a **new** image object. Any `ImageDraw.Draw` created before the blend still references the **old** image. All subsequent `draw.text()`, `draw.rectangle()`, etc. silently write to the discarded image — leaving the saved image blank (just background + blend layer, no text).

**Always re-create `draw` after blend operations:**

```python
img = Image.blend(img, glow, 0.25)
draw = ImageDraw.Draw(img)  # ← MUST recreate after blend
```

This also applies to: `Image.alpha_composite()`, `ImageChops.*()`, `Image.composite()`.

### 2. Font Rendering Offset

`draw.text((x, y), text)` does NOT place the top-left of the rendered text at (x, y). TrueType fonts have ascender/descender metrics that shift the actual position. For Roboto Bold 132pt at draw position (718, 196), the text actually renders at y=220 (24px lower) and x=723 (5px right).

**Always measure empirically** before computing center positions:

```python
# Draw on temporary black image
tmp = Image.new("RGB", (W, H), (0, 0, 0))
td = ImageDraw.Draw(tmp)
td.text((0, 0), "Text", fill=(255, 255, 255), font=font)

# Scan for non-black pixels
mx, my, Mx, My = 9999, 9999, 0, 0
for y in range(H):
    for x in range(W):
        if tmp.getpixel((x, y)) != (0, 0, 0):
            mx = min(mx, x); my = min(my, y)
            Mx = max(Mx, x); My = max(My, y)

tw, th = Mx - mx + 1, My - my + 1
x_offset, y_offset = mx, my

# Center on canvas
draw_x = (canvas_w - tw) // 2 - x_offset
draw_y = target_y - y_offset
draw.text((draw_x, draw_y), "Text", fill="white", font=font)
```
