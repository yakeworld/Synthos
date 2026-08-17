# GOLDEN_SET.md — baoyu-infographic

> 对应原则：P0（证据可溯性：输入输出可复现可验证）+ P1（原子可复现性）
> golden_set_origin: self_defined

## 设计依据

本技能将用户提供的源内容转化为结构化信息图（infographic）：分析内容 → 生成结构化内容 → 推荐 layout×style 组合 → 生成 prompt → 出图。金标准是自设的，用于验证：

1. **数据保真**（BAOY-002）：源文本中的统计数据/引用在 `structured_content` 中逐字保留，且凭证被剥离
2. **组合选择**（BAOY-001/003/004/005/006）：关键词短路、默认组合、内容类型匹配 三种路径均正确
3. **交付物完整性**：输出目录含 5 类交付文件
4. **错误路径**：源内容为空/缺失时应拒绝并给出恢复建议（RULES-3 异常约束）

## 金标准覆盖范围

| 维度 | 覆盖 | 说明 |
|------|:--:|------|
| 正常路径 | 1 | 关键词"信息图"触发 bento-grid + craft-handmade 默认组合 |
| 正常路径（内容推断） | 1 | 时间线内容 + 无关键词 → linear-progression |
| 错误路径 | 1 | 空源内容 → 拒绝执行并报错 |
| 数据保真 | 全部 | 统计数字逐字保留 |
| 凭证剥离 | 全部 | 源中 API key 不出现在任何输出 |
| 宽高比映射 | 正常路径 | 自定义 3:4 → image_generate portrait |

## 测试用例 (cases/)

### case_001: 正常路径 — 关键词"信息图"（bento-grid 默认）
- **输入**: 含统计数字（"73% increase"）和一处 API key 的源文本；request 含关键词"信息图"
- **期望**:
  - `layout == "bento-grid"`, `style == "craft-handmade"`（BAOY-003 默认 + 关键词短路）
  - `aspect == "landscape"`（关键词表默认档）
  - `structured_content` 含逐字 "73% increase"
  - 输出中不出现 `sk-` 开头的凭证
  - 交付文件清单含 5 项：source/analysis/structured-content/prompts/infographic.png

### case_002: 正常路径 — 时间线内容推断（linear-progression）
- **输入**: 产品发布时间线源文本，无关键词，aspect 指定为自定义 "3:4"
- **期望**:
  - `layout == "linear-progression"`（BAOY-004）
  - `image_generate_format == "portrait"`（3:4 → 最近档映射，SKILL Step 6 规则 5）
  - 统计数字逐字保留

### case_003: 错误路径 — 空源内容
- **输入**: `source_content: ""`
- **期望**: `status == "error"`，`error.message` 含上下文与恢复建议（RULES-3），且不生成任何交付文件

## 期望输出 (expected/)

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`。采用**语义等价判定**：

- `status` / `layout` / `style` / `aspect` / `image_generate_format` 必须精确匹配
- `deliverables` 列表必须包含全部 5 个文件名（case_001/002）
- `data_integrity`：期望中的 `verbatim_data_points` 必须逐字出现在 `structured_content`
- `secrets_stripped`: true 表示输出文本中不得出现 case 输入的凭证字符串
- 错误 case 检查 `status == "error"` 且 `error.suggestion` 非空

## pass_threshold: 1.00

含义：3 个测试用例全部通过。

### 阈值理由
- **设 1.0**：本技能有机械性契约（数据逐字保留、凭证剥离、组合映射表），无风格自由度空间；任一失败即违反 P0/BAOY-002 红线
- **不设 < 1.0**：交付文件清单与错误契约是硬性约束，错误会直接泄漏凭证或丢失数据

## 更新历史

| 版本 | 日期 | 变更 | 审批 |
|------|------|------|------|
| 0.1.0 | 2026-06-27 | 初始自设金标准，3 个 case | Synthos Agent |
