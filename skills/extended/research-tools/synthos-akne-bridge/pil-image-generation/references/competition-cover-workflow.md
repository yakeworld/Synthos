# Competition Cover Image Workflow

Generated for Synthos competition submission (AI for Medicine, 2026-05-13).
Seasoned patterns reusable for future competition/event covers.

## Workflow Steps

### 1. Font Discovery

```python
FONT_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"   # ≥30pt CJK+English
FONT_REG  = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
```

- Bold TTC for large title text (renders both CJK and Latin well ≥30pt)
- Regular TTC for body text
- Verify existence first: `ls /usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc`

### 2. Layout Architecture (1920×1080)

```
┌─────────────────────────────────────────────┐
│  ▲ corner     ┌─── hexagon atoms ───┐       │
│  accent       │ ① ⑤           ④ ② │       │ y=40..600
│               │     ⑥ Router ③     │       │
│               └─────────────────────┘       │
│                                             │
│              Synthos (72pt, teal)           │ y=660
│         自主进化学术科研平台 (28pt)           │
│         English tagline (18pt, gray)        │
│                                             │
│ ┌─── features ──────┐ ┌─── metrics ──────┐  │ y=820..1050
│ │ ◆ 6 认知原子 ...   │ │ 覆盖率    95%+   │  │
│ │ ◆ CRISP-DM ...    │ │ 质量分    0.97   │  │
│ │ ◆ ...             │ │ 通过率   100%    │  │
│ └────────────────────┘ └──────────────────┘  │
│ ██ AI for Medicine · 医学研究支持智能体 ██  │ y=1032..1080
└─────────────────────────────────────────────┘
```

### 3. Key Patterns

**Radial Glow** behind atoms:
```python
def glow_effect(draw, cx, cy, r, color, steps=30):
    for i in range(steps, 0, -2):
        rr = int(r * i / steps)
        draw.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=color)
```

**Subtle Grid** (darker than background accent):
```python
gs = 80
for x in range(0, W, gs):
    draw.line([(x, 0), (x, H)], fill=(12, 28, 52), width=1)
# Same for Y
```

**Corner Accents** (L-shapes):
```python
def corner_accent(draw, x, y, dx, dy):
    draw.line([(x, y), (x + dx, y)], fill=TEAL, width=3)
    draw.line([(x, y), (x, y + dy)], fill=TEAL, width=3)
```

**Text Centering with getlength()**:
```python
tw = font.getlength("Synthos")
draw.text((cx - tw/2, title_y), "Synthos", fill=TEAL, font=font)
```

**Double-Draw for Bolder Text** (adds ~7% more bright pixels):
```python
draw.text((x, y), "Title", fill=TEAL, font=font)
draw.text((x+1, y), "Title", fill=TEAL, font=font)
```

### 4. Color Constants

```python
TEAL      = (0, 188, 212)    # accent
NAVY_DARK = (8, 18, 36)      # bg base
NAVY_MID  = (14, 30, 56)     # bg mid
WHITE     = (255, 255, 255)  # text
GRAY      = (170, 170, 170)  # secondary text
DIM       = (60, 70, 90)     # grid line
BOTTOM_BG = (0, 80, 120)     # bottom bar
```

### 5. Text Rendering Verification

After generating, verify text is visible by scanning for bright pixels:

```python
bright = 0
for y in range(650, 740):
    for x in range(800, 1120):
        p = img.getpixel((x,y))
        if p[0] > 30 or p[1] > 50:  # teal is bright in G channel
            bright += 1
print(f"Title bright pixels: {bright}")
```

Expected ranges (1920×1080):
- Title (72pt Bold): ~6,000-7,000 bright pixels
- Each hex atom label (18pt): ~3,200 bright pixels
- Each feature row (20pt): ~2,200-2,800 bright pixels
- Bottom bar text (22pt): ~3,300 bright pixels

### 6. Anonymous Competition Constraint

- NO personal names (参赛教师姓名)
- NO department/school names (院系名称)
- Bottom bar: track name only (e.g., "AI for Medicine · 医学研究支持智能体")
- Metrics: project metrics only (no references to specific institutions)

### 7. Quick File Check

```bash
python3 -c "
from PIL import Image
img = Image.open('cover.png')
print(f'Size: {img.size}, Mode: {img.mode}')
# Verify center teal pixel
print(f'Center: {img.getpixel((960,320))}')  # should be teal-ish
"
```

### 8. Clean Cover Layout (v5 Design Pattern, 2026-05-25)

After iterative feedback (v3→v4→v5), the final clean cover layout for Synthos competition:

```
┌────────────────────────────────────────────────┐
│  ▲ corner              ┌─── orbital ring ────┐ │
│  accent                │  ┌─hexagon ring────┐ │ │
│                        │  │  KA  KE  AD    │ │ │
│                        │  │  RI  HG  AE    │ │ │
│                        │  └────────────────┘ │ │
│                        └──────────────────────┘ │
│                            ○ TR (center)        │
│                                                 │
│              SYNTHOS (60pt, teal)               │
│         自主进化学术科研平台 (24pt)               │
│         English tagline (14pt, gray)             │
│                                                 │
│      ▎动灵在内，不假外求。                        │
│      ▎宪临万法，一维一修。        ← 文言文       │
│      ▎先立后动，凡数必源。          panel         │
│      ▎凡作必省，去形留神。          (右侧)       │
│      ▎...                                      │
│                                                 │
│    53轮 | 0.98 | 18次 | 78.3% | 7原子           │
│   ─────────────────────────────────────────      │
│    自主进化 | 质量评分 | 技能吸收 | 引用F1 | 认知 │
└────────────────────────────────────────────────┘
```

**Key v5 rules (user-enforced)**:
1. **No Chinese text ON nodes** — English abbreviations ONLY (KA/KE/AD/RI/HG/AE). Chinese goes in side panel or nowhere.
2. **No duplicate metrics** — If it's in the bottom bar, it must NOT appear anywhere else on the canvas.
3. **One orbited ring** for visual structure, not two overlapping circles.
4. **Right-align the 文言文 panel** — semi-transparent, non-distracting, philosophical framework.
5. **Bottom metrics bar** with vertical dividers between entries, cyan values + gray labels.
6. **Minimal corner accents** — just L-shaped lines, no extra ornamentation.

**Cover iteration history for reference**:
- v3 (base): Full Chinese atom labels, quality gate labels above title, 文言文 panel
- v4: English abbreviations + small Chinese below atoms, smaller 文言文 font
- v5: ❝要保持界面的清洁。中文全名标注取消。synthos上方的这些什么质量门啊这些都去掉❞ → English only, redundant labels removed

### 9. HTML+Chromium Alternative (Session 2026-05-25)

**PIL limitation discovered**: User explicitly rejected PIL-generated cover as "这个作图排版不好看啊" (this image layout is ugly). The HTML+Chromium approach produces significantly better results:

```bash
# 1. Create cover.html with:
#    - Inter font (Google Fonts CDN)
#    - radial-gradient background
#    - CSS grid for grid lines
#    - Flexbox-absolute positioned atom nodes
#    - SVG for connection lines between nodes
#    - Bottom metrics bar with flex layout

# 2. Screenshot:
chromium-browser --headless --disable-gpu --no-sandbox \
  --screenshot=Synthos_cover.png \
  --window-size=1920,1080 \
  file:///$(pwd)/cover.html
```

**HTML structure pattern**:
```html
<!-- Grid background: CSS linear-gradient repeating pattern -->
<div class="grid-bg"
  style="background-image: linear-gradient(..., rgba(0,188,212,0.04) 1px, transparent 1px);
         background-size: 60px 60px;
         mask-image: radial-gradient(ellipse at 50% 45%, black 40%, transparent 70%);">

<!-- Hexagon ring: absolute positioned circular nodes (86px circles) -->
<div class="atom-node" style="top:Npx; left:Npx; background:var(--atom-ka);">KA</div>

<!-- Connection lines: SVG overlay -->
<svg viewBox="0 0 1920 1080">
  <line x1="960" y1="270" x2="635" y2="178" stroke="rgba(0,188,212,0.08)" stroke-width="1.5"/>
</svg>

<!-- Bottom metrics: flex container centered -->
<div class="bottom-bar" style="display:flex; gap:60px; align-items:center;">
  <span class="metric-value" style="color:#00bcd4; font-weight:600;">53轮</span>
  <span class="metric-label" style="color:#5a5a72;">自主进化</span>
</div>
```

**Key styling differences from PIL**:
- CSS radial-gradient is smoother than PIL's manual concentric ellipse falloff
- Browser text rendering is CRT anti-aliased — no CJK faintness issue
- CSS box-shadow creates realistic glow without manual pixel loops
- SVG lines are perfectly anti-aliased and can use dashed/dotted patterns
- Font loading from CDN (Inter) looks cleaner than system Noto Sans CJK
- 文言文 panel can use CSS opacity to create natural semi-transparency

**Lessons learned**:
1. When user says "不好看" on a PIL output, don't iterate PIL — switch to HTML
2. The user's existing PPT covers in ~/下载/*.pptx are their preferred design language — check those as reference before starting
3. Always screenshot at exact 1920×1080 with `--window-size=1920,1080`
4. The user's taste: clean, minimal, dark-themed, no clutter, English-only abbreviations
