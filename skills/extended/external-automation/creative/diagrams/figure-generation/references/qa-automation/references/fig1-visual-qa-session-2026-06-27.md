# Figure 1 视觉 QA — 2026-06-27 会话发现

## 工具配置发现

### vision_analyze 后端配置

- `auxiliary.vision` 配置在 `auxiliary.vision.provider: auto` 时，会尝试调用 Qwen3VL 模型，但该模型对大尺寸图像（>2000px）报错 `Failed to apply Qwen3VLProcessor`。
- 正确的配置是 `auxiliary.vision.provider: custom:amax-1` + `base_url: http://100.125.10.93:8000/v1` + `api_key: EMPTY` + `model: qwen3.6-35b-nvfp4`。
- amax-1 节点是唯一支持图片输入的 vLLM 节点。amax（100.100.252.99）和 amax-fallback（100.82.27.51，离线）均不支持。

### 图像预处理要求

- vision_analyze 对超过 2000×2000 像素的图片返回 400 错误。
- 修复：使用 Pillow 缩放到 max 2000px 长边后再发送。
- 缩放后仍保持足够分辨率用于文字检查（2000px 宽 ≈ 2-3pt 文字仍可辨识）。

## 视觉 QA 检查清单（来自 2026-06-27 会话）

对 HCS-3WT Figure 1 (generate_figures_v2.py) 的逐项检查结果：

| # | 检查项 | 状态 | 详情 |
|---|--------|------|------|
| 1 | Expert B 框内标题文字溢出 | ❌ P0 | "Expert B: Catcher" 12pt 加粗字，从 y=6.40 开始（va="top"），框顶 y=6.70，字母上缘超出框边界 |
| 2 | Expert A 框内标题文字溢出 | ❌ P0 | "Expert A: Refiner" 12pt 加粗字，从 y=3.90 开始，框顶 y=4.20，同样问题 |
| 3 | Expert C 框文字溢出 | ✅ 无 | 文字完整在框内 |
| 4 | Key Design Principles 框文字 | ✅ 无 | 完整在框内 |
| 5 | Overall Performance 框数值 | ✅ 无 | 数值完整显示 |
| 6 | Meta-Feature Pipeline 框文字 | ✅ 无 | 列表完整显示 |
| 7 | Clear Negative/Positive 框文字 | ✅ 无 | 完整显示 |
| 8 | 箭头1穿入 Expert B 框 | ❌ P0 | 箭头 tip y=6.72 超出 eb_box 顶 y=6.70，箭头尖端穿入框内约 1-2pt |
| 9 | 箭头4/5在 Expert C 顶部交叉 | ⚠️ P1 | 两条虚线同时指向 ec_box 顶部同一点 (2.4, 1.67)，在视觉上交叉 |
| 10 | 主标题清晰度 | ✅ 无 | 清晰居中，无问题 |

## QA 代码分析 vs 视觉确认的对比

QA 代码分析（figure-qa-check.py）发现 3 个错误 + 1 个警告：
- 错误1: arrow1 tip 超出 eb_box（与视觉确认一致 ✅）
- 错误2: arrow4 target 推断错误（QA 工具误报，实际是 ec_box 问题）
- 错误3: arrow5 同上
- 警告1: arrow1 source 推断缺失

**关键洞察**: QA 代码在框推断环节有假阳性，但核心几何边界检查（文本溢出、箭头超出框）是正确的。两者结合使用最佳：
1. 先用 QA 代码发现几何边界问题
2. 再用 vision_analyze 确认视觉实际影响
3. 对 QA 工具推断错误的箭头，人工验证坐标

## 修复记录

| 问题 | 修复方案 | 状态 |
|------|----------|------|
| arrow1 超出 Expert B | eb_box y_min: 6.70→6.78 或 arrow1 y2: 6.72→6.70 | 待实施 |
| arrow4/5 超出 Expert C | ec_box y_min: 1.65→1.72 或 arrow4/5 y2: 1.67→1.65 | 待实施 |
| Expert B 标题溢出 | 框顶与标题间距增加 0.08in | 待实施 |
| Expert A 标题溢出 | 同 Expert B | 待实施 |
| arrow4/5 交叉 | 终点错开 0.1in 或使用分叉箭头 | 待实施 |
