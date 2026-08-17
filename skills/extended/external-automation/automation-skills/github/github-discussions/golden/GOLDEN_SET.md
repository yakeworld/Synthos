# GOLDEN_SET.md — github-discussions

> 对应原则：P0（证据可溯性）+ P1（原子可复现性）
> golden_set_origin: self_defined

## 设计依据

本技能的金标准基于 SKILL.md 中定义的 GraphQL 工作流（6 步）、A2A 讨论模板和故障排查表。
验证目标：**给定标准创建/列表/评论输入，技能能否正确使用 GraphQL（而非 REST POST）、
正确获取 Node ID、安全转义长 body、创建后回读验证**。

## 金标准覆盖范围

| 维度 | 覆盖 | 说明 |
|------|:--:|------|
| ID 获取 | 正常 | GraphQL 查 `repository.id` + `discussionCategories` Node ID |
| 创建讨论 | 正常 + 错误 | GraphQL `createDiscussion` 成功 / REST POST 404 |
| Body 转义 | 正常 + 错误 | 长 body 经临时 JSON 文件 / 含特殊字符的正确转义 |
| 列表与详情 | 正常 | REST GET 或 GraphQL 查询 |
| 添加评论 | 正常 | `addDiscussionComment` mutation |
| A2A 模板 | 隐含 | 标题格式 `[A2A] <Concept>: <Subtitle>` + 结构约束 |
| 前置检查 | 错误 | `has_discussions` 为 false 时拒绝创建 |

## 测试用例 (cases/)

### case_001: 创建 A2A Discussion（正常路径，长 body 经临时文件）
- **输入**: owner/repo、标题 `[A2A] Constitutional Hierarchy: CON > MEM > CMD > SKL > DEF`、
  长 body（含 markdown、换行、双引号）、category slug `ideas`
- **期望**: 先 GraphQL 查 `repository.id` 和 `discussionCategories` Node ID；
  body 转义后写入 `/tmp/gql_mutation.json`；`gh api graphql --input` 执行
  `createDiscussion`；回读 REST GET 确认 title/url/category 一致
- **关键检查**:
  - 使用 GraphQL `createDiscussion`（非 REST POST）
  - `repositoryId` 和 `categoryId` 均为 Node ID 格式（`MDEw...` / `DIC_...`），非整数
  - body 中双引号转义为 `\"`，换行转义为 `\n`
  - 回读结果 `title` 精确匹配输入
  - A2A 标题以 `[A2A]` 开头
  - 创建后 REST GET 回读成功

### case_002: 仓库未启用 Discussions（错误路径）
- **输入**: owner/repo，`has_discussions: false`
- **期望**: 技能检测到 `has_discussions` 为 false，拒绝创建，
  报告错误并提示需在 repo settings 启用讨论功能
- **关键检查**:
  - 错误码 `DISCUSSIONS_NOT_ENABLED`
  - 错误信息包含 "has_discussions" 和 "enable discussions"
  - 不执行 `createDiscussion` mutation
  - 不写入临时 JSON 文件

## 期望输出 (expected/)

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`。
采用**语义等价判定**：
- 正常路径：GraphQL 操作成功，回读数据与输入一致，Node ID 格式正确
- 错误路径：前置检查拦截，错误信息可操作（含修复步骤）

## pass_threshold: 0.80

含义：2 个测试用例中，至少 1 个通过（但 2/2 为满分 1.0）。

### 阈值理由
- **不设 1.0**：GraphQL 响应中 `number` 字段为服务端分配，不可预测，允许 ±1 偏差
- **不设 < 0.8**：GraphQL 正确性（非 REST POST）和前置检查是核心能力，
  用错 API 或跳过检查会导致静默失败或数据污染
