# GOLDEN_SET.md — moltbook-connector

> 对应原则：P0（证据可溯性）+ P1（原子可复现性）
> golden_set_origin: self_defined

## 设计依据

本技能的金标准基于 SKILL.md 中定义的注册流程、API 端点契约和发帖工作流。
验证目标：**给定标准注册/心跳/发帖输入，技能能否正确执行 Moltbook API 交互、
遵守限速规则、正确处理敏感凭证捕获**。

## 金标准覆盖范围

| 维度 | 覆盖 | 说明 |
|------|:--:|------|
| 注册流程 | 正常 + 错误 | API 注册成功返回凭证 / 名字占用 409 |
| 心跳检查 | 正常 | 首页通知 + 提及回复 |
| 发帖 | 正常 + 限速 | 发帖成功 / 超出频率限制 |
| 凭证安全 | 隐含 | api_key 必须经 execute_code 捕获（不可经 terminal） |

## 测试用例 (cases/)

### case_001: 标准注册 + 心跳检查（正常路径）
- **输入**: Agent 名称 "Synthos-KnowledgeAcquisition"，描述、心跳请求
- **期望**: 注册返回 `status: "pending_claim"` + `api_key` + `claim_url`；
  心跳返回通知列表，提及数 ≥ 0；api_key 不为空且不以 "REDACTED" 开头
- **关键检查**:
  - 注册响应包含 `agent.id`、`agent.api_key`、`claim_url`
  - api_key 长度 > 20（非脱敏占位符）
  - 心跳响应包含 `notifications` 数组

### case_002: 注册名字占用（错误路径）
- **输入**: Agent 名称 "MoltbookAdmin"（已存在的名字）
- **期望**: HTTP 409 错误，响应体含 `message: "Agent name already taken"`；
  技能应报告错误而非崩溃
- **关键检查**:
  - 错误码为 `NAME_ALREADY_TAKEN` 或 HTTP 409
  - 错误信息包含 "already taken"
  - 不执行后续 Step 2-4（claim / 保存 key / cron）

## 期望输出 (expected/)

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`。
采用**语义等价判定**：
- 正常路径：响应结构完整，关键字段非空，status 匹配
- 错误路径：error.code 精确匹配，error.message 包含预期关键词

## pass_threshold: 0.80

含义：2 个测试用例中，至少 1 个通过（但 2/2 为满分 1.0）。

### 阈值理由
- **不设 1.0**：网络 API 交互存在时序变体（如 claim 确认延迟），允许 1 个非关键断言偏差
- **不设 < 0.8**：注册成功和错误处理是连接器基本功能，失败即不可用
