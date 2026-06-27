#!/usr/bin/env python3
"""小红书推广卡片生成 — 9:16竖版轮播图。

SKILL.md 原理绑定：
- 模式D: 宣传封面/海报/社交卡片（Pillow深色科技风）
- 设计规则: 竖版1080×1920（轮播），正方形1080×1080（单图）
- 设计规则: 背景#0D111C，白字，蓝金点缀
- 设计规则: CJK双描 — 深色底上draw.text(x,y)两次
- 设计规则: 字体分级 — 标题36-44pt，正文20-24px
- 坑点: 避免emoji，用文字替代（🔬→"研究"，✅→"通过"）
- 坑点: 字体必须用ImageFont.truetype(NotoSansCJK*)

输出: 5张竖版PNG轮播图（封面+3详情+结尾）
"""

import os, math
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920       # 9:16 portrait (Xiaohongshu standard)
BG = (13, 17, 28)       # dark navy
CARD_BG = (22, 28, 46)  # slightly lighter
ACCENT = (0, 188, 212)  # teal/cyan
ACCENT_DIM = (0, 140, 160)
WHITE = (255, 255, 255)
GRAY = (160, 170, 190)
DARK_TEXT = (200, 210, 230)

# CJK font paths — adjust for your system
FONT_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_REG = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_LIGHT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Light.ttc"
FONT_MEDIUM = "/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc"


def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def draw_glow_bg(draw):
    """Subtle radial glow at center-top."""
    cx, cy = W // 2, int(H * 0.2)
    for r in range(800, 0, -30):
        alpha = max(0, int(20 * (1 - r / 800)))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(0, 188, 212, alpha))


def draw_accent_line(draw, y, w=80):
    draw.rounded_rectangle([(W // 2 - w // 2, y), (W // 2 + w // 2, y + 4)], radius=2, fill=ACCENT)


def draw_card_base(name, subtitle, body_lines, tag="", card_num=1, total=5, output_dir="."):
    """
    name:     multi-line title (\\n separated)
    subtitle: one-line subtitle (shown under title)
    body_lines: list of strings. Prefix rules:
               '!!' = highlight (accent color, bold)
               '> ' = muted secondary text
               '#'  = section header
               plain = body text
    tag:      small badge at top
    card_num: current card number (1-indexed)
    total:    total cards
    """
    img = Image.new("RGBA", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Background glow + subtle grid
    draw_glow_bg(draw)
    for x in range(0, W, 60):
        draw.line([(x, 0), (x, H)], fill=(18, 22, 35), width=1)
    for y in range(0, H, 60):
        draw.line([(0, y), (W, y)], fill=(18, 22, 35), width=1)

    # Card number indicator (top-right)
    fnt_small = load_font(FONT_REG, 24)
    draw.text((W - 120, 40), f"{card_num}/{total}", fill=(60, 70, 90), font=fnt_small)

    # Corner decoration
    csize = 40
    draw.line([(40, 60), (40, 60 + csize)], fill=ACCENT_DIM, width=3)
    draw.line([(40, 60), (40 + csize, 60)], fill=ACCENT_DIM, width=3)
    draw.line([(W - 40, H - 60), (W - 40 - csize, H - 60)], fill=ACCENT_DIM, width=3)
    draw.line([(W - 40, H - 60), (W - 40, H - 60 - csize)], fill=ACCENT_DIM, width=3)

    # Tag badge
    if tag:
        fnt_tag = load_font(FONT_MEDIUM, 28)
        tw = draw.textlength(tag, font=fnt_tag)
        tag_bg_x = (W - tw - 40) // 2
        draw.rounded_rectangle([(tag_bg_x, 100), (tag_bg_x + tw + 40, 150)], radius=20, fill=ACCENT)
        draw.text((tag_bg_x + 20, 113), tag, fill=BG, font=fnt_tag)

    # Title section
    title_y = 200
    fnt_title = load_font(FONT_BOLD, 48)
    fnt_sub = load_font(FONT_LIGHT, 30)
    draw_accent_line(draw, title_y - 20)

    for i, line in enumerate(name.split('\n')):
        ly = title_y + i * 70
        draw.text((W // 2, ly), line, fill=WHITE, font=fnt_title, anchor="mt")
        draw.text((W // 2 + 1, ly), line, fill=WHITE, font=fnt_title, anchor="mt")  # double-draw for boldness

    if subtitle:
        sy = title_y + len(name.split('\n')) * 70 + 20
        draw.text((W // 2, sy), subtitle, fill=ACCENT, font=fnt_sub, anchor="mt")

    # Body card
    body_y = title_y + len(name.split('\n')) * 70 + 90
    card_x0, card_x1 = 60, W - 60
    card_h = H - body_y - 80
    draw.rounded_rectangle([(card_x0, body_y), (card_x1, body_y + card_h)], radius=24, fill=CARD_BG)

    # Body content
    fnt_body = load_font(FONT_REG, 32)
    fnt_highlight = load_font(FONT_BOLD, 32)
    cy = body_y + 50
    for line in body_lines:
        is_highlight = line.startswith('!!')
        is_sub = line.startswith('> ')
        if is_highlight:
            line = line[2:]
            fnt = fnt_highlight
            clr = ACCENT
        elif is_sub:
            line = line[2:]
            fnt = load_font(FONT_MEDIUM, 28)
            clr = GRAY
        else:
            fnt = fnt_body
            clr = DARK_TEXT

        if line.startswith('#'):
            line = line[1:]
            fnt = fnt_highlight
            clr = WHITE
            cy += 20
            draw_accent_line(draw, cy - 8, 40)
            cy += 10

        # Simple line wrapping for long text
        text_width = draw.textlength(line, font=fnt)
        if text_width > W - 160:
            words = list(line)
            parts, cur = [], ""
            for ch in words:
                test = cur + ch
                if draw.textlength(test, font=fnt) > W - 160 and cur:
                    parts.append(cur)
                    cur = ch
                else:
                    cur = test
            if cur:
                parts.append(cur)
            for part in parts:
                xp = (W - draw.textlength(part, font=fnt)) // 2
                draw.text((xp, cy), part, fill=clr, font=fnt)
                cy += 50
        else:
            xp = (W - text_width) // 2
            draw.text((xp, cy), line, fill=clr, font=fnt)
            if is_highlight:
                draw.text((xp + 1, cy), line, fill=clr, font=fnt)
            cy += 55

    # Bottom bar
    draw.rectangle([(0, H - 20), (W, H)], fill=ACCENT_DIM)

    path = os.path.join(output_dir, f"card_{card_num:02d}.png")
    img.save(path, "PNG")
    print(f"Saved: {path}")
    return path


# =========================================================================
# Example: Synthos project promotion cards
# =========================================================================
if __name__ == "__main__":
    OUT = os.path.join(os.path.dirname(__file__), "..", "outputs", "cards")
    os.makedirs(OUT, exist_ok=True)

    draw_card_base(
        name="Project Name",
        subtitle="Your tagline here",
        body_lines=[
            "> ",
            "Not another tool — a cognitive framework",
            "> ",
            "# Four Core Innovations",
            "> ",
            "  Feature 1  ·  Key metric",
            "  Feature 2  ·  Key metric",
            "  Feature 3  ·  Key metric",
            "  Feature 4  ·  Key metric",
            "> ",
            "> open source · MIT License",
            "> github.com/your/repo",
        ],
        tag="Your Tag",
        card_num=1,
        total=5,
        output_dir=OUT,
    )

    # Define 4 more cards matching your 4 key messages...
    # See gen_synthos_cards.py in the session for a full example.

    print(f"\n✅ Cards generated in {OUT}")
