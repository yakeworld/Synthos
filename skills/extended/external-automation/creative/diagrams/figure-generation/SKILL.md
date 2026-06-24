---

name: figure-generation
description: 科研图表创建：Figure契约方法论——结论Claim→证据层级→面板映射→出口契约→审核。 支持Nature语义色板（蓝主-绿正-红基+中性色），16种排版模式。兼容所有SCI/会议图表场景。
version: 1.5.0
license: MIT
author: Synthos
allowed-tools:
- terminal (Python plotting, shell)
- file_read (data inspection)
- file_search (data location)
- execute (data preprocessing, code execution)
- file_write (figure scripts)
metadata:
  synthos_atom_type: extended
  synthos_version: 1.1.0
  synthos_skill_md_hash: figure-generation-v1.1.0
  synthos_model_tested_on: '2026-05-15T00:00:00Z'
  synthos_data_access_level: verified_only
  synthos_priority: P2
  synthos_author: Synthos
  synthos_absorbed_from: Synthos internal (originally from research-paper-search skill)
  synthos_absorbed_date: '2026-05-15'
  synthos_depends_on: knowledge-acquisition
  synthos:
    author: Synthos
    signature: 'input: claim, evidence_levels -> output: figure_contract, publication_ready_figure'
    related_skills:
    - academic-diagram
    - architecture-diagram
    - comfyui
    - excalidraw
    - ffmpeg-video-audio-sync
    version: 1.1.0
    tags:
    - figure-generation
    - data-visualization
    - scientific-figures
    - nature-style
    - publication-ready


---


## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）




## 原理层·文言

### 图表之道

> 一图胜千言，一计定乾坤。
> 画图先立约：结论→证据→面板→出口→审核，五步不可移。
> Nature规范为本，色盲友好为德，TikZ矢量为体，高清输出为用。
> 统计标注不可省，审稿质疑不可躲。
> 科学之图，诚实为先。不误导、不夸大、不隐瞒。
> **域有其模，模载其法。无证不立，无约不画。**

**核心理念**：图表生成是视觉论证设计。每张图从可证伪的结论Claim开始。不画无主之图，不展无据之像。

## 方法层·白话

**Figure Generation Skill** — 不是画图工具，是**视觉论证设计器**。

## 核心方法论：Figure契约

画任何图之前，先建立契约。Agent原生推理完成，不需要Python脚本。

### 契约模板

```
结论Claim: [一句话可证伪的核心主张，带动词]
图表原型: [quantitative-grid | schematic-led-composite | image-plate+quant | asymmetric-mixed-modality]
目标出口: [Nature | Science | SCI 2-3区 | PPT报告 | 竞赛视频]
最终尺寸: [单栏89mm | 双栏183mm | 自定义]
面板映射:
  a: [面板a解决的问题]
  b: [面板b解决的问题]
  c: [面板c解决的问题]
证据层级:
  主证据: [英雄面板，视觉最强]
  验证证据: [支撑面板，视觉次强]
  对照/稳健性: [辅助面板，视觉最弱]
所需统计: [样本量、误差棒类型、检验方法]
源数据: [CSV路径、列名、行数]
审稿风险: [审稿人可能质疑的三件事]
```

### 原型选择

| 原型 | 使用场景 | 英雄面板 | 支撑面板 |
|------|---------|---------|---------|
| `quantitative-grid` | 数值比较为主 | 可选，一般是主导汇总指标 | 共享轴、对齐刻度、紧凑图例 |
| `schematic-led-composite` | 需先理解流程/机制/装置 | 左或上方的示意图，占40-60%面积 | 2-4个定量验证面板 |
| `image-plate+quant` | 成像/显微/组织学/电泳 | 图像板或代表性图像 | 比例尺、叠加、裁剪、定量 |
| `asymmetric-mixed-modality` | 混合示意图/光栅/热图/定量 | 一个面板跨行/列 | 按证据值排序的小面板 |

### 冗余检查

- [ ] 面板b不是面板a的数据以不同形式重新显示
- [ ] 面板c增加了a和b中没有的维度
- [ ] 每个面板有自己的轴标签词汇（不同的x/y量纲）
- [ ] 遮住任一面板不会削弱论证 → 删除或合并

### 与ARG协同

Figure契约的结论Claim直接来自ARG论证链。
输出接口：接收ARG的 `claim` + `evidence`，输出 `SVG asset` + `figure legend text`。

---

## 执行流程

```
契约确认 → 加载风格模板 → 生成Python脚本 → terminal执行 → QA审核
```

Python代码示例、配色方案、辅助函数 → 详见 `references/python-recipes.md`

### 执行失败回退（Pitfall）

| 场景 | 症状 | 对策 |
|:-----|:-----|:-----|
| matplotlib + NumPy 版本冲突 | `ImportError: numpy.core.multiarray failed to import` 或 `cannot be run in NumPy 2.0` | **立即切换 Pillow 纯代码路径**。pil-image-generation skill 中 `技法#1-7` 可直接绘制雷达图/柱状图/轨迹图。不要死磕 matplotlib。 |
| 服务器无 GUI / 无 headless chrome | HTML→Chromium 路径报 `Chrome exited early` | 跳过 HTML，直接 Pillow。HTML 渲染是最后手段。 |
| matplotlib 可用但渲染差 | 图表模糊、CJK 不可读、色盲不可分辨 | 设置 `svg.fonttype='none'` + Arial/Helvetica + Nature 色板。输出 SVG 做 QA。 |

### 环境依赖检查
### 执行失败回退层级（完整）

```
matplotlib → 版本冲突/缺失 → Pillow 纯代码 → HTML + Firefox → HTML + Chromium → 静态生成
```

| 层级 | 工具 | 触发条件 |
|:-----|:-----|:---------|
| 1 | matplotlib | 服务器环境正常 |
| 2 | Pillow 纯代码 | NumPy 版本冲突 / matplotlib 缺失 / 无 GUI |
| 3 | HTML + Firefox | 复杂排版需求，Chromium snap 不可用时首选 |
| 4 | HTML + Chromium | Firefox 不可用，Chrome snap 可用时 |
| 5 | Pillow + 结构化 | 最简方案，手动布局 |

**Firefox headless 截图法**（2026-06-21 实测，`firefox --headless --screenshot /tmp/out.png URL`）：
- 用 `python3 -c "import http.server,socketserver,threading;...TCPServer(('127.0.0.1',8899)..."` 起本地 HTTP 服务
- Firefox 不依赖 Chrome snap，是 headless Linux 上 HTML→PNG 的最可靠路径
- Firefox `--width` 只控制渲染宽度，`--window-size` 部分版本不生效；默认 1366px 可完整渲染
- 如需精确尺寸（如 1080px），用 Pillow `Image.resize()` 缩放到目标宽度
- 输出为 RGBA，用 `.convert('RGB')` 转 RGB

```python
# 执行前检查渲染路径（按优先级）
import importlib, subprocess
def best_backend():
    try: import matplotlib; has_mpl=True
    except: has_mpl=False
    try: subprocess.run(['firefox','--version'],capture_output=True); has_ff=True
    except: has_ff=False
    try: subprocess.run(['chromium-browser','--version'],capture_output=True); has_ch=True
    except: has_ch=False
    if has_mpl: return 'matplotlib'
    if has_ff: return 'firefox'
    if has_ch: return 'chromium'
    return 'pillow'
```

---

## 色彩体系（速查）

### 语义色板（Nature标准）

```
蓝主 #0F4D92  | 绿正 #8BCF8B  | 红基 #B64342
中性 #767676  | 强调金 #FFD700 | 青 #42949E
```

### 分领域色板

| 领域 | 特征色 |
|------|--------|
| 成像/显微 | 黑底+灰+青+品红 |
| 临床/纵向 | 基线灰→周6橙→周13红→年1蓝 |
| 消融实验 | 同色alpha渐变（1.0→0.2） |

---

## 16种排版模式速查

| # | 模式 | 一句话场景 |
|:-:|:-----|:----------|
| 1 | 超宽多指标 | 3-4指标×多方法 |
| 2 | 专用图例面板 | 图例过大/多面板共享 |
| 3 | 隐藏X轴 | 方法名已在图例中 |
| 4 | 动态Y轴紧缩 | 数据集中在狭窄区间 |
| 5 | Alpha消融 | 同方法消融变体 |
| 6 | Hatch灰度 | 印刷黑白区分 |
| 7 | 语义色映射 | 跨面板颜色一致 |
| 8 | 柱内亮度感知文本 | 深色柱白字/浅色柱黑字 |
| 9 | Fill-between hatch | 面积图灰度安全 |
| 10 | 趋势事件标注 | 时间线上标注事件 |
| 11 | 数据集内分组柱 | 多数据集×多方法 |
| 12 | 示意图主+定量辅 | 机制/流程图带头 |
| 13 | 暗底图像板 | 显微/渲染 |
| 14 | 临床三联画 | 纵向+森林图+汇总 |
| 15 | 非对称英雄面板 | 某面板概念核心 |
| 16 | 填充区域直接标签 | 类别多图例大 |

详情 + 代码 → `references/common-patterns.md`

---

## 出口契约

```python
fig.savefig(f"{filename}.svg", bbox_inches="tight")   # 可编辑矢量（必需）
fig.savefig(f"{filename}.png", dpi=300, ...)           # 位图
fig.savefig(f"{filename}.pdf", bbox_inches="tight")    # PDF
```

字体：font.size=7（期刊密度）/ 24（大面板）, Arial/sans-serif, `svg.fonttype='none'`

---

## 触发条件

加载本技能当：用户要求创建/修改论文图表、"Nature风格"、"SCI图表"、"发表级图表"、"架构图"、"流程图"、"flow diagram"。

**不加载**：EDA探索性图表、交互式图表（Plotly/Altair）、3D/GIS/非科学插图。

---

## 模式三：架构/流程图（schematic-led-composite 的纯图版）

**不包含数据面板，纯框+箭头说明系统结构/流程关系。** 使用 matplotlib patches 绘制。

### 为什么不用 TikZ

| 方案 | 问题 | 结论 |
|:-----|:-----|:------|
| TikZ `node distance` + `below of` | 多层堆叠时间距计算混乱，混合绝对坐标与相对定位导致上下重叠 | ❌ PIMA Figure 1 两次失败 |
| TikZ 缩放 `scale=0.95, transform shape` | 缩放同时压缩文字，反而加剧重叠 | ❌ 不治本 |
| **matplotlib patches**（`FancyBboxPatch` + `FancyArrowPatch`） | 像素级精确控制，坐标全由变量计算 | ✅ 一次成功 |

### 程序化布局方法论

**不要手写坐标**。定义间距变量，从底部向上计算每个箱体的 y 位置：

```python
# 统一设计系统变量
SINGLE_H = 0.50    # 单行文字框高 (fontsize 7 → 0.20" text + 0.15" pad×2)
DOUBLE_H = 0.70    # 双行文字框高 (核心/输出/消融/注册箱)
BOX_W    = 3.0     # 侧栏框宽 (≥3.0, 否则"Engineering Execution Strand"碰边)
CORE_W   = 4.8     # 核心框宽
BOT_W    = 5.2     # 底部链框宽
PAD_BOX  = 0.12    # FancyBbox 内边距 (所有框统一)

GAP_S    = 0.20    # 同区内框间距 (子箱之间/底部链箱之间)
GAP_M    = 0.55    # 区间隔 (侧栏↔核心↔输出)
GAP_T    = 0.35    # 标题→内容间距
PAD_BOT  = 0.50    # 底部留白

# 从底部向上计算
reg_y = PAD_BOT
ab_y  = reg_y + DOUBLE_H + GAP_S
out_y = ab_y  + DOUBLE_H + GAP_S
core_y = out_y + DOUBLE_H + GAP_M
c4_y  = core_y + DOUBLE_H + GAP_M
c3_y  = c4_y   + SINGLE_H + GAP_S
c2_y  = c3_y   + SINGLE_H + GAP_S
c1_y  = c2_y   + SINGLE_H + GAP_S
strand_title_y = c1_y + SINGLE_H + GAP_S
title_y = strand_title_y + SINGLE_H + GAP_T
```

这样做的好处：
- 改一个间距变量，**全部重算**，不需要逐行调坐标
- 底部永远对齐，顶部自动确定画布尺寸
- 可预先检查 `fig_needed > fig_actual` 防溢出

### 箭头设计规范 (架构图专用)

箭头必须**汇聚到目标框的顶边内侧**，不能悬在框外：

```python
# ❌ 错误 — 箭头终点在框外
arrow(lx, c4_y, lx, core_top)  # lx=1.8, 核心框左缘=2.6 → 箭头在框外

# ✅ 正确 — 汇聚到顶边内侧
cx0 = xc - CORE_W/2          # 核心框左缘 (必须定义于箭头之前)
core_top_l = cx0 + CORE_W*0.25   # 顶左1/4
core_top_r = cx0 + CORE_W*0.75   # 顶右3/4
arrow(lx, c4_y + SINGLE_H/2, core_top_l, core_y + DOUBLE_H, rad=-0.20)
arrow(rx, c4_y + SINGLE_H/2, core_top_r, core_y + DOUBLE_H, rad=0.20)
```

**代码顺序陷阱**: `cx0` 必须在箭头代码之前定义，否则变量未定义错误。

### 实现模板

详见 `references/architecture-flow-diagrams.md`——包含完整可运行的 Figure 1 代码模板。

### 色板扩展（架构图专用）

| 元素 | 颜色 | 语义 |
|:-----|:-----|:------|
| Clinical/方法论 | `#8BCF8B`（绿） 或 `#D0E8D0` 浅底 | 正确/正向 |
| Engineering/工程 | `#E8954A`（橙） 或 `#F5E0C0` 浅底 | 执行/操作 |
| 核心/协议 | `#7B5EA7`（紫） | 创新/核心贡献 |
| 输出/结果 | `#8BCF8B` 深边框 | 验证过的输出 |
| 对照/基线 | `#B64342`（红） 或 `#F0C8C8` 浅底 | 风险/基线 |
| 中性/参考 | `#999999`（灰） | 参考/随机基线 |

### 输出规范

```python
# 必须使用此保存方式——SVG可编辑+PDF出版级
fig.savefig(f"{name}.svg", bbox_inches='tight', pad_inches=0.1)  # 矢量可编辑
fig.savefig(f"{name}.pdf", bbox_inches='tight', pad_inches=0.1)  # 出版
```

### 用户偏好: 长文本框内居中

当架构图/流程图的 TikZ 版本出现重叠问题时：
1. **不要继续调试TikZ**（`node distance` 越调越乱）
2. 直接切换到 `matplotlib patches` 程序化布局
3. 使用统一设计系统（SINGLE_H/DOUBLE_H + GAP_S/GAP_M/GAP_T）
4. 所有 FancyBboxPatch 用同一 `pad` 值（推荐 0.12），确保框形态一致
5. 长标题（如 "Engineering Execution Strand"）用字≤7 + 加宽边框（BOX_W ≥ 3.0）避免文字碰边缘
6. 把生成脚本保存到 `03-code/` 目录作为可重复 artifact
7. 用 `\includegraphics{path}` 替换 LaTeX 中的内联 TikZ

### 🔴 强制措施: 生成前 QA 验证 (2026-06-24 新增)

**背景**: 本技能前几次渲染的架构图存在箭头终点在目标框外、文字超框等问题，用户发现后要求"既然能计算出问题，为什么写代码的过程没有监督"。

**规则**: 每次 matplotlib patches 绘图脚本必须在 `plt.subplots()` 之前嵌入 QA 验证。

**QAReport 模板** (放入脚本顶部，渲染逻辑之前):

```python
def text_width_inches(text, fontsize_pt):
    """估计文字渲染宽度 (保守: avg_char = fontsize * 0.60 pt)"""
    return len(text) * fontsize_pt * 0.60 / 72.0

class QAReport:
    def __init__(self):
        self.issues = []
    def check_text_fits(self, label, text, fontsize, box_w, box_h, pad):
        tw = text_width_inches(text, fontsize)
        if tw > box_w - 2*pad:
            self.issues.append(f"[{label}] 文字超宽: '{text[:30]}' ({tw:.2f}in) > {box_w-2*pad:.2f}in")
        if fontsize/72.0 > box_h - 2*pad:
            self.issues.append(f"[{label}] 文字超高: {fontsize}pt > {box_h-2*pad:.2f}in")
    def check_arrow_inside(self, label, x2, y2, target_name, tx, ty, tw, th):
        if not (tx <= x2 <= tx+tw and ty <= y2 <= ty+th):
            self.issues.append(f"[{label}] 箭头终点({x2:.1f},{y2:.1f}) 在 '{target_name}' 框外")
    def assert_clean(self):
        if self.issues:
            for i in self.issues: print(f"  ❌ {i}")
            sys.exit(1)
        print("  [QA] All checks passed ✓")
```

**必须检查的项**:
- 每个 `draw_box` 调用配一个 `check_text_fits` (含长标题如"Engineering Execution Strand")
- 每个 `draw_arrow` 调用配一个 `check_arrow_inside` (终点必须在目标框**内部**，不能只接近边框)
- 侧栏→核心箭头必须汇聚到核心顶边**内侧** (x = cx0 + CORE_W*0.25/0.75)，不能悬在外围
- 底部链箭头终点必须在目标箱体范围内 (bx0 ≤ x ≤ bx0+BOT_W)
- QA 不通过 → `sys.exit(1)` → 无输出 → 修复后重新生成

### 实战教训

| 问题 | 检查方式 | 本会话实例 |
|:-----|:---------|:----------|
| 箭头终点落在目标框外 | `check_arrow_inside()` | 左栏箭头终点 x=1.8，核心框左缘 x=2.6 |
| 长标题文字碰框边 | `check_text_fits()` | "Engineering Execution Strand" 30字符在 fs=7.5, 2.8in框内溢出 |
| 底部链文字超出框高度 | `check_text_fits()` 检查行高 | 双行框第二行过长 |
| 画布高度不足 | 布局计算后 `fig_needed > fig_actual` | 需从底部向上计算并比较 |
| 侧栏→核心箭头汇聚到框外 | `check_arrow_inside()` 终点坐标 | 垂直向下到 lx=1.8, rx=8.2，核心框始于2.6止于7.4 |

---

## 验证清单

### 执行前
- [ ] 结论Claim已明确，每个面板映射到唯一证据
- [ ] 原型已声明
- [ ] 面板层级已确定（英雄/验证/对照）
- [ ] 最终尺寸符合目标出口
- [ ] 源数据已确认
- [ ] 色盲可分辨性已检查
- [ ] 灰度打印可读性已确认

### 执行后
- [ ] SVG文本可编辑（`svg.fonttype='none'`）
- [ ] 无彩虹色板；红绿不是唯一编码
- [ ] 误差棒和统计检验已正确显示
- [ ] 可比较面板间的轴范围可比
- [ ] 已保存至 `./figures/` 目录

---

## 参考文献

| 文件 | 内容 |
|------|------|
| references/figure-contract.md | 详细Figure契约模板和证据层级检查 |
| references/python-recipes.md | Python初始化、保存函数、多面板布局、配色代码（原嵌入代码已迁移至此） |
| references/style-library.md | Visual Style Library A-D + 完整色板（原嵌入代码已迁移至此） |
| references/common-patterns.md | 16种排版模式的完整代码示例 |
| references/design-theory.md | 字体、色彩理论、排版原理 |
| references/qa-contract.md | 提交前完整QA审核清单 |
| references/matplotlib-fallback.md | matplotlib 不可用时的 Pillow 纯代码回退路径（雷达图/进度条/轨迹图原语） |
| references/sci-figure-recipes.md | 实战代码示例：ROC曲线、SHAP重要性柱状图、消融对比图（PIMA案例，2026-06-24） |
| references/architecture-flow-diagrams.md | 架构/流程图程序化布局模板（matplotlib patches，2026-06-24新增） |
| references/quality-report-render.md | 质检报告→视觉图的三模式（HTML+Firefox/Pillow/Markdown），含深色科技风设计模板 |

## 脚本

| 文件 | 内容 |
|------|------|
| scripts/architecture_fig_template.py | 可直接运行的架构/流程图模板（2026-06-24新增） |

---

## IO契约

**输入**：`claim` + `data`(CSV路径) + `target`(出口) + `panel_count`

**输出**：`SVG asset`路径 + `figure_legend`文本 + `pipeline_meta`

**副作用**：在 `./figures/` 下创建SVG/PDF/TIFF文件
