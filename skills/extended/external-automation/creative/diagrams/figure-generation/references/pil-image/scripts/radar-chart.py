#!/usr/bin/env python3
"""雷达图生成 — 多维评分可视化（CLI工具，用于科学报告）。

SKILL.md 原理绑定：
- 模式D: Pillow原语 — 雷达图是7个统一原语之一
- 设计规则: CJK双描 — draw.text()两次（偏移1px）
- 设计规则: 字体必须用ImageFont.truetype(NotoSansCJK*)
- 设计规则: 灰度打印可读性 — 线条+填充双编码

输出: RGB PNG雷达图
"""

import argparse, math
from PIL import Image, ImageDraw, ImageFont

def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def draw_text_bold(draw, x, y, text, fill, font):
    draw.text((x, y), text, fill=fill, font=font)
    draw.text((x+1, y), text, fill=fill, font=font)

def draw_radar_chart(dimensions, scores, output_path, title="", width=400, height=400, max_radius=120, center_x=None, center_y=None, grid_levels=(0.2, 0.4, 0.6, 0.8, 1.0), grid_color=(200, 200, 205), data_color=(15, 77, 146), data_fill_alpha=30, label_color=(45, 45, 45), value_color=(45, 45, 45), bg_color=(250, 250, 252), title_font_size=12, label_font_size=7, font_path="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", font_path_reg="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"):
    assert len(dimensions) == len(scores) and len(dimensions) >= 3
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    cx = center_x or width // 2
    cy = center_y or height // 2
    n = len(dimensions)
    angles = [i * 2 * math.pi / n for i in range(n)]
    f_title = load_font(font_path, title_font_size)
    f_label = load_font(font_path_reg, label_font_size)
    f_value_bold = load_font(font_path, label_font_size)
    if title:
        draw_text_bold(draw, (width - 1) // 2, 10, title, label_color, f_title)
    for ratio in grid_levels:
        r = int(max_radius * ratio)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=grid_color, width=1)
    line_points = []
    for i in range(n):
        angle = angles[i] - math.pi / 2
        ex = cx + int(max_radius * math.cos(angle))
        ey = cy + int(max_radius * math.sin(angle))
        line_points.append((ex, ey))
        draw.line([(cx, cy), (ex, ey)], fill=grid_color, width=1)
    poly = []
    for i in range(n):
        angle = angles[i] - math.pi / 2
        dr = int(max_radius * scores[i])
        dx = cx + int(dr * math.cos(angle))
        dy = cy + int(dr * math.sin(angle))
        poly.append((dx, dy))
        draw.ellipse([dx - 3, dy - 3, dx + 3, dy + 3], fill=data_color, outline="white", width=1)
    fill_color = tuple(min(c + data_fill_alpha, 255) for c in data_color)
    draw.polygon(poly, fill=fill_color, outline=data_color, width=2)
    for i in range(n):
        angle = angles[i] - math.pi / 2
        dr = int(max_radius * scores[i])
        dx = cx + int(dr * math.cos(angle))
        dy = cy + int(dr * math.sin(angle))
        lx = dx + int(15 * math.cos(angle))
        ly = dy + int(15 * math.sin(angle))
        draw_text_bold(draw, lx - 12, ly - 4, f"{scores[i]:.2f}", value_color, f_value_bold)
    for i, (label, (lx, ly)) in enumerate(zip(dimensions, line_points)):
        angle = angles[i] - math.pi / 2
        offset_r = max_radius + 20
        lx2 = cx + int(offset_r * math.cos(angle))
        ly2 = cy + int(offset_r * math.sin(angle))
        draw_text_bold(draw, lx2 - 15, ly2 - 5, label, label_color, f_label)
    img.save(output_path, 'PNG')
    return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate radar chart")
    parser.add_argument("--dimensions", default="D1,D2,D3,D4,D5,D6,D7")
    parser.add_argument("--scores", default="0.95,0.95,0.95,1.00,0.95,0.95,0.80")
    parser.add_argument("--output", default="/tmp/radar.png")
    parser.add_argument("--title", default="Quality Scores")
    parser.add_argument("--size", type=int, default=400)
    parser.add_argument("--font", default="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")
    parser.add_argument("--font-reg", default="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
    args = parser.parse_args()
    draw_radar_chart(args.dimensions.split(","), [float(s) for s in args.scores.split(",")], args.output, args.title, args.size, args.size, font_path=args.font, font_path_reg=args.font_reg)
    print(f"Saved {args.output}")
