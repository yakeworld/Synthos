# Codex CLI — DeepSeek 兼容性限制

**关键事实：Codex CLI 只能使用 OpenAI Responses API (`wire_api = "responses"`)。** 这限制了可接入的模型供应商。

## 兼容性矩阵

| 供应商 | API 格式 | 是否兼容 Codex | 说明 |
|--------|----------|----------------|------|
| OpenAI | OpenAI Responses API | ✅ 是 | 原生支持 |
| vLLM (本地) | OpenAI Responses API | ✅ 是 | 需 `wire_api = "responses"` + 本地 vLLM 节点 |
| DeepSeek | OpenAI Chat Completions (`/v1/chat/completions`) | ❌ 否 | 不支持 `/v1/responses` 端点 |
| OpenRouter | OpenAI Chat Completions | ❌ 否 | 同上 |
| Google Gemini | 原生 Gemini API | ❌ 否 | 不兼容 OpenAI 协议 |

## 诊断命令

```bash
# 检查 Codex 配置是否有效
codex doctor 2>&1 | grep -E "model|provider|config_path"

# 测试 profile 是否加载
codex -p <profile> doctor 2>&1 | head -20

# 测试实际调用
codex -p <profile> exec "Reply: OK" --yolo 2>&1 | head -10
```

## 错误特征

- `unknown variant \`chat/completions\`, expected \`responses\`` — wire_api 值不合法
- `ERROR: unexpected status 401 Unauthorized: ... /v1/responses` — API 不支持 Responses API
- `ERROR: Missing environment variable: \`...\`` — env_key 指向的环境变量不存在

## 架构决策

Codex 和 DeepSeek 各司其职：

- **Codex CLI** → 仅调本地 vLLM 模型（支持 responses API）→ 编码任务主力
- **Cron Agent** → 可调用 DeepSeek（通过 provider 配置）→ 推理/研究任务
- **OpenCode** → 支持 OpenAI 兼容 API（chat/completions）→ 可调用 DeepSeek

不要尝试将 DeepSeek 接入 Codex — 协议不兼容。