---
name: nature-paper2ppt
description: "Nature-style Chinese PPTX from academic papers — argument-driven slide generation with figure-first layout optimization. Extracts paper argument, selects evidence figures, writes Chinese slide content + speaker notes, builds real .pptx deck (python-pptx). Cross-platform Python stack (PyMuPDF, Pillow, python-pptx)."
version: 1.0.0
author: Synthos + GARCH-QUANT (absorbed)
license: MIT
allowed-tools: shell Read Write file_search
signature: "source: str (PDF|text|notes) -> presentation: PPTX, qa_report: MD, figure_assets: list[Image]"
metadata:
  synthos_atom_type: "extended"
  synthos_version: "1.0.0"
  synthos_skill_md_hash: "da875dcf6601e2738ebd94a85bc8a0d9"
  synthos_data_access_level: "verified_only"
  absorbed_from: "https://github.com/GARCH-QUANT/garch-nature-paper2ppt"
  absorption_date: "2026-05-21"
  absorption_notes: "Full absorption of Nature Paper2PPT skill. Key innovation: figure-first layout optimization — asymmetric slide composition, evidence hierarchy, Nature-style page design. Python cross-platform stack (PyMuPDF/Pillow/python-pptx)."
---

# Nature Paper2PPT — 科学论文转Nature风格PPT

## 原理层·文言

### 转化之道

> 论文千言，不过一图。PPT者，图为首，文为佐，心法皆备矣。
> 引论以明其问，证据以立其说，限界以知其不足。
> 先分类而后定势：Claim-First、Question-to-Evidence、Problem-to-Solution等，五势各异。
> 图非装饰，乃论证之骨。布局随图而定，不套模板，不强对称。
> 总十二至十六帧，每帧一义，义尽而止。
> 宁缺毋滥，宁简勿繁。

**核心理念**：论文演示的核心是**视觉论证**——每张幻灯片只讲一个观点，用图做主角，文字做配角。布局随图而变（70/30、全宽、上下堆叠），不从固定模板。图文优化的精华在于"图优先，文辅助，不对称是常态"。

## 方法层·白话

### 核心流程图

```
论文/PDF/文本 → Step 1 提取元数据 → Step 2 分类定势 → Step 3 构建计划
→ Step 4 选图为证 → Step 5 裁剪素材 → Step 6 写逐帧内容
→ Step 7 生成PPTX → Step 8 QA验证
```

### 图文优化核心（"重点在于优化图文"解读）

| 优化维度 | 方法 | 具体规则 |
|:---------|:-----|:---------|
| **布局自适应** | 按图选布局，不套模板 | 全宽(图复杂) / 窄文轨+高图(纵向) / 上下堆叠(横向) / 70/30非对称 |
| **证据层级** | 每帧一主角 | Hero图 > 解释轨 > 标注；文字不喧宾夺主 |
| **图优先** | 有图则图为主 | 结果帧绝不无图纯文；无图时用可编辑表格 |
| **裁剪策略** | 宁裁剪不缩小 | 密集多面板 → 裁剪关键面板；可读性优先 |
| **标题结论化** | 结论式标题 | "PathAgent主动识别信息不足" 而非 "Figure 3" |
| **视觉密度** | 一帧一图清晰 | 不可读则分帧/裁剪，不挤入小框 |

### 论文分类与呈现逻辑

| 论文类型 | 呈现逻辑 | 适用场景 |
|:---------|:---------|:---------|
| 发现/机制论文 | Question-to-Evidence | 现象→机制→假说→验证 |
| 方法/AI/工具 | Problem-to-Solution | 瓶颈→方法→评估→复用 |
| 资源/数据集/基准 | Workflow-to-Validation | 需要原因→构建→验证→应用 |
| 临床/人群/干预 | Design-to-Inference | 问题→设计→结果→推断 |
| 材料/化学/工程 | Property-to-Mechanism | 挑战→设计→表征→性能 |
| 综述/观点 | Evidence-Map | 主题→框架→各主题→争议→展望 |

### 默认结构（12-16帧，15-20分钟报告）

1. **标题页**
2. **研究背景** — 为什么重要
3. **知识缺口/技术瓶颈**
4. **核心问题与主张**
5. **研究设计/技术路线**
6-8. 关键证据 1/2/3（每帧一图，图为主）
9. **验证/对照/稳健性**
10. **机制模型/方法优势**
11. **创新点与可复用价值**
12. **局限性与未解决问题**
13. **总结与讨论**

### 布局自适应规则

| 图宽高比 | 推荐布局 | 图占比 | 说明 |
|:---------|:---------|:------:|:-----|
| 宽幅图（landscape）| 全宽或上下堆叠 | 70-100% | 图占主导，文字窄条 |
| 高图（portrait）| 左图右文轨 | 65-75% | 图高，右列窄文字 |
| 密集多面板 | 裁剪关键面板后全宽 | 80-100% | 不可缩小，宁可裁剪 |
| 单面板+标注 | 非对称 70/30 | 70% | 图大文字小 |
| 表格/数据 | 全宽表格 | 100% | 或分帧避免拥挤 |

**核心原则**: 50/50等分是例外，非默认。结果帧必须有一方明显主导。

### 提取与裁剪流程

**Step 1**: PyMuPDF 提取元数据、标题、图注、表格
**Step 2**: 确定论文类型 → 选择呈现逻辑
**Step 3**: 识别候选图（4-8张）：工作流/主结果/验证/机制
**Step 4**: 高分辨率渲染选中的图页 → 裁剪面板
**Step 5**: 保存到 `output/assets/figures/` + 记录 `asset_manifest.md`
**Step 6**: 用 python-pptx 构建PPTX：16:9、中文标题+要点+讲稿、可选模板
**Step 7**: QA验证 — 重开PPTX检查幻灯片数/图片数/讲稿存在

### 图注与归属规则

- 标题帧：论文标题+期刊+年份+DOI
- 图帧：`Source: Fig. 2b, Nature, 2024` 标注来源
- 改编内容：`整理自` 或 `改绘自`
- 不删除原图标注、不篡改科学数据

### 输出文件

| 文件 | 说明 | 必须 |
|:-----|:-----|:----:|
| `output/final_presentation_cn.pptx` | 完整中文PPTX | ✅ 主产出 |
| `output/qa_report.md` | QA报告 | ✅ |
| `output/assets/figures/` | 裁剪图素材 | ✅ |
| `output/asset_manifest.md` | 图溯源清单 | 有图时 |
| `output/ppt_outline_cn.md` | 中文大纲 | 可选 |
| `output/ppt_script_cn_with_figures.md` | 逐帧脚本 | 可选 |

### 质量要求

- ✅ 必须生成真实 .pptx 文件，不止于提纲
- ✅ 不虚构结果/方法/数字/图细节
- ✅ 不添加昂贵处理步骤除非必要
- ✅ 结果帧有图则图文结合，无纯文
- ✅ 每帧服务于论文的核心论证
- ✅ 图清晰可读，文字不溢出
- ✅ 不确定内容明确标注

### 已知陷阱

- **无头渲染器不可用**：跳过全帧截图QA，改用重开PPTX轻量验证
- **PDF提取失败**：从OCR兜底，但仅对选中图页执行
- **图注不全**：在qa_report中如实记录
- **平台依赖**：所有代码必须跨平台（macOS/Linux/Windows）
- **LibreOffice可选**：不强制安装，不依赖桌面自动化

## 命令层·English

- **Signature**: `source: str (PDF|text|notes) -> presentation: PPTX, qa_report: MD, figure_assets: list[Image]`
- **Allowed tools**: `shell` (PyMuPDF/Pillow/python-pptx), `Read`, `Write`, `file_search`
- **Default stack**: PyMuPDF (extract) → Pillow (crop/resize) → python-pptx (build PPTX)
- **Cross-platform**: macOS, Linux, Windows — no OS-specific paths or fonts
- **Default length**: 12-16 slides (15-20 min)
- **Default language**: Simplified Chinese
- **Presentation logics**: `claim-first`, `question-to-evidence`, `problem-to-solution`, `workflow-to-validation`, `design-to-inference`, `property-to-mechanism`, `evidence-map`
- **Layout modes**: full-width, narrow-rail+tall-image, top-bottom-stack, asymmetric-70-30, compact-callout
- **Layout rule**: NO 50/50 default for result slides — let figure dictate layout
- **Figure count**: 4-8 per deck (select by argument relevance, not by section)
- **Title rule**: conclusion-style titles preferred ("Method X improves Y" not "Figure 3")
- **QA method**: reopen PPTX, check slide/media/notes counts, write qa_report.md
- **Minimal output**: `final_presentation_cn.pptx` + `qa_report.md` + `assets/figures/`
- **Do NOT**: fabricate numbers/details, run OCR on all pages, install full Office suite, use desktop automation, stop at markdown outline
