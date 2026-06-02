# SynthOS Figure Iteration — Real Failure Cases

This file documents real layout bugs, user corrections, and fixes from SynthOS paper figure iteration at `/media/yakeworld/sda2/Synthos/outputs/runs/*/latex/figures/`.

## Case 1: `cap` Style Name Conflict (2026-05-18)

**Symptom:** TikZ log showed repeated `pgfkeys Error: The key '/tikz/cap' requires a value`. Although compilation succeeded, the caption text nodes using `\node[cap]` were NOT getting the custom style applied — they rendered at default TikZ font size, likely with no color or alignment styling.

**Root cause:** TikZ reserves `cap`, `butt`, `round`, and `rect` as built-in `/tikz/cap` key values for line-end configuration. Defining `cap/.style={...}` conflicts — TikZ interprets `cap` as setting line cap style, not applying the custom style.

**Fix:** Rename to `cpt` (or `annot`, `captionstyle`, etc.). Change both the style definition AND all `\node[cap]` usages:
```diff
-    cap/.style={text=black!35, font=\sffamily\tiny, align=center},
+    cpt/.style={text=black!35, font=\sffamily\tiny, align=center},
- \node[cap] at (0,5.55) {text};
+ \node[cpt] at (0,5.55) {text};
```

**Detection:** Always grep the `.log` file for `pgfkeys Error`. If present, immediately find and rename the conflicting style name.

## Case 2: Cross-Layer Size Inconsistency (2026-05-18)

**Symptom:** User reports "you changed the first box but the second and third didn't change — inconsistency." After expanding L3 (Absorption) container from 10cm→11cm wide, L2 (Evolution) and L1 (Cognitive Atoms) stayed at 10cm.

**Root cause:** Focused only on the problem layer (L3 had overflowing text), didn't review ALL layers for consistency after the change.

**Fix:** When modifying ANY layer's container, verify ALL `\draw[layer] (-W, ...) rectangle (W, ...)` commands share the same width. Expand remaining layers to match.

**Prevention checklist when resizing:**
1. ✅ Did I change all layer container widths to match?
2. ✅ Did I check that arrows still connect properly between layers?
3. ✅ Did I verify the title position doesn't overlap the expanded top layer?
4. ✅ Did I re-verify text fits in ALL layers' boxes (not just the modified one)?

## Case 3: User Said "Text Outside Box" When Text Technically Fits (2026-05-18)

**Symptom:** User kept reporting "two words outside the box" in L3. After verifying with pdftotext measurement, the widest text ("Philosophy" at 24.59pt) fit inside the 20mm (56.9pt) box with 57% margin.

**Root cause:** The `cap` style naming conflict (Case 1) was likely causing the caption text to render unstyled, making it appear at wrong size/position and creating visual confusion. Once `cap`→`cpt` was fixed, the visual issue disappeared.

**Lesson:** When user reports layout issues that measurements don't confirm, check for silent TikZ errors (color/style definition conflicts) that might cause incorrect rendering.

## Case 4: Failed to Load Skill Before Figure Iteration (2026-05-18)

**Symptom:** User was iterating on Figure 1 — expanding box sizes, adjusting spacing, fixing `cap` conflict. After 4 cycles of dimension tweaks, user said: *"作图应该调用技能去完成的。"*

**Root cause:** Agent skipped `skill_view("academic-diagram")` before touching figure code, assuming iteration was "simple resizing" that didn't need the full workflow. This caused:
- No Figure Contract written before modifications
- No verification checklist run before each push
- No full-layer consistency check — three partial edits instead of one coordinated pass
- User had to correct the approach explicitly

**Fix sequence when ANY figure issue arises:**
1. `skill_view("academic-diagram")` — immediately, before any code change
2. Load `references/synthos-figure-iteration.md` for known bugs
3. Write Figure Contract (Step 0)
4. Plan ALL changes across ALL layers in one pass
5. Run Step 5 verification before pushing

**Detection:** If you're modifying figure code and haven't loaded `academic-diagram` in the same message, STOP and load it first.

**Prevention:** The skill's opening warning was strengthened to include iteration.
The "When to load" section was expanded with explicit iteration triggers and a
rule-of-thumb: *if response involves `\documentclass[tikz]` or
`\includegraphics{fig_...}`, load this skill first.*

## Case 5: Layer Height Inconsistency After Width Fix (2026-05-18)

**Symptom:** After fixing cross-layer width (all → 11cm), user reported:
*"图1，它的三个框高度不一致"* — L3=3.5cm, L2=2.8cm, L1=2.0cm.

**Root cause:** Focused on width only. Each layer's `\draw[layer]` was sized
independently to "just fit" content, producing three different heights.

**Fix:** Set ALL layers to uniform height. Pick height that accommodates
tallest content with ≥0.3cm padding, then apply identically:
```diff
-L3: (-5.5,5.2)-(5.5,8.7)  h=3.5
-L2: (-5.5,1.4)-(5.5,4.2)  h=2.8
-L1: (-5.5,-1.0)-(5.5,1.0) h=2.0
+L3: (-5.5,5.5)-(5.5,8.5)  h=3.0
+L2: (-5.5,2.2)-(5.5,5.2)  h=3.0
+L1: (-5.5,-0.5)-(5.5,2.5) h=3.0
```

**Checklist when making ANY rectangle dimension change:**
1. ✅ All `\draw[layer]` have same width → verify both x-coordinates match
2. ✅ All `\draw[layer]` have same height → verify (ymax - ymin) is identical
3. ✅ Content vertically centered within each layer after height change
4. ✅ Inter-layer arrows still connect with uniform spacing

This bug was discovered independently after Case 2 (width only) was fixed,
showing width+height must be verified TOGETHER. A partial fix wastes cycles.

## Case 6: Layer Background Overlap From Rounded Corners (2026-05-18)

**Symptom:** User reported *"图一的框2和框三发生了重叠"* — layers 2 and 3 visually
overlapped despite bg_gap=0.3cm in the code.

**Root cause:** The layer style used `rounded corners=2.5mm`. Each rounded corner
extends 2.5mm beyond its rectangle bounds. With bg_gap=0.3cm:
- L3 visual bottom = L3_bottom - 0.25 = 5.5 - 0.25 = 5.25
- L2 visual top = L2_top + 0.25 = 5.2 + 0.25 = 5.45
- Overlap = 5.45 - 5.25 = 0.2cm (2mm)

The Gap Verification algorithm in `references/layout-algorithm.md` did not account
for `rounded corners` visual extension. Users see overlapping rectangles even
when coordinates show a gap.

**Fix:** Increase bg_gap to ≥ 0.8cm for 2.5mm rounding (0.3cm visual gap +
0.5cm rounded corner allowance). After fix: L3_bottom=5.5, L2_top=4.7:
- visual_gap = (5.5-4.7) - 2×0.25 = 0.8-0.5 = 0.3cm ✅

**Detection:** Any time `rounded corners` > 1.5mm is used, calculate visual
overlap before assuming gaps are clean. Do: `visual_gap = bg_gap - 2*R_mm/10`.

**Prevention:** The gap verification formula in `references/layout-algorithm.md`
was corrected to include rounded corner visual extension. Always use the
corrected formula instead of the naive `bg_gap ≥ 0.3`.

**Inter-layer arrow check:** After fixing gap, verify arrows still connect
properly. Arrow should start at one layer's inner edge and end at the other
layer's inner edge, not overshoot into the layer interior:
```diff
-% Before: arrows overshooting
+% After: arrow just crosses the gap
+\draw[arr] (0,4.7) -- (0,5.5);    % L2→L3: from L2 top edge to L3 bottom edge
```
