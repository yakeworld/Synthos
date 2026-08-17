# GOLDEN_SET.md — claude-design

> 对应原则：P0（证据可溯性：验证声明必须对应实际执行的验证）+ P1（原子可复现性）
> golden_set_origin: self_defined

## 设计依据

本技能在 CLI/API 环境中执行 Claude Design 式设计工作：理解 brief → 收集上下文 → 定义设计系统 → 构建自包含 HTML 交付物 → 用本地手段验证 → 简短报告。金标准是自设的，用于验证：

1. **上下文优先**（CLAU-004/006）：高保真任务在设计前读取真实上下文（仓库主题/token 文件），而非凭空生成通用布局
2. **技能路由**（CLAU-001/002/007）：品牌匹配请求联动 `popular-web-designs`；DESIGN.md token 创作路由到 `design-md`；仓库实现请求不输出独立 HTML
3. **交付物契约**（CLAU-003）：自包含 HTML（CSS 内联 `<style>`、JS 内联 `<script>`）、无远程依赖（CDN 需锁版本）、响应式
4. **验证诚实**：只声明实际执行过的验证（"Never say done if the file was not actually written"）
5. **无填充内容**（Anti-Slop）：无虚构指标、无装饰性统计、无泛化功能网格

## 金标准覆盖范围

| 维度 | 覆盖 | 说明 |
|------|:--:|------|
| 正常路径 | 2 | (a) 自包含 HTML 原型（含 Tweaks 面板）；(b) 品牌匹配请求的技能路由 |
| 错误路径 | 1 | 高保真 + 零上下文 + 拒绝提问 → 必须先问再设计 |
| 上下文读取 | 正常路径 a | 先读 repo 主题文件再设计 |
| Anti-Slop | 全部 | 禁止词/禁止结构检查 |

## 测试用例 (cases/)

### case_001: 正常路径 — 命令面板原型（自包含 HTML）
- **输入**: 要求生成键盘命令面板原型，提供仓库主题文件路径（`theme.ts` 含颜色/间距 token），要求 2 个变体 + Tweaks 面板
- **期望**:
  - `context_gathered` 含 `theme.ts`（CLAU-006：读了真实源文件）
  - 产物为单一自包含 HTML 文件，CSS 内联 `<style>`，JS 内联 `<script>`
  - `remote_dependencies: []`（无 CDN）
  - 含 2 个变体 + Tweaks 控件（density/theme）
  - 验证声明只含实际执行的检查（file_exists + html_saved）
  - 无填充内容：无 fake metrics / 装饰统计

### case_002: 正常路径 — "让它看起来像 Linear"（技能路由）
- **输入**: 要求页面视觉匹配 Linear 品牌
- **期望**:
  - `loaded_skills` 含 `popular-web-designs`（CLAU-001：品牌视觉词汇由该技能提供）
  - `loaded_skills` 含 `claude-design`（本技能驱动流程）
  - 未加载 `design-md`（交付物是渲染产物而非 token 规范）

### case_003: 错误路径 — 高保真且零上下文、且调用方禁止提问
- **输入**: "为外部客户做一个高保真营销落地页"，无任何品牌/仓库/截图上下文，`allow_questions: false`
- **期望**: `status == "error"`（或 `status == "blocked"`），错误含上下文说明缺什么（品牌/受众/保真度）与恢复建议（提供品牌文档或允许澄清提问）；**不得**直接产出通用 SaaS 布局（Pitfalls: "Do not produce generic SaaS layouts and call them designed"）

## 期望输出 (expected/)

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`。采用**语义等价判定**：

- `status`、`loaded_skills`、`artifact.path_pattern` 精确匹配
- `artifact`（case_001）：`self_contained == true`、`inline_style == true`、`inline_script == true`、`remote_dependencies` 为空数组
- `verification` 列表只允许包含实际执行的检查名；出现 `browser_check` 而环境无浏览器工具 → 失败（验证诚实红线）
- `anti_slop`：`forbidden_terms` 与 `forbidden_structures` 不得出现在交付物中
- 错误 case 检查 `status`、`error.message_contains_context`、`generic_layout_produced == false`

## pass_threshold: 1.00

含义：3 个测试用例全部通过。

### 阈值理由
- **设 1.0**：验证诚实（不谎报浏览器验证）、上下文优先（不凭空设计）是本技能最硬的契约；谎报验证 = 违反 P0 数据诚实门
- **不设 < 1.0**：交付物自包含性（可被浏览器直接打开）与 Anti-Slop 红线是可机械检查的硬约束

## 更新历史

| 版本 | 日期 | 变更 | 审批 |
|------|------|------|------|
| 0.1.0 | 2026-06-27 | 初始自设金标准，3 个 case | Synthos Agent |
