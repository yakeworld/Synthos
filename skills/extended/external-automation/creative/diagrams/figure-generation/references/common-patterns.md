# Figure Generation — Common Layout Patterns

16种可复用排版模式的完整代码参考。详见 SKILL.md 中的模式概览表。

## 模式1: 超宽多指标柱状图

```python
fig = plt.figure(figsize=(45, 12))
gs = gridspec.GridSpec(1, n_metrics)
for i, metric in enumerate(metrics):
    ax = fig.add_subplot(gs[i])
    ax.bar(x, values[metric], color=colors, ...)
    ax.set_ylabel(metric, fontsize=54, labelpad=12)
    ax.set_xticks([])
ax_leg = fig.add_subplot(gs[-1])
ax_leg.legend(handles, labels, fontsize=38, loc='center', frameon=False)
ax_leg.set_axis_off()
```

## 模式2: 专用图例面板

```python
fig, axes = plt.subplots(1, n_data + 1, figsize=(...))
for i, ax in enumerate(axes[:-1]):
    ax.bar(...)
axes[-1].legend(handles, labels, fontsize=28, loc='center', frameon=False)
axes[-1].set_axis_off()
```

## 模式3: 隐藏X轴标签

当图例已命名所有方法时：
```python
ax.set_xticks([])
```

## 模式4: 动态Y轴紧缩

```python
margin = (values.max() - values.min()) * 0.1
ax.set_ylim([values.min() - margin, values.max() + margin])
ax.set_yticks([0.75, 0.80, 0.85, 0.90])
```

## 模式5: Alpha渐变消融

```python
blue_rgb = (0.215686, 0.458824, 0.729412)
alphas = np.linspace(0.2, 1.0, n_ablations)
colors = [(blue_rgb[0], blue_rgb[1], blue_rgb[2], a) for a in alphas]
```

## 模式6: Hatch灰度安全

```python
hatches = ['/', '\\\\', '.', 'x', 'o', '+']
for bar_container, hatch in zip(grouped_bars, hatches):
    for patch in bar_container:
        patch.set_hatch(hatch)
        patch.set_edgecolor('black')
```

## 模式7: 语义色映射

```python
method_colors = {
    'ResNet1d18': '#484878', 'ResNet1d34': '#7884B4',
    'ECGFounder': '#B4C0E4', 'CSFM-Tiny': '#E4E4F0',
    'CSFM-Base': '#E4CCD8', 'CSFM-Large': '#F0C0CC',
}
colors = [method_colors[m] for m in methods]
```

## 模式8: 柱内亮度感知文本

```python
c = color.lstrip('#')
r, g, b = int(c[0:2],16)/255, int(c[2:4],16)/255, int(c[4:6],16)/255
lum = 0.299*r + 0.587*g + 0.114*b
textcolor = 'white' if lum < 0.5 else 'black'
ax.text(x, y, f'{value:.2f}', ha='center', color=textcolor, ...)
```

## 模式12: 示意图主+定量辅

```python
fig = plt.figure(figsize=(7.2, 6.2))
gs = fig.add_gridspec(2, 4, height_ratios=[2.2, 1.0], hspace=0.18, wspace=0.28)
ax_top = fig.add_subplot(gs[0, :])    # 英雄示意图
ax_b = fig.add_subplot(gs[1, 0])
ax_c = fig.add_subplot(gs[1, 1:3])
ax_d = fig.add_subplot(gs[1, 3])
```

## 模式13: 暗底图像板

```python
gs = fig.add_gridspec(3, 5, hspace=0.08, wspace=0.04)
for r in range(3):
    for c in range(5):
        ax = fig.add_subplot(gs[r, c])
        ax.set_facecolor('black')
        ax.set_xticks([]); ax.set_yticks([])
```

## 模式14: 临床三联画

```python
gs = fig.add_gridspec(3, 3, height_ratios=[1.0, 1.35, 0.8], hspace=0.28, wspace=0.32)
axes_top = [fig.add_subplot(gs[0, i]) for i in range(3)]
axes_mid = [fig.add_subplot(gs[1, i]) for i in range(3)]
axes_bot = [fig.add_subplot(gs[2, i]) for i in range(3)]
```

## 模式15: 非对称英雄面板

```python
gs = fig.add_gridspec(3, 4, hspace=0.25, wspace=0.28)
ax_a = fig.add_subplot(gs[0, :2])
ax_b = fig.add_subplot(gs[0, 2])
ax_e = fig.add_subplot(gs[:, 3])      # 英雄面板跨所有行
ax_f = fig.add_subplot(gs[2, :2])
```

## 模式9: 填充区域直接标签（面积图，灰度安全）

```python
fig, ax = plt.subplots(figsize=(6, 4))

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
val1 = [10, 12, 15, 14, 18, 20]
val2 = [8, 9, 11, 10, 13, 15]

ax.fill_between(months, val1, color='#0F4D92', alpha=0.6, label='Method A')
ax.fill_between(months, val2, color='#8BCF8B', alpha=0.6, label='Method B')

# Direct labels on filled areas (no legend needed)
ax.text('Mar', 15.5, 'A: 15', ha='center', fontsize=7, fontweight='bold',
        color='white', alpha=0.8)
ax.text('Mar', 11.5, 'B: 11', ha='center', fontsize=7, fontweight='bold',
        color='#222222', alpha=0.8)

ax.set_ylabel('Value', fontsize=7)
```

## 模式10: 趋势事件标注（时间线 + 事件标记）

```python
fig, ax = plt.subplots(figsize=(8, 4))

time = np.arange(1, 37)  # 36 months
accuracy = np.random.uniform(0.85, 0.95, 36)

ax.plot(time, accuracy, color='#0F4D92', linewidth=1.5, marker='o', markersize=3)

# Add event annotations
events = [
    (6, 'Data Collection Started'),
    (12, 'Model v1.0 Deployed'),
    (18, 'Algorithm Upgrade'),
    (24, 'Clinical Trial Phase II'),
]

for month, label in events:
    if month <= len(time):
        ax.axvline(x=month, color='#999999', linestyle='--', linewidth=0.5, alpha=0.5)
        ax.text(month, accuracy[month-1] + 0.02, label,
                ha='center', fontsize=5.5, color='#555555', rotation=0,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#F0F0F0', edgecolor='#CCCCCC'))

ax.set_xlabel('Month', fontsize=7)
ax.set_ylabel('Accuracy', fontsize=7)
ax.set_ylim(0.80, 0.98)
```

## 模式11: 数据集内分组柱（多数据集 × 多方法）

```python
fig, ax = plt.subplots(figsize=(8, 5))

datasets = ['WBC', 'WDBC', 'PIMA', 'MNIST']
methods = ['HCS-3WT', 'SVC', 'RF', 'LogReg']
# data[dataset_idx][method_idx] = accuracy
data = [
    [0.98, 0.96, 0.97, 0.96],  # WBC
    [0.97, 0.96, 0.96, 0.95],  # WDBC
    [0.88, 0.85, 0.86, 0.84],  # PIMA
    [0.95, 0.94, 0.94, 0.93],  # MNIST
]

n_datasets = len(datasets)
n_methods = len(methods)
width = 0.15
colors = ['#0F4D92', '#8BCF8B', '#E8954A', '#B64342']

for i, (method, color) in enumerate(zip(methods, colors)):
    x_offset = i * width - width/2 * (n_methods - 1)
    x_pos = [d + x_offset for d in range(n_datasets)]
    bars = ax.bar(x_pos, [row[i] for row in data], width=width,
                  color=color, edgecolor='#555555', linewidth=0.3, label=method)

ax.set_xticks(range(n_datasets))
ax.set_xticklabels(datasets, fontsize=7)
ax.set_ylabel('Accuracy', fontsize=7)
ax.legend(fontsize=6, loc='upper right')
ax.set_ylim(0.80, 1.00)
```

更多模式详见原nature-figure common-patterns.md（模式16直接标签在原skill文档中）。
