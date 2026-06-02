# PPTX Layout Pitfalls (from Synthos competition deck QA)

These pitfalls were discovered during QA of a 12-slide competition deck built with pptxgenjs on LAYOUT_WIDE (13.33" × 7.5"). The deck used dark navy (#0A1628) backgrounds, teal (#00BCD4) accents, and card-style layouts.

## 1. LAYOUT_WIDE Safe Zone

**Problem**: LibreOffice (used for PDF conversion) clips elements whose right or bottom edge exceeds the printable area.

**Rule**: Keep all element right edges ≤ 12.8", bottom edges ≤ 7.0". Leave ≥ 0.5" margin on all edges.

**Check**: For any card at position (x, y) with width w and height h, verify `x + w ≤ 12.8` and `y + h ≤ 7.0`.

## 2. Alternating Row Colors Must Contrast with Background

**Problem**: A table with alternating row fills of `#0A1628` (same as slide background) and `#0F1F3A` made even rows invisible — they blended into the slide behind the table.

**Fix**: Use a visibly different shade like `#14243A` (RGB difference > 20 per channel from the background).

```javascript
// ❌ WRONG — even rows invisible
const bgColor = i % 2 === 0 ? "0F1F3A" : "0A1628";  // 0A1628 == slide bg

// ✅ CORRECT — rows visible
const bgColor = i % 2 === 0 ? "0F1F3A" : "14243A";
```

## 3. Grid Layout Right-Edge Overflow

**Problem**: 4-column card grids with `x = 0.6 + col * 3.15`, `w = 2.9` produce a right edge at `0.6 + 3*3.15 + 2.9 = 12.95"` — exceeding the 12.8" safe zone.

**Formula**: `rightEdge = startX + (columnCount - 1) * spacing + cardWidth`

**Fix**: For 4 cards, use tighter spacing (3.1") or narrower cards (2.85"), or limit to 3 columns.

## 4. Bottom Margin Density

**Problem**: Stacking multiple text lines near the slide bottom with 0" vertical gap makes them seem to touch.

**Fix**: When placing multiple text elements near y = 6.5", add at least 0.15" gap between them and ensure the last element ends by y = 7.0".

## 5. Text Box Width vs. Content Length

**Problem**: English text at 14pt bold in a 2.2" wide box forces wrapping for strings like "creative-cognition" (~22 chars × 0.17"/char ≈ 3.7").

**Rule of thumb**: 
- 14pt Arial: ~0.17" per Latin char, ~0.26" per CJK char
- 12pt Arial: ~0.15" per Latin char, ~0.22" per CJK char
- For a text box of width W, max chars per line ≈ W / charWidth
- If content exceeds this, either widen the box or reduce font size

## 6. QA Without Vision Access

When vision_analyze is unavailable:
1. Convert PPTX → PDF via LibreOffice
2. Convert PDF → JPEG via pdftoppm
3. Inspect text content via pptx text extraction (python-pptx or markitdown)
4. Calculate expected positions from the source code — check x + w and y + h for every element against safe zone boundaries
5. Check alternating row colors against the slide background color

## 7. Cover Slide Central Glow

A teal oval at 95% transparency on a dark navy background is barely visible. For a subtle glow effect, use transparency=85-90% and consider stacking two ovals (one larger at higher transparency, one smaller at lower transparency) for a gradient-like effect.
