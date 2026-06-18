# Codex CLI 调用本地 vLLM 模型 — 调试记录与结论

> **最终结论**：Codex CLI (v0.139.0) **无法用于本地模型**。硬编码 OpenAI API 且 `--oss` 模式只支持 `lmstudio`/`ollama`。
> **决策**：2026-06-13 清理完成 — 删除 npm 包、配置、shim、proxy。专注 OpenCode。

## 技术事实

### 1. Codex 硬编码

```
https://api.openai.com/v1/responses  ← 不受 OPENAI_BASE_URL 影响
wss://api.openai.com/v1/responses   ← WebSocket 连接也硬编码
```

配置 `model_providers.generic` 在 `config.toml` 中**不被 Codex 的 rollout 引擎使用**。

### 2. `--oss` 模式限制

Codex 的 `--oss`（open-source sandbox）模式**只接受 `lmstudio` 和 `ollama`** 作为 `--local-provider` 的值。任何自定义 provider 会被拒绝：

```
Error: No default OSS provider configured. Use --local-provider=provider 
or set oss_provider to one of: lmstudio, ollama in config.toml
```

### 3. Shim 本身完全正常

`codex-vllm-shim.py`（port 8789）能正确处理：
- Responses API → Chat Completions 双向转换
- system/developer 消息折叠进 `instructions`
- 工具调用格式翻译（`type:function` 有顶层 `name` → `{type:function, function:{name:...}}`）
- 流式 SSE 响应（`response.created` → `response.completed` 完整链路）

curl 直接测试返回完整 20KB+ 响应。但 **Codex 从未尝试连接 shim**（`ss -tnp` 无 8789 连接记录）。

### 4. 根本原因链

1. Codex 硬编码 OpenAI API URL → 不受任何配置影响
2. Codex 通过 WebSocket 连接 OpenAI API → auth.json 的 `OPENAI_API_KEY` 被发送
3. `--oss` 模式不支持自定义 provider → generic provider 被忽略
4. sandbox 网络策略 `restricted` 进一步阻止 localhost 连接

## 清理记录

2026-06-13 执行完整清理：
- `rm -rf ~/.codex/` — 所有配置和状态
- `npm uninstall -g @openai/codex` — 移除 CLI
- `rm /home/yakeworld/scripts/codex-vllm-shim.py` — 移除 shim
- `rm /home/yakeworld/scripts/codex-vllm-proxy.py` — 移除旧版 proxy
- `rm -rf /home/yakeworld/.mimo2codex/` — 移除中间层

## 替代方案评估

| 方案 | 可行性 | 推荐度 |
|------|--------|--------|
| OpenCode + vLLM | ✅ 已可用 | **首选** |
| Ollama + Codex | ✅ 可行但冗余 | 不推荐 |
| CLIProxyAPI | ✅ 可能 | 需评估 |
| 修改 Codex 源码 | ⚠️ 复杂 | 不推荐 |

**决策**：不追求 Codex。OpenCode 已满足需求。
