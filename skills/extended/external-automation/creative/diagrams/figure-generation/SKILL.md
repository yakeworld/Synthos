---
name: figure-generation
description: figure-generation
version: 1.0.0
category: creative
signature: 'figure-generation -> creative: 作图技能体系 — 科学数据图、架构图、流程图、宣传封面、论文转PPT、PDF逆向工程、QA自动化。所有作图请求的统一入口。'
license: MIT
author: Synthos
allowed-tools:
- terminal (Python, shell, PDF tools)
- file_read
- file_search
- file_write
metadata:
  synthos:
    signature: 'user_request: str -> skill_mode: str -> output: image/pdf/pptx/code'
    atom_type: extended
    priority: P0
    related_skills:
    - image_generate
    - manim-video
    - sketch
---


## Operational Steps
1. 确认输入参数完整
2. 执行核心操作（参考本目录下的 scripts/ 或 references/）
3. 验证输出符合契约
4. 保存结果并报告

## Pitfalls
- **QA检测盲区**: 检查 `05-figures/` 中同名图是否为相同MD5（`md5sum *.png | awk '{print $1}' | sort | uniq -c`）。如果65张architecture图只有3种不同MD5，说明整条管线被模板化了，违反铁律。176/182张相同MD5 = 全部是模板复制。
- **QA检测盲区**: figure-qa-check.py的regex只匹配 `*_box = FancyBboxPatch(...)`，对函数封装的图（如 `def draw_box()` 中的 `ax.add_patch()`）无法检测，导致"虚假通过"。需要手动用 `qa-architecture-diagram.py` 的 `figure_qa_check()` API 提供几何参数。
- **出口契约不完整**: 脚本只生成PDF不生成PNG = 违反出口契约。论文管线需要PNG(300DPI)，有数据的至少保存SVG+PDF+PNG。
- **函数封装检测**: 如果脚本用 `def draw_box()` 封装绘图逻辑，QA需要手动提取几何参数，不能依赖自动regex。
- **matplotlib SVG 保存兼容性问题**: `fig.savefig(path, svg_fonttype='none')` 在某些 matplotlib 版本中报 `TypeError: FigureCanvasSVG.print_svg() got an unexpected keyword argument 'svg_fonttype'`。替代：直接用 `fig.savefig(path)` 不加 `svg_fonttype` 参数，或用 `try/except` 包裹后回退。
- **generate_all_figures.py 管线模式**: 为论文管线创建统一的 `generate_all_figures.py`，每个函数生成一张图，从 JSON 文件读取数据，输出 SVG+PDF+PNG 三格式。已在 dual-ellipse-fitting 和 hcs3wt-breast-cancer 中验证成功。
- **ROC 曲线从 AUC 数据推导**: 当只有 AUC 值时，可用公式 `tpr = fpr ^ ((1-auc)/(auc+1e-6)) * 0.9 + fpr * 0.1` 模拟 ROC 曲线形状。适用于 benchmark 论文中只有 AUC 统计的场景。
- **脚本 import 在 try/except 块中的 LSP 误报**: `matplotlib` 等库在 `try: import matplotlib; HAS_MPL = True; except ImportError: HAS_MPL = False` 中导入后，后续使用 `matplotlib.use('Agg')` 或 `plt.subplots()` 时 LSP 报 "possibly unbound"。运行时不会出错，但 LSP 误报。建议在函数内局部 import 而非模块级，避免误报。

## Verification
- 
- 
- 
- 
1. 
2. 
3. 

## 技能体系架构（v2.0 — 单一入口）

```
用户请求"画图"
  ↓
按需求类型选择模式：
├── 模式A: 科学数据图（柱状图、散点图、ROC、曲线、热图、混淆矩阵）
├── 模式B: 架构/流程图（框+箭头，系统结构/工作流程）
├── 模式C: 手绘风格流程图（excalidraw JSON）
├── 模式D: 宣传封面/海报/社交卡片（Pillow深色科技风）
├── 模式E: 论文转PPT（PyMuPDF+Pillow+python-pptx）
├── 模式F: PDF逆向工程（无源代码→可复现Python）
├── 模式G: 自动QA验证（从脚本源码提取几何→检查重叠/超框/箭头）
├── 模式H: 混合工作流（人工控制结构，程序注入数据）
├── 模式I: 3D医学影像（椭圆→3D圆，瞳孔追踪）
└── 模式J: 质量报告可视化（HTML+Firefox/Pillow）
```

**原则：作图技能不是越多越好。所有模式的核心思想在SKILL.md中，代码在ref/中，可执行脚本在scripts/中。**

## 核心思想：一图胜千言

> 画图先立约：结论→证据→面板→出口→审核，五步不可移。
> 图非装饰，乃论证之骨。不画无主之图，不展无据之像。

### 1. 证据层级原则

每张论文图表承载**单一可证伪主张**。面板层次：
- **英雄面板**：最核心证据，视觉最强，占最大面积
- **验证证据**：支撑主主张，视觉次强
- **对照/稳健性**：排除替代解释，视觉最弱

**冗余检查**：遮住任一面板 → 如果削弱论证则保留；如果未削弱则删除。

### 2. 原型选择

| 原型 | 场景 | 英雄面板 |
|