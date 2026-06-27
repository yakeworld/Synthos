# Figure Generation Skill — Test Results 2026-06-27

## 测试概览

5/5 全部通过。验证了模式 A/B/C/D/G 的完整管线。

## 测试结果

| 测试 | 模式 | 输出 | 状态 |
|:-----|:-----|:------|:-----|
| Test 1 | A 科学数据图 | PNG 176KB + PDF 26KB + SVG 76KB | ✅ |
| Test 2 | B 架构图 | PNG 63KB + PDF 16KB + SVG 30KB | ✅ |
| Test 3 | C Excalidraw | JSON 4.2KB | ✅ |
| Test 4 | D 封面卡片 | PNG 23KB + JPG 46KB | ✅ |
| Test 5 | G QA自动化 | 0错误, 0警告 | ✅ |

## 发现的问题（非阻塞）

### 1. bbox_inches='tight' 导致QA边界检查误报
逻辑坐标（fig.transFigure）中框坐标为 (-0.4, 1.5) → (0.8, 2.5)，超出 set_xlim(-0.5, 10.5) 标记为超框。但实际渲染时 `bbox_inches='tight'` 扩展了画布，文字可见。已在 SKILL.md 补充陷阱说明。

### 2. 封面图大小偏小
Test 4 封面 PNG 仅 23KB，原因是无中文字体指定，默认字体导致渲染面积小。生产环境需配置 `references/pil-image/references/cjk-font-paths.md` 中的字体路径。

### 3. QA 脚本依赖 FancyBboxPatch
figure-qa-check.py 仅支持 FancyBboxPatch/FancyArrowPatch，不支持 Rectangle/annotate 等方式。

## 环境状态
- matplotlib: ✅ numpy: ✅ Pillow: ✅ python-pptx: ✅
- 中文字体: 439个（Noto CJK等）
- pdf2image: ❌（不影响核心功能）
