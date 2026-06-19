---

name: figure-generation
description: 科研图表创建：Figure契约方法论——结论Claim→证据层级→面板映射→出口契约→审核。 支持Nature语义色板（蓝主-绿正-红基+中性色），16种排版模式。兼容所有SCI/会议图表场景。
version: 1.0.0
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

加载本技能当：用户要求创建/修改论文图表、"Nature风格"、"SCI图表"、"发表级图表"。

**不加载**：EDA探索性图表、交互式图表（Plotly/Altair）、3D/GIS/非科学插图。

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

---

## IO契约

**输入**：`claim` + `data`(CSV路径) + `target`(出口) + `panel_count`

**输出**：`SVG asset`路径 + `figure_legend`文本 + `pipeline_meta`

**副作用**：在 `./figures/` 下创建SVG/PDF/TIFF文件
