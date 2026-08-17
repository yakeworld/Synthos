# GOLDEN_SET.md — p5js

> 对应原则：P1（认知原子语义可复现：同一输入 → 等价技术设计决策通过金标准测试）
> golden_set_origin: self_defined
> skill_role: external-automation 叶子技能 / p5.js 创意编程生产管线

## 设计依据

本技能是 p5.js 创意编程方法论原子，核心职责是从用户请求出发产出：技术设计决策（模式/画布/渲染器/帧率/导出）+ 单文件 HTML 结构 + 验证规则。金标准验证目标：

1. **技术设计正确性**：给定请求，能否映射到正确的模式/渲染器/帧率/导出格式（方法2 技术设计表）
2. **首帧卓越**：是否要求自定义调色板/非纯色背景/审美一致性（P1/P3/P4 原则）
3. **可复现性**：是否要求 `randomSeed()`+`noiseSeed()`、CONFIG/PALETTE/globals 分离
4. **性能纪律**：热循环用 Math.*/beginShape()/pixelBuffer、`pixelDensity(1)`、`p5.disableFriendlyErrors`
5. **错误路径**：输入无法映射到 7 种模式时的降级（不硬造、给出模式列表与恢复建议）

## 金标准覆盖范围

| 维度 | 覆盖 | 说明 |
|------|:--:|------|
| 正常路径 | 2 类 | 交互式生成艺术（60fps/交互）、无头导出 MP4（noLoop+Puppeteer） |
| 错误路径 | 2 类 | 请求不属于 7 种模式、请求含不合法画布/帧率参数 |
| 契约完整性 | 所有 case | 检查输出字段完备性（mode/renderer/fps/export/qa_checks） |

## 测试用例 (cases/)

### case_001: 正常路径 — 交互式生成艺术（seed 探索，60fps）
- **输入**: 用户请求"交互式生成艺术，粒子噪声流场，浏览器可探索 seed，1920×1080"
- **期望**: mode=generative art；renderer=P2D；fps=60；interaction=seed 探索（用 templates/viewer.html）；单文件 HTML；`randomSeed()`+`noiseSeed()`；CONFIG/PALETTE/globals 分离；自定义调色板 3-7 色；非纯色背景；`p5.disableFriendlyErrors=true`；`pixelDensity(1)`；快捷键 S/G/R/Space；至少一个主动发明元素

### case_002: 正常路径 — 无头渲染导出 MP4（noLoop + Puppeteer）
- **输入**: 用户请求"把 p5 草图无头渲染导出为 30 秒 30fps 的 MP4，1920×1080"
- **期望**: mode=animation/motion graphics；export=MP4；setup 必须 `noLoop()` 且设 `window._p5Ready`；帧率=30；使用 `scripts/render.sh` + ffmpeg；`pixelDensity(1)`；`p5.disableFriendlyErrors=true`；帧前进由捕获脚本 `redraw()` 控制（1:1 对应）

### case_003: 错误路径 — 请求不属于 7 种模式
- **输入**: 用户请求"用 p5.js 做一个 Unity 风格 3D 实时物理引擎"
- **期望**: 不硬造草图；返回 error 非空（超出 7 种模式能力边界），suggestions 非空（列出 7 种模式 + 建议 3D scene 模式的近似或改用 WebGL 物理库），mode 为 null/"unmatched"

### case_004: 错误路径 — 不合法参数（帧率/画布）
- **输入**: 用户请求草图参数 `fps=120`、`canvas=4096×4096`（超性能目标）
- **期望**: 参数校验失败；error 非空（指出 fps 超 60fps 交互目标 / canvas 超 3840×2160 导出上限），给出合规范围（交互 60fps / 动画 30fps / noLoop；画布 ≤3840×2160），mode 为 null

## 期望输出 (expected/)

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`。

期望输出采用**语义等价判定**：
- `mode`/`renderer`/`fps`/`export` 必须精确匹配技术设计表
- `reproducibility`：`randomSeed`+`noiseSeed`=true、`state_separation` 含 CONFIG/PALETTE/globals
- `performance`：`disable_fes`+`pixel_density_1`+ 热循环优化（Math.*/beginShape/pixelBuffer）
- `first_frame`：`custom_palette` 3-7 色、`non_plain_background`=true、`invented_element` 非空
- 错误路径：`error` 非空、`suggestions` 非空、`mode` 为 null 或 "unmatched"

## 通过标准

- 加权总分 ≥ 0.80
- 所有 critical 检查通过（技术设计正确、无头必须 noLoop、错误路径不硬造）
- expected 与 cases 数量、命名一一对应

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 技术设计正确（模式/渲染器/帧率/导出）/ 无头必须 noLoop / 错误路径不硬造 |
| high | 0.7 | 可复现性（seeds+状态分离）、性能纪律（FES/pixelDensity/热循环）、首帧卓越（调色板/非纯色背景） |
| medium | 0.4 | 主动发明元素、快捷键约定、导出管线细节 |

## 验证命令

```bash
# JSON 有效性
for f in golden/cases/*.json golden/expected/*.json; do
  python3 -c "import json; json.load(open('$f'))" || echo "FAIL: $f"
done

# 数量配对
test "$(ls golden/cases/*.json | wc -l)" -eq "$(ls golden/expected/*.json | wc -l)"
```
