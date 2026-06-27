# Pillow 纯代码绘图原语 — 统一入口

> 当 matplotlib/NumPy 不可用时，使用 Pillow 原语。
> 所有 Pillow 绘图代码从此文件加载，不在多个技能中复制。

## 触发条件

`import matplotlib` 失败，或 NumPy 版本冲突，或服务器无 GUI。

## 核心原语

### 原语 1: 雷达图（极坐标图）

```python
import math
from PIL import Image, ImageDraw, ImageFont

def draw_radar_chart(draw, scores, labels, max_r=110, cx=300, cy=300,
                     font_size=8, palette=None, grid_levels=5):
    n = len(scores)
    angles = [i * 2 * math.pi / n for i in range(n)]
    if palette is None:
        palette = ['#0F4D92', '#8BCF8B', '#B64342', '#42949E', '#9A4D8E', '#CFCECE']

    # 网格圆
    for ratio in [0.2, 0.4, 0.6, 0.8, 1.0][:grid_levels]:
        r = int(max_r * ratio)
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline='#B8B8B8', width=1)

    # 轴线
    for i in range(n):
        angle = angles[i] - math.pi/2
        ex = cx + int(max_r * math.cos(angle))
        ey = cy + int(max_r * math.sin(angle))
        draw.line([(cx, cy), (ex, ey)], fill='#B8B8B8', width=1)

    # 数据多边形
    poly = []
    for i in range(n):
        dr = int(max_r * scores[i])
        px = cx + int(dr * math.cos(angles[i] - math.pi/2))
        py = cy + int(dr * math.sin(angles[i] - math.pi/2))
        poly.append((px, py))
    draw.polygon(poly, fill=(*palette[0][:3], 30), outline=palette[0], width=2)

    # 数据点
    for i in range(n):
        dr = int(max_r * scores[i])
        px = cx + int(dr * math.cos(angles[i] - math.pi/2))
        py = cy + int(dr * math.sin(angles[i] - math.pi/2))
        draw.ellipse([px-3, py-3, px+3, py+3], fill=palette[0], outline='#FFFFFF')

    # 标签
    for i in range(n):
        angle = angles[i] - math.pi/2
        lx = cx + int((max_r+20) * math.cos(angle))
        ly = cy + int((max_r+20) * math.sin(angle))
        draw_text(draw, lx, ly, labels[i], font_size=font_size, ha='center', va='center')
```

### 原语 2: 进度条/水平条形图

```python
def draw_progress_bars(draw, metrics, start_y=50, bar_h=50, bar_gap=12,
                       panel_w=300, x=20, palette=None, font_size=9):
    if palette is None:
        palette = ['#0F4D92', '#8BCF8B', '#B64342', '#42949E']

    for i, (label, val, color) in enumerate(metrics):
        by = start_y + i * (bar_h + bar_gap)
        fill_w = int((panel_w - 30) * val)

        draw.rounded_rectangle([(x, by), (x + panel_w - 30, by + bar_h)],
                               radius=8, fill='#F0F4F8')
        draw.rounded_rectangle([(x, by), (x + fill_w, by + bar_h)],
                               radius=8, fill=color)
        draw_text(draw, x + 20, by + 14, label, font_size=font_size, fontweight='bold')
        draw_text(draw, x + fill_w + 15, by + 14, f'{val:.1%}', font_size=font_size)
```

### 原语 3: 轨迹图（改善轨迹）

```python
def draw_trajectory(draw, history, x0=50, plot_start=50, plot_end=300,
                    y_min=0.70, y_max=1.00, color='#0F4D92',
                    font_size=8, annotate=True):
    history = list(history)
    if not history:
        return

    def score_to_y(val):
        return plot_end - (val - y_min) / (y_max - y_min) * (plot_end - plot_start)

    for gv in [0.72, 0.80, 0.85, 0.90, 0.95]:
        gy = score_to_y(gv)
        draw.line([(x0, gy), (x0 + 250, gy)], fill='#E0E0E0', width=1)

    step_x = 250 / max(len(history) - 1, 1)
    points = []
    for i, (label, val) in enumerate(history):
        px = x0 + i * step_x
        py = score_to_y(val)
        points.append((px, py))
        draw.ellipse([px-5, py-5, px+5, py+5], fill=color, outline='#FFFFFF', width=2)
        if annotate:
            draw_text(draw, px - 10, py - 16, f'{val:.2f}',
                     font_size=font_size, fontweight='bold', color=color)

    for i in range(len(points) - 1):
        draw.line([points[i], points[i+1]], fill=color, width=2)

    if len(points) >= 2:
        draw_arrow(draw, points[0][0], points[0][1],
                  points[-1][0], points[-1][1], color, width=2)
```

### 原语 4: 箭头

```python
def draw_arrow(draw, x1, y1, x2, y2, color='#0F4D92', width=2,
               head_len=8, head_angle=math.pi/6):
    draw.line([(x1, y1), (x2, y2)], fill=color, width=width)
    angle = math.atan2(y2-y1, x2-x1)
    lx = x2 - head_len * math.cos(angle - head_angle)
    ly = y2 - head_len * math.sin(angle - head_angle)
    rx = x2 - head_len * math.cos(angle + head_angle)
    ry = y2 - head_len * math.sin(angle + head_angle)
    draw.polygon([(x2, y2), (int(lx), int(ly)), (int(rx), int(ry))], fill=color)
```

### 原语 5: 文本（支持双描加粗）

```python
def draw_text(draw, x, y, text, font_size=8, color='#272727',
              fontweight='normal', ha='left', va='top'):
    try:
        font = ImageFont.truetype('Arial.ttf', font_size)
    except Exception:
        try:
            font = ImageFont.truetype('DejaVuSans.ttf', font_size)
        except Exception:
            font = ImageFont.load_default()

    if fontweight == 'bold':
        for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
            draw.text((x+dx, y+dy), text, fill='#272727', font=font)
        draw.text((x, y), text, fill=color, font=font)
    else:
        draw.text((x, y), text, fill=color, font=font)
```

### 原语 6: 面板标签 (a, b, c...)

```python
def draw_panel_label(draw, label, x=0, y=0, font_size=14,
                     circle_r=12, color='#0F4D92', text_color='#FFFFFF'):
    draw.ellipse([x-circle_r, y-circle_r, x+circle_r, y+circle_r],
                fill=color, outline=None)
    draw_text(draw, x-4, y-5, label, font_size=font_size,
             color=text_color, fontweight='bold', ha='center', va='center')
```

### 原语 7: 热图

```python
def draw_heatmap(draw, matrix, x0=50, y0=50, cell_w=40, cell_h=30,
                 font_size=7):
    palette = ['#0F4D92', '#8BCF8B', '#B64342']
    n_rows = len(matrix)
    n_cols = len(matrix[0]) if matrix else 0
    max_val = max(max(row) for row in matrix) if matrix else 1

    for r in range(n_rows):
        for c in range(n_cols):
            val = matrix[r][c]
            intensity = val / max_val if max_val else 0
            r_c = int(0 + intensity * (0xb6 - 0))
            g_c = int(0 + intensity * (0xcf - 0))
            b_c = int(0 + intensity * (0x42 - 0))
            fill = f'#{r_c:02x}{g_c:02x}{b_c:02x}'

            draw.rounded_rectangle(
                [x0 + c*cell_w, y0 + r*cell_h,
                 x0 + (c+1)*cell_w - 1, y0 + (r+1)*cell_h - 1],
                radius=3, fill=fill
            )
            draw_text(draw, x0 + c*cell_w + 5, y0 + r*cell_h + 10,
                     f'{val:.3f}', font_size=font_size)
```

## 字体大小映射

| 用途 | 字号 | 加粗 |
|:-----|:-----|:------|
| 图表标题 | 12pt | Bold |
| 面板标签 (a,b,c) | 10pt | Bold |
| 维度/指标名 | 8pt | Bold |
| 数值/标签 | 7pt | Regular |
| 注释/脚注 | 6pt | Regular |

## 已知限制

1. Pillow 无法生成 SVG/PDF — 仅适用于 PNG
2. CJK 字体需要手动安装 Arial/NotoSans
3. 无法生成统计检验标注（p-value）— 需要 matplotlib
4. 无法生成色盲检测 — 需要 matplotlib
5. 不适用于期刊提交 — 仅用于展示/汇报

## 使用决策

| 场景 | 选择 |
|:-----|:-----|
| 期刊提交 | matplotlib -> SVG/PDF |
| 汇报展示 | Pillow（快速PNG） |
| 服务器无 matplotlib | Pillow（唯一选择） |
| 需要统计标注 | matplotlib（必须） |
| 需要色盲检测 | matplotlib（必须） |
