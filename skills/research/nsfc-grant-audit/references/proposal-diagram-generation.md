# Proposal Diagram Generation — Technical Roadmap Flowcharts

> From: 2026-05-21 session — FBS risk prediction + PD aspiration prediction proposals (温州市科技局)
> Preferred tool: Excalidraw (user explicitly rejected PIL flat rectangles as "排版不好看")

## When to Use

When a Chinese medical proposal has a multi-stage technical workflow described in text but lacks a visual flowchart. Reviewers strongly prefer a diagram. The proposal typically has 3-5 stages that can be visually organized as a vertical flow.

## Preferred Approach: Academic-Diagram (Nature-style TikZ)

2026-05-21 Update (PD Aspiration Project): For proposals requiring high-quality, publication-ready vector graphics, the `academic-diagram` skill (Nature-style TikZ) produces the best results. This is now the **first choice** for technical roadmap figures in Chinese medical proposals.

### Workflow

```bash
# 1. Load both skills
skill_view(name='academic-diagram')
skill_view(name='nsfc-grant-audit')

# 2. Design the figure contract (from academic-diagram Step 0)
# Core conclusion: 3-phase vertical flow for medical risk prediction
# Archetype: architecture (3-layer stacked) adapted for vertical pipeline
# Target: Wenzhou city project proposal
# Size: double column (~183mm / ~12cm wide)

# 3. Write TikZ figure with xelatex (REQUIRED for CJK support)
# Use Nature 6-color palette:
#   Phase 1 指标体系构建     → nat_blue (#0072B2)
#   Phase 2 预测模型构建与验证 → nat_green (#009E73)
#   Phase 3 护理预警与临床转化 → nat_orange (#E69F00)
#   Output boxes            → nat_pink (#CC79A7)
#   Intervention boxes      → nat_brown (#D55E00)

# 4. Key TikZ preamble for CJK:
% \\usepackage{fontspec}
% \\usepackage{xeCJK}
% \\setCJKmainfont{Noto Sans CJK SC}

# 5. Compile
xelatex fig_roadmap.tex

# 6. Convert for insertion
pdftoppm -png -r 300 fig_roadmap.pdf fig_roadmap

# 7. Insert into docx
python3 -c "
from docx import Document
from docx.shared import Inches
doc = Document('proposal.docx')
p = doc.add_paragraph()
p.add_run().add_picture('fig_roadmap-1.png', width=Inches(6.2))
doc.save('proposal_with_fig.docx')
"
```

### Nature Palette Adaptation for 3-Phase Medical Proposals

```latex
\\definecolor{nat_blue}{HTML}{0072B2}
\\definecolor{nat_cyan}{HTML}{56B4E9}
\\definecolor{nat_green}{HTML}{009E73}
\\definecolor{nat_orange}{HTML}{E69F00}
\\definecolor{nat_pink}{HTML}{CC79A7}
\\definecolor{nat_brown}{HTML}{D55E00}

% Per-phase box style
\\node[box=nat_blue] at (0,0) {Phase 1};
\\node[box=nat_green] at (2,0) {Phase 2};
\\node[box=nat_orange] at (4,0) {Phase 3};
% Output/validation boxes
\\node[oval=nat_pink] at (6,0) {Output};
% Intervention boxes
\\node[box=nat_brown] at (0,-1) {Intervention};
```

### 3-Phase Vertical Layout Template

Phase zone heights: ~3.5cm each with 0.7-0.9cm gap between phases.

```
Y-coordinates (cm):
  Phase 1 Top:  +10.2  |  Phase 1 Bot: +6.5
  Phase 2 Top:  +5.6   |  Phase 2 Bot: +1.5
  Phase 3 Top:  +0.8   |  Phase 3 Bot: -3.0
  Gap P1-P2:    0.9cm  |  Gap P2-P3: 0.7cm
  Box ctr:      (phase_top + phase_bot)/2
```

### Critical Pitfalls (TikZ-specific)

| Pitfall | Fix |
|:--------|:----|
| `cap` style name conflicts with TikZ `/tikz/cap` key | Rename to `annot` or `captionstyle` |
| CJK characters render as boxes | Use xelatex + xeCJK + `\setCJKmainfont{Noto Sans CJK SC}` |
| Chinese text missing in PDF | Run `fc-list :lang=zh` to verify CJK font installed |
| Layer backgrounds overlap from rounded corners | Increase inter-phase gap to ≥0.8cm for 2mm rounding |
| Box text overflow | Set `minimum width` based on character count, ~2.5mm per CJK char |

### Comparison: Excalidraw vs TikZ vs PIL

| Criterion | PIL (retired) | Excalidraw | TikZ (academic-diagram) ✅ |
|:----------|:-------------|:-----------|:-------------------|
| Visual quality | Flat/dated | Hand-drawn, friendly | Publication-grade, Nature-style |
| Vector output | No | Via excalidraw.com PNG | Native PDF vector |
| CJK support | Fragile | Built-in | xelatex+Noto |
| Editing | Regenerate code | User edits live at URL | Modify .tex + recompile |
| Insert into docx | .add_picture() | Download PNG | pdf→png→docx |
| Best for | Legacy only | Quick hand-drawn drafts | Final submission-quality figures |

## Alternate Approach: Excalidraw (Hand-drawn Style)

2026-05-21 Update: User explicitly rejected the PIL flat-rectangle approach as "排版有些不好看" and asked for "synthos不是有这个做图的技能吗？" — referring to Excalidraw. Use Excalidraw for all technical roadmap diagrams in Chinese medical proposals.

### Why Excalidraw over PIL

| Criterion | PIL (retired) | Excalidraw ✅ |
|:----------|:-------------|:--------------|
| Visual style | Flat rectangles | Hand-drawn, professional |
| Editability | Must regenerate code | Interactive web link, user edits live |
| Shareability | Static PNG | Encrypted shareable URL |
| Chinese font | Fragile font detection | Built-in hand-drawn CJK support |
| Layout complexity | Hard to debug alignment | Drag-and-drop after loading |
| Output to docx | Must script insertion | User downloads PNG from excalidraw.com |

### Workflow

```
1. Load excalidraw skill:  skill_view(name='excalidraw')
2. Read its element format (container binding, arrows, bindings)
3. Plan layout: 3 phases × 4-5 steps each, vertical flow
4. Write Excalidraw JSON array
5. Save as .excalidraw file
6. Upload:  python3 <skill_dir>/scripts/upload.py <file>.excalidraw
7. Send shareable URL to user
```

### Excalidraw JSON Patterns for Medical Proposals

**Phase Zone Background:**
```json
{"type": "rectangle", "id": "zone1_bg", "x": 30, "y": 100,
 "width": 1240, "height": 520,
 "backgroundColor": "#e3f2fd", "fillStyle": "solid",
 "opacity": 70, "roundness": { "type": 3 } }
```

**Container-bound Text Box (MUST use boundElements+containerId — DO NOT use `label` field):**
```json
{"type": "rectangle", "id": "box1", "x": 130, "y": 150,
 "width": 300, "height": 70,
 "backgroundColor": "#a5d8ff", "fillStyle": "solid",
 "boundElements": [{"id": "t1", "type": "text"}]},
{"type": "text", "id": "t1", "x": 140, "y": 160,
 "text": "文献系统检索\n与Meta分析",
 "fontSize": 18, "fontFamily": 1,
 "textAlign": "center", "verticalAlign": "middle",
 "containerId": "box1",
 "originalText": "文献系统检索\n与Meta分析", "autoResize": true}
```

**Arrow with Start/End Bindings (connects boxes):**
```json
{"type": "arrow", "id": "a1", "x": 280, "y": 220,
 "width": 0, "height": 30, "points": [[0,0],[0,30]],
 "endArrowhead": "arrow",
 "startBinding": {"elementId": "box1", "fixedPoint": [0.5, 1]},
 "endBinding": {"elementId": "box2", "fixedPoint": [0.5, 0]}}
```

**Dashed Arrow for Side Panel Connections:**
```json
{"type": "arrow", "id": "side_arrow", "x": 430, "y": 810,
 "width": 220, "height": 0, "points": [[0,0],[220,0]],
 "endArrowhead": "arrow", "strokeStyle": "dashed"}
```

### Color Scheme for 3-Phase Medical Proposals

| Phase | Zone BG | Box Fill | Text Label Color |
|:------|:--------|:---------|:-----------------|
| 1. 指标体系构建 | `#e3f2fd` (light blue) | `#a5d8ff` | `#1565c0` |
| 2. 预测模型构建与验证 | `#e8f5e9` (light green) | `#b2f2bb` | `#2e7d32` |
| 3. 护理预警与临床转化 | `#fff3e0` (light orange) | `#ffd8a8` | `#e65100` |
| Output/Special boxes | — | `#d0bfff` (purple) or `#69db7c` (green) | `#1a237e` |
| Closed loop / intervention | — | `#fff3bf` (yellow) | `#c62828` |

### Typography Guidelines

| Element | Font Size | Font Family |
|:--------|:---------:|:-----------:|
| Title | 32 | 1 (Virgil/hand-drawn) |
| Phase label | 22 | 1 |
| Box body | 16-18 | 1 |
| Sub-details | 14 | 1 |
| Small annotations | 14 | 1 |
| Footer | 14 | 1 |

### Upload to excalidraw.com

```bash
pip install cryptography  # AES-GCM encryption
python3 <skill_dir>/scripts/upload.py diagram.excalidraw
# Output: https://excalidraw.com/#json=<file_id>,<key>
```

The link is encrypted client-side — the server never sees the plaintext content.

### Pitfalls

1. **DO NOT use `label` field on shapes** — Excalidraw silently ignores it. Use `boundElements` + separate `text` element with `containerId`.
2. **Place text element immediately after its container shape** in the JSON array — z-order depends on array position.
3. **`\\n` for line breaks** in the text field — Excalidraw renders multi-line text correctly.
4. **Arrow coordinates**: `x`/`y` = start of arrow, `points[last]` = end. If start and end y-coords differ, arrow is diagonal.
5. **Keep max text line under ~30 chars** to avoid overflow.
6. **Spacing**: Leave 25-30px gap between vertical flow boxes, 40-50px for phase zones.
7. **Excalidraw link needs internet** — user can open it in any browser. If offline needed, export as PNG from excalidraw.com.

## Legacy Approach: PIL (only if Excalidraw unavailable)

The original PIL-based approach uses Python Pillow to draw rectangles with rounded corners and arrows. Only use this as fallback when the excalidraw upload fails or for automated batch generation.

### PIL Design

Canvas: 1200x1080px, white background
Box: 700px wide at x=250, 100-130px tall, rounded corners
Arrow gap: 25px between stages

### Font Loading (PIL)

```python
def find_cjk_font(size=15):
    for path in [
        '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
    ]:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    import subprocess
    result = subprocess.run(['fc-list', ':lang=zh'], capture_output=True, text=True, timeout=5)
    for line in result.stdout.split('\n'):
        if ':' in line:
            fp = line.split(':')[0].strip()
            if os.path.exists(fp):
                return ImageFont.truetype(fp, size)
    return ImageFont.load_default()
```

### Insert PIL-generated PNG into docx

```python
from docx import Document
from docx.shared import Inches, Pt
doc = Document('proposal.docx')
img_p = doc.add_paragraph()
img_p.add_run().add_picture('diagram.png', width=Inches(6.2))
cap_p = doc.add_paragraph()
cap_r = cap_p.add_run('图1  技术路线图')
cap_r.font.size = Pt(9)
cap_r.font.name = '黑体'
cap_r.bold = True
```

### PIL Pitfalls

1. **Missing CJK font**: Pillow cannot render Chinese without a CJK font. Install `fonts-noto-cjk` or `fonts-wqy-zenhei`. Always try multiple font paths.
2. **Text overflow**: Keep each detail line under ~30 chars. Use manual `\n` splitting.
3. **Arrowheads**: Use `draw.polygon([(cx-5, y2-10), (cx+5, y2-10), (cx, y2)])` for arrow tips.
4. **Caption formatting**: Set 黑体/粗体/9pt for proper Chinese figure labels.
5. **Side notes overlap**: Keep right annotations within 190px starting at x=980.