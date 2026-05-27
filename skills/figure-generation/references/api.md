# Figure Generation API Reference

Python辅助函数和色板常量（吸收自nature-figure）。

## 色板常量

```python
PALETTE = {
    "blue_main":      "#0F4D92",
    "blue_secondary": "#3775BA",
    "green_1": "#DDF3DE", "green_2": "#AADCA9", "green_3": "#8BCF8B",
    "red_1":   "#F6CFCB", "red_2":   "#E9A6A1", "red_strong": "#B64342",
    "neutral_light": "#CFCECE", "neutral_mid": "#767676",
    "neutral_dark":  "#4D4D4D", "neutral_black": "#272727",
    "gold": "#FFD700", "teal": "#42949E", "violet": "#9A4D8E", "magenta": "#EA84DD",
}
DEFAULT_COLORS = ["#0F4D92", "#8BCF8B", "#B64342", "#42949E", "#9A4D8E", "#CFCECE"]

PALETTE_NMI_PASTEL = {
    "baseline_dark": "#484878", "baseline_mid": "#7884B4", "baseline_soft": "#B4C0E4",
    "ours_tiny": "#E4E4F0", "ours_base": "#E4CCD8", "ours_large": "#F0C0CC",
    "delta_up": "#2E9E44", "delta_down": "#E53935",
}
```

## apply_publication_style()

```python
def apply_publication_style(font_size=16, axes_linewidth=2.5, use_tex=False):
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
    plt.rcParams['svg.fonttype'] = 'none'
    plt.rcParams['font.size'] = font_size
    plt.rcParams['axes.spines.right'] = False
    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.linewidth'] = axes_linewidth
    plt.rcParams['legend.frameon'] = False
    if use_tex:
        plt.rcParams['text.usetex'] = True
```

## 辅助函数

| 函数 | 用途 | 关键参数 |
|------|------|---------|
| `apply_publication_style()` | 全局样式 | font_size, axes_linewidth |
| `save_pub(fig, filename, dpi=600)` | SVG+PDF+TIFF | dpi |
| `add_panel_label(ax, label, ...)` | 面板标签a/b/c | x=-0.06, y=1.02, fontsize=14 |
| `make_grouped_bar(ax, categories, series, ...)` | 分组柱状图 | categories, series, colors, annotate |
| `make_trend(ax, x, y_series, ...)` | 多线趋势图 | show_shadow, lw=2.5 |
| `make_forest_plot(ax, labels, estimates, ...)` | 森林图 | ci_low, ci_high, ref |
| `make_heatmap(ax, matrix, ...)` | 热图 | cmap, annotate |
| `style_dark_image_ax(ax)` | 暗底成像板 | facecolor='black' |
| `finalize_figure(fig, out_path, ...)` | 保存+关闭 | formats=['svg','pdf','png'], dpi |

详见完整函数签名在 SKILL.md 内联代码块或原nature-figure api.md。
