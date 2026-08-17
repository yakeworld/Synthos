---
name: pretext
description: pretext 金测集 — @chenglou/pretext 文本测量/布局创意 demo 的可执行测试
---

# 金测集: pretext

> 来源: SKILL.md Golden 集合 + 验证清单（VERIFICATION 6 项）+ Genes (PRET-001~007)。
> 本技能封装 `@chenglou/pretext`（15KB 零依赖 TS 库）的 DOM-free 文本测量与多行布局能力，
> 用于构建单文件创意 demo（环绕障碍物重排、文本几何游戏、破碎粒子、kinetic typography 等）。
> 技能产出 = 单文件自包含 `.html` demo；本 golden 集验证"输入 brief → 决策 + 产物结构"的正确性。
> 每个 case 验证策略决策（pattern 选型 / API 选型 / 构建约束）的正确性（P1 可复现性）。

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常路径：文本环绕拖拽精灵的重排 demo（reflow-around-obstacle pattern） | pattern 精确匹配 → API 选型 = `prepareWithSegments` + `layoutNextLineRange` + 每行动态宽度函数（PRET-001）；产物为单文件 `.html` 且经 `esm.sh` 引入固定版本 `@chenglou/pretext@0.0.6`（PRET-007）；font 字符串与 CSS 一致；`prepare` 仅调用一次 |
| case_002 | 正常路径：点击破碎粒子（shatter）效果 demo（shatter/particles pattern） | pattern → API 选型 = `prepareWithSegments` 取每字素 (x,y) 坐标 + 物理模拟（PRET-002）；CJK/emoji 文本必须用 `Intl.Segmenter` 字素分割（PRET-005）；`ctx.font` 每帧仅设一次 |
| case_003 | 错误路径：非法 font 字符串 + unpkg 引入（双陷阱） | `prepareWithSegments` 因非法 font 字符串必须抛错并给出上下文（哪一行、哪个 font 串）+ 恢复建议（改用 `esm.sh` 固定版本 + 合法 canvas font 格式）；禁止静默 404 回退（Common Pitfalls #1/#5） |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: pattern 选型必须精确为 "reflow-around-obstacle"，核心 API 必须含 `layoutNextLineRange` + 每行宽度函数；产物检查必须含：单文件 `.html`、`esm.sh` 固定版本、font 字符串与 CSS 一致、`prepare` 缓存仅一次、真实 corpus 非 lorem ipsum、至少一个交互/idle 运动（VERIFICATION 6 项全过）
- case_002: pattern 选型必须精确为 "shatter/particles"，核心 API 必须含 `prepareWithSegments` + 字素坐标物理；含 emoji/CJK 时字素分割必须用 `Intl.Segmenter`（PRET-005），禁止 `"str".split("")`
- case_003: 必须走 Golden Error 路径 —— 错误信息同时含 `context`（失败调用点 + 非法 font 串值）与 `recovery`（≥2 条建议：esm.sh 固定版本、canvas `ctx.font` 合法格式），禁止仅返回通用错误；unpkg 引入 TS-only 入口必须被识别为 404 陷阱并拒绝（Common Pitfalls #5）

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001 / case_003） |
| high | 0.7 | 重要但不致命（case_002） |

## 期望输出

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，包含：
- `expected_output`: 决策结构（pattern / core_api / product_checks）或错误结构（context / recovery）
- `verification`: 可执行的校验断言列表

期望输出采用**语义等价判定**：
- pattern 选型必须精确匹配 Demo Recipe Patterns 表（7 选 1，无歧义）
- 核心 API 必须与 Genes 策略一致（PRET-001/002/005/007）
- 错误路径必须同时含 `context` 与 `recovery` 两个字段
- 产物约束（单文件/esm.sh/固定版本/font 同步/prepare 仅一次）为不可协商项

## 关联

- SKILL.md Genes: PRET-001~007
- SKILL.md 验证清单: 6 项（单文件+esm.sh 固定版本 / font 与 CSS 一致 / prepare 仅一次 / 真实 corpus / 交互或 idle 运动 / 本地验证 60fps 无 console 错误）
- Common Pitfalls: #1（font 漂移）/ #5（unpkg TS 入口 404）/ #7（跳过行 vs 调窄宽度）
