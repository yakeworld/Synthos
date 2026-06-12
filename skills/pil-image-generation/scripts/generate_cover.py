#!/usr/bin/env python3
"""
Reusable cover image generator using Pillow (PIL).
Generate project cover images for competitions, presentations, documentation.

Usage:
    python3 scripts/generate_cover.py --project "ProjectName" --title "Subtitle" --features "..." --output /path/to/output/

This is a template — customize the design, colors, and layout for your specific project.
"""

import sys
import os
import math
import argparse
from PIL import Image, ImageDraw, ImageFont


def get_font(size):
    """Find best CJK font available on the system."""
    for path in [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    ]:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                continue
    try:
        return ImageFont.truetype("Noto Sans CJK SC", size)
    except:
        return ImageFont.load_default()


def draw_hexagon(draw, cx, cy, r, fill_color, outline="white"):
    """Draw a regular hexagon."""
    points = []
    for i in range(6):
        angle = (i * 60 - 90) * math.pi / 180
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        points.append((x, y))
    draw.polygon(points, fill=fill_color, outline=outline)


def generate_cover(
    project_name="Synthos",
    subtitle="自主进化学术科研平台",
    tagline="A computable, collaborative, and evolving system",
    features=None,
    metrics=None,
    width=1920,
    height=1080,
    output_path=None,
):
    """Generate a professional cover image."""

    features = features or [
        "◆ 原创认知操作系统",
        "◆ 6认知原子 + DAG架构",
        "◆ CRISP-DM + TRIPOD+AI 方法论",
        "◆ 73个教学来源",
        "◆ 质量评分 0.97",
    ]
    metrics = metrics or [
        ("覆盖率", "95%+"),
        ("质量", "0.97"),
        ("通过率", "100%"),
        ("效率", "4-6x"),
    ]

    # Background gradient
    img = Image.new("RGB", (width, height), (10, 22, 40))
    draw = ImageDraw.Draw(img)
    cx, cy = width // 2, height // 2

    max_r = int(math.sqrt(cx**2 + cy**2))
    for r in range(max_r, 0, -20):
        ratio = 1.0 - r / max_r
        color = (
            int(10 + 20 * ratio),
            int(22 + 40 * ratio),
            int(40 + 80 * ratio),
        )
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)

    # Grid
    gs = 60
    for x in range(0, width, gs):
        draw.line([(x, 0), (x, height)], fill=(0, 188, 212), width=1)
    for y in range(0, height, gs):
        draw.line([(0, y), (width, y)], fill=(0, 188, 212), width=1)

    # Central node
    cr = 35
    draw.ellipse(
        [cx - cr, cy - cr, cx + cr, cy + cr], fill="#00BCD4", outline="white"
    )
    draw.text((cx - 25, cy - 8), "Router", fill="white", font=get_font(12))

    # 6 atoms in hexagon
    atom_names = [
        "知识获取",
        "知识提取",
        "关联发现",
        "观点生成",
        "论证表达",
        "观点验证",
    ]
    atom_colors = [
        "#00BCD4",
        "#9C27B0",
        "#FF9800",
        "#4CAF50",
        "#E91E63",
        "#2196F3",
    ]

    # Phase 1: Pre-compute all coordinates
    positions = []
    for i in range(6):
        angle = (i * 60 - 90) * math.pi / 180
        r = 240
        x = cx + int(r * math.cos(angle))
        y = cy + int(r * math.sin(angle))
        positions.append((x, y))

    # Phase 2: Draw everything
    for i in range(6):
        x, y = positions[i]
        draw_hexagon(draw, x, y, 30, atom_colors[i])
        draw.text((x - 30, y - 5), atom_names[i], fill="white", font=get_font(15))
        draw.line([(cx, cy), (x, y)], fill=(255, 255, 255), width=2)
        if i < 5:
            nx, ny = positions[i + 1]
            draw.line([(x + 25, y), (nx - 25, ny)], fill=(200, 200, 200), width=2)

    if len(positions) >= 2:
        lx, ly = positions[-1]
        fx, fy = positions[0]
        draw.line([(lx + 25, ly), (fx - 25, fy)], fill=(200, 200, 200), width=2)

    # Title
    ty = cy + 80
    draw.text((cx - 120, ty), project_name, fill="#00BCD4", font=get_font(64))
    draw.text((cx - 160, ty + 50), subtitle, fill="white", font=get_font(26))
    draw.text(
        (cx - 220, ty + 90),
        tagline,
        fill="#AAAAAA",
        font=get_font(14),
    )

    # Features (bottom-left)
    fy2 = height - 200
    for i, f in enumerate(features):
        draw.text((80, fy2 + i * 32), "  " + f, fill="#FFFFFF", font=get_font(15))

    # Metrics (bottom-right)
    for i, (label, val) in enumerate(metrics):
        x, y = 1000, fy2 + i * 32
        draw.text((x, y), label, fill="#AAAAAA", font=get_font(13))
        draw.text((x + 60, y), val, fill="#00BCD4", font=get_font(18))

    # Bottom bar
    draw.rectangle([0, height - 45, width, height], fill=(0, 100, 150))
    draw.text(
        (cx - 180, height - 25),
        "AI for Medicine · 医学研究支持智能体",
        fill="white",
        font=get_font(16),
    )

    # Corner accents
    draw.line([(0, 0), (40, 0), (40, 40)], fill=(0, 188, 212), width=2)
    draw.line([(width - 40, 0), (width, 0), (width, 40)], fill=(0, 188, 212), width=2)
    draw.line([(0, height - 40), (0, height), (40, height)], fill=(0, 188, 212), width=2)
    draw.line(
        [(width - 40, height), (width, height), (width, height - 40)],
        fill=(0, 188, 212),
        width=2,
    )

    if output_path:
        img.save(output_path, "PNG")
        print(f"Saved: {output_path}")

    return img


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate project cover image")
    parser.add_argument("--project", default="Synthos", help="Project name")
    parser.add_argument("--subtitle", default="自主进化学术科研平台", help="Subtitle")
    parser.add_argument("--tagline", default="A computable, collaborative system", help="Tagline")
    parser.add_argument("--output", required=True, help="Output file path")
    args = parser.parse_args()

    generate_cover(
        project_name=args.project,
        subtitle=args.subtitle,
        tagline=args.tagline,
        output_path=args.output,
    )
