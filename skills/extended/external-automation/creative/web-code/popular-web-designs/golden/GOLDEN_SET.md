# GOLDEN_SET.md — popular-web-designs

> 对应原则：P1（认知原子语义可复现：同一输入 → 等价设计系统路由 + HTML 契约通过金标准测试）
> golden_set_origin: self_defined
> skill_role: external-automation 叶子技能 / 54 个真实设计系统模板库

## 设计依据

本技能是 54 个真实网站设计系统模板库，核心职责是从用户内容出发路由到正确的设计模板，并产出符合该模板视觉语言的 HTML。金标准验证目标：

1. **路由正确性**：给定内容/风格需求，能否从 54 个模板中匹配到正确的设计系统（按类别 Choosing a Design）
2. **HTML 契约**：`:root` 含模板 Section 2 调色板、排版（Section 3）与组件/阴影（Section 4-6）一致、viewport+lang 正确
3. **字体替换纪律**：专有字体按 Font Substitution 参考表替换为 Google Fonts 替代（含 `<link>` 标签），并严格沿用 weight/size/letter-spacing
4. **技能边界**：交付物为 DESIGN.md 令牌规范时，路由切换到 `design-md` 技能（POPU-005）
5. **错误路径**：请求的模板不在 54 个目录中时，降级（不硬造模板、给出同类替代建议）

## 金标准覆盖范围

| 维度 | 覆盖 | 说明 |
|------|:--:|------|
| 正常路径 | 2 类 | developer dashboard（linear.app.md）、marketing landing（stripe.md 专有字体替换） |
| 错误路径 | 2 类 | 模板不在 54 目录、交付物为 DESIGN.md（应路由 design-md） |
| 契约完整性 | 所有 case | 检查输出字段完备性（template/root_vars/typography/font_substitution） |

## 测试用例 (cases/)

### case_001: 正常路径 — developer dashboard（dark mode，数据密集）
- **输入**: 内容 = 数据密集的分析面板，需 dark mode
- **期望**: 路由到 `linear.app.md`（超极简暗色+紫色强调）或 `sentry.md`（数据密集）；`:root` 含模板 Section 2 调色板为 CSS 变量；排版 Section 3 一致；组件/阴影 Section 4-6；viewport+lang 正确

### case_002: 正常路径 — Spotify 风格落地页（专有字体替换）
- **输入**: 选用 `spotify.md`（Circular 无 CDN），落地页
- **期望**: 字体按 Font Substitution 表替换为 DM Sans（Google Fonts `<link>` 粘贴）；严格沿用原模板 weight/size/letter-spacing；`:root` 含 Spotify 绿色品牌特征；组件/间距遵循模板

### case_003: 错误路径 — 模板不在 54 目录
- **输入**: 请求用 "templates/notion-redesign.md"（不存在于 54 目录）
- **期望**: 不硬造模板；返回 error 非空（模板不存在于 54 目录），suggestions 非空（列出最接近的真实模板 + 恢复建议），template 为 null

### case_004: 技能边界 — 交付物为 DESIGN.md 令牌规范
- **输入**: 用户要"给我一份可复用的设计令牌文件（DESIGN.md）"而非渲染页面
- **期望**: 路由切换到 `design-md` 技能（POPU-005）；本技能仅作为模板视觉词汇来源；交付物为规范文件而非渲染 HTML；routed_skill="design-md"

## 期望输出 (expected/)

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`。

期望输出采用**语义等价判定**：
- `template` 必须精确匹配 54 目录中的文件名片段（如 `linear.app`）
- `root_variables`：含 Section 2 调色板（≥3 个 CSS 自定义属性）
- `typography`：字号/字重/字间距与模板 Section 3 一致（`matches_section3=true`）
- `font_substitution`：专有字体时 `substitute` 非空且 `google_fonts_link=true`、`keeps_weight_size_spacing=true`
- 错误路径：`error` 非空、`suggestions` 非空、`template` 为 null
- 边界路径：`routed_skill="design-md"`、`deliverable="DESIGN.md"`

## 通过标准

- 加权总分 ≥ 0.80
- 所有 critical 检查通过（路由正确、HTML 契约完整、错误路径不硬造、边界切换正确）
- expected 与 cases 数量、命名一一对应

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 模板路由正确 / HTML 契约（:root+viewport+lang）/ 错误路径不硬造 / 边界切换 design-md |
| high | 0.7 | 排版 Section 3 一致、字体替换纪律（含 <link>+沿用 weight/size/spacing） |
| medium | 0.4 | 组件/阴影 Section 4-6、browser_vision 验证步骤 |

## 验证命令

```bash
# JSON 有效性
for f in golden/cases/*.json golden/expected/*.json; do
  python3 -c "import json; json.load(open('$f'))" || echo "FAIL: $f"
done

# 数量配对
test "$(ls golden/cases/*.json | wc -l)" -eq "$(ls golden/expected/*.json | wc -l)"
```
