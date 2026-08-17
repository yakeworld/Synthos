---
name: webhook-subscriptions
description: GOLDEN_SET.md
---

# GOLDEN_SET.md — webhook-subscriptions

> 对应原则：P0（证据可溯性：订阅条目落盘 `~/.hermes/webhook_subscriptions.json` 可核对）+ P1（原子可复现性）
> golden_set_origin: self_defined

## 设计依据

本技能金标准为自设（`self_defined`），验证目标：**给定 webhook 订阅请求，技能能否在 Gateway 就绪前提下创建含 HMAC secret 的订阅、正确渲染 `{dot.notation}` Prompt 模板、配置交付目标**，并在错误路径下（`--deliver-only` 配 `--deliver log`）被拒绝。

## 金标准覆盖范围

| 维度 | 覆盖 | 说明 |
|------|:--:|------|
| 订阅创建 + 模板渲染 | 1 | GitHub issues 事件 → telegram 交付 |
| 直接透传模式 | 1 | `--deliver-only` 零 LLM 成本推送，200/502 语义 |
| 错误路径 | 1 | `--deliver-only` + `--deliver log` 被拒绝 |
| 签名验证失败 | 1 | HMAC 签名不匹配时请求被拒并提示核对 secret |

## 测试用例 (cases/)

### case_001: GitHub issues 订阅创建（正常路径）
- **输入**: Gateway 健康检查通过 + subscribe 请求（events=issues, prompt 模板, deliver=telegram）
- **期望**: 返回 webhook_url + 自动生成的 HMAC-SHA256 secret；`webhook list` 显示订阅；`webhook test --payload` 渲染出 `{issue.number}`/`{issue.title}` 等字段

### case_002: `--deliver-only` 透传订阅（正常路径）
- **输入**: 匹配通知订阅，`--deliver telegram --deliver-only`
- **期望**: POST 成功返回 200；目标不可达时返回 502（上游可重试）；不触发 agent run（零 LLM 成本）

### case_003: `--deliver-only` 配 `--deliver log`（错误路径）
- **输入**: subscribe 请求同时含 `--deliver log` 与 `--deliver-only`
- **期望**: 拒绝创建，error 说明 log-only 直接透传无意义，建议改用真实目标（telegram/discord/slack/github_comment）

### case_004: HMAC 签名不匹配（错误路径）
- **输入**: 上游 POST 携带错误 `X-Hub-Signature-256`
- **期望**: 请求被 401 拒绝；日志/错误信息提示核对 `hermes webhook list` 中的 secret 与上游配置

## 期望输出 (expected/)

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，采用**语义等价判定**：
- `webhook_url` 匹配 `^https?://[a-z0-9./-]+/hooks/[a-z0-9-]+$`
- `secret` 为 40 位十六进制（HMAC-SHA256 摘要长度），且 `hermes webhook list` 输出与落盘 JSON 一致
- Prompt 渲染结果中不得残留未渲染的 `{...}` 占位符
- 错误路径必须 `status: "rejected"` 且 `error.recovery` 非空

## pass_threshold: 0.80

含义：4 个测试用例中，至少 3 个通过（80%）。

### 阈值理由
- **不设 1.0**：webhook_url 主机/端口随环境变化，用正则匹配而非精确值
- **不设 < 0.8**：HMAC 安全校验与签名验证是 Webhook 安全底线（WEBH-004），签名旁路视为 critical 失败
- case_003/004 为错误路径 critical 权重：错误放行（log 透传/签名绕过）直接违反 SKILL Security 小节
