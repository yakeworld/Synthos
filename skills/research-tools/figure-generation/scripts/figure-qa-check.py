#!/usr/bin/env python3
"""
figure-qa-check.py — 从 matplotlib 绘图脚本自动提取几何元素并运行 QA。

用法:
  python3 figure-qa-check.py /path/to/generate_figX.py --fig-h 9.5 --fig-w 14

退出码: 0=PASS, 1=FAIL
"""

import re
import sys
import os
import importlib.util
import argparse
import matplotlib
matplotlib.use('Agg')


def parse_fancy_box_patches(source_code):
    """Extract FancyBboxPatch: var_name -> (x, y, w, h)"""
    pattern = r'(\w+_box)\s*=\s*FancyBboxPatch\(\s*\(([\d.\-]+),\s*([\d.\-]+)\)\s*,\s*([\d.]+),\s*([\d.]+)'
    results = {}
    for m in re.finditer(pattern, source_code):
        results[m.group(1)] = (float(m.group(2)), float(m.group(3)), float(m.group(4)), float(m.group(5)))
    return results


def parse_fancy_arrow_patches(source_code):
    """Extract FancyArrowPatch: var_name -> (x1, y1, x2, y2)"""
    pattern = r'(\w+arrow\w*|arrow\d+)\s*=\s*FancyArrowPatch\(\s*\(([\d.\-]+),\s*([\d.\-]+)\)\s*,\s*\(([\d.\-]+),\s*([\d.\-]+)\)'
    results = {}
    for m in re.finditer(pattern, source_code):
        results[m.group(1)] = (float(m.group(2)), float(m.group(3)), float(m.group(4)), float(m.group(5)))
    return results


def parse_ax_text_calls(source_code):
    """Extract ax.text() calls: (x, y, text_content)
    
    Note: source code contains literal \\n which should be converted to actual newlines
    so that text extent estimation matches matplotlib's rendering behavior.
    """
    # Match content between quotes, but first replace escaped sequences
    pattern = r'ax\.text\(\s*([\d.\-]+),\s*([\d.\-]+),\s*[\x22\x27]([^\x22\x27]*)[\x22\x27]'
    results = []
    for m in re.finditer(pattern, source_code):
        x, y = float(m.group(1)), float(m.group(2))
        text = m.group(3)
        # Convert literal \n to actual newline (matplotlib renders these as multi-line text)
        text = text.replace('\\n', '\n')
        results.append((x, y, text))
    return results


def determine_text_fontsize_and_weight(source_code, x, y, text_content):
    """Extract fontsize and fontweight. Uses line-based search for multi-line calls."""
    # Find the line containing the text and look for fontsize in nearby lines
    lines = source_code.split('\n')
    for i, line in enumerate(lines):
        if text_content in line and 'ax.text' in line:
            context = '\n'.join(lines[i:i+3])
            m = re.search(r'fontsize=(\d+(?:\.\d+)?)', context)
            if m:
                fs = float(m.group(1))
                if 'fontweight="bold"' in context or "fontweight='bold'" in context:
                    return fs, 'bold'
                return fs, 'normal'
    return 8, 'normal'


def determine_text_box(x, y, box_aabb):
    """Find which box a text element belongs to (AABB format: x_min, y_min, x_max, y_max)."""
    best_name = None
    best_overlap = -1
    for name, (bx, by, bx2, by2) in box_aabb.items():
        x1, y1, x2, y2 = x, y, x + 0.1, y + 0.1
        overlap_x = max(0, min(x2, bx2) - max(x1, bx))
        overlap_y = max(0, min(y2, by2) - max(y1, by))
        if overlap_x > 0 and overlap_y > 0:
            coverage = overlap_x * overlap_y / 0.01
            if coverage > best_overlap:
                best_overlap = coverage
                best_name = name
    return best_name


def determine_text_align_va(source_code, x, y, text_content):
    """Extract ha and va from source code."""
    safe_text = re.escape(text_content)
    pattern = rf'ax\.text\(\s*{x},\s*{y},\s*["\']{safe_text}["\'].*?ha=["\']?(\w+)'
    m = re.search(pattern, source_code)
    align = 'center'
    if m and m.group(1) == 'left':
        align = 'left'

    pattern = rf'ax\.text\(\s*{x},\s*{y},\s*["\']{safe_text}["\'].*?va=["\']?(\w+)'
    m = re.search(pattern, source_code)
    va = 'center'
    if m:
        va = m.group(1)
    return align, va


def infer_arrow_targets(x1, y1, x2, y2, boxes):
    """Infer source and target box names from arrow geometry (boxes in AABB format)."""
    source = target = None
    for name, (bx, by, bx2, by2) in boxes.items():
        if bx <= x1 <= bx2 and by <= y1 <= by2:
            source = name; break
    for name, (bx, by, bx2, by2) in boxes.items():
        if bx <= x2 <= bx2 and by <= y2 <= by2:
            target = name; break
    if not target and x2 < 5:
        experts = {n: b for n, b in boxes.items() if 'expert' in n.lower() or 'ec_' in n or 'eb_' in n or 'ea_' in n}
        if experts:
            target = min(experts.items(), key=lambda k: abs((k[1][0]+k[1][2])/2 - x2))[0]
    if not source and x1 < 5:
        experts = {n: b for n, b in boxes.items() if 'expert' in n.lower() or 'ec_' in n or 'eb_' in n or 'ea_' in n}
        if experts:
            source = min(experts.items(), key=lambda k: abs((k[1][0]+k[1][2])/2 - x1))[0]
    return source, target


def build_qa_input(boxes_raw, arrows_raw, texts_raw, source_code):
    """Build input for figure_qa_check."""
    # boxes: (x,y,w,h) -> (x_min, y_min, x_max, y_max)
    boxes = {}
    for name, (x, y, w, h) in boxes_raw.items():
        boxes[name] = (x, y, x + w, y + h)

    # arrows: (name, x1, y1, x2, y2, from, to)
    arrows = []
    for name, (x1, y1, x2, y2) in arrows_raw.items():
        src, tgt = infer_arrow_targets(x1, y1, x2, y2, boxes)
        arrows.append((name, x1, y1, x2, y2, src or name, tgt or name))

    # texts: (text, x, y, fs, fw, box_name, align, va)
    texts = []
    for x, y, text_content in texts_raw:
        box_name = determine_text_box(x, y, boxes)
        fs, fw = determine_text_fontsize_and_weight(source_code, x, y, text_content)
        align, va = determine_text_align_va(source_code, x, y, text_content)
        texts.append((text_content, x, y, fs, fw, box_name or '', align, va))

    return boxes, arrows, texts


def run_qa_on_source(source_file, fig_h=9.5, fig_w=14):
    """Load a figure generation script, extract geometry, run QA."""
    with open(source_file, 'r') as f:
        source_code = f.read()

    boxes_raw = parse_fancy_box_patches(source_code)
    arrows_raw = parse_fancy_arrow_patches(source_code)
    texts_raw = parse_ax_text_calls(source_code)

    qa_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'qa-architecture-diagram.py')
    spec = importlib.util.spec_from_file_location('qa', qa_path)
    if spec is None:
        print("ERROR: Cannot load qa-architecture-diagram.py")
        sys.exit(1)
    qa = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(qa)

    boxes, arrows, texts = build_qa_input(boxes_raw, arrows_raw, texts_raw, source_code)

    passed, errors, warnings = qa.figure_qa_check(
        boxes=boxes, arrows=arrows, texts=texts,
        fig_h=fig_h, fig_w=fig_w, margin_pt=5,
    )

    return passed, errors, warnings, boxes, arrows, texts


def main():
    parser = argparse.ArgumentParser(description='QA-check matplotlib figure generation scripts')
    parser.add_argument('source_file', help='Path to generate_figX.py')
    parser.add_argument('--fig-h', type=float, default=9.5)
    parser.add_argument('--fig-w', type=float, default=14)
    args = parser.parse_args()

    if not os.path.exists(args.source_file):
        print(f"ERROR: File not found: {args.source_file}")
        sys.exit(1)

    print("=" * 70)
    print("FIGURE QA CHECK — Automated from Source Code")
    print("=" * 70)
    print(f"Source: {args.source_file}")
    print()

    with open(args.source_file, 'r') as f:
        source_code = f.read()

    boxes_raw = parse_fancy_box_patches(source_code)
    arrows_raw = parse_fancy_arrow_patches(source_code)
    texts_raw = parse_ax_text_calls(source_code)

    print(f"Boxes: {len(boxes_raw)}")
    print(f"Arrows: {len(arrows_raw)}")
    print(f"Text elements: {len(texts_raw)}")
    print()

    passed, errors, warnings, boxes, arrows, texts = run_qa_on_source(
        args.source_file, args.fig_h, args.fig_w
    )

    print("RESULT:")
    print(f"  {'PASS ✅' if passed else 'FAIL ❌'}")
    print(f"  Errors: {len(errors)}")
    print(f"  Warnings: {len(warnings)}")
    print()

    if errors:
        print("ERRORS:")
        for e in errors:
            print(f"  ❌ {e}")
        print()

    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(f"  ⚠️  {w}")
        print()

    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()
