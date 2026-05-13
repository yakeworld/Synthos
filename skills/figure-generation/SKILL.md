---
name: figure-generation
description: >-
  发表级科研图表创建——Figure契约方法论：结论Claim→证据层级→面板映射→出口契约→审核风险，再画图。
  支持matplotlib (Python) 单/多面板排版，Nature语义色板（蓝主-绿正-红基+中性色+NMI淡色系），16种排版模式，
  按需生成SVG/PDF/PNG。认知原子层负责契约设计，terminal执行Python生成图像。
  兼容nature-figure方法论，但不绑定特定期刊风格——适用于所有SCI/会议图表场景。
|version: 1.0.0
|inherits: nature-figure (absorbed 2026-05-11), academic-plotting (absorbed 2026-05-14)
|allowed-tools:
|  - terminal (Python plotting)
|  - read_file (data inspection)
|  - search_files (data location)
|  - execute_code (data preprocessing)
|  - write_file (figure scripts)
|metadata:
|  synthos_atom_type: "extended"
|  synthos_data_access_level: "verified_only"
|  archetype: cognitive-atom
|  layer: extended
|  absorbed_from: https://github.com/Yuan1z0825/nature-skills (袁一哲, 上海交大)
|  absorption_date: 2026-05-11
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

---

## Visual Style Library [SYNTHOS_P0_ABSORBED_FROM: NanoResearch academic-plotting]

从NanoResearch academic-plotting吸收的4种视觉风格和4种色板，用于替代或补充默认的Nature色板体系。风格选择应在**Figure契约阶段完成**——出口契约中应声明使用的风格代号。

### 视觉风格一览

| 代号 | 名称 | 精神 | 适合出口 |
|:----:|------|------|---------|
| A | Sketch | 手绘感、速写风格 | 评审答辩、竞赛海报、概念说明 |
| B | Modern Minimal | 干净、留白、信息密度低 | Nature/Science/Cell 主图 |
| C | Illustrated Technical | 半技术插图、高信息密度 | NeurIPS/ICLR、面板组合图 |
| D | Accent Bar | 强调色条带、高对比入口 | 会议Keynote、主页Hero图、封面 |

---

### A — Sketch Style

手绘速写风格——非正式、亲和力强。适合概念说明、方法概览、答辩开场图。

```python
STYLE_A = {
    # ---- 主轴 ----
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": True,
    "axes.spines.bottom": True,
    "axes.linewidth": 1.8,               # 粗手绘感
    "axes.edgecolor": "#2C3E50",         # 深蓝灰
    "axes.facecolor": "#FAF7F2",         # 暖白纸底
    "figure.facecolor": "#FAF7F2",
    # ---- 文字 ----
    "font.family": "sans-serif",
    "font.sans-serif": ["Comic Sans MS", "Snell Roundhand", "Arial", "sans-serif"],
    "font.size": 9,
    "axes.labelsize": 10,
    "axes.titlesize": 11,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    # ---- 刻度 ----
    "xtick.major.size": 4,
    "ytick.major.size": 4,
    "xtick.color": "#2C3E50",
    "ytick.color": "#2C3E50",
    # ---- 网格 ----
    "axes.grid": True,
    "grid.alpha": 0.30,
    "grid.linestyle": "--",
    "grid.color": "#BDC3C7",
    "grid.linewidth": 0.6,
}
DEFAULT_COLORS_A = ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12", "#9B59B6", "#1ABC9C"]
```

#### 视觉特征
- 暖白纸底 `#FAF7F2` + 深蓝灰轴 `#2C3E50`
- 粗轴（1.8pt）模拟手绘边界
- 建议使用圆形marker（`o`）或交叉marker（`x`）增强手绘感
- 柱状图建议加hatch（`//` 或 `..`）
- 适合**方法概览**、**概念图**、**评审答辩开场**、**竞赛海报**

---

### B — Modern Minimal Style

极致干净，最大化数据-墨水比。Nature主图常用风格。

```python
STYLE_B = {
    # ---- 主轴 ----
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": True,
    "axes.spines.bottom": True,
    "axes.linewidth": 0.5,               # 极细轴
    "axes.edgecolor": "#555555",
    "axes.facecolor": "#FFFFFF",
    "figure.facecolor": "#FFFFFF",
    # ---- 文字 ----
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
    "font.size": 7,
    "axes.labelsize": 8,
    "axes.titlesize": 9,
    "xtick.labelsize": 6.5,
    "ytick.labelsize": 6.5,
    # ---- 刻度 ----
    "xtick.major.size": 3,
    "ytick.major.size": 3,
    "xtick.color": "#555555",
    "ytick.color": "#555555",
    # ---- 无网格 ----
    "axes.grid": False,
    # ---- 图例 ----
    "legend.frameon": False,
    "legend.fontsize": 6,
}
DEFAULT_COLORS_B = ["#0F4D92", "#8BCF8B", "#B64342", "#42949E", "#9A4D8E", "#CFCECE"]
```

#### 视觉特征
- 纯白底 `#FFFFFF` + 浅灰轴 `#555555`
- 极细轴（0.5pt），最大化数据面积
- 无网格、无装饰、无背景色
- Arial字体，严格对称排版
- 适合**Nature/Science/Cell主图**、**严谨定量比较**、**双栏多面板**

---

### C — Illustrated Technical Style

半技术插图风格——高信息密度、多色标注、适合NeurIPS面板图和组合图。

```python
STYLE_C = {
    # ---- 主轴 ----
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": True,
    "axes.spines.bottom": True,
    "axes.linewidth": 1.0,
    "axes.edgecolor": "#333333",
    "axes.facecolor": "#F8F9FA",         # 浅冰灰底
    "figure.facecolor": "#F8F9FA",
    # ---- 文字 ----
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
    "font.size": 8,
    "axes.labelsize": 9,
    "axes.titlesize": 10,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    # ---- 刻度 ----
    "xtick.major.size": 4,
    "ytick.major.size": 4,
    "xtick.color": "#333333",
    "ytick.color": "#333333",
    # ---- 微网格 ----
    "axes.grid": True,
    "grid.alpha": 0.20,
    "grid.linestyle": "-",
    "grid.color": "#CCCCCC",
    "grid.linewidth": 0.3,
    # ---- 图例 ----
    "legend.frameon": True,
    "legend.fancybox": True,
    "legend.edgecolor": "#CCCCCC",
    "legend.fontsize": 7,
}
DEFAULT_COLORS_C = ["#E63946", "#457B9D", "#1D3557", "#2A9D8F", "#F4A261", "#9C89B8"]
```

#### 视觉特征
- 浅冰灰底 `#F8F9FA` + 深灰轴 `#333333`
- 亚光视觉感受，适合高密度面板
- 极浅网格线（alpha=0.20）辅助数据阅读
- 图例有细边框框线
- 适合**NeurIPS/ICLR多面板**、**组合实验结果**、**技术附录图**

---

### D — Accent Bar Style

强调色条带风格——高视觉入口冲击力，适合封面、Keynote、主页Hero图。

```python
STYLE_D = {
    # ---- 主轴 ----
    "axes.spines.top": True,
    "axes.spines.right": True,
    "axes.spines.left": True,
    "axes.spines.bottom": True,
    "axes.linewidth": 0.8,
    "axes.edgecolor": "#222222",
    "axes.facecolor": "#FFFFFF",
    "figure.facecolor": "#FFFFFF",
    # ---- 文字 ----
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 13,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    # ---- 刻度 ----
    "xtick.major.size": 5,
    "ytick.major.size": 5,
    "xtick.color": "#222222",
    "ytick.color": "#222222",
    # ---- 强调色条 ----
    "axes.spines.left.color": None,      # 客户端设置强调条
}
ACCENT_BAR_COLOR = "#E63946"            # 默认强调色
ACCENT_BAR_WIDTH = 4                    # 左轴加粗为色条 (客户端代码实现)
```

#### 视觉特征
- 四边全轴，左轴加粗为**强调色条**（默认`#E63946`红，可替换）
- 大字号排版，适合大画幅展示
- 高对比度，数据点使用实心填充/粗线
- 建议配合**半透明填充**使用
- 适合**会议Keynote**、**论文封面/图形摘要**、**主页Hero图**、**竞赛视频封面**

实现强调色条的Python示例：

```python
# 左轴加粗为强调色条
ax.spines["left"].set_linewidth(4)
ax.spines["left"].set_color("#E63946")
# 或使用ax.axvline添加色条带
ax.axvspan(-0.5, 0.2, color="#E63946", alpha=0.08, zorder=0)
```

---

### 色板

4种色板，每种6色，可直接替换 `STYLE_X["DEFAULT_COLORS_X"]`。

#### Palette 1: Ocean Dusk — 海洋暮色

低饱和蓝灰调，优雅克制。适合Nature风格、临床/纵向数据、连续数据的微妙区分。

```python
PALETTE_OCEAN_DUSK = [
    "#4A6FA5",   # 深海蓝
    "#6B8EB5",   # 中蓝灰
    "#9BB7D4",   # 浅蓝灰
    "#D4C9B5",   # 沙色
    "#A8957A",   # 褐色
    "#7D6B5A",   # 深棕
]
```

| 色号 | 用途 | 色值 |
|:----:|------|:----:|
| 1 | 主对比组 | `#4A6FA5` |
| 2 | 次要组 | `#6B8EB5` |
| 3 | 参考/基线 | `#9BB7D4` |
| 4 | 强调/标注 | `#D4C9B5` |
| 5 | 辅助标注 | `#A8957A` |
| 6 | 中性/背景 | `#7D6B5A` |

#### Palette 2: Ink & Wash — 水墨

高对比黑白灰 + 单色强调。适合打印出版物、灰度友好、黑白打印优先场景。

```python
PALETTE_INK_WASH = [
    "#1A1A1A",   # 墨黑
    "#4A4A4A",   # 深灰
    "#808080",   # 中灰
    "#B3B3B3",   # 浅灰
    "#D9D9D9",   # 极浅灰
    "#C41E3A",   # 朱砂红（唯一强调色）
]
```

| 色号 | 用途 | 色值 |
|:----:|------|:----:|
| 1 | 英雄数据 | `#1A1A1A` |
| 2 | 对比1 | `#4A4A4A` |
| 3 | 对比2 | `#808080` |
| 4 | 参考/通道 | `#B3B3B3` |
| 5 | 背景/填充 | `#D9D9D9` |
| 6 | 唯一强调（可用于p值、显著性标记） | `#C41E3A` |

#### Palette 3: Nord — 北欧

取自Nord主题的北极蓝青色系，高可读性、低视觉疲劳。适合长时间阅读论文、线上发表、深色模式兼容。

```python
PALETTE_NORD = [
    "#5E81AC",   # 北极蓝
    "#81A1C1",   # 亮蓝灰
    "#88C0D0",   # 冰湖蓝
    "#8FBCBB",   # 苔原青
    "#D08770",   # 暖橙
    "#B48EAD",   # 紫罗兰
]
```

| 色号 | 用途 | 色值 |
|:----:|------|:----:|
| 1 | 主方法/实验组 | `#5E81AC` |
| 2 | 第二方法 | `#81A1C1` |
| 3 | 第三方法/基线 | `#88C0D0` |
| 4 | 中性参照 | `#8FBCBB` |
| 5 | 强调/关注 | `#D08770` |
| 6 | 次强调/分类标记 | `#B48EAD` |

#### Palette 4: Okabe-Ito — 色盲友好

源自Okabe & Ito的色盲友好色板。所有色点对红绿色盲、蓝黄色盲可分辨。**所有图表默认推荐色板。**

```python
PALETTE_OKABE_ITO = [
    "#E69F00",   # 橙
    "#56B4E9",   # 天蓝
    "#009E73",   # 绿
    "#F0E442",   # 黄
    "#0072B2",   # 蓝
    "#D55E00",   # 朱红
    "#CC79A7",   # 粉紫
    "#000000",   # 黑
]
```

| 色号 | 用途 | 色值 |
|:----:|------|:----:|
| 1 | 第一对比 | `#E69F00` |
| 2 | 第二对比 | `#56B4E9` |
| 3 | 正向/提升 | `#009E73` |
| 4 | 注意/标注 | `#F0E442` |
| 5 | 英雄方法 | `#0072B2` |
| 6 | 强调/下降 | `#D55E00` |
| 7 | 次强调 | `#CC79A7` |
| 8 | 基线 | `#000000` |

> **色板选择原则**：非特殊需求优先使用 **Okabe-Ito**（色盲友好）；打印出版物用 **Ink & Wash**；Nature风格用 **Ocean Dusk** 或 **Nord**。

---

### 图表类型决策指南

在Figure契约阶段，根据数据结构和论证目标选择图表类型：

| 数据结构 | 论证目标 | 推荐图表 | 候补图表 | 不推荐 |
|---------|---------|---------|---------|--------|
| 1个分类 × 1个连续值 | 组间比较 | **柱状图** (bar) | 点图 (strip/dot) | 折线图 |
| 1个连续 × 1个连续 | 相关性/趋势 | **散点图** (scatter) + 回归线 | 六边形分箱 (hexbin) | 柱状图 |
| 1个连续 × 1个连续 × 密度 | 分布密度 | **散点+边缘直方** (scatter + marginals) | 核密度 (kdeplot) | 柱状图 |
| 1个分类 × 多个连续值 | 多指标比较 | **分组柱状图** (grouped bar) | 热图 (heatmap) | 雷达图 |
| 1个时间 × 1个连续 | 时间趋势 | **折线图** (line) + 误差带 | 面积图 (fill_between) | 柱状图 |
| 多个时间序列 | 趋势对比 | **多折线图** (multi-line) | 分面折线图 (faceted line) | 堆叠面积 |
| 2个分类 × 1个连续 | 交互效应 | **热图** (heatmap) 或 **聚类热图** | 分面柱状图 | 3D图 |
| 2个连续 × 1个连续 | 二维场 | **填充等值线** (contourf) | 热图 (imshow) | 3D曲面 |
| 高维 → 2D (PCA/UMAP) | 聚类可视化 | **散点图** (scatter) + 椭圆标注 | 2D直方 | 平行坐标 |
| 分布比较 | 分布形状/异常值 | **箱线图** (boxplot) / **小提琴图** (violin) | 直方图 (hist) | 柱状图 |

#### 快速决策矩阵

```
数据中有分类变量？
├─ 是 → 比较的是均值？→ 柱状图
│       比较的是分布？→ 箱线图/小提琴图
│       比较的是比例？→ 堆叠柱状图
│       比较的是趋势？→ 折线图（分类有序）
└─ 否 → 变量是连续的？
        ├─ 两个连续变量 → 散点图 + 回归
        ├─ 一个时间变量 → 折线图 + 误差带
        └─ 两个以上连续变量 → 热图 / 散点矩阵
```

---

### 风格选择指南

| 场景 | 推荐风格 | 推荐色板 | 原因 |
|------|---------|---------|------|
| Nature/Science主图 | **B — Modern Minimal** | Ocean Dusk 或 Nord | 严谨、干净、高数据-墨水比 |
| 评审答辩PPT | **A — Sketch** | Ink & Wash | 亲和力强、非正式沟通 |
| NeurIPS/ICLR面板 | **C — Illustrated Technical** | Okabe-Ito 或 Nord | 高信息密度、技术感 |
| 会议Keynote/封面 | **D — Accent Bar** | Okabe-Ito | 视觉入口强、冲击力大 |
| 竞赛海报/视频 | **A — Sketch 或 D — Accent Bar** | Ocean Dusk 或 Okabe-Ito | 视觉效果优先，风格醒目 |
| 临床论文 | **B — Modern Minimal** | Ocean Dusk | 优雅克制，适合临床数据 |
| 打印/物理刊物 | **B — Modern Minimal** | Ink & Wash | 灰度打印友好 |
| 附录/补充材料 | **C — Illustrated Technical** | 任意（选信息密度最高的） | 空间紧凑，需高密度 |
| 方法/流程图 | **A — Sketch** | Ink & Wash | 概念化、快速理解 |
| 线上预印本(arXiv) | **B — Modern Minimal** | Nord | 屏幕阅读舒适、低视觉疲劳 |
| 色盲读者为主 | **B 或 C** | **Okabe-Ito**（必须） | 无障碍第一原则 |

---

### 5点检查清单（追加至此技能原有QA清单之后）

- [ ] 风格代号已声明（A/B/C/D），色板已选定，在Figure契约中记录
- [ ] 所选风格的字体、轴粗细、底色与出口目标匹配（期刊 vs 答辩 vs 封面）
- [ ] 色盲可分辨性已检查——非Okabe-Ito色板时确认红绿并非唯一编码
- [ ] 灰度打印可读性已确认（Ink & Wash已天然支持，其他风格需检查hatch/pattern备用）
- [ ] 风格一致——同论文/同竞赛的所有图表使用同一风格+色板组合，不混搭
