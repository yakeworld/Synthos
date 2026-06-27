---
name: figure-generation
description: 作图技能体系 — 科学数据图、架构图、流程图、宣传封面、论文转PPT、PDF逆向工程、QA自动化。所有作图请求的统一入口。
version: 2.2.0
license: MIT
author: Synthos
allowed-tools:
- terminal (Python, shell, PDF tools)
- file_read
- file_search
- file_write
metadata:
  synthos:
    signature: "user_request: str -> skill_mode: str -> output: image/pdf/pptx/code"
    atom_type: extended
    priority: P0
    related_skills:
    - image_generate
    - manim-video
    - sketch
---

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

**原则：作图技能不是越多越好。所有模式的核心思想在SKILL.md中，代码在references/中，可执行脚本在scripts/中。**

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
|------|------|---------|
| `quantitative-grid` | 数值比较为主 | 汇总指标图 |
| `schematic-led-composite` | 需理解流程/机制 | 左/上方的示意图 |
| `image-plate+quant` | 成像/显微/组织学 | 图像板+定量 |
| `asymmetric-mixed-modality` | 混合示意图/光栅/热图 | 跨行/列面板 |

### 3. 布局自适应原则

**不要套模板。图决定布局。**

| 图特征 | 布局 | 图占比 |
|--------|------|:------:|
| 宽幅/复杂 | 全宽或上下堆叠 | 70-100% |
| 高窄 | 左图右文轨 | 65-75% |
| 密集多面板 | 裁剪关键面板 | 80-100% |
| 单面板+标注 | 非对称 70/30 | 70% |
| 表格/数据 | 全宽表格 | 100% |

**核心：50/50等分是例外，非默认。结果帧必须有一方明显主导。**

## 设计规则（速查）

### 色彩语义

| 语义 | 色值 | 用途 |
|------|------|------|
| 正确/正向 | `#8BCF8B` | 成功、阳性、临床有效 |
| 风险/基线 | `#B64342` | 对照、阴性、风险 |
| 核心/创新 | `#7B5EA7` | 核心贡献、协议 |
| 执行/操作 | `#E8954A` | 工程、操作步骤 |
| 中性参考 | `#999999` | 随机、参考 |
| 失败/阴性 | `#D0C0C0` | 清除阴性 |

**色盲安全**：≥3色时必须同时使用颜色+形状/线型双编码。红绿不能是唯一区分。

### 排版规则

| 要素 | 规则 |
|------|------|
| 字体 | Arial/sans-serif，`svg.fonttype='none'` |
| 标题字号 | 论文7pt / 大图24pt / 封面48-60px |
| 正文字号 | 论文7pt / 大图10pt / 封面20-24px |
| 留白 | 卡片内边距≥20px，元素间距≥16px |
| CJK双描 | 深色底上：`draw.text(x,y)`两次（偏移1px） |

### 架构图箭头规则

- 箭头终点必须在目标框AABB内，不是"接近"
- 从上方进入 → 终点 y = 框顶 y
- 从下方进入 → 终点 y = 框底 y
- 从左/右进入 → 终点 x = 框左/右 x
- 多箭头同框 → 终点x错开 ≥20px
- 长文本框：字数≤7或加宽边框（BOX_W≥3.0）

### 数据图规则

- ≥3条曲线 → 必须line_style + marker双编码
- 表格 → 永远在axes外部（y < -0.1），不在plot area内
- 水平条形图 → 颜色编码必须有legend；x-limit = max * 1.28
- 网格图低值 → 标签额外offset（低值<0.7: 0.008, 高值: 0.003）
- ≥3条曲线 → 必须line_style + marker双编码

### Pillow封面规则

- 背景：#0F172A（深蓝黑）
- 主蓝：#3B82F6，强调金：#F59E0B
- 成功：(0,221,170)，警告：(255,169,77)，错误：(255,107,107)
- 字体分级：标题36-44pt，核心指标32-40pt，正文20-24pt，小字14-18px
- 尺寸：正方形1080×1080（单图），竖版1080×1920（轮播）

## 方法层：16种排版模式

| # | 模式 | 场景 | 代码位置 |
|---|------|------|---------|
| 1 | 超宽多指标 | 3-4指标×多方法 | `references/common-patterns.md` |
| 2 | 专用图例面板 | 图例过大/多面板共享 | `references/common-patterns.md` |
| 3 | 隐藏X轴 | 方法名已在图例中 | `references/common-patterns.md` |
| 4 | 动态Y轴紧缩 | 数据集中在狭窄区间 | `references/common-patterns.md` |
| 5 | Alpha消融 | 同方法消融变体 | `references/common-patterns.md` |
| 6 | Hatch灰度 | 印刷黑白区分 | `references/common-patterns.md` |
| 7 | 语义色映射 | 跨面板颜色一致 | `references/common-patterns.md` |
| 8 | 柱内亮度感知文本 | 深色柱白字/浅色柱黑字 | `references/common-patterns.md` |
| 9 | Fill-between hatch | 面积图灰度安全 | `references/common-patterns.md` |
| 10 | 趋势事件标注 | 时间线上标注事件 | `references/common-patterns.md` |
| 11 | 数据集内分组柱 | 多数据集×多方法 | `references/common-patterns.md` |
| 12 | 示意图主+定量辅 | 机制/流程图带头 | `references/common-patterns.md` |
| 13 | 暗底图像板 | 显微/渲染 | `references/common-patterns.md` |
| 14 | 临床三联画 | 纵向+森林图+汇总 | `references/common-patterns.md` |
| 15 | 非对称英雄面板 | 某面板概念核心 | `references/common-patterns.md` |
| 16 | 填充区域直接标签 | 类别多图例大 | `references/common-patterns.md` |

## 核心工作流

```
用户请求 → 选择模式 → 建立契约 → 验证数据 → 生成代码 → QA验证 → 执行 → 输出
                              ↑                          ↑
                         数据错误→sys.exit(1)      检查不通过→sys.exit(1)
```

1. **契约确认**：结论Claim、图表原型、目标出口、面板映射、证据层级
2. **数据验证**：完整、正确、样本一致
3. **生成脚本**：Python代码（matplotlib/Pillow/SVG/excalidraw/Python-pptx）
4. **QA验证**：重叠检测、超框检测、箭头终点、色盲安全、色彩对比
5. **执行输出**：PNG (300DPI) + PDF/SVG + figure legend
6. **发送确认**：向用户发送输出，附带简要说明

## 各模式详细说明

### 模式A: 科学数据图（matplotlib）

标准科研图表：柱状图、散点图、ROC、AUC、SHAP、消融图、混淆矩阵、生存曲线。

- 见 `references/python-recipes.md` — Python代码模板
- 见 `references/quantitative-data-qa-traps.md` — 定量数据QA规则
- 见 `references/sci-figure-recipes.md` — 实战代码示例
- 见 `references/global-palette.md` — 色板常量
- 见 `references/pillow-primitives.md` — Pillow回退原语

### 模式B: 架构/流程图（matplotlib patches）

框+箭头：系统结构、工作流程、技术路线、实验设计。

- 程序化布局：SINGLE_H/DOUBLE_H + GAP_S/GAP_M/GAP_T，底部对齐向上计算
- 箭头汇聚到目标框顶边内侧（x = cx0 + CORE_W*0.25/0.75）
- 所有箭头必须严格水平或垂直，不可有斜线
- 箭头起点在源框边缘，终点在目标框边缘（不穿入）
- 框间重叠检测 margin=5pt，所有框两两检查
- 见 `references/architecture-flow-diagrams.md` — 完整架构图库
- 见 `references/arrow-endpoint-qa.md` — 箭头QA规则
- 见 `references/hcs3wt-figure1-case-study.md` — 实战案例
- 见 `03-code/generate_fig1_system_architecture_v2.py` — HCS-3WT Figure 1 完整重写示例（从零开始，QA前置，所有坐标从常量计算）

### 模式C: 手绘风格流程图（excalidraw）

快速原型、白板风格、中文医疗提案路线图。

- 输出：.excalidraw JSON文件，直接拖到 excalidraw.com 打开
- 元素：rectangle/ellipse/diamond + text + arrow
- 容器绑定：shape的`boundElements`指向text，text的`containerId`指回shape
- 字号：最小16（正文）、20（标题）、14（次要）
- 见 `references/excalidraw/` — 完整格式参考和示例
- 脚本：`references/excalidraw/scripts/upload.py` — 上传获取分享链接

### 模式D: 宣传封面/海报/社交卡片（Pillow）

深色科技风封面、数据卡片、小红书推广图、竞赛海报。

- 背景#0F172A，白字，蓝金点缀
- 双描CJK：`draw.text(x,y)`两次（偏移1px）
- 避免emoji，用文字替代
- 渐变背景：`ImageDraw.rectangle + for y in range(h): fill(y)`
- 见 `references/pil-image/scripts/` — 可执行封面生成脚本
- 见 `references/pil-image/references/` — 设计规范和案例

### 模式E: 论文转PPT（PyMuPDF+Pillow+python-pptx）

从PDF提取元数据→分类定势→构建计划→选图为证→生成PPTX。

- 流程：PDF提取 → 论文分类 → 选图 → 裁剪 → 生成16:9 PPTX
- 论文类型→呈现逻辑：
  - 发现/机制 → Question-to-Evidence
  - 方法/AI → Problem-to-Solution
  - 临床/人群 → Design-to-Inference
- 12-16帧，每帧一义，结论式标题
- 见 `references/paper2ppt/` — 测试用例和流程参考
- 输出：`final_presentation_cn.pptx` + `qa_report.md` + `assets/figures/`

### 模式F: PDF逆向工程

PDF中无源代码的图 → pdftotext提取坐标 → 重建Python脚本。

- `pdftotext -bbox-layout PDF` 提取每个字的精确坐标（PDF点，1/72英寸）
- HTML结构：`<doc>→<page>→<flow>→<block>→<line>→<word>`
- 用坐标作为ground truth重建布局
- **陷阱**：先检查PDF元数据（Producer=GIMP说明不是matplotlib）
- **铁律**：先检查 `/media/yakeworld/sda2/academic_writer/` 是否有原始脚本
- 见 `references/pdf-to-reproducible-code.md` — 完整方法论

### 模式G: 自动QA验证

从绘图脚本源码提取几何元素 → 运行检查 → 输出PASS/FAIL。

**6项检查**：
1. 文字不超框 — `get_text_extent()` 精确测量
2. 箭头终点在目标框AABB内
3. 箭头起点在源框AABB内
4. 箭头互不交叉
5. 所有框无重叠（margin=5pt）
6. 元素不越画布边界

**铁律**: QA不通过 → sys.exit(1) → 无输出 → 修复后重新生成。不通过不能发图给用户。

### QA 陷阱

#### bbox_inches='tight' 导致逻辑坐标与渲染边界不匹配

`qa-architecture-diagram.py` 检查的是**逻辑坐标**（fig.transFigure），但 matplotlib 的 `bbox_inches='tight'` 会重新裁剪画布边界。QA 代码可能在逻辑坐标系中标记"超框"，实际渲染的 PNG/PDF 中文字/框是可见的。

**处理方式**：QA 检查框重叠、箭头终点、文字内容——这些是绝对正确的。边界检查（元素是否超出画布）——QA 标记失败时，用 `bbox_inches='tight'` 重新保存，如果导出后文字/框可见，则忽略该 QA 警告。

#### 自动提取工具的局限性

`figure-qa-check.py`（自动提取）仅支持 `FancyBboxPatch`、`ax.text()`、`FancyArrowPatch`。不支持 `Rectangle`/`Circle`/`plt.gca().add_patch()`/`annotate()` 等。如果脚本使用这些方式，QA 需要手动用 `qa-architecture-diagram.py` 的 `figure_qa_check()` API 自行提供几何参数。

- 见 `scripts/qa-architecture-diagram.py` — QA核心（`figure_qa_check()`）
| references/test-results-2026-06-27.md | QA与完整功能测试结果记录 |
| references/breast-cancer-figure-audit-case.md | 乳腺癌论文作图审计实战案例（6张图、7步审计管线、3个bug修复） |
| references/qa-contract.md | 提交前完整QA审核清单 |
- 见 `references/static-vs-runtime-qa-validation.md` — 静态vs运行时验证等价性
- 见 `references/qa-automation/references/` — 历史调试记录

**铁律**：QA不通过 → sys.exit(1) → 无输出 → 修复后重新生成。不通过不能发图给用户。

### 模式H: 混合工作流

结构由人工控制（draw.io），数据由程序注入（Python）。

- 适用于：架构/流程图/系统结构图（框+箭头，数值文本随数据变化）
- 不适用：定量数据图（柱状图、散点图等）
- 数据注入脚本必须保证布局不变
- 见 `references/hybrid-figure-workflow.md` — 完整示例
- 见 `references/hcs3wt-figure1-case-study.md` — 实战案例

### 模式I: 3D医学影像

椭圆逆投影为3D空间圆 — 瞳孔追踪中椭圆→3D圆通过解剖约束。

- R=2r, d=√3r
- 法向量参数化、光轴平面
- 见 `3d-curve-fitting-figures/` — 完整3D医学影像子模块

### 模式J: 质量报告可视化

质检报告→视觉图 — HTML+Firefox/Pillow三模式。

- 见 `feishu-file-send/references/pdf-chinese-rendering.md` — PDF 中文渲染修复（pandoc + xelatex + ctex header）
- 见 `feishu-image-send/references/pdf-image-extraction.md` — PDF 图片提取与发送（无脚本场景）

### 执行失败回退层级

```
matplotlib → Pillow纯代码 → HTML+Firefox → Pillow+结构化
```

| 层级 | 工具 | 触发条件 |
|------|------|---------|
| 1 | matplotlib | 服务器环境正常 |
| 2 | Pillow纯代码 | NumPy版本冲突 / matplotlib缺失 / 无GUI |
| 3 | HTML+Firefox | 复杂排版需求 |
| 4 | Pillow结构化 | 最简方案 |

## 出口契约

```python
# 必须保存为：
fig.savefig(f"{name}.svg", bbox_inches='tight', pad_inches=0.1)  # 矢量可编辑
fig.savefig(f"{name}.png", dpi=300, ...)                          # 位图 300 DPI
fig.savefig(f"{name}.pdf", bbox_inches='tight', pad_inches=0.1)  # 出版级PDF
```

## 论文作图铁律

1. **05-figures下每张图必须有对应生成脚本**（03-code/下的.py）
2. **脚本必须可独立运行**：`python script.py` → 输出PNG + PDF
3. **没有脚本的PDF** → P0严重问题 → 逆向工程或从notebook提取
4. **QA必须运行** — 写了但不执行 = 白写
5. **修改重叠 ≤ 5行** — 超过说明在重构，破坏原始图
6. **修改前先还原原始图** — 不可信"记忆中的代码"
7. **用户反馈当金律** — 不争论、不解释、直接修

## 验证清单

### 执行前
- [ ] 结论Claim已明确，每个面板映射到唯一证据
- [ ] 原型已声明
- [ ] 面板层级已确定（英雄/验证/对照）
- [ ] 最终尺寸符合目标出口
- [ ] 源数据已确认完整性和正确性
- [ ] 色盲可分辨性已检查（≥3色时）
- [ ] 灰度打印可读性已确认

### 执行后
- [ ] SVG文本可编辑（`svg.fonttype='none'`）
- [ ] 无彩虹色板；红绿不是唯一编码
- [ ] 误差棒和统计检验已正确显示
- [ ] 可比较面板间的轴范围可比
- [ ] 已保存至目标目录（PNG+PDF/SVG）
- [ ] QA检查已通过（架构图/数据图）

## 铁律：脚本原理绑定

所有 scripts/ 和 references/ 中的 Python 脚本必须在头部注释包含 `SKILL.md 原理绑定` 块，声明它遵循哪些模式/规则/铁律。

双向验证（合并后必须检查）：
- SKILL.md 引用的脚本必须存在
- 脚本声明的原理必须在 SKILL.md 中找到
- 缺失原理绑定的脚本视为不完整

详见 `skill-consolidation` 技能的"SKILL.md ↔ 脚本 思想一致性"章节。

## 铁律：数据诚信

凡数必源——每个数值必须可追溯至单一数据源文件（JSON/CSV/实验结果）。

**硬编码检测规则**（由 `scripts/figure-audit.py` 自动执行）:
- ❌ 数值硬编码在 Python 代码中 → 错误（P0）
  - 特征重要性直接写入代码 `FEATURE_IMPORTANCE = [('worst_radius', 0.285), ...]`
  - 模型性能字典直接写入代码 `models_data = {'LR': {'auc': 0.9897, ...}}`
  - 混淆矩阵数值直接计算而非从实验结果读取
- ✅ 从 JSON/CSV/实验结果文件读取 → 正确
  - `json.load('experiment_results.json')`
  - `pd.read_csv('results.csv')`
  - 任何 `json.load`/`json.loads`/`pd.read_*`/`csv.*`/`np.load`
- ⚠️ 无明确数据源但含 `import` 和 `data` 关键词 → 需人工审查

**修复路径**：
1. 定位硬编码数据在脚本中的位置
2. 找到对应的实验输出文件（通常为 `experiment_results.json` 或 `fold_data.json`）
3. 修改脚本，将硬编码改为从文件读取
4. 运行脚本验证输出与之前一致

## 铁律：脚本可运行

每个生成脚本 `python script.py` 必须无错误地执行并输出图片。
脚本失败（KeyError, FileNotFoundError, AttributeError 等）属于 P0 缺陷。

常见失败原因：
- 数据键名不匹配（`results['n_folds']` vs `results['n_splits']`）
- 相对路径错误（`.json` 文件找不到，应使用 `os.path.dirname(os.path.abspath(__file__))`）
- matplotlib API 版本差异（`fig.inset_axes()` 在旧版 matplotlib 不存在，改用 `fig.add_axes()`）

## 参考文件索引
| 文件 | 内容 |
|------|------|
| **原理/方法** | |
| references/global-palette.md | 全局色板常量 — 5个色板+语义规则+字体常量 |
| references/pillow-primitives.md | 统一 Pillow 原语（7个原语：雷达图/进度条/轨迹图/箭头/文本/面板标签/热图） |
| references/python-recipes.md | Python代码模板：初始化、保存、多面板布局、配色 |
| references/style-library.md | Visual Style Library A-D |
| references/design-theory.md | 字体、色彩理论、排版原理 |
| references/common-patterns.md | 16种排版模式完整代码 |
| references/test-results-2026-06-27.md | QA与完整功能测试结果记录 |
| references/breast-cancer-figure-audit-case.md | 乳腺癌论文作图审计实战案例（6张图、7步审计管线、3个bug修复） |
| references/qa-contract.md | 提交前完整QA审核清单 |
| **PDF中文渲染** | |
| references/pdf-chinese-encoding.md | pandoc + xelatex + ctex header 生成中文PDF（CJK字体、编码、错误处理） |
- 见 `references/figure-audit-runbook.md` — 论文作图完整性审计管线（6步）
- 见 `references/pupil-shape-literature-search.md` — 文献检索方法（PubMed API，本地 session 无 API 密钥）
- 见 `feishu-file-send/references/pdf-chinese-rendering.md` — PDF 中文渲染修复（pandoc + xelatex + ctex header）
| **模式代码** | |
| references/architecture-flow-diagrams.md | 架构/流程图程序化布局模板 |
| references/hybrid-figure-workflow.md | 混合工作流模式（架构→数据分离） |
| references/hcs3wt-figure1-case-study.md | 文字/箭头重叠检测实战 |
| references/quantitative-data-qa-traps.md | 定量数据图视觉QA规则（ROC/混淆矩阵/条形图/消融/趋势图） |
| references/sci-figure-recipes.md | 实战代码：ROC曲线、SHAP、消融对比图 |
| references/arrow-endpoint-qa.md | 箭头终点QA模式 |
| references/matplotlib-fallback.md | matplotlib不可用时的Pillow回退 |
| references/quality-report-render.md | 质检报告→视觉图三模式 |
| references/figure-audit-checklist.md | 论文作图完整性检查清单 |
| references/visual-qa-large-image-trap.md | 大图片视觉检查陷阱（>2000px） |
| references/output-path-trap.md | 图生成输出路径陷阱（03-code vs 05-figures） |
| references/nature-2026-observations.md | Nature 2026观察记录 |
| **Excalidraw** | |
| references/excalidraw/references/colors.md | 颜色对照表 |
| references/excalidraw/references/dark-mode.md | 深色模式指南 |
| references/excalidraw/references/examples.md | 完整Excalidraw元素示例 |
| references/excalidraw/references/pd_risk_roadmap.excalidraw | 示例文件（风险路线图） |
| references/excalidraw/scripts/upload.py | 上传Excalidraw获取分享链接 |
| **Pillow封面** | |
| references/pil-image/scripts/generate_cover.py | 标准封面图生成 |
| references/pil-image/scripts/generate_competition_cover.py | 竞赛封面生成 |
| references/pil-image/scripts/generate_xiaohongshu_cards.py | 小红书推广卡片 |
| references/pil-image/scripts/radar-chart.py | 雷达图生成（CLI） |
| references/pil-image/references/xiaohongshu-card-patterns.md | 小红书卡片设计模式 |
| references/pil-image/references/competition-cover-workflow.md | 竞赛封面工作流 |
| references/pil-image/references/competition-ppt-design-language.md | 竞赛PPT设计语言 |
| references/pil-image/references/github-banner-style.md | GitHub Banner样式 |
| references/pil-image/references/cjk-font-paths.md | CJK字体路径 |
| references/pil-image/references/pil-color-format.md | Pillow颜色格式 |
| references/pil-image/references/svg-png-conversion.md | SVG→PNG转换 |
| references/pil-image/references/user-ppt-cover-references.md | PPT封面参考 |
| **PDF逆向** | |
| references/pdf-to-reproducible-code.md | PDF逆向工程方法论 |
| **论文转PPT** | |
| references/paper2ppt/golden/cases/ | 论文转PPT测试用例（3个） |
| references/paper2ppt/golden/expected/ | 论文转PPT预期输出 |
| **QA自动化** | |
| scripts/qa-architecture-diagram.py | QA核心：figure_qa_check() — 6项检查 |
| scripts/figure-qa-check.py | 从脚本源代码自动提取几何元素并运行QA |
| scripts/fig-generation-qa.py | 静态QA审计管线（正则解析，无需运行时） |
| references/test-results-2026-06-27.md | QA与完整功能测试结果记录 |
| references/breast-cancer-figure-audit-case.md | 乳腺癌论文作图审计实战案例（6张图、7步审计管线、3个bug修复） |
| references/qa-contract.md | 提交前完整QA审核清单 |
| references/static-vs-runtime-qa-validation.md | 静态vs运行时QA验证等价性 |
| references/test-results-2026-06-27.md | QA与完整功能测试结果记录 |
| references/breast-cancer-figure-audit-case.md | 乳腺癌论文作图审计实战案例（6张图、7步审计管线、3个bug修复） |
| references/qa-contract.md | 提交前完整QA审核清单 |
| 3d-curve-fitting-figures/SKILL.md | 3D医学影像：椭圆→3D圆逆投影 |
| references/cross-repo-code-recovery.md | Cross-repo代码恢复：academic_writer→Synthos |
| references/v1.6-changelog.md | v1.6变更日志 |
| references/fig1-qa-report.md | Figure 1 QA报告 |

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。