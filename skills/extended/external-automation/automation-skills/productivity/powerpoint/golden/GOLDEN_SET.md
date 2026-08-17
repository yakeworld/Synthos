---
name: powerpoint
description: GOLDEN_SET.md
---

# GOLDEN_SET.md — powerpoint

> 对应原则：P0（证据可溯性：交付物通过 quality_check.py 可复算）+ P1（原子可复现性）
> golden_set_origin: self_defined

## 设计依据

本技能金标准为自设（`self_defined`），验证目标：**给定的 PPTX 生成任务，技能能否产出通过布局数学检查（无溢出/重叠）、安全区 0.92 系数合规、网格列索引无重叠的 .pptx 文件**，并在错误路径下（元素超出页面安全区）被质量门拦截而非静默交付。

## 金标准覆盖范围

| 维度 | 覆盖 | 说明 |
|------|:--:|------|
| 多页结构化生成 | 1 | 6 卡 3×2 网格 + 页眉页脚 helper 函数 |
| 交付前质量门 | 1 | `scripts/quality_check.py` 三步验证（L0.5/布局/规范一致性） |
| 错误路径 | 1 | 元素 right > 13.333" 溢出被检出并拦截 |
| 页面顺序调整 | 1 | sldIdLst XML 重排（POWE-008） |

## 测试用例 (cases/)

### case_001: 生成 6 卡 3×2 网格页（正常路径）
- **输入**: 6 个卡片文本项 + 页面 13.333"×7.5" + 网格 num_cols=3
- **期望**: `col = i % 3; row = i // 3` 分布无重叠；所有元素 (left+width)/914400 ≤ 13.333 且 (top+height)/914400 ≤ 7.5；非零尺寸已乘 0.92 系数

### case_002: 交付前质量门检查（正常路径）
- **输入**: case_001 产出的 pptx 路径
- **期望**: `quality_check.py` 报告 0 overflow、0 越界、0 重叠；L0.5 硬事实核对通过

### case_003: 元素溢出安全区（错误路径）
- **输入**: 卡片 width=Inches(5.0) 且 left=Inches(9.0)（right=14.0" > 13.333"）
- **期望**: quality_check 检出 overflow 且标记 deliverable 为 blocked；不静默交付，error 含溢出坐标与修复建议（应用 0.92 系数或缩小布局）

### case_004: 页面顺序重排（正常路径）
- **输入**: 4 页 pptx + 目标顺序 [0, 2, 1, 3]
- **期望**: 直接改写 `ppt/presentation.xml` 的 `sldIdLst`（非 `slideIdLst`），重排后页面顺序匹配目标

## 期望输出 (expected/)

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，采用**语义等价判定**：
- 布局数值按 EMU 整数精确比较（1 英寸 = 914400 EMU），容差 0
- `grid_positions` 中 (row, col) 对不得重复
- 错误路径必须 `deliverable_blocked: true` 且 `overflow_count ≥ 1`
- 页面顺序 case 校验重排后 `sldId` 序列与目标一致

## pass_threshold: 0.80

含义：4 个测试用例中，至少 3 个通过（80%）。

### 阈值理由
- **不设 1.0**：字体渲染/行高在不同系统有 ±1pt 差异，布局数值用整数 EMU 容差吸收
- **不设 < 0.8**：溢出/重叠直接导致 LibreOffice 导出 PDF 裁剪元素（SKILL 页面尺寸陷阱 ⚡P0），质量门失败必须拦截
- case_003（错误路径）为 critical 权重：质量门放行溢出页视为 self_deception，单独计 1.0
