---
name: figure-generation
description: >-
  发表级科研图表创建——Figure契约方法论：结论Claim→证据层级→面板映射→出口契约→审核风险，再画图。
  支持matplotlib (Python) 单/多面板排版，Nature语义色板（蓝主-绿正-红基+中性色+NMI淡色系），16种排版模式，
  按需生成SVG/PDF/PNG。认知原子层负责契约设计，terminal执行Python生成图像。
  兼容nature-figure方法论，但不绑定特定期刊风格——适用于所有SCI/会议图表场景。
version: 1.0.0
inherits: nature-figure (absorbed 2026-05-11)
allowed-tools:
  - terminal (Python plotting)
  - read_file (data inspection)
  - search_files (data location)
  - execute_code (data preprocessing)
  - write_file (figure scripts)
meta:
  archetype: cognitive-atom
  layer: extended
  absorbed_from: https://github.com/Yuan1z0825/nature-skills (袁一哲, 上海交大)
  absorption_date: 2026-05-11
  absorption_notes: >
    完全吸收nature-figure的Figure契约方法论（结论→证据链→面板映射→出口契约）、Nature语义色板体系
    （蓝-绿-红+中性色+NMI淡色系+分领域色板）、16种多面板布局模式、API参考和QA审核清单。
    与原技能的区别：移除Python/R后端二选一闸门（默认Python/matplotlib）、移除隐私规则、
    增加Synthos认知原子风格的前导格式和IO契约、增加与argument-expression的协同接口。
---

# Figure Generation Skill

面向Synthos认知流水线的**科学图表生成**技能。不是画图工具，是**视觉论证设计器**：每张图表从可证伪的结论Claim开始，经过证据链分析、面板映射、排版契约，最后通过terminal执行Python生成SVG/PDF。

## 核心方法论：Figure契约

画任何图之前，先建立契约。这是从nature-figure吸收的核心认知步骤，由Agent原生推理完成，不需要Python脚本。

### 契约模板

```
结论Claim: [一句话可证伪的核心主张，带动词。如"Treatment X reduces Y by restoring Z"]
图表原型: [quantitative-grid | schematic-led-composite | image-plate+quant | asymmetric-mixed-modality]
目标期刊/出口: [Nature | Science | Cell | NeurIPS | SCI 2-3区 | PPT报告 | 竞赛视频]
最终尺寸: [单栏89mm | 双栏183mm | 自定义]
面板映射:
  a: [图a解决的问题]
  b: [图b解决的问题]
  c: [图c解决的问题]
证据层级:
  主证据: [英雄面板，视觉最强]
  验证证据: [支撑面板，视觉次强]
  对照/稳健性: [辅助面板，视觉最弱]
所需统计: [样本量、误差棒类型、检验方法]
源数据: [CSV路径、列名、行数]
图像完整性备注: [是否全局调色、是否裁剪]
审稿风险: [审稿人可能质疑的三件事]
```

### 原型选择

| 原型 | 使用场景 | 英雄面板 | 支撑面板 |
|------|---------|---------|---------|
| `quantitative-grid` | 以数值比较为主 | 可选，一般是主导汇总指标 | 共享轴、对齐刻度、紧凑图例 |
| `schematic-led-composite` | 需先理解流程/机制/装置 | 左或上方的示意图，占40-60%面积 | 2-4个定量验证面板 |
| `image-plate+quant` | 成像/显微/组织学/电泳 | 图像板或代表性图像 | 比例尺、叠加、裁剪、定量 |
| `asymmetric-mixed-modality` | 混合示意图/光栅/热图/定量 | 一个面板跨行/列 | 按证据值排序的小面板 |

### 面板逻辑顺序（除非故事另有要求）

1. 建立系统：样本、方法、队列、装置或实验设计
2. 展示主要效应或核心比较
3. 展示机制或定位
4. 量化代表性图像或定性观察
5. 稳健性、对照、亚组分析或敏感性分析

### 冗余检查

契约完成后执行冗余检查：
- [ ] 面板b不是面板a的数据以不同形式重新显示
- [ ] 面板c增加了a和b中没有的维度（关联、生物学关系）
- [ ] 每个面板有自己的轴标签词汇（不同的x/y量纲）
- [ ] 遮住任一面板不会削弱论证 → 删除或合并

### 与ARG（argument-expression）协同

当Figure用于论文时，Figure契约的结论Claim应直接来自ARG的论证链。
输出接口：`figure-generation`接收ARG的 `claim` + `evidence` 作为输入，
输出 `SVG asset` + `figure legend text` 返回ARG嵌入论文。

---

## Python执行

契约确认后，通过terminal执行Python生成图表。以下为标准配置：

### 必备初始化

```python
import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
    "svg.fonttype": "none",         # SVG可编辑文本
    "pdf.fonttype": 42,             # PDF可编辑TrueType文本
    "font.size": 7,                 # 期刊密度用7，大面板用24
    "axes.spines.right": False,
    "axes.spines.top": False,
    "axes.linewidth": 0.8,
    "legend.frameon": False,
})
```

### 保存函数

```python
def save_pub(fig, filename, dpi=600):
    fig.savefig(f"{filename}.svg", bbox_inches="tight")
    fig.savefig(f"{filename}.pdf", bbox_inches="tight")
    fig.savefig(f"{filename}.tiff", dpi=dpi, bbox_inches="tight")
```

### 多面板布局

使用 `gridspec` 创建非等分多面板：

```python
from matplotlib import gridspec
fig = plt.figure(figsize=(7.2, 6.2))
gs = fig.add_gridspec(2, 4, height_ratios=[2.2, 1.0], hspace=0.18, wspace=0.28)
ax_top = fig.add_subplot(gs[0, :])    # 英雄面板（上方示意图）
ax_b = fig.add_subplot(gs[1, 0])
ax_c = fig.add_subplot(gs[1, 1:3])
ax_d = fig.add_subplot(gs[1, 3])
```

---

## 色彩体系

### 语义色板（Nature标准）

```python
PALETTE = {
    "blue_main":      "#0F4D92",   # 英雄方法/实验组
    "blue_secondary": "#3775BA",   # 第二方法/对比组
    "green_1":  "#DDF3DE",         # 正向提升（浅）
    "green_2":  "#AADCA9",
    "green_3":  "#8BCF8B",         # 正向提升（深）
    "red_1":    "#F6CFCB",         # 基线/对照（浅）
    "red_2":    "#E9A6A1",
    "red_strong": "#B64342",       # 基线/对照（深）
    "neutral_light": "#CFCECE",
    "neutral_mid":   "#767676",
    "neutral_dark":  "#4D4D4D",
    "neutral_black": "#272727",
    "gold":   "#FFD700",           # 强调色（少量使用）
    "teal":   "#42949E",
    "violet": "#9A4D8E",
    "magenta":"#EA84DD",
}
DEFAULT_COLORS = ["#0F4D92", "#8BCF8B", "#B64342", "#42949E", "#9A4D8E", "#CFCECE"]
```

### NMI淡色系（多方法对比用——统一家族色胜过高饱和度区分）

```python
PALETTE_NMI = {
    "baseline_dark": "#484878",
    "baseline_mid":  "#7884B4",
    "baseline_soft": "#B4C0E4",
    "ours_tiny":  "#E4E4F0",
    "ours_base":  "#E4CCD8",
    "ours_large": "#F0C0CC",
    "delta_up":   "#2E9E44",
    "delta_down": "#E53935",
}
```

### 分领域色板

| 领域 | 特征 |
|------|------|
| 成像/显微 | 黑底`#000000` + 灰`#B8B8B8` + 青`#22D7E6` + 品红`#FF2AD4` |
| 材料/化学 | 青绿`#77D7D1` + 蓝绿`#33B5A5` + 淡紫`#B9A7E8` + 紫`#7C6CCF` |
| 临床/纵向 | 基线`#272727` → 周6`#E28E2C` → 周13`#D24B40` → 年1`#5B8FD6` |
| 基因组 | 中性灰 + 红`#D9544D` + 蓝`#5B7FCA` + 紫`#B89BD9` |

### 消融实验Alpha编码

```python
blue_rgb = (0.215686, 0.458824, 0.729412)
alphas = np.linspace(0.2, 1.0, n_variants)
colors = [(blue_rgb[0], blue_rgb[1], blue_rgb[2], a) for a in alphas]
# alpha=1.0 → 完整方法, alpha=0.2 → 最消融变体
```

### 色板使用原则

1. 同一图表使用**一个中性族 + 一个信号族 + 一个强调族**
2. 条件/方法颜色跨面板保持一致
3. 绿色/红色仅用于**方向性注释**（提升/下降），不作主系列身份
4. 减少饱和度优于增加色相种类
5. 考虑灰度打印可读性 → hatch叠加

---

## 16种排版模式

| # | 模式 | 使用场景 | 关键参数 |
|---|------|---------|---------|
| 1 | 超宽多指标柱状图 | 3-4指标×多方法 | figsize=(45,12), 末面板专用图例 |
| 2 | 专用图例面板 | 图例大或多面板共享 | `axes[-1].legend(); axes[-1].set_axis_off()` |
| 3 | 隐藏X轴标签 | 方法名已在图例中 | `ax.set_xticks([])` |
| 4 | 动态Y轴紧缩 | 数据集中在狭窄区间 | `margin = (max-min)*0.1; ax.set_ylim([min-margin, max+margin])` |
| 5 | Alpha渐变消融 | 同一方法的消融变体 | 同色不同alpha，full→alpha=1.0 |
| 6 | Hatch灰度安全 | 印刷黑白区分 | `hatches = ['/','\\\\','.','x','o']` |
| 7 | 语义色映射 | 跨面板颜色一致 | `method_colors = {方法名: 色值, ...}` |
| 8 | 柱内亮度感知文本 | 深色柱白字/浅色柱黑字 | luminance计算 + textcolor |
| 9 | Fill-between hatch | 面积图灰度安全 | hatch + edgecolor叠加 |
| 10 | 趋势事件标注 | 时间线上标注事件 | arrowprops + 文本标记 |
| 11 | 数据集内分组柱 | 多数据集×多方法 | 数据集间留gap |
| 12 | 示意图主+定量辅 | 机制/流程图带头 | height_ratios=[2.2, 1.0] |
| 13 | 暗底图像板 | 显微/渲染 | facecolor='black', 白色比例尺 |
| 14 | 临床三联画 | 纵向+森林图+汇总 | height_ratios=[1.0, 1.35, 0.8] |
| 15 | 非对称英雄面板 | 某面板概念核心 | gs范围跨行列 |
| 16 | 填充区域直接标签 | 类别多图例大 | 稳定区域内直接文本 |

详见 `references/common-patterns.md`

---

## 出口契约

```python
# SVG是必需的主要格式（可编辑文本）
fig.savefig(f"{filename}.svg", bbox_inches="tight")
# PNG/PDF/TIFF为次要格式
fig.savefig(f"{filename}.png", dpi=300, bbox_inches="tight")
fig.savefig(f"{filename}.pdf", bbox_inches="tight")
```

字体尺寸层级：
| 上下文 | font.size | 图宽 (inch) |
|--------|-----------|-------------|
| 期刊密度多面板 | 7-9 | 7.0-7.4 |
| 大面板柱状图 | 24 | 28-45 |
| 紧凑子图 | 15-16 | 9-16 |
| 趋势/折线 | 7-9 | 14 |
| 热图 | 7-9 | 8-20 |

---

## QA审核清单（提交前）

- [ ] 结论Claim存在，每个面板映射到唯一证据
- [ ] 原型已声明，面板层级已确定
- [ ] 最终尺寸符合目标期刊（单栏89mm/双栏183mm）
- [ ] 文本在SVG中可编辑（`svg.fonttype='none'`）
- [ ] Arial/sans-serif字体一致
- [ ] 无彩虹色板；红绿不是唯一编码
- [ ] 灰度打印可分辨（考虑hatch）
- [ ] 误差棒、区间和统计检验已定义
- [ ] 可比较面板间的轴范围可比
- [ ] 代表性图像已量化并追溯到源文件
- [ ] `tight_layout(pad=2)` + `plt.close(fig)`

---

## 加载时机

- 用户要求创建、修改或润色论文图表
- 用户提到"Nature风格"、"SCI图表"、"发表级图表"
- 竞赛视频需要插图
- 需要多面板排版、审美优化、期刊适配

## 不加载的时机

- 数据探索性（EDA）图表，无发表目标
- Plotly/Altair/Bokeh等交互式图表
- 主要流程是3D/GIS/非科学插图
- Illustrator/Figma优先的图表

---

## 参考文献

| 文件 | 何时打开 |
|------|---------|
| references/figure-contract.md | 需要详细Figure契约模板和证据层级检查 |
| references/design-theory.md | 字体、色彩理论、排版原理、出口政策 |
| references/common-patterns.md | 16种排版模式的完整代码示例 |
| references/api.md | Python辅助函数签名和色板常量 |
| references/qa-contract.md | 提交前完整QA审核清单 |
| references/nature-2026-observations.md | 真实Nature 2026页面原型分析 |

---

## IO契约

**输入**（来自认知流水线）：
- `claim`: 一句可证伪的结论（通常来自ARG原子）
- `data`: 数据文件路径（CSV/NPY/HDF5），列名和统计描述
- `target`: 目标出口（期刊/竞赛/PPT）
- `panel_count`: 面板数（可选，默认由证据层级推导）

**输出**（流向流水线）：
- `SVG asset`: 可编辑矢量图文件路径
- `figure_legend`: 图注文本（可直接嵌入LaTeX/Word）
- `pipeline_meta`: {claim, archetype, panel_map, dpi, fonts}

**副作用**：在 `./figures/` 下创建SVG/PDF/TIFF文件
