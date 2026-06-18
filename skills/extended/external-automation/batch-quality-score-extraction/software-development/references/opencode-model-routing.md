# opencode 多模型路由配置与陷阱

## 架构概览

opencode 使用 `~/.config/opencode/opencode.json` 配置多提供商模型路由：

```json
{
  "provider": {
    "hermes": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Hermes vLLM",
      "options": { "baseURL": "http://100.125.10.93:8000/v1", "apiKey": "opencode_local" },
      "models": { "qwen3.6-35b-nvfp4": { "name": "Hermes Qwen3.6 35B", "tools": true } }
    },
    "deepseek": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "DeepSeek",
      "options": { "baseURL": "https://api.deepseek.com/v1", "apiKey": "DEEPSEEK_API_KEY" },
      "models": { "deepseek-v4-flash": { "name": "DeepSeek V4 Flash", "tools": true },
                  "deepseek-v4-pro": { "name": "DeepSeek V4 Pro", "reasoning": true } }
    }
  },
  "model": "hermes/qwen3.6-35b-nvfp4"  // 默认提供商/模型
}
```

## 关键陷阱

### 陷阱 1：apiKey 是字面字符串，非环境变量引用

`opencode.json` 中的 `"DEEPSEEK_API_KEY"` 是**字面字符串**（占位符），opencode 不会自动去环境变量读取 `DEEPSEEK_API_KEY`。

- **症状**：配置写好了，API key 也在 `.env` 里设了，调用时报认证失败。
- **修复**：必须把真实 API key 直接写入 `opencode.json` 的 `"apiKey"` 字段，或通过 `export DEEPSEEK_API_KEY=real_key` 后用 `${DEEPSEEK_API_KEY}` 格式（如果 opencode 支持 dotenv-expand）。

### 陷阱 2：Hermes Agent 与 opencode 路由完全独立

- **Hermes Agent**：默认模型在 `~/.hermes/config.yaml` 的 `model.default` 中配置，走 `~/.hermes/.env` 中的 API key。
- **opencode**：模型路由在 `opencode.json` 中独立配置，走 `~/.config/opencode/opencode.json`。
- **二者不互通**：Hermes cron 任务不会自动使用 opencode 的模型配置，反之亦然。

要让 Hermes cron 使用 DeepSeek：
1. 在 `~/.hermes/config.yaml` 中添加 DeepSeek 作为 provider
2. 或在 `~/.hermes/.env` 中设置 `DEEPSEEK_API_KEY` 并配置 baseURL
3. 或在 opencode 中配置 `HERMES_DEFAULT_MODEL=deepseek/deepseek-v4-flash`

### 陷阱 3：oh-my-openagent 插件不自动同步 API key

opencode 的 `oh-my-openagent` 插件（`plugin: ["oh-my-openagent@latest"]`）提供额外的模型发现功能，但：
- 模型发现 ≠ API key 注入
- `provider-models.json` 和 `model-capabilities.json` 只缓存模型元数据
- 真实 API key 仍需手动配置在 `opencode.json` 或环境变量中

## 验证方法

```bash
# 1. 测试 API key 是否有效
curl -s https://api.deepseek.com/v1/models -H 'Authorization: Bearer YOUR_KEY'

# 2. 检查 opencode 配置是否加载
cat ~/.config/opencode/opencode.json | python3 -m json.tool

# 3. 检查环境变量是否设置
env | grep DEEPSEEK
```

## 清理决策

Codex CLI 已被彻底移除（2026-06-13）：
- `@openai/codex` npm 包已删除
- `codex-vllm-shim.py` 已删除
- `codex-vllm-proxy.py` 已删除
- `~/.codex/` 配置目录已删除
- `~/.mimo2codex/` 数据目录已删除

**原因**：Codex CLI 硬编码 `https://api.openai.com/v1/responses`，本地 vLLM 只提供 Chat Completions，需要中间 shim。且与 OpenCode 功能重叠，维护成本高。OpenCode 作为主要本地模型调用工具。
