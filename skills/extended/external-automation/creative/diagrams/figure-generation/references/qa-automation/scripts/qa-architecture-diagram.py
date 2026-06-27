#!/usr/bin/env python3
"""QA核心 — 验证所有matplotlib图表几何正确性（qa-automation副本）。

SKILL.md 原理绑定：
- 模式G: QA自动化
- 铁律: QA不通过→sys.exit(1)→无输出→修复后重新生成
- 设计规则: 箭头终点必须在目标框AABB内，不是"接近"
- 设计规则: 所有框无重叠（margin=5pt）
- 设计规则: 文字必须在框内（精确测量，非fontsize估算）

注: 这是 scripts/qa-architecture-diagram.py 的副本，位于 references/qa-automation/ 作为历史参考。
优先使用 scripts/qa-architecture-diagram.py。
"""
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import re
import numpy as np

fig, ax = plt.subplots(figsize=(1, 1))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)


def get_text_extent(text, fontsize, fontweight='normal', fontfamily='sans-serif'):
    """Measure text rendering size in inches using matplotlib's renderer."""
    text_obj = ax.text(0, 0, text, fontsize=fontsize, fontweight=fontweight, fontfamily=fontfamily)
    fig.canvas.draw()
    bbox = text_obj.get_window_extent(fig.canvas.get_renderer())
    bbox_fig = bbox.transformed(fig.transFigure.inverted())
    w = bbox_fig.width
    h = bbox_fig.height
    text_obj.remove()
    return w, h


def estimate_text_extent(text, fontsize, fontweight='normal'):
    """Fast estimate without canvas.draw(). Good for pre-plot checks."""
    if fontweight == 'bold':
        multiplier = 0.65
    else:
        multiplier = 0.55
    return len(text) * fontsize * multiplier / 72.0  # inches


def check_color_blind_safe(colors_list, label='colors'):
    """Check if colors are distinguishable by common color-blind profiles.
    
    Uses a simplified approach: checks for pure red/green pairs and high-saturation
    combinations that are indistinguishable to deuteranopes.
    
    Returns (safe: bool, issues: list).
    """
    import colorsys
    
    issues = []
    colors_hex = [c for c in colors_list if isinstance(c, str) and c.startswith('#')]
    
    # Convert to RGB
    colors_rgb = []
    for c in colors_hex:
        r = int(c[1:3], 16) / 255.0
        g = int(c[3:5], 16) / 255.0
        b = int(c[5:7], 16) / 255.0
        colors_rgb.append((r, g, b))
    
    # Check each pair for red-green proximity (deuteranopia test)
    for i in range(len(colors_rgb)):
        for j in range(i + 1, len(colors_rgb)):
            r1, g1, b1 = colors_rgb[i]
            r2, g2, b2 = colors_rgb[j]
            
            # Simulate deuteranopia (red-green colorblindness)
            # Simple approximation: L and M cone signals merge
            sim1_r = 0.59 * r1 + 0.41 * b1  # deuteranopia sim
            sim1_g = 0.59 * g1 + 0.41 * b1
            sim2_r = 0.59 * r2 + 0.41 * b2
            sim2_g = 0.59 * g2 + 0.41 * b2
            
            # If both simulated colors are very close, flag it
            dist = np.sqrt((sim1_r - sim2_r)**2 + (sim1_g - sim2_g)**2 + (b1 - b2)**2)
            if dist < 0.15:
                issues.append(
                    f"[{label}] Colors {colors_hex[i]} and {colors_hex[j]} may be "
                    f"indistinguishable to red-green colorblind viewers (Euclidean "
                    f"distance in simulated space: {dist:.3f} < 0.15)"
                )
    
    # Check for red-green as the ONLY distinguishing pair
    red_green_pairs = []
    for i in range(len(colors_rgb)):
        for j in range(i + 1, len(colors_rgb)):
            r1, g1, b1 = colors_rgb[i]
            r2, g2, b2 = colors_rgb[j]
            # Red-green: high R diff, high G diff, low B diff
            if abs(r1 - r2) > 0.3 and abs(g1 - g2) > 0.3 and abs(b1 - b2) < 0.1:
                red_green_pairs.append((i, j))
    
    if red_green_pairs and len(colors_hex) <= 3:
        issues.append(
            f"[{label}] Colors may rely solely on red-green distinction for "
            f"{len(colors_hex)} entries. Add a non-RGB color (blue, orange, purple) "
            f"or use patterns (hatch) for accessibility."
        )
    
    # Grayscale check: all colors too similar?
    if len(colors_rgb) > 1:
        lums = [0.299 * r + 0.587 * g + 0.114 * b for r, g, b in colors_rgb]
        if max(lums) - min(lums) < 0.15:
            issues.append(
                f"[{label}] All colors have similar luminance (range: "
                f"{max(lums)-min(lums):.3f}). Figures will be indistinguishable in grayscale."
            )
    
    return len(issues) == 0, issues


def figure_qa_check(boxes=None, arrows=None, texts=None, data_points=None, 
                    stats_annotations=None, axis_ranges=None, colors=None,
                    fig_h=9.5, fig_w=14, margin_pt=5):
    """Run all QA checks on a matplotlib figure design.
    
    Returns (pass: bool, errors: list, warnings: list).
    """
    errors = []
    warnings = []
    margin_in = margin_pt / 72.0
    
    boxes = boxes or {}
    arrows = arrows or []
    texts = texts or []
    data_points = data_points or []
    stats_annotations = stats_annotations or []
    axis_ranges = axis_ranges or {}
    
    # ===== 1. All elements within figure boundary =====
    for name, b in boxes.items():
        x1, y1, x2, y2 = b
        if x1 < -0.05 or y1 < -0.05 or x2 > fig_w + 0.05 or y2 > fig_h + 0.05:
            errors.append(
                f"Box '{name}' outside figure: ({x1:.2f},{y1:.2f})-({x2:.2f},{y2:.2f}) "
                f"> [0,{fig_w:.2f}]x[0,{fig_h:.2f}]"
            )
    
    for name, x, y, *_ in data_points:
        for ax_name, (ax_xmin, ax_xmax, ax_ymin, ax_ymax) in axis_ranges.items():
            if ax_xmin - 0.1 <= x <= ax_xmax + 0.1 and ax_ymin - 0.1 <= y <= ax_ymax + 0.1:
                pass  # Within range
                break
    
    for name, x, y, *_ in stats_annotations:
        if x < 0 or y < 0 or x > fig_w or y > fig_h:
            errors.append(
                f"Stats annotation '{name}' ({x:.2f},{y:.2f}) outside figure bounds"
            )
    
    # ===== 2. Arrow endpoints inside target/source boxes =====
    for name, x1, y1, x2, y2, from_name, to_name in arrows:
        tb = boxes.get(to_name)
        if tb:
            if not (tb[0] <= x2 <= tb[2] and tb[1] <= y2 <= tb[3]):
                errors.append(
                    f"Arrow '{name}' tip ({x2:.3f},{y2:.3f}) outside '{to_name}' box "
                    f"AABB {tb}"
                )
        else:
            warnings.append(
                f"Arrow '{name}' target '{to_name}' not found in boxes"
            )
        
        sb = boxes.get(from_name)
        if sb:
            if not (sb[0] <= x1 <= sb[2] and sb[1] <= y1 <= sb[3]):
                errors.append(
                    f"Arrow '{name}' start ({x1:.3f},{y1:.3f}) outside '{from_name}' box "
                    f"AABB {sb}"
                )
        else:
            warnings.append(
                f"Arrow '{name}' source '{from_name}' not found in boxes"
            )
    
    # ===== 3. Arrow-to-arrow intersection =====
    for i in range(len(arrows)):
        n1, x1, y1, x2, y2, _, _ = arrows[i]
        for j in range(i + 1, len(arrows)):
            n2, x3, y3, x4, y4, _, _ = arrows[j]
            denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
            if abs(denom) < 0.001:
                continue  # Parallel
            t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
            u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
            if 0 < t < 1 and 0 < u < 1:
                ix = x1 + t * (x2 - x1)
                iy = y1 + t * (y2 - y1)
                errors.append(
                    f"Arrows {n1} and {n2} cross at ({ix:.2f}, {iy:.2f})"
                )
    
    # ===== 4. Text-within-box checks (precise via canvas) =====
    for text_str, x, y, fs, fw, bname, align, va in (
        [t + ('top',) if len(t) < 8 else t for t in texts]  # default va='top'
    ):
        if bname and bname not in boxes:
            warnings.append(f"Text '{text_str[:30]}' references unknown box '{bname}'")
            continue
        
        tw, th = get_text_extent(text_str, fs, fw)
        
        if bname and bname in boxes:
            b = boxes[bname]
            if va == 'top':
                top = y
                bottom = y - th
            else:  # center
                top = y + th / 2
                bottom = y - th / 2
            
            if bottom < b[1] - 0.005:
                errors.append(
                    f"Text '{text_str[:30]}' bottom {bottom:.4f} < box '{bname}' "
                    f"bottom {b[1]:.4f} (overflow {b[1] - bottom:.4f}in)"
                )
            if top > b[3] + 0.005:
                errors.append(
                    f"Text '{text_str[:30]}' top {top:.4f} > box '{bname}' top {b[3]:.4f}"
                )
            
            if align == 'left':
                if x + tw > b[2] + 0.005:
                    errors.append(
                        f"Text '{text_str[:30]}' right {x+tw:.4f} > box '{bname}' right {b[2]:.4f}"
                    )
            else:  # center
                if x - tw/2 < b[0] + 0.005:
                    errors.append(
                        f"Text '{text_str[:30]}' left {x-tw/2:.4f} < box '{bname}' left {b[0]:.4f}"
                    )
                if x + tw/2 > b[2] + 0.005:
                    errors.append(
                        f"Text '{text_str[:30]}' right {x+tw/2:.4f} > box '{bname}' right {b[2]:.4f}"
                    )
    
    # Also check stats_annotations against boxes
    for name, x, y, text_str, fs, bname in stats_annotations:
        if bname and bname in boxes:
            b = boxes[bname]
            if not (b[0] <= x <= b[2] and b[1] <= y <= b[3]):
                errors.append(
                    f"Stats '{name}' ({x:.2f},{y:.2f}) outside box '{bname}'"
                )
    
    # ===== 5. Box-to-box overlap (with margin) =====
    for n1, b1 in boxes.items():
        for n2, b2 in boxes.items():
            if n1 >= n2:
                continue
            if b1[0] < b2[2] + margin_in and b2[0] < b1[2] + margin_in and \
               b1[1] < b2[3] + margin_in and b2[1] < b1[3] + margin_in:
                ox = min(b1[2], b2[2]) - max(b1[0], b2[0])
                oy = min(b1[3], b2[3]) - max(b1[1], b2[1])
                if ox > 0 and oy > 0:
                    errors.append(
                        f"Box '{n1}' overlaps '{n2}': {ox:.3f}\" x {oy:.3f}\" "
                        f"[{n1}:({b1[0]:.2f},{b1[1]:.2f})-({b1[2]:.2f},{b1[3]:.2f}), "
                        f"{n2}:({b2[0]:.2f},{b2[1]:.2f})-({b2[2]:.2f},{b2[3]:.2f})]"
                    )
    
    # ===== 6. Data point visibility in axes =====
    for name, x, y, *_ in data_points:
        for ax_name, (ax_xmin, ax_xmax, ax_ymin, ax_ymax) in axis_ranges.items():
            if y < ax_ymin or y > ax_ymax or x < ax_xmin or x > ax_xmax:
                warnings.append(
                    f"Data point '{name}' ({x:.2f},{y:.2f}) may be clipped by "
                    f"axis range {ax_name}: [{ax_xmin:.2f},{ax_xmax:.2f}]x"
                    f"[{ax_ymin:.2f},{ax_ymax:.2f}]"
                )
    
    # ===== 7. Color blind accessibility check =====
    if colors:
        safe, issues = check_color_blind_safe(colors, 'color-blind')
        for issue in issues:
            errors.append(issue)
    
    # ===== 8. Stats annotation overlap check =====
    for i in range(len(stats_annotations)):
        n1, x1, y1, t1, fs1, _ = stats_annotations[i]
        for j in range(i + 1, len(stats_annotations)):
            n2, x2, y2, t2, fs2, _ = stats_annotations[j]
            dist = np.sqrt((x1-x2)**2 + (y1-y2)**2)
            if dist < 0.15:  # Less than 0.15 inches apart
                warnings.append(
                    f"Stats '{n1}' and '{n2}' may overlap at "
                    f"({(x1+x2)/2:.2f},{(y1+y2)/2:.2f}) — distance {dist:.3f}\" < 0.15\""
                )
    
    # ===== 9. Text overlap check (simplified, no canvas for speed) =====
    # ===== 8. Text overlap check (within same box only, using precise measurement) =====
    import matplotlib
    matplotlib.use('Agg')
    fig_tmp, ax_tmp = plt.subplots(figsize=(1,1))
    # Measure all text widths at once for efficiency
    text_measurements = {}
    for text_str, x, y, fs, fw, bname, align, va in texts:
        key = (text_str, fs, fw)
        if key not in text_measurements:
            tw, th = get_text_extent(text_str, fs, fw)
            text_measurements[key] = (tw, th)

    for i in range(len(texts)):
        text_str1 = texts[i][0]
        x1 = texts[i][1]
        y1 = texts[i][2] if len(texts[i]) > 2 else texts[i][3]
        fs1 = texts[i][3] if len(texts[i]) > 3 else texts[i][2]
        bname1 = texts[i][5] if len(texts[i]) > 5 else ''
        align1 = texts[i][6] if len(texts[i]) > 6 else 'center'
        for j in range(i + 1, len(texts)):
            text_str2 = texts[j][0]
            x2 = texts[j][1]
            y2 = texts[j][2] if len(texts[j]) > 2 else texts[j][3]
            fs2 = texts[j][3] if len(texts[j]) > 3 else texts[j][2]
            bname2 = texts[j][5] if len(texts[j]) > 5 else ''
            # Only check overlap within the same box
            if bname1 != bname2:
                continue
            # Skip if either text has no box assignment
            if not bname1:
                continue
            tw1, th1 = text_measurements[(text_str1, fs1, texts[i][4])]
            tw2, th2 = text_measurements[(text_str2, fs2, texts[j][4])]
            if align1 == 'left':
                left1 = x1
                right1 = x1 + tw1
            else:  # center
                left1 = x1 - tw1 / 2
                right1 = x1 + tw1 / 2
            align2 = texts[j][6] if len(texts[j]) > 6 else 'center'
            if align2 == 'left':
                left2 = x2
                right2 = x2 + tw2
            else:
                left2 = x2 - tw2 / 2
                right2 = x2 + tw2 / 2
            if abs(y1 - y2) < max(th1, th2) / 1.5:
                # Check x overlap only
                x_overlap = max(0, min(right1, right2) - max(left1, left2))
                y_overlap = max(0, min(y1 + th1/2, y2 + th2/2) - max(y1 - th1/2, y2 - th2/2))
                if x_overlap > 0.05 and y_overlap > 0.02:
                    warnings.append(
                        f"Text '{text_str1[:20]}' and '{text_str2[:20]}' may overlap "
                        f"at ({x1:.2f},{y1:.2f})"
                    )
    
    if errors:
        return False, errors, warnings
    return True, [], warnings


if __name__ == '__main__':
    # Quick self-test with HCS-3WT figure parameters
    test_boxes = {
        "KDP": (0.3, 8.0, 3.7, 9.15),
        "InputBox": (5.3, 7.15, 8.7, 7.75),
        "ExpertB": (0.3, 5.3, 4.5, 6.7),
        "ClearNeg": (5.3, 5.55, 8.5, 6.4),
        "Core": (9.0, 5.5, 11.0, 6.9),   # Far right, no overlap
    }
    test_arrows = [
        ("arrow1", 8.7, 7.20, 9.0, 6.7, "InputBox", "Core"),
        ("arrow2", 4.5, 6.0, 5.3, 6.05, "ExpertB", "ClearNeg"),
        ("arrow3", 10.0, 6.9, 3.7, 8.5, "Core", "KDP"),
    ]
    test_texts = [
        ("Key Design Principles", 2.0, 9.02, 9, "bold", "KDP", "center", "top"),
        ("PowerTransformer", 7.0, 7.25, 7.5, "normal", "InputBox", "center", "center"),
        ("Clinical Credibility", 2.0, 8.6, 7, "normal", "KDP", "center", "top"),
    ]
    test_colors = ["#8BCF8B", "#E8954A", "#7B5EA7", "#0F4D92"]
    
    print("=== QA Self-Test ===")
    passed, errors, warnings = figure_qa_check(test_boxes, test_arrows, test_texts, colors=test_colors)
    
    if warnings:
        for w in warnings:
            print(f"  ⚠️  {w}")
    
    if passed:
        print("  ✅ [QA] ALL CHECKS PASSED")
    else:
        for e in errors:
            print(f"  ❌ {e}")
        sys.exit(1)
    
    # Test color-blind detection
    print("\n=== Color-Blind Test ===")
    # Should pass (distinct colors)
    safe, issues = check_color_blind_safe(["#8BCF8B", "#E8954A", "#7B5EA7"], "good_colors")
    print(f"  Good colors: safe={safe}, issues={len(issues)}")
    
    # Should fail (red-green pair)
    safe2, issues2 = check_color_blind_safe(["#B64342", "#8BCF8B", "#767676"], "bad_colors")
    print(f"  Red-green: safe={safe2}, issues={len(issues2)}")
    if issues2:
        for issue in issues2:
            print(f"    → {issue}")
