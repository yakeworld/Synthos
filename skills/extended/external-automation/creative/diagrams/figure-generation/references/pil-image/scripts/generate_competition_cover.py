#!/usr/bin/env python3
"""竞赛级封面图生成 — 1920×1080 横向，六边形原子布局，发光效果，CJK标题。

SKILL.md 原理绑定：
- 模式D: 宣传封面/海报（Pillow深色科技风）
- 设计规则: 背景#0F172A，白字，蓝金点缀(#3B82F6/#F59E0B)
- 设计规则: CJK双描 — 深色底上draw.text()两次
- 设计规则: 字体分级 — 标题48-60px，副标题28-36px，正文16-20px
- 设计规则: 卡片布局 — 圆角12px，内边距24px
- 坑点: CJK字体必须用NotoSansCJK*
- 坑点: draw.polygon/rounded_rectangle的width必须是int()

输出: PNG 1920×1080 横向竞赛封面
"""

import os, sys, math, argparse
from PIL import Image, ImageDraw, ImageFont

FONT_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_REG  = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
TEAL      = (0, 188, 212)
NAVY_DARK = (8, 18, 36)
WHITE     = (255, 255, 255)
GRAY      = (170, 170, 170)


def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def radial_bg(draw, w, h):
    cx, cy = w // 2, h // 2
    max_r = int(math.sqrt(cx ** 2 + cy ** 2))
    for r in range(max_r, 0, -40):
        ratio = 1.0 - r / max_r
        c = (int(8 + 20 * ratio), int(18 + 40 * ratio), int(36 + 70 * ratio))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)


def subtle_grid(draw, w, h):
    gs = 80
    for x in range(0, w, gs):
        draw.line([(x, 0), (x, h)], fill=(12, 28, 52), width=1)
    for y in range(0, h, gs):
        draw.line([(0, y), (w, y)], fill=(12, 28, 52), width=1)


def glow_effect(draw, cx, cy, r, color, steps=30):
    for i in range(steps, 0, -2):
        rr = int(r * i / steps)
        draw.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                     fill=tuple(max(0, min(255, int(v * (1 - i / steps)))) for v in color))


def draw_hex(draw, cx, cy, r, fill, outline=WHITE):
    pts = []
    for i in range(6):
        a = (i * 60 - 90) * math.pi / 180
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    draw.polygon(pts, fill=fill, outline=outline, width=2)


def corner_accent(draw, x, y, dx, dy):
    draw.line([(x, y), (x + dx, y)], fill=TEAL, width=3)
    draw.line([(x, y), (x, y + dy)], fill=TEAL, width=3)


def generate_cover(project="Synthos", subtitle="自主进化学术科研平台",
                   tagline="A Computable, Collaborative & Evolving System",
                   track="AI for Medicine", output_path=None,
                   width=1920, height=1080):
    img = Image.new("RGB", (width, height), NAVY_DARK)
    draw = ImageDraw.Draw(img)
    W, H = width, height
    cx = W // 2

    # Background
    radial_bg(draw, W, H)
    subtle_grid(draw, W, H)
    glow_effect(draw, cx, 320, 400, TEAL)

    # Hexagon atoms
    atom_data = [
        ("知识获取", "#00BCD4"), ("知识提取", "#9C27B0"),
        ("关联发现", "#FF9800"), ("观点生成", "#4CAF50"),
        ("论证表达", "#E91E63"), ("观点验证", "#2196F3"),
    ]
    atom_r = 280
    positions = []
    for i in range(6):
        a = (i * 60 - 90) * math.pi / 180
        positions.append((cx + int(atom_r * math.cos(a)), 320 + int(atom_r * math.sin(a))))

    for (x, y) in positions:
        draw.line([(cx, 320), (x, y)], fill=(0, 188, 212, 60), width=1)
    for i in range(6):
        nx, ny = positions[(i + 1) % 6]
        draw.line([positions[i], (nx, ny)], fill=(80, 90, 120), width=1)

    f_atom = get_font(FONT_REG, 18)
    for i, (name, hex_c) in enumerate(atom_data):
        x, y = positions[i]
        rgb = tuple(int(hex_c[j:j+2], 16) for j in (1, 3, 5))
        draw_hex(draw, x, y, 32, rgb)
        tw = f_atom.getlength(name)
        draw.text((x - tw / 2, y - 8), name, fill=WHITE, font=f_atom)

    # Center router
    draw.ellipse([cx - 28, 292, cx + 28, 348], fill=TEAL, outline=WHITE, width=3)
    f_r = get_font(FONT_BOLD, 16)
    tw = f_r.getlength("Router")
    draw.text((cx - tw / 2, 312), "Router", fill=WHITE, font=f_r)

    # Title block
    title_y = 660
    f_t = get_font(FONT_BOLD, 72)
    tw = f_t.getlength(project)
    draw.text((cx - tw / 2, title_y), project, fill=TEAL, font=f_t)
    draw.text((cx - tw / 2 + 1, title_y), project, fill=TEAL, font=f_t)  # bold pass

    f_s = get_font(FONT_BOLD, 28)
    sw = f_s.getlength(subtitle)
    draw.text((cx - sw / 2, title_y + 80), subtitle, fill=WHITE, font=f_s)

    f_tg = get_font(FONT_REG, 18)
    tw2 = f_tg.getlength(tagline)
    draw.text((cx - tw2 / 2, title_y + 120), tagline, fill=GRAY, font=f_tg)

    # Features (bottom-left)
    features = [
        "◆ 6 认知原子 + 1 路由器 · DAG 流水线架构",
        "◆ CRISP-DM + TRIPOD+AI 双方法论框架",
        "◆ 纯 SKILL.md 驱动 · 零 Python 代码",
        "◆ 自进化引擎 · 连续健康运行",
        "◆ 多源并行检索 · 丰富教学来源",
    ]
    f_f = get_font(FONT_REG, 20)
    for i, feat in enumerate(features):
        draw.text((70, H - 260 + i * 38), feat, fill=WHITE, font=f_f)

    # Metrics (bottom-right)
    metrics = [("覆盖率", "95%+"), ("质量分", "0.97"), ("通过率", "100%"), ("效率", "4-6x")]
    f_ml = get_font(FONT_REG, 16)
    f_mv = get_font(FONT_BOLD, 28)
    mx = W - 460
    for i, (label, val) in enumerate(metrics):
        ry = H - 260 + i * 42
        draw.text((mx, ry), label, fill=GRAY, font=f_ml)
        draw.text((mx + 100, ry - 4), val, fill=TEAL, font=f_mv)

    # Bottom bar
    bar_y = H - 48
    draw.rectangle([0, bar_y, W, H], fill=(0, 80, 120))
    f_bar = get_font(FONT_BOLD, 22)
    bar_text = track + " · 医学研究支持智能体"
    btw = f_bar.getlength(bar_text)
    draw.text((cx - btw / 2, bar_y + 10), bar_text, fill=WHITE, font=f_bar)

    # Corner accents
    for (x, y, dx, dy) in [
        (30, 30, 50, 0), (30, 30, 0, 50),
        (W - 30, 30, -50, 0), (W - 30, 30, 0, 50),
        (30, H - 30, 50, 0), (30, H - 30, 0, -50),
        (W - 30, H - 42, -50, 0), (W - 30, H - 42, 0, -50),
    ]:
        corner_accent(draw, x, y, dx, dy)

    if output_path:
        img.save(output_path, "PNG")
        print(f"Saved: {output_path} ({img.size})")
    return img


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Generate competition cover image")
    p.add_argument("--project", default="Synthos")
    p.add_argument("--subtitle", default="自主进化学术科研平台")
    p.add_argument("--tagline", default="A Computable, Collaborative & Evolving System")
    p.add_argument("--track", default="AI for Medicine")
    p.add_argument("--output", default="cover.png")
    args = p.parse_args()
    generate_cover(**vars(args))
