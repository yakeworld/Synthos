# Matplotlib Fallback — Pillow 纯代码路径

## 触发条件

`import matplotlib` 失败，或 `numpy` 2.x 与系统 matplotlib 版本冲突。

## 已验证可用的绘图原语

### 雷达图（Polar Chart）

```python
import math
from PIL import Image, ImageDraw, ImageFont

# 雷达图参数
cx, cy = 300, 300  # 中心
max_r = 110         # 最大半径
angles = [i * 2 * math.pi / n for i in range(n)]  # n = 维度数

# 网格圆
for ratio in [0.2, 0.4, 0.6, 0.8, 1.0]:
    r = int(max_r * ratio)
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=MED_GRAY, width=1)

# 轴线
for i in range(n):
    angle = angles[i] - math.pi/2  # 从顶部开始
    ex = cx + int(max_r * math.cos(angle))
    ey = cy + int(max_r * math.sin(angle))
    draw.line([(cx, cy), (ex, ey)], fill=MED_GRAY, width=1)
    label_points.append((ex, ey))

# 数据多边形
poly = [(int(cx + max_r * math.cos(angles[i] - math.pi/2)),
         int(cy + max_r * math.sin(angles[i] - math.pi/2))) for i in range(n)]
draw.polygon(poly, fill=(*BLUE[:3], 30), outline=BLUE, width=2)

# 数据点
for i in range(n):
    angle = angles[i] - math.pi/2
    dr = int(max_r * score[i])
    dx = cx + int(dr * math.cos(angle))
    dy = cy + int(dr * math.sin(angle))
    draw.ellipse([dx-3, dy-3, dx+3, dy+3], fill=BLUE, outline=WHITE)
```

### 进度条/柱状图

```python
bar_w = 300
bar_h = 50
bar_gap = 12

for i, (val, color) in enumerate(metrics):
    by = start_y + i * (bar_h + bar_gap)
    fill_w = int((panel_w - 30) * val)
    
    # 背景
    draw.rounded_rectangle([(x, by), (x + panel_w - 30, by + bar_h)], radius=8, fill=(240,240,243))
    # 填充
    draw.rounded_rectangle([(x, by), (x + fill_w, by + bar_h)], radius=8, fill=color)
    # 标签
    draw_text_bold(draw, x + 20, by + 14, label, DARK, f_8bold)
```

### 轨迹图（Improvement Trajectory）

```python
def score_to_y(val, y_min=0.70, y_max=1.00, plot_start=50, plot_end=300):
    return plot_end - (val - y_min) / (y_max - y_min) * (plot_end - plot_start)

# 网格线
for gv in [0.72, 0.80, 0.85, 0.90, 0.95]:
    gy = score_to_y(gv)
    draw.line([(x0, gy), (x1, gy)], fill=MED_GRAY, width=1)

# 数据点 + 连线箭头
for i, (label, val) in enumerate(history):
    px = x0 + 35 + i * step_x
    py = score_to_y(val)
    draw.ellipse([px-5, py-5, px+5, py+5], fill=color, outline=WHITE, width=2)
    draw_text_bold(draw, px - 10, py - 16, f"{val:.2f}", DARK, f_8bold)

# 箭头（标注改善）
draw_arrow(draw, x1, y1, x2, y2, TEAL, width=2)
```

### 箭头绘制

```python
def draw_arrow(draw, x1, y1, x2, y2, color, width=2):
    draw.line([(x1, y1), (x2, y2)], fill=color, width=width)
    angle = math.atan2(y2-y1, x2-x1)
    head_len = 8
    head_angle = math.pi / 6
    lx = x2 - head_len * math.cos(angle - head_angle)
    ly = y2 - head_len * math.sin(angle - head_angle)
    rx = x2 - head_len * math.cos(angle + head_angle)
    ry = y2 - head_len * math.sin(angle + head_angle)
    draw.polygon([(x2, y2), (int(lx), int(ly)), (int(rx), int(ry))], fill=color)
```

## 字体大小映射

| 用途 | 字号 | 加粗 |
|:-----|:-----|:-----|
| 图表标题 | 12pt | Bold |
| 面板标签 (a,b,c) | 10pt | Bold |
| 维度/指标名 | 8pt | Bold |
| 数值/标签 | 7pt | Regular |
| 注释/脚注 | 6pt | Regular |

## Session 日志

- 2026-06-21: matplotlib 因 NumPy 2.x 冲突全部失败。Pillow 纯代码路径成功生成三面板图（雷达+进度条+轨迹）。所有原语在此文档中验证过。
