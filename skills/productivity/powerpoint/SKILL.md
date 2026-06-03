---
name: powerpoint
description: "Create, read, edit .pptx decks, slides, notes, templates."
signature: "spec: dict -> pptx_path: str"
related_skills: [airtable, chinese-form-automation, google-workspace, jupyter-live-kernel, linear]
allowed-tools: [terminal, file]
license: Proprietary. LICENSE.txt has complete terms
---

# Powerpoint Skill

## When to use

Use this skill any time a .pptx file is involved in any way — as input, output, or both. This includes: creating slide decks, pitch decks, or presentations; reading, parsing, or extracting text from any .pptx file (even if the extracted content will be used elsewhere, like in an email or summary); editing, modifying, or updating existing presentations; combining or splitting slide files; working with templates, layouts, speaker notes, or comments. Trigger whenever the user mentions "deck," "slides," "presentation," or references a .pptx filename, regardless of what they plan to do with the content afterward. If a .pptx file needs to be opened, created, or touched, use this skill.

## Quick Reference

| Task | Guide |
|------|-------|
| Read/analyze content | `python -m markitdown presentation.pptx` |
| Edit or create from template | Read [editing.md](editing.md) |
| Create from scratch | Read [pptxgenjs.md](pptxgenjs.md) |

---

## Reading Content

```bash
# Text extraction
python -m markitdown presentation.pptx

# Visual overview
python scripts/thumbnail.py presentation.pptx

# Raw XML
python scripts/office/unpack.py presentation.pptx unpacked/
```

---

## Editing Workflow

**Read [editing.md](editing.md) for full details. For quick content edits without unpack/re-pack, see [references/python-pptx-direct-edit.md](references/python-pptx-direct-edit.md).**

1. Analyze template with `thumbnail.py`
2. Unpack → manipulate slides → edit content → clean → pack

### Quick Edit: python-pptx Direct Text Replacement (No Unpack)

For simple content changes (update text, swap metrics, rename sections) without touching layout/theme:

1. Analyze the PPTX shapes first:
   ```bash
   python3 -c "
   from pptx import Presentation
   prs = Presentation('input.pptx')
   for i, slide in enumerate(prs.slides):
       print(f'=== Slide {i+1} ===')
       for s in slide.shapes:
           if s.has_text_frame:
               print(f'  {s.name} @ ({s.left},{s.top}) = \"{s.text_frame.text[:50]}\"')
   "
   ```

2. Identify text boxes by `shape.name` — these are stable across saves because WPS/PowerPoint preserves them.

3. Modify text directly:
   ```python
   from pptx import Presentation
   from pptx.dml.color import RGBColor

   prs = Presentation('input.pptx')
   slide = prs.slides[0]
   for s in slide.shapes:
       if s.name == 'TextBox 3':  # stable name
           s.text_frame.clear()
           p = s.text_frame.paragraphs[0]
           r = p.add_run()
           r.text = 'New Title'
           r.font.size = Pt(24)
           r.font.color.rgb = RGBColor(0xF8, 0xFA, 0xFC)
           r.font.name = 'Arial'
   prs.save('output.pptx')
   ```

4. Convert to images for visual QA:
   ```bash
   libreoffice --headless --convert-to pdf output.pptx
   pdftoppm -png -r 150 output.pdf slide
   ```

**Useful for**: updating metrics, renaming sections, fixing typos, updating team info — all without touching the original layout or design work done in WPS/PowerPoint.

### MINIMAL CHANGES WORKFLOW (⚠️ Critical — Corrected Behavior)

When the user says **"最小改动"** (minimal changes), **"只改数字"**, or specifies a narrow set of edits:

**RULE 1: Always start from the ORIGINAL source file.**
- ❌ **Never modify an already-optimized/intermediate version** (e.g., don't edit `_优化版.pptx` when `_Original.pptx` exists)
- ✅ Find the original/backup file — check `Synthos_Original_PPT.pptx`, WPS backup dir (`~/.local/share/Kingsoft/office6/data/backup/`), or ask the user
- The original defines the baseline; modifying an already-modified version compounds unintended changes

**RULE 2: Diagnose the ORIGINAL structure first.**
```python
from pptx import Presentation
prs = Presentation('original.pptx')
for i, slide in enumerate(prs.slides):
    print(f'Slide {i}:')
    for s in slide.shapes:
        if s.has_text_frame:
            t = s.text_frame.text.strip()
            if t: print(f'  {s.name}: "{t[:70]}"')
```
This gives an accurate shape map before any edits.

**RULE 3: Make only the explicit changes — nothing else.**
- Leave titles, subtitles, labels, formatting, colors, font sizes unchanged unless explicitly requested
- Don't relabel sections, don't restyle cards, don't rewrite descriptions
- If the user says "只改数字", change ONLY the numeric text — not the surrounding labels or headers

**RULE 4: Watch slide index shifts when inserting slides.**
When you insert a new slide (e.g., 文言宪章 page), ALL subsequent slides shift by +1 index. If you were targeting `slides[7]` as the 应用成效 page in the original 10-slide deck, it becomes `slides[8]` after inserting one slide. Always verify the final index before applying changes.

```python
# After inserting slide at position 2:
# Original: [0,1,2,3,4,5,6,7,8,9]
# After:    [0,1,NEW,2,3,4,5,6,7,8,9]
#                              ↑ was 6, now 7
#                                ↑ was 7 (应用成效), now 8
```

**Verification:**
After minimal changes, re-check that only the requested elements changed:
```python
# Compare text before/after for EVERY slide (not just the edited one)
python3 -c "
from pptx import Presentation
prs = Presentation('output.pptx')
prs_orig = Presentation('original.pptx')
# ... compare each slide's text
print('Slides unchanged:', same_count)
print('Slides changed:', diff_count)
"
```

**Pitfall:** "最小改动" does NOT mean "preserve the spirit of the original while improving it." It means literally touch nothing except the exact items the user named. When in doubt, don't change it.

---

## Creating from Scratch

**Read [pptxgenjs.md](pptxgenjs.md) for full details.**

Use when no template or reference presentation is available.

### Design Token Extraction (Alternative — python-pptx)

When the user has an existing PPTX they consider "beautiful", extract its design tokens (colors, fonts, spacing) and recreate with python-pptx rather than guessing. See [references/design-token-extraction.md](references/design-token-extraction.md) for the full workflow: XML parsing → token extraction → python-pptx design system → QA.

### NotebookLM → PPT Pipeline

For content-rich presentations (competitions, demos), use NotebookLM's `generate slide-deck` for content generation, then recreate with python-pptx matching the user's existing design language:

1. Upload source docs to NotebookLM
2. `notebooklm generate slide-deck` + `notebooklm ask` to extract content (download may fail due to auth; use `ask` to get descriptions as fallback)
3. python-pptx recreation with extracted design tokens
4. PDF → image QA loop

**Synthos competition PPT design tokens** (confirmed beautiful style):
- Background: `#0F172A` (slate-900), solid fill
- Accent: `#3B82F6` (blue-500) — vertical bars on left of cards, metric numbers
- Card: `#1E293B` (slate-800) fill + `#334155` border
- Text: `#F8FAFC` (light) / `#06B6D4` (cyan for subtitle) / `#94A3B8` (secondary)
- Font: Arial, slide size 13.33×7.5 inches (1280×720, 16:9)
- Decorative pattern: blue vertical Rectangle (45720 × ~1M EMU) on left edge of each card — this is the signature visual element, do NOT remove
- Cards: Rounded Rectangle (MSO_SHAPE.ROUNDED_RECTANGLE) with card fill + border

**7+1 Philosophy Framework Slide Pattern:**
When the user says "哲学框架应该重点论述" or wants to highlight 文言 (Classical Chinese) philosophy expressions, repurpose the 2×3 card grid. Each card shows:
- **Title line** (top, bold 16pt, colored): The 文言 four-character maxim (e.g., "源一不二，熵减生生")
- **Description line** (bottom, lighter 11pt): Modern explanation
- **Left accent bar**: Color-coded per dimension (blue for 终极目的, cyan for 贯穿, green for 东方, purple for 西方)

Card mapping for 7+1 framework:
- Row 1: 终极目的 (熵减生生) + 贯穿原则 (大道至简)
- Row 2: 东方本体论 (格物通理 + 天人合一)
- Row 3: 西方认识论 (经权度信 + 庄周观模)

**Number Verification Protocol for Competition PPTs:**
The user insists on data accuracy. Before placing ANY number in a competition PPT:
1. Ask: "Can this number be traced to a run log, state file, or code output?"
2. If unsure → use qualitative language ("多轮" not "53轮", "优异" not "0.982", "多次" not "18次")
3. "自进化引擎" is acceptable as a concept name (user confirmed it can judge thresholds and execute autonomously)
4. Never use unverified efficiency claims like "6X faster", "85% coverage", "-40% time"
5. When user says "核查数字" — search session history and system state files for source data before accepting any number

---

## Design Ideas

**Don't create boring slides.** Plain bullets on a white background won't impress anyone. Consider ideas from this list for each slide.

### Before Starting

- **Pick a bold, content-informed color palette**: The palette should feel designed for THIS topic. If swapping your colors into a completely different presentation would still "work," you haven't made specific enough choices.
- **Dominance over equality**: One color should dominate (60-70% visual weight), with 1-2 supporting tones and one sharp accent. Never give all colors equal weight.
- **Dark/light contrast**: Dark backgrounds for title + conclusion slides, light for content ("sandwich" structure). Or commit to dark throughout for a premium feel.
- **Commit to a visual motif**: Pick ONE distinctive element and repeat it — rounded image frames, icons in colored circles, thick single-side borders. Carry it across every slide.

### Color Palettes

Choose colors that match your topic — don't default to generic blue. Use these palettes as inspiration:

| Theme | Primary | Secondary | Accent |
|-------|---------|-----------|--------|
| **Midnight Executive** | `1E2761` (navy) | `CADCFC` (ice blue) | `FFFFFF` (white) |
| **Forest & Moss** | `2C5F2D` (forest) | `97BC62` (moss) | `F5F5F5` (cream) |
| **Coral Energy** | `F96167` (coral) | `F9E795` (gold) | `2F3C7E` (navy) |
| **Warm Terracotta** | `B85042` (terracotta) | `E7E8D1` (sand) | `A7BEAE` (sage) |
| **Ocean Gradient** | `065A82` (deep blue) | `1C7293` (teal) | `21295C` (midnight) |
| **Charcoal Minimal** | `36454F` (charcoal) | `F2F2F2` (off-white) | `212121` (black) |
| **Teal Trust** | `028090` (teal) | `00A896` (seafoam) | `02C39A` (mint) |
| **Berry & Cream** | `6D2E46` (berry) | `A26769` (dusty rose) | `ECE2D0` (cream) |
| **Sage Calm** | `84B59F` (sage) | `69A297` (eucalyptus) | `50808E` (slate) |
| **Cherry Bold** | `990011` (cherry) | `FCF6F5` (off-white) | `2F3C7E` (navy) |

### For Each Slide

**Every slide needs a visual element** — image, chart, icon, or shape. Text-only slides are forgettable.

**Layout options:**
- Two-column (text left, illustration on right)
- Icon + text rows (icon in colored circle, bold header, description below)
- 2x2 or 2x3 grid (image on one side, grid of content blocks on other)
- Half-bleed image (full left or right side) with content overlay

**Data display:**
- Large stat callouts (big numbers 60-72pt with small labels below)
- Comparison columns (before/after, pros/cons, side-by-side options)
- Timeline or process flow (numbered steps, arrows)

**Visual polish:**
- Icons in small colored circles next to section headers
- Italic accent text for key stats or taglines

### Typography

**Choose an interesting font pairing** — don't default to Arial. Pick a header font with personality and pair it with a clean body font.

| Header Font | Body Font |
|-------------|-----------|
| Georgia | Calibri |
| Arial Black | Arial |
| Calibri | Calibri Light |
| Cambria | Calibri |
| Trebuchet MS | Calibri |
| Impact | Arial |
| Palatino | Garamond |
| Consolas | Calibri |

| Element | Size |
|---------|------|
| Slide title | 36-44pt bold |
| Section header | 20-24pt bold |
| Body text | 14-16pt |
| Captions | 10-12pt muted |

### Spacing

- 0.5" minimum margins
- 0.3-0.5" between content blocks
- Leave breathing room—don't fill every inch

### Avoid (Common Mistakes)

- **Don't repeat the same layout** — vary columns, cards, and callouts across slides
- **Don't center body text** — left-align paragraphs and lists; center only titles
- **Don't skimp on size contrast** — titles need 36pt+ to stand out from 14-16pt body
- **Don't default to blue** — pick colors that reflect the specific topic
- **Don't mix spacing randomly** — choose 0.3" or 0.5" gaps and use consistently
- **Don't style one slide and leave the rest plain** — commit fully or keep it simple throughout
- **Don't create text-only slides** — add images, icons, charts, or visual elements; avoid plain title + bullets
- **Don't forget text box padding** — when aligning lines or shapes with text edges, set `margin: 0` on the text box or offset the shape to account for padding
- **Don't use low-contrast elements** — icons AND text need strong contrast against the background; avoid light text on light backgrounds or dark text on dark backgrounds
- **Don't use accent lines under titles without user confirmation** — some users' existing PPTs use vertical accent bars as their signature element. Inspect the user's reference PPT first. If they already use accent lines, preserve them. If creating from scratch, skip them unless explicitly requested.

---

## QA (Required)

**Assume there are problems. Your job is to find them.**

Your first render is almost never correct. Approach QA as a bug hunt, not a confirmation step. If you found zero issues on first inspection, you weren't looking hard enough.

### Content QA

```bash
python -m markitdown output.pptx
```

Check for missing content, typos, wrong order.

**When using templates, check for leftover placeholder text:**

```bash
python -m markitdown output.pptx | grep -iE "xxxx|lorem|ipsum|this.*(page|slide).*layout"
```

If grep returns results, fix them before declaring success.

### Visual QA

**⚠️ USE SUBAGENTS** — even for 2-3 slides. You've been staring at the code and will see what you expect, not what's there. Subagents have fresh eyes.

Convert slides to images (see [Converting to Images](#converting-to-images)), then use this prompt:

```
Visually inspect these slides. Assume there are issues — find them.

Look for:
- Overlapping elements (text through shapes, lines through words, stacked elements)
- Text overflow or cut off at edges/box boundaries
- Decorative lines positioned for single-line text but title wrapped to two lines
- Source citations or footers colliding with content above
- Elements too close (< 0.3" gaps) or cards/sections nearly touching
- Uneven gaps (large empty area in one place, cramped in another)
- Insufficient margin from slide edges (< 0.5")
- Columns or similar elements not aligned consistently
- Low-contrast text (e.g., light gray text on cream-colored background)
- Low-contrast icons (e.g., dark icons on dark backgrounds without a contrasting circle)
- Text boxes too narrow causing excessive wrapping
- Leftover placeholder content

For each slide, list issues or areas of concern, even if minor.

Read and analyze these images:
1. /path/to/slide-01.jpg (Expected: [brief description])
2. /path/to/slide-02.jpg (Expected: [brief description])

Report ALL issues found, including minor ones.
```

### Verification Loop

1. Generate slides → Convert to images → Inspect
2. **List issues found** (if none found, look again more critically)
3. Fix issues
4. **Re-verify affected slides** — one fix often creates another problem
5. Repeat until a full pass reveals no new issues

**Do not declare success until you've completed at least one fix-and-verify cycle.**

---

## Converting to Images

Convert presentations to individual slide images for visual inspection:

```bash
python scripts/office/soffice.py --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 150 output.pdf slide
```

This creates `slide-01.jpg`, `slide-02.jpg`, etc.

To re-render specific slides after fixes:

```bash
pdftoppm -jpeg -r 150 -f N -l N output.pdf slide-fixed
```

### Converting to Video (for Demos)

When slides are intended for video presentation (competition demos, online courses), convert high-res PNGs to video segments. See `ffmpeg-video-audio-sync` skill's `references/pptx-video-workflow.md` for the full pipeline: PPTX → PDF → PNG (300dpi) → MP4 segments → narration sync.

**⚠️ Critical for video:** Use `-preset medium -crf 18` (not `ultrafast`/`fast`) when encoding PNG→MP4 segments, and convert to TS before binary concatenation. MP4 concat with `-c copy` silently drops frames.

---

## Dependencies

- `pip install "markitdown[pptx]"` - text extraction
- `pip install Pillow` - thumbnail grids
- `npm install -g pptxgenjs` - creating from scratch
- LibreOffice (`soffice`) - PDF conversion (auto-configured for sandboxed environments via `scripts/office/soffice.py`)
- Poppler (`pdftoppm`) - PDF to images
