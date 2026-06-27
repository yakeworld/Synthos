# Python 配方 — Figure Generation

所有代码片段均可独立使用或组合。单位统一为 **inches**。

---

## A. 初始化与环境

### A1. 安全导入（不阻塞无 matplotlib 环境）

```python
import importlib, subprocess, sys

def check_backend():
    """Return available backend in priority order."""
    backends = []
    try:
        import matplotlib; backends.append('matplotlib')
    except ImportError:
        pass
    try:
        subprocess.run(['firefox', '--version'], capture_output=True)
        backends.append('firefox')
    except (FileNotFoundError, OSError):
        pass
    try:
        subprocess.run(['chromium-browser', '--version'], capture_output=True)
        backends.append('chromium')
    except (FileNotFoundError, OSError):
        pass
    backends.append('pillow')  # Always available
    return backends

print(f"Available backends: {check_backend()}")
```

### A2. Matplotlib 标准初始化（期刊密度）

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

plt.rcParams.update({
    'font.size': 7,              # Default for single-column
    'axes.titlesize': 8,
    'axes.labelsize': 7,
    'xtick.labelsize': 6,
    'ytick.labelsize': 6,
    'legend.fontsize': 6,
    'figure.titlesize': 9,
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'svg.fonttype': 'none',      # Editable text in SVG
    'pdf.fonttype': 42,          # TrueType fonts in PDF
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1,
    'axes.grid': False,
    'axes.spines.top': False,
    'axes.spines.right': False,
})
```

### A3. 输出函数（统一）

```python
def save_figure(fig, name, fmt='auto'):
    """Save figure in all required formats with consistent settings."""
    base = f"figures/{name}"
    
    formats = ['svg', 'pdf', 'png'] if fmt == 'auto' else [fmt]
    for f in formats:
        if f == 'svg':
            fig.savefig(f"{base}.svg", bbox_inches='tight', pad_inches=0.1,
                       facecolor='white', edgecolor='none',
                       svg_fonttype='none')
        elif f == 'pdf':
            fig.savefig(f"{base}.pdf", bbox_inches='tight', pad_inches=0.1,
                       facecolor='white', dpi=300)
        elif f == 'png':
            fig.savefig(f"{base}.png", bbox_inches='tight', pad_inches=0.1,
                       facecolor='white', dpi=300)
    
    # Add version tag
    print(f"  [OK] Saved {base} (svg/pdf/png)")
```

---

## B. 色板与样式

### B1. Nature 语义色板

```python
NATURE = {
    'blue_main':    '#0F4D92',    # Primary evidence
    'blue_sec':     '#3775BA',    # Secondary
    'blue_light':   '#D6E4F0',    # Background
    'green_1':      '#DDF3DE',    # Positive result (light)
    'green_2':      '#AADCA9',    # Positive result
    'green_3':      '#8BCF8B',    # Positive result (strong)
    'red_strong':   '#B64342',    # Baseline / error / risk
    'red_light':    '#F6CFCB',    # Baseline (light)
    'red_sec':      '#E9A6A1',    # Baseline (secondary)
    'gray':         '#767676',    # Neutral / baseline
    'gray_light':   '#E0E0E0',    # Background
    'gold':         '#FFD700',    # Emphasis
    'cyan':         '#42949E',    # Tertiary
    'purple':       '#7B5EA7',    # Innovation / core
    'orange':       '#E8954A',    # Engineering / execution
}
```

### B2. 亮度感知文本颜色

```python
def text_color_for_bg(hex_color):
    """Return 'white' or 'black' based on background luminance."""
    c = hex_color.lstrip('#')
    r, g, b = int(c[0:2],16)/255, int(c[2:4],16)/255, int(c[4:6],16)/255
    lum = 0.299*r + 0.587*g + 0.114*b
    return 'white' if lum < 0.5 else 'black'

# Usage:
# text_color_for_bg('#8BCF8B') → 'black' (light background)
# text_color_for_bg('#B64342') → 'white' (dark background)
```

### B3. Hatch 灰度安全编码

```python
HATCHES = ['/', '\\\\', '.', 'x', 'o', '+', '|', '-']

def apply_hatches(bar_container, hatch_char):
    for patch in bar_container:
        patch.set_hatch(hatch_char)
        patch.set_edgecolor('black')
        patch.set_linewidth(0.5)

# Or per-bar:
for i, bar in enumerate(bars):
    bar.set_hatch(HATCHES[i % len(HATCHES)])
    bar.set_edgecolor('black')
```

### B4. Alpha 渐变消融

```python
def alpha_gradient(base_hex, n_steps, alpha_start=1.0, alpha_end=0.2):
    """Create n_steps steps from full alpha to transparent."""
    c = base_hex.lstrip('#')
    r, g, b = int(c[0:2],16)/255, int(c[2:4],16)/255, int(c[4:6],16)/255
    alphas = [alpha_start - i * (alpha_start - alpha_end) / (n_steps - 1)
              for i in range(n_steps)]
    return [(r, g, b, a) for a in alphas]

# Usage:
# colors = alpha_gradient('#0F4D92', 5) → 5 steps from #0F4D92@1.0 to #0F4D92@0.2
```

---

## C. 数据验证

### C1. 数据类型检查

```python
import pandas as pd
import numpy as np

def validate_dataframe(df, required_cols, dtype_map=None):
    """Validate a DataFrame for plotting.
    
    Args:
        df: DataFrame to validate
        required_cols: list of required column names
        dtype_map: dict{col_name: 'numeric'|'categorical'|'date'}
    
    Returns: (valid, errors, warnings)
    """
    errors = []
    warnings = []
    
    # Check required columns
    for col in required_cols:
        if col not in df.columns:
            errors.append(f"Missing required column: '{col}'")
    
    if not errors:
        # Check dtypes
        for col, dtype in (dtype_map or {}).items():
            if dtype == 'numeric':
                if not pd.api.types.is_numeric_dtype(df[col]):
                    errors.append(f"Column '{col}' should be numeric, got {df[col].dtype}")
            elif dtype == 'categorical':
                if pd.api.types.is_numeric_dtype(df[col]):
                    warnings.append(f"Column '{col}' may be categorical but is numeric")
    
    # Check missing values
    nans = df.isnull().sum().sum()
    if nans > 0:
        warnings.append(f"Missing values: {nans} total ({nans/len(df)*100:.1f}%)")
    
    # Check sample size
    if len(df) < 10:
        errors.append(f"Sample size too small: {len(df)} (minimum 10)")
    elif len(df) < 50:
        warnings.append(f"Small sample size: {len(df)}")
    
    # Check for constant columns
    for col in df.select_dtypes(include=[np.number]).columns:
        if df[col].nunique() == 1:
            errors.append(f"Column '{col}' is constant (all same value)")
    
    return len(errors) == 0, errors, warnings

# Usage:
# valid, errs, warns = validate_dataframe(df, ['x', 'y'], {'x': 'numeric', 'y': 'numeric'})
```

### C2. 异常值检测

```python
def detect_outliers(series, method='iqr', multiplier=1.5):
    """Detect outliers in a numeric series.
    
    Args:
        series: pandas Series with numeric data
        method: 'iqr' (interquartile range) or 'zscore'
        multiplier: IQR multiplier or z-score threshold
    
    Returns: (has_outliers, outlier_count, outlier_mask)
    """
    if not series.dtype in [np.float64, np.int64, np.float32, np.int32]:
        return False, 0, pd.Series(False, index=series.index)
    
    clean = series.dropna()
    if len(clean) < 5:
        return False, 0, pd.Series(False, index=series.index)
    
    if method == 'iqr':
        q1, q3 = clean.quantile(0.25), clean.quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - multiplier * iqr, q3 + multiplier * iqr
        mask = (~series.isna()) & ((series < lower) | (series > upper))
    else:  # zscore
        from scipy import stats
        z = np.abs(stats.zscore(clean))
        mask = pd.Series(False, index=series.index, dtype=bool)
        for i in clean.index:
            if i in series.index and z[clean.index.get_loc(i)] > multiplier:
                mask[i] = True
    
    return mask.sum() > 0, mask.sum(), mask

# Usage:
# has_outliers, count, mask = detect_outliers(df['accuracy'])
```

### C3. 样本量一致性检查

```python
def check_sample_consistency(results_dict, key='accuracy'):
    """Check that all models report results for the same number of samples.
    
    Args:
        results_dict: dict{model_name: {'accuracy': 0.95, 'std': 0.01, ...}}
        key: metric key to check
    
    Returns: (consistent, inconsistencies)
    """
    inconsistencies = []
    
    for model, metrics in results_dict.items():
        if isinstance(metrics, dict) and key in metrics:
            if 'n_samples' in metrics:
                pass  # Explicit sample count
            elif 'std' in metrics:
                # If std is 0 or very small, check if n_replicates was sufficient
                if metrics['std'] < 0.001 and key == 'accuracy':
                    inconsistencies.append(
                        f"Model '{model}': {key} std={metrics['std']} may indicate "
                        f"insufficient repeats or identical folds"
                    )
    
    return len(inconsistencies) == 0, inconsistencies
```

---

## D. 架构/流程图

### D1. 框+箭头基础

```python
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

def draw_box(ax, x, y, w, h, facecolor, edgecolor='#555555', lw=0.5, 
             pad=0.12, radius=0.08):
    """Standard box with rounded corners."""
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle=f"round,pad={pad},rounding_size={radius}",
                                facecolor=facecolor, edgecolor=edgecolor, linewidth=lw, zorder=2))

def draw_text(ax, x, y, text, fontsize=7, bold=False, color='#222222',
              ha='center', va='center', fontfamily='sans-serif'):
    """Standard text with consistent styling."""
    fw = 'bold' if bold else 'normal'
    ax.text(x, y, text, ha=ha, va=va, fontsize=fontsize, fontweight=fw,
            fontfamily=fontfamily, color=color, zorder=3)

def draw_arrow(ax, x1, y1, x2, y2, color='#666666', lw=1.0,
               rad=0, style='->', zorder=1):
    """Standard arrow with arc connection."""
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2),
                                arrowstyle=style,
                                connectionstyle=f"arc3,rad={rad}",
                                color=color, linewidth=lw, zorder=zorder))

# Usage:
# draw_box(ax, 0.5, 1.0, 2.0, 0.5, '#8BCF8B')
# draw_text(ax, 1.5, 1.25, 'Title', fontsize=8, bold=True)
# draw_arrow(ax, 0.5, 1.25, 2.5, 2.0, rad=-0.2)
```

### D2. 程序化布局（从底部向上）

```python
# Design system variables
SINGLE_H = 0.50    # Single-line box height
DOUBLE_H = 0.70    # Double-line box height
BOX_W = 3.0        # Side box width (≥3.0 for long titles)
CORE_W = 4.8       # Core box width
BOT_W = 5.2        # Bottom chain box width
GAP_S = 0.20       # Small gap (within zone)
GAP_M = 0.55       # Medium gap (between zones)
GAP_T = 0.35       # Title gap
PAD_BOT = 0.50     # Bottom padding

# Calculate from bottom
reg_y = PAD_BOT
ab_y = reg_y + DOUBLE_H + GAP_S
out_y = ab_y + DOUBLE_H + GAP_M
core_y = out_y + DOUBLE_H + GAP_M
c4_y = core_y + DOUBLE_H + GAP_M
c3_y = c4_y + SINGLE_H + GAP_S
c2_y = c3_y + SINGLE_H + GAP_S
c1_y = c2_y + SINGLE_H + GAP_S
strand_y = c1_y + SINGLE_H + GAP_S
title_y = strand_y + SINGLE_H + GAP_T

xc = 5.0; cx0 = xc - CORE_W/2
lx = 1.5; lx0 = lx - BOX_W/2
rx = 8.5; rx0 = rx - BOX_W/2
```

### D3. 箭头汇聚到核心顶边内侧

```python
# Core top edge inner points (25% and 75%)
core_top = core_y + DOUBLE_H
cx_l = cx0 + CORE_W * 0.25  # 25% from left
cx_r = cx0 + CORE_W * 0.75  # 75% from left

# Side→Core arrows (converge to core top edge inner)
draw_arrow(ax, lx, c4_y + SINGLE_H/2, cx_l, core_top, rad=-0.20)
draw_arrow(ax, rx, c4_y + SINGLE_H/2, cx_r, core_top, rad=0.20)

# Bottom chain (vertical)
draw_arrow(ax, xc, out_y, xc, ab_y + DOUBLE_H)
draw_arrow(ax, xc, ab_y, xc, reg_y + DOUBLE_H, dash=True)
```

---

## E. 数据图

### E1. 柱状图（带误差棒）

```python
fig, ax = plt.subplots(figsize=(4, 3))

methods = ['Method A', 'Method B', 'Method C']
accuracies = [0.95, 0.97, 0.94]
stds = [0.01, 0.008, 0.012]

bars = ax.bar(methods, accuracies, yerr=stds, capsize=3,
              color=[NATURE['blue_main'], NATURE['green_3'], NATURE['orange']],
              edgecolor='#555555', linewidth=0.5)

ax.set_ylim(0.90, 0.99)
ax.set_ylabel('Accuracy', fontsize=7)
ax.tick_params(axis='both', labelsize=6)

# Value labels on bars
for bar, acc, std in zip(bars, accuracies, stds):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
            f'{acc:.3f}±{std:.3f}', ha='center', fontsize=5.5, va='bottom')
```

### E2. 散点图（带趋势线）

```python
fig, ax = plt.subplots(figsize=(4, 3.5))

x_vals = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
y_vals = [0.72, 0.76, 0.78, 0.81, 0.83, 0.85, 0.87]

ax.scatter(x_vals, y_vals, s=40, color=NATURE['blue_main'],
           edgecolor='white', linewidth=0.5, zorder=3)

# Trendline
z = np.polyfit(x_vals, y_vals, 1)
p = np.poly1d(z)
x_line = np.linspace(min(x_vals), max(x_vals), 100)
ax.plot(x_line, p(x_line), color=NATURE['red_strong'], linewidth=1.5,
        linestyle='--', label=f'slope={z[0]:.3f}')

ax.set_xlabel('Feature Quality', fontsize=7)
ax.set_ylabel('Accuracy', fontsize=7)
ax.legend(fontsize=6)
```

### E3. 箱线图

```python
fig, ax = plt.subplots(figsize=(5, 3.5))

data = [group_accs_1, group_accs_2, group_accs_3]  # List of lists
bp = ax.boxplot(data, labels=['Group A', 'Group B', 'Group C'],
                patch_artist=True,
                boxprops=dict(facecolor=NATURE['blue_light'], edgecolor='#555555'),
                medianprops=dict(color=NATURE['blue_main'], linewidth=1.5),
                whiskerprops=dict(color='#555555'),
                capprops=dict(color='#555555'))

# Color each box
for patch, color in zip(bp['boxes'], 
                        [NATURE['blue_light'], NATURE['green_1'], NATURE['red_light']]):
    patch.set_facecolor(color)

ax.set_ylabel('Accuracy', fontsize=7)
```

---

## F. 多面板 Figure（a/b/c/d）

### F1. 基础 2×2 网格

```python
fig, axes = plt.subplots(2, 2, figsize=(7, 6), 
                         gridspec_kw={'wspace': 0.3, 'hspace': 0.35})

labels = ['a', 'b', 'c', 'd']
for i, ax in enumerate(axes.flat):
    # Panel label (lowercase bold, top-left)
    ax.text(-0.05, 1.05, f'{labels[i]})', transform=ax.transAxes,
            fontsize=8, fontweight='bold', va='bottom', ha='right')
    
    # Your plot here
    ax.plot(x, y, color=NATURE['blue_main'])
    ax.set_xlabel('X', fontsize=7)
    ax.set_ylabel('Y', fontsize=7)
```

### F2. 非对称布局（英雄面板）

```python
fig = plt.figure(figsize=(8, 6))
gs = fig.add_gridspec(2, 3, width_ratios=[1, 1, 1], 
                      height_ratios=[2, 1],
                      wspace=0.3, hspace=0.3)

# Panel a: wide hero (spans 2 cols)
ax_a = fig.add_subplot(gs[0, :2])
ax_a.text(-0.05, 1.05, 'a)', transform=ax_a.transAxes,
          fontsize=8, fontweight='bold', va='bottom', ha='right')

# Panel b: narrow right
ax_b = fig.add_subplot(gs[0, 2])
ax_b.text(-0.05, 1.05, 'b)', transform=ax_b.transAxes,
          fontsize=8, fontweight='bold', va='bottom', ha='right')

# Panel c: bottom span
ax_c = fig.add_subplot(gs[1, :])
ax_c.text(-0.05, 1.05, 'c)', transform=ax_c.transAxes,
          fontsize=8, fontweight='bold', va='bottom', ha='right')
```

### F3. 共享色标/图例

```python
fig, axes = plt.subplots(1, 3, figsize=(10, 3), sharey=True)

# Shared colorbar
im = axes[0].imshow(data, cmap='viridis')
for ax in axes[1:]:
    ax.imshow(data, cmap='viridis')

# Shared colorbar on right
cbar = fig.colorbar(im, ax=list(axes), orientation='vertical', fraction=0.05)
cbar.set_label('Value', fontsize=7)
```

---

## G. 统计标注

### G1. 自动添加 p-value 标注

```python
from scipy import stats

def add_significance(ax, data_groups, y_pos=None, y_offset=0.02, fontsize=6):
    """Add significance brackets between groups.
    
    Args:
        ax: matplotlib axes
        data_groups: list of (name, data_array)
        y_pos: y position for bracket (auto if None)
        y_offset: distance above max data for bracket
    """
    if y_pos is None:
        y_pos = max(g[1].max() for g in data_groups) + y_offset
    
    # Compare adjacent groups
    for i in range(len(data_groups) - 1):
        _, d1 = data_groups[i]
        _, d2 = data_groups[i + 1]
        
        # T-test
        t_stat, p_val = stats.ttest_ind(d1, d2, equal_var=False)
        
        if p_val < 0.001:
            sig = '***'
        elif p_val < 0.01:
            sig = '**'
        elif p_val < 0.05:
            sig = '*'
        else:
            sig = 'n.s.'
        
        # Draw bracket
        x1 = i + 0.5
        x2 = i + 1.5
        ax.plot([x1, x1, x2, x2], [y_pos, y_pos + 0.03, y_pos + 0.03, y_pos],
                color='#555555', linewidth=0.8)
        ax.text((x1 + x2) / 2, y_pos + 0.05, sig, ha='center', va='bottom',
                fontsize=fontsize, fontweight='bold')

# Usage:
# add_significance(ax, [('Control', group_a), ('Treatment', group_b)])
```

### G2. 均值+误差棒+显著性

```python
def plot_mean_errorbars(ax, data, labels, colors=None, yerr_type='std',
                       sig_level=0.05):
    """Plot mean with error bars and add significance stars."""
    means = [d.mean() for d in data]
    if yerr_type == 'std':
        stds = [d.std() for d in data]
    else:
        stds = [d.std() / len(d) ** 0.5 for d in data]  # SE
    
    bars = ax.errorbar(range(len(data)), means, yerr=stds, fmt='o',
                       capsize=3, color='#555555', ecolor='#555555',
                       markersize=5, markerfacecolor=colors or NATURE['blue_main'],
                       elinewidth=1, capthick=0.8)
    
    # Add significance between adjacent groups
    y_max = max(m + s for m, s in zip(means, stds))
    for i in range(len(data) - 1):
        t, p = stats.ttest_ind(data[i], data[i+1], equal_var=False)
        if p < sig_level:
            sig = '***' if p < 0.001 else '**' if p < 0.01 else '*'
            ax.text((i + i + 1) / 2 + 0.5, y_max + 0.02, sig,
                    ha='center', fontsize=7, fontweight='bold')
    
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=6)
```

---

## H. 图例管理

### H1. 图例条目过载检测

```python
def check_legend(ax):
    """Check legend quality."""
    legend = ax.get_legend()
    if legend is None:
        return True, []
    
    texts = legend.get_texts()
    n = len(texts)
    issues = []
    
    if n > 10:
        issues.append(f"Legend has {n} entries (>10). Consider direct labels or split legend.")
    
    # Check if legend overlaps data
    bb = legend.get_window_extent(ax.get_figure().canvas.get_renderer())
    # Simple heuristic
    if n > 6:
        issues.append(f"Legend with {n} entries may crowd the plot. Consider moving outside axes.")
    
    return len(issues) == 0, issues

# Usage:
# valid, issues = check_legend(ax)
```

### H2. 图例外置（防止遮挡数据）

```python
# Place legend outside axes
ax.legend(loc='upper left', bbox_to_anchor=(-0.05, 1.05),
          fontsize=6, frameon=False)

# Or right side outside
ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5),
          fontsize=6, frameon=False)
```

---

## I. 版本标记

### I1. 图底部版本戳

```python
def add_version_tag(ax, project='Project', version='v1.0', date=None):
    """Add small version text at bottom of figure."""
    if date is None:
        from datetime import datetime
        date = datetime.now().strftime('%Y-%m-%d')
    
    ax.text(0.5, -0.08, f'{project} {version} | {date}',
            transform=ax.transAxes, ha='center', va='bottom',
            fontsize=5, color='#999999', fontstyle='italic')

# Usage:
# add_version_tag(ax, 'HCS-3WT', 'v1.2', '2026-06-26')
```

---

## J. 混合工作流

### J1. SVG 模板数据注入

```python
import re
import json

def inject_data_into_svg(svg_path, data_dict, output_path=None):
    """Replace {{placeholder}} in SVG with actual values.
    
    Args:
        svg_path: path to SVG template
        data_dict: dict{placeholder_key: value}
        output_path: where to save (auto from svg_path if None)
    """
    with open(svg_path) as f:
        svg = f.read()
    
    for key, value in data_dict.items():
        placeholder = f'{{{{{key}}}}}'
        svg = svg.replace(placeholder, str(value))
    
    if output_path is None:
        output_path = svg_path.replace('.svg', '_data.svg')
    
    with open(output_path, 'w') as f:
        f.write(svg)
    
    return output_path

# Usage:
# inject_data_into_svg('template.svg', {'accuracy': '96.88%', 'f1': '97.55%'})
# → outputs 'template_data.svg' with values injected
```
