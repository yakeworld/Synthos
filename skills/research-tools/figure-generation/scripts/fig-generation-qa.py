#!/usr/bin/env python3
"""
Precise QA using get_window_extent (the correct method per figure-generation skill).
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import json
import os

fig, ax = plt.subplots(figsize=(14, 9.5))
ax.set_xlim(0, 14)
ax.set_ylim(0, 9.5)
ax.axis('off')

C_EXPERT_A = '#2166AC'
C_EXPERT_B = '#67A938'
C_EXPERT_C = '#E07A2F'
C_CLEAR_NEG = '#00A86B'
C_CLEAR_POS = '#A6CEE3'
C_SOTA = '#D95F02'

with open("/media/yakeworld/sda2/academic_writer/article10_breast/generalization_results.json") as f:
    all_results = json.load(f)
wdbc = all_results.get("WDBC (sklearn - Diagnostic)", {})
accuracy = wdbc.get("mean_overall_accuracy", 96.88)
f1 = wdbc.get("mean_overall_f1", 97.55)
auc_v = wdbc.get("mean_overall_auc", 98.6)
auto_rate = wdbc.get("mean_automation_rate", 61.6)
auto_acc = wdbc.get("mean_automation_accuracy", 99.42)
gray_acc = wdbc.get("mean_gray_zone_accuracy", 92.2)

boxes = {}

input_box = FancyBboxPatch((5.3, 7.55), 3.4, 0.6, boxstyle="round,pad=0.06",
                            edgecolor="#333333", facecolor="#f0f0f0", linewidth=1.5)
ax.add_patch(input_box)
boxes['input'] = input_box
ax.text(7, 7.85, "Breast Cancer Sample", ha="center", va="center",
        fontsize=10, fontweight="bold", color="#222222")
ax.text(7, 7.5, "PowerTransformer + SelectKBest (ANOVA F)", ha="center", va="center",
        fontsize=7.5, color="#777777")

from matplotlib.patches import FancyArrowPatch
arrow1 = FancyArrowPatch((7, 7.55), (4.35, 6.68),
                         arrowstyle="->", mutation_scale=22,
                         color="#444444", linewidth=2.2)
ax.add_patch(arrow1)

eb_box = FancyBboxPatch((0.3, 5.3), 4.2, 1.4, boxstyle="round,pad=0.08",
                        edgecolor=C_EXPERT_B, facecolor="#f0f8ec",
                        linewidth=2.2)
ax.add_patch(eb_box)
boxes['expert_b'] = eb_box
ax.text(2.4, 6.4, "Expert B: Catcher", ha="center", va="top",
        fontsize=12, fontweight="bold", color=C_EXPERT_B)
ax.text(2.4, 6.0, "Support Vector Classifier (SVC)", ha="center", va="top",
        fontsize=9, color="#444444")
ax.text(2.4, 5.7, "RBF Kernel, Probability Calibrated", ha="center", va="top",
        fontsize=8, color="#666666")
ax.text(2.4, 5.45, "Borderline-SMOTE + Aggressive Class Weighting", ha="center", va="top",
        fontsize=7.5, color="#888888")

cn_box = FancyBboxPatch((5.3, 5.55), 3.2, 0.85, boxstyle="round,pad=0.06",
                        edgecolor=C_CLEAR_NEG, facecolor="#e8f5e9",
                        linewidth=1.8)
ax.add_patch(cn_box)
boxes['clear_negative'] = cn_box
ax.text(6.9, 6.15, "CLEAR NEGATIVE", ha="center", va="center",
        fontsize=10.5, fontweight="bold", color="#2e7d32")
ax.text(6.9, 5.85, "P(malignant) < 0.03", ha="center", va="center",
        fontsize=8.5, color="#2e7d32", fontweight="bold")
ax.text(6.9, 5.65, "Automated \u2014 No pathologist review needed",
        ha="center", va="center", fontsize=7.5, color="#555555")

arrow2 = FancyArrowPatch((4.5, 6.0), (5.3, 5.97),
                         arrowstyle="->", mutation_scale=20,
                         color=C_EXPERT_B, linewidth=2)
ax.add_patch(arrow2)

ea_box = FancyBboxPatch((0.3, 2.8), 4.2, 1.4, boxstyle="round,pad=0.08",
                        edgecolor=C_EXPERT_A, facecolor="#e3f2fd",
                        linewidth=2.2)
ax.add_patch(ea_box)
boxes['expert_a'] = ea_box
ax.text(2.4, 3.9, "Expert A: Refiner", ha="center", va="top",
        fontsize=12, fontweight="bold", color=C_EXPERT_A)
ax.text(2.4, 3.5, "VotingClassifier: RF + CatBoost + ExtraTrees",
        ha="center", va="top", fontsize=9, color="#444444")
ax.text(2.4, 3.15, "Soft Voting, 300 estimators each", ha="center", va="top",
        fontsize=8, color="#666666")
ax.text(2.4, 2.95, "High Precision Optimized", ha="center", va="top",
        fontsize=8, color=C_EXPERT_A, fontweight="bold")

cp_box = FancyBboxPatch((5.3, 3.05), 3.2, 0.85, boxstyle="round,pad=0.06",
                        edgecolor=C_CLEAR_POS, facecolor="#e8f5e9",
                        linewidth=1.8)
ax.add_patch(cp_box)
boxes['clear_positive'] = cp_box
ax.text(6.9, 3.65, "CLEAR POSITIVE", ha="center", va="center",
        fontsize=10.5, fontweight="bold", color=C_EXPERT_A)
ax.text(6.9, 3.35, "P(malignant) > 0.95", ha="center", va="center",
        fontsize=8.5, color=C_EXPERT_A, fontweight="bold")
ax.text(6.9, 3.15, "Automated \u2014 No pathologist review needed",
        ha="center", va="center", fontsize=7.5, color="#555555")

arrow3 = FancyArrowPatch((4.5, 3.5), (5.3, 3.47),
                         arrowstyle="->", mutation_scale=20,
                         color=C_EXPERT_A, linewidth=2)
ax.add_patch(arrow3)

arrow4 = FancyArrowPatch((2.4, 5.3), (2.4, 1.62),
                         arrowstyle="->", mutation_scale=20,
                         color=C_EXPERT_C, linewidth=1.8, linestyle="--", alpha=0.7)
ax.add_patch(arrow4)
arrow5 = FancyArrowPatch((2.4, 2.8), (2.4, 1.62),
                         arrowstyle="->", mutation_scale=20,
                         color=C_EXPERT_C, linewidth=1.8, linestyle="--", alpha=0.7)
ax.add_patch(arrow5)
ax.text(0.6, 3.6, "Uncertain\nCases", ha="center", va="center",
        fontsize=8, color="#888888", rotation=90, fontweight="bold")

ec_box = FancyBboxPatch((0.3, 0.2), 4.2, 1.45, boxstyle="round,pad=0.08",
                        edgecolor=C_EXPERT_C, facecolor="#fff3e0",
                        linewidth=2.5)
ax.add_patch(ec_box)
boxes['expert_c'] = ec_box
ax.text(2.4, 1.45, "Expert C: Arbiter", ha="center", va="top",
        fontsize=12, fontweight="bold", color=C_EXPERT_C)
ax.text(2.4, 1.1, "Meta-Learning Stacking Classifier", ha="center", va="top",
        fontsize=9, color="#444444")
ax.text(2.4, 0.78, "Base: RF + SVC  |  Meta: Logistic Regression",
        ha="center", va="top", fontsize=8, color="#666666")
ax.text(2.4, 0.5, "Class Weight 1:10 (malignancy prioritized)",
        ha="center", va="top", fontsize=7.5, color="#888888")
ax.text(2.4, 0.32, "5-Fold CV Meta-Features from Experts A & B",
        ha="center", va="top", fontsize=7, color="#999999")

arrow6 = FancyArrowPatch((4.5, 0.92), (5.3, 0.92),
                         arrowstyle="->", mutation_scale=20,
                         color=C_EXPERT_C, linewidth=2)
ax.add_patch(arrow6)

fd_box = FancyBboxPatch((5.3, 0.55), 3.2, 0.85, boxstyle="round,pad=0.06",
                        edgecolor=C_EXPERT_C, facecolor="#fff8e1",
                        linewidth=2)
ax.add_patch(fd_box)
boxes['gray_zone'] = fd_box
ax.text(6.9, 1.12, "GRAY ZONE", ha="center", va="center",
        fontsize=10.5, fontweight="bold", color=C_EXPERT_C)
ax.text(6.9, 0.88, "Expert C Final Decision", ha="center", va="center",
        fontsize=8.5, color=C_EXPERT_C, fontweight="bold")
ax.text(6.9, 0.67, "Requires pathologist review",
        ha="center", va="center", fontsize=7.5, color="#555555")

meta_box = FancyBboxPatch((9.2, 5.5), 4.3, 3.0,
                           boxstyle="round,pad=0.06",
                           edgecolor="#555555", facecolor="#fafafa",
                           linewidth=1.2, linestyle="dashed")
ax.add_patch(meta_box)
boxes['meta_pipeline'] = meta_box
ax.text(11.35, 8.2, "Meta-Feature Pipeline", ha="center", va="top",
        fontsize=10.5, fontweight="bold", color="#333333")
for i, line in enumerate([
    "1. Expert B Probability  \u2192  Expert C Input",
    "2. Expert A Probability  \u2192  Expert C Input",
    "3. Combined with 33 engineered features",
    "    \u2014 size_shape_interaction",
    "    \u2014 nuclear_abnormality_score",
    "    \u2014 triple_product_score",
    "4. Stacking: RF + SVC \u2192 LR Meta-Learner",
    "5. 5-Fold CV to prevent overfitting",
]):
    weight = "bold" if i < 3 else "normal"
    ax.text(9.5, 7.9 - i * 0.33, line, ha="left", va="top",
            fontsize=7.8, color="#444444", fontweight=weight)

bench_box = FancyBboxPatch((9.2, 1.3), 4.3, 3.6,
                            boxstyle="round,pad=0.06",
                            edgecolor=C_SOTA, facecolor="#fafafa",
                            linewidth=1.2)
ax.add_patch(bench_box)
boxes['benchmarks'] = bench_box
ax.text(11.35, 4.7, "Overall Performance", ha="center", va="top",
        fontsize=10.5, fontweight="bold", color="#333333")
bench_lines = [
    ("Overall Accuracy",  f"{accuracy:.2f}%"),
    ("Overall F1-Score",  f"{f1:.2f}%"),
    ("Overall AUC",       f"{auc_v:.2f}%"),
    ("",                  ""),
    ("Automation Rate",   f"{auto_rate:.2f}%"),
    ("Automation Acc.",   f"{auto_acc:.2f}%"),
    ("Gray Zone Acc.",    f"{gray_acc:.2f}%"),
    ("",                  ""),
    ("Clear Negative%",   f"{wdbc.get('mean_clear_negative_count', 22.67)/569*100:.1f}%"),
    ("Clear Positive%",   f"{wdbc.get('mean_clear_positive_count', 82.67)/569*100:.1f}%"),
    ("Gray Zone%",        f"{wdbc.get('mean_gray_zone_count', 65.67)/569*100:.1f}%"),
]
for i, (label, value) in enumerate(bench_lines):
    if label == "":
        ax.plot([9.6, 13.1], [4.35 - i * 0.28, 4.35 - i * 0.28],
                color="#dddddd", linewidth=0.5)
        continue
    ax.text(9.5, 4.45 - i * 0.28, f"{label}:", ha="left", va="top",
            fontsize=8.5, color="#555555")
    ax.text(11.0, 4.45 - i * 0.28, f"{value}", ha="left", va="top",
            fontsize=8.5, fontweight="bold", color="#222222")

design_box = FancyBboxPatch((0.3, 8.0), 3.4, 1.0,
                             boxstyle="round,pad=0.05",
                             edgecolor="#333333", facecolor="#f9f9f9",
                             linewidth=1)
ax.add_patch(design_box)
boxes['key_principles'] = design_box
ax.text(2.0, 8.8, "Key Design Principles", ha="center", va="top",
        fontsize=9, fontweight="bold", color="#333333")
for i, p in enumerate(["Sequential cascaded triage", "High-recall Catcher (B) first",
                          "High-precision Refiner (A) second", "Expert C arbitrates Gray Zone"]):
    ax.text(0.6, 8.55 - i * 0.18, f"\u2022 {p}", ha="left", va="top",
            fontsize=7.5, color="#555555")

# =============================================================================
# DRAW AND MEASURE
# =============================================================================

fig.canvas.draw()
renderer = fig.canvas.get_renderer()

print("=" * 70)
print("PRECISE QA: get_window_extent measurement")
print("=" * 70)
print()

# Get all box extents in axes coordinates
box_extents = {}
for name, patch in boxes.items():
    bb = patch.get_window_extent(renderer)
    # Convert to axes coordinates
    t = ax.transData.inverted()
    bb_ax = bb.transformed(t)
    box_extents[name] = (bb_ax.x0, bb_ax.y0, bb_ax.width, bb_ax.height)
    print(f"  Box '{name}': axes coords x={bb_ax.x0:.2f}, y={bb_ax.y0:.2f}, w={bb_ax.width:.2f}, h={bb_ax.height:.2f}")

# Check all text elements
print()
print("TEXT EXTENTS:")
print("-" * 50)
text_overflow = []
for child in ax.get_children():
    if isinstance(child, matplotlib.text.Text):
        text = child.get_text()
        if not text or text.startswith('0') or text.startswith('1') or text.startswith('2'):
            # Skip bench value texts that might look like numbers
            pass
        
        bbox = child.get_window_extent(renderer)
        # Convert to axes coordinates
        bbox_ax = bbox.transformed(ax.transData.inverted())
        x, y = child.get_position()
        fs = child.get_fontsize()
        
        # Find which box this text is in
        in_box = None
        for name, (bx, by, bw, bh) in box_extents.items():
            if bx - 0.1 <= x <= bx + bw + 0.1 and by - 0.1 <= y <= by + bh + 0.1:
                in_box = name
                break
        
        if in_box:
            bx, by, bw, bh = box_extents[in_box]
            pad = 0.06  # FancyBbox pad
            avail_w = bw - 2 * pad
            avail_h = bh - 2 * pad
            
            tw = bbox_ax.width
            th = bbox_ax.height
            
            overflow = ""
            if tw > avail_w:
                overflow = f"WIDTH: text {tw:.4f}in > box avail {avail_w:.4f}in"
            if th > avail_h:
                if overflow:
                    overflow += f" + HEIGHT: text {th:.4f}in > box avail {avail_h:.4f}in"
                else:
                    overflow = f"HEIGHT: text {th:.4f}in > box avail {avail_h:.4f}in"
            
            status = "✅" if not overflow else "❌"
            if overflow:
                text_overflow.append(f"TEXT_OVERFLOW: '{text[:30]}' in {in_box}: {overflow}")
            print(f"  {status} '{text[:40]}...' in '{in_box}' at ({x:.1f},{y:.2f}): {tw:.4f}x{th:.4f}in vs avail {avail_w:.4f}x{avail_h:.4f}in{(' ['+overflow+']') if overflow else ''}")

# Arrow endpoint check
print()
print("ARROW ENDPOINTS:")
print("-" * 50)

arrow_defs = [
    ("arrow1", (7, 7.55), (4.35, 6.68), 'expert_b'),
    ("arrow2", (4.5, 6.0), (5.3, 5.97), 'clear_negative'),
    ("arrow3", (4.5, 3.5), (5.3, 3.47), 'clear_positive'),
    ("arrow4", (2.4, 5.3), (2.4, 1.62), 'expert_c'),
    ("arrow5", (2.4, 2.8), (2.4, 1.62), 'expert_c'),
    ("arrow6", (4.5, 0.92), (5.3, 0.92), 'gray_zone'),
]

arrow_failures = []
for aname, (x1, y1), (x2, y2), target in arrow_defs:
    if target in box_extents:
        tx, ty, tw, th = box_extents[target]
        x_ok = tx <= x2 <= tx + tw
        y_ok = ty <= y2 <= ty + th
        inside = x_ok and y_ok
        
        status = "✅" if inside else "❌"
        if not inside:
            arrow_failures.append(f"{aname}: ({x2},{y2}) not in {target}[{tx:.2f},{ty:.2f}+{tw:.2f}x{th:.2f}]")
        
        print(f"  {status} {aname}: ({x2},{y2}) in {target}: x_ok={x_ok}({x2:.2f} in [{tx:.2f},{tx+tw:.2f}]) y_ok={y_ok}({y2:.2f} in [{ty:.2f},{ty+th:.2f}])")

# Box overlaps
print()
print("BOX OVERLAPS:")
print("-" * 50)
overlap = False
for n1, (x1, y1, w1, h1) in box_extents.items():
    for n2, (x2, y2, w2, h2) in box_extents.items():
        if n1 < n2:
            if not (x1+w1 < x2 or x2+w2 < x1 or y1+h1 < y2 or y2+h2 < y1):
                print(f"  ❌ OVERLAP: {n1} <-> {n2}")
                overlap = True
if not overlap:
    print("  ✅ No overlaps")

# Boundary
print()
print("BOUNDARY:")
print("-" * 50)
boundary_issues = []
for name, (x, y, w, h) in box_extents.items():
    if x < 0 or y < 0:
        boundary_issues.append(f"{name}: negative coord ({x:.2f},{y:.2f})")
    if x + w > 14:
        boundary_issues.append(f"{name}: right {x+w:.2f} > 14")
    if y + h > 9.5:
        boundary_issues.append(f"{name}: bottom {y+h:.2f} > 9.5")
if boundary_issues:
    for b in boundary_issues:
        print(f"  ❌ {b}")
else:
    print("  ✅ All within bounds")

print()
print("=" * 70)
print("RESULT")
print("=" * 70)
print(f"  Text overflow:   {len(text_overflow)}")
for t in text_overflow:
    print(f"    - {t}")
print(f"  Arrow failures:  {len(arrow_failures)}")
for a in arrow_failures:
    print(f"    - {a}")
print(f"  Box overlaps:    {'Yes' if overlap else 'No'}")
print(f"  Boundary:        {'Yes' if boundary_issues else 'No'}")
print()

if text_overflow or arrow_failures or overlap or boundary_issues:
    print("OVERALL: FAIL ❌")
    for t in text_overflow:
        print(f"  ISSUE: {t}")
else:
    print("OVERALL: PASS ✅")

fig.savefig('/tmp/fig1_precise_qa.png', dpi=300, facecolor='white')
plt.close(fig)
print(f"\nSaved: /tmp/fig1_precise_qa.png")
