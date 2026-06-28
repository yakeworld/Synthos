# PptxGenJS Dark-Tech Presentation (v3 proven structure)

## When to use this approach

Use pptxgenjs (Node.js) when you need to generate a presentation from scratch with:
- **Custom dark theme** (not available from python-pptx templates)
- **Complex shapes** (rounded rectangles, accent bars, oval badges, custom layouts)
- **No template available** — pure code generation
- **Iterative design** — quick to regenerate after layout fixes

## Requirements

```bash
npm install pptxgenjs
# Optional: for icons
npm install react-icons react react-dom sharp
```

## Proven 12-slide structure for Synthos competition

This structure was refined over 3 iterations (v1→v2→v3) based on user feedback. The key insight: **focus on Synthos core features, not tangential topics.** The user explicitly redirected from "eye-brain interface" to "自我进化是最重要的特征".

### Slide priority order (in order of importance)

| # | Slide | Duration | Why this order |
|:-:|-------|----------|----------------|
| 1 | Cover | ~13s | Brand first impression |
| 2 | TOC | ~18s | Navigation |
| 3 | Core architecture + 15 skills | ~59s | **Foundation** — what Synthos is |
| 4 | Flow control + classical Chinese | ~45s | **Differentiator** — unique technical innovations |
| 5 | **Self-evolution engine (CORE)** | ~57s | **★ Most important** — user emphasized this |
| 6 | External absorption + comparison | ~47s | Proof of evolution capability (merged into 1 slide per user request) |
| 7 | Self-generated papers | ~46s | **Real output** — Synthos writing its own papers |
| 8 | Paper writing workflow | ~50s | How it works — human-in-the-loop |
| 9 | Knowledge acquisition demo | ~31s | Feature showcase |
| 10 | Education support | ~35s | Teaching application |
| 11 | Results data | ~29s | Quantitative proof |
| 12 | Closing | ~14s | Call to action |

Total: ~444s = 7:24 (within 6-10min competition requirement)

### What to avoid
- **Don't spend a whole slide on tangential topics** (like eye-brain interface, hardware specs) — the user said "PPT是否应该着重于Synthos项目特性"
- **Don't use emoji** — use text markers like "■" or "▸" instead (emoji renders as tofu in system fonts)
- **Don't use fabricated numbers** — rigorous data verification is the user's hard requirement ("所有数字必须严谨，不要虚构")

## Color palette (proven for dark theme)

```javascript
const C = {
  bg: "0A1628",          // Deep navy background
  teal: "00BCD4",        // Primary accent (competition brand color)
  white: "FFFFFF",       // Main text
  gray: "AABBCC",        // Secondary text
  dim: "3A4A5A",         // Grid lines
  card: "0F1F3A",        // Card backgrounds
  cardBorder: "1A3050",  // Card borders
  accentLight: "4DD0E1", // Highlight text (quotes, emphasis)
  textMuted: "8899AA",   // Footnotes, metrics
};
```

## PptxGenJS setup

```javascript
const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";  // 13.33 × 7.5 inches
pres.author = "Synthos";
pres.title = "Synthos — 自主进化学术科研平台";
```

Always use `LAYOUT_WIDE` (13.33×7.5) for competition presentations — it gives the most horizontal space and looks best on 16:9 displays.

## Key patterns

### Card with accent bar (used on ~80% of slides)

```javascript
function cd(slide, x, y, w, h, fill) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h,
    fill: { color: fill || "0F1F3A" },
    line: { color: "1A3050", width: 0.5 },
    shadow: { type: "outer", blur: 4, offset: 2, angle: 135, color: "000000", opacity: 0.2 }
  });
}

// Accent bar (colored vertical strip on left edge of card)
slide.addShape(pres.shapes.RECTANGLE, {
  x: cardX, y: cardY, w: 0.06, h: cardHeight,
  fill: { color: "00BCD4" }
});
```

### ⚠️ Never reuse option objects

PptxGenJS mutates option objects in-place (converting shadow values to EMU). Sharing one object between calls corrupts the second shape.

```javascript
// WRONG
const shadow = { type: "outer", blur: 4, ... };
slide.addShape(RECTANGLE, { shadow, ... });  // First call works
slide.addShape(RECTANGLE, { shadow, ... });  // ❌ Corrupted

// CORRECT — factory function creates fresh objects
const makeShadow = () => ({ type: "outer", blur: 4, offset: 2, angle: 135, color: "000000", opacity: 0.2 });
slide.addShape(RECTANGLE, { shadow: makeShadow(), ... });
slide.addShape(RECTANGLE, { shadow: makeShadow(), ... });
```

### Slides with many similar items (TOC, atoms, absorptions)

Use a loop with calculated y-positions:

```javascript
const items = [["01","Title 1"], ["02","Title 2"], ...];
items.forEach((item, i) => {
  const y = 1.7 + i * 0.55;
  slide.addText(item[0], { x: 1.5, y, w: 0.7, h: 0.45, ... });
  slide.addText(item[1], { x: 2.4, y, w: 8, h: 0.45, ... });
});
```

### Tables (CRISP-DM mapping slide)

```javascript
// Header
s8.addShape(pres.shapes.RECTANGLE, { x: 0.8, y: hdrY, w: 11.7, h: 0.5, fill: { color: C.teal } });
s8.addText("CRISP-DM 阶段", { x: 1.0, y: hdrY, w: 3.5, h: 0.5, ... });

// Data rows
crispdm.forEach((row, i) => {
  const y = hdrY + 0.5 + i * 0.65;
  const bgColor = i % 2 === 0 ? "0F1F3A" : "14243A";
  s8.addShape(pres.shapes.RECTANGLE, { x: 0.8, y, w: 11.7, h: 0.65, fill: { color: bgColor } });
  s8.addText(row[0], { x: 1.0, y, w: 3.5, h: 0.65, ... });
  s8.addText(row[1], { x: 4.8, y, w: 3, h: 0.65, bold: true, color: C.teal, ... });
});
```

### ⚠️ Avoid accent lines under titles (if skill says so)

The `powerpoint` skill says "NEVER use accent lines under titles — these are a hallmark of AI-generated slides". BUT for dark-themed academic presentations, title accent lines are an effective visual separator. Use if the presentation's dark background needs them. If the user complains about "AI-looking slides", remove them.

## Post-generation QA

After generating, always:
1. `libreoffice --headless --convert-to pdf output.pptx` (check no errors)
2. `pdftoppm -jpeg -r 150 output.pdf slide` → check visual output
3. Verify slide count matches expected
4. Verify all text is rendering correctly (Chinese characters especially)
5. If possible, do a visual inspection — catch overlapping elements, text overflow, edge clipping

## Common layout fixes (from v1→v2→v3 iterations)

- **Card right-edge spacing**: With `LAYOUT_WIDE` (13.33"), cards at x=0.8 with w=5.2 leave 7.33" for right panels. Keep cards within 12.5" (0.83" from right edge minimum).
- **Text overflow**: Labels like "creative-cognition" at 14pt bold need at least 3" width. In 2.2" they will wrap. Use wider boxes or shorter labels.
- **Asymmetric grids**: 5 items in a 2-column grid leaves a blank spot. Acceptable but note it.
- **Row colors**: Alternating table rows need both colors DIFFERENT from background. Even rows = "0F1F3A" is OK, "0A1628" (= background) is invisible. Use "14243A" instead.
