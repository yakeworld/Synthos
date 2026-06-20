# Provider 配置

## 核心原则：本地优先

```yaml
# ~/.hermes/config.yaml
model:
  default: qwen3.6-35b-nvfp4
  provider: custom:amax
  base_url: http://100.100.252.99:8000/v1
  api_key: EMPTY
```

**交互会话默认走本地模型**，需要高质量推理时临时切到 DeepSeek API。

## 自定义本地 Provider（vLLM）

```yaml
custom_providers:
- name: amax
  base_url: http://100.100.252.99:8000/v1
  api_key: EMPTY
  model: qwen3.6-35b-nvfp4
- name: amax-fallback
  base_url: http://100.82.27.51:8000/v1
  api_key: EMPTY
  model: qwen3.6-35b-nvfp4
```

使用方式：
```bash
# 临时指定 provider
hermes --provider custom:amax

# cron job 指定
hermes cron update JOB_ID \
  --model '{"model":"qwen3.6-35b-nvfp4","provider":"custom:amax"}'
```

## 云 Provider 配置

```yaml
providers:
  deepseek:
    base_url: https://api.deepseek.com/v1
    api_key: DEEPSEEK_API_KEY

  openrouter:
    base_url: https://openrouter.ai/api/v1
    api_key: OPENROUTER_API_KEY

  anthropic:
    base_url: https://api.anthropic.com/v1
    api_key: ANTHROPIC_API_KEY
```

### 按需切到 DeepSeek

```bash
# 整会话切换
hermes config set model.provider deepseek

# 单条指令
hermes run "复杂任务..." --provider deepseek --model deepseek-v4-flash

# 当前会话内临时切换
hermes config set model.provider deepseek
hermes config set model.deepseek-v4-flash
# 用完切回
hermes config set model.provider custom:amax
```

## 上下文压缩模型

```yaml
# config.yaml
compression:
  provider: deepseek
  model: deepseek-v4-flash
  base_url: https://api.deepseek.com/v1
  api_key: ${DEEPSEEK_API_KEY}
```

压缩任务轻量，也可切到本地模型：
```yaml
compression:
  provider: custom:amax
  model: qwen3.6-35b-nvfp4
  base_url: http://100.100.252.99:8000/v1
  api_key: EMPTY
```

## 各子服务模型参考

| 服务 | provider | model | 说明 |
|:-----|:---------|:------|:-----|
| delegation | custom:amax | qwen3.6-35b-nvfp4 | 子Agent |
| session_search | custom:amax-fallback | qwen3.6-35b-nvfp4 | 搜索 |
| approval | custom:amax | qwen3.6-35b-nvfp4 | 审批 |
| compression | deepseek | deepseek-v4-flash | 上下文压缩 |
| default | custom:amax | qwen3.6-35b-nvfp4 | 交互会话 |

## ⚠️ 陷阱

1. **cron job 的 provider 覆盖不是可选的。** 如果 cron job 明确写了 `provider: deepseek`，即使模型名是本地模型，仍会走 DeepSeek API 并失败或空耗费用。必须同时改 model 和 provider。

2. **`api_key: EMPTY` 适用于本地 vLLM。** vLLM 默认不验证 API key，但 Hermes 需要非空值。用 `EMPTY` 作为占位符。

3. **`fallback_providers` 仅触发于限流/服务错误。** 不是高可用切换，而是故障应急。

4. **自定义 provider 名不能重复。** `custom_providers` 中的 name 在 providers 命名空间下以 `custom:` 前缀引用。

5. **`.env` 和 shell 环境变量是隔离的。** `~/.hermes/.env` 由 Hermes 的 honcho loader 在启动时 source，shell 的 `env` 看不到它。配置中 `api_key: DEEPSEEK_API_KEY` 是变量引用，Hermes 从 `.env` 解析，不是字面字符串值。shell 里 `echo $DEEPSEEK_API_KEY` 为空不代表 key 没配置。

6. **验证 API key 的方法。** 用 curl 或 python urllib 直接调 endpoint：
   ```bash
   curl -s -X POST https://api.deepseek.com/v1/chat/completions \
     -H "Authorization: Bearer YOUR_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model":"deepseek-v4-flash","messages":[{"role":"user","content":"OK"}],"max_tokens":5}'
   ```
   返回 JSON 且含 `choices` 字段 → key 有效。返回 401 → key 无效或过期。返回 404 → endpoint 不对。超时 → 网络问题。
