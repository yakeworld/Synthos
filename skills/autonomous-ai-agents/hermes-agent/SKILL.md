---
name: herm
## 原理层·文言

> 文以验法，技乃所产。Configure, extend, or contribute to Hermes Agent — the open-source AI agent framework by Nous Res...。
es-agent
description: Configure, extend, or contribute to Hermes Agent — the open-source AI agent framework by Nous Research.
allowed-tools:
- terminal
- file
- web
license: MIT
metadata:
  synthos:
    version: 2.1.0
    author: Synthos
    signature: 'query: str -> config_change: dict'
---

# Hermes Agent

Hermes Agent runs in terminal, messaging platforms, and IDEs. Works with any LLM provider (OpenRouter, Anthropic, OpenAI, DeepSeek, local models).

## Quick Install

```bash
pip install hermes-agent  # or pipx
hermes setup               # interactive setup

# or manual:
hermes config set provider openrouter
hermes config set model openrouter/anthropic/claude-sonnet-4
hermes config set api_key "sk-..."
```

## Key Commands

| 功能 | 命令 |
|:-----|:------|
| 运行 | `hermes` (交互式) / `hermes run "prompt"` |
| 技能列表 | `hermes skills list` |
| 技能加载 | `hermes skills load <name>` |
| 技能创建 | `hermes skills create <name>` |
| 工具配置 | `hermes config set tools.<name> <value>` |
| Agent spawn | `hermes agent spawn <name> --provider ... --model ...` |
| Cron job | `hermes cron create --name "job" --prompt "..." --schedule "..."` |

## Provider Config

```yaml
# ~/.hermes/config.yaml
provider: openrouter        # anthropic, openai, deepseek, custom
model: anthropic/claude-sonnet-4
api_key: "${HERMES_API_KEY}"  # 环境变量引用
```

See `references/provider-setup.md` for full 15+ provider configs.

## Skills Directory

```yaml
# 外部技能目录
skills:
  external_dirs:
    - /media/yakeworld/sda2/Synthos/skills
```

## Multi-Agent Spawning

```bash
# 子Agent
hermes agent spawn researcher --provider anthropic --model claude-sonnet-4
hermes agent spawn coder --provider openai --model gpt-4o

# 后台任务
hermes run "analyze this" --background --notify-on-complete
```

## Cost Optimization (本地优先)

**铁律：cron 无 memory 后端。** `memory` 工具在 cron 模式不可用。定时任务依赖 memory 会空跑。用 no_agent 脚本或文件替代。

### Provider 优先级策略

```yaml
# 默认用本地 → 省成本
model:
  default: qwen3.6-35b-nvfp4
  provider: custom:amax
  base_url: http://100.100.252.99:8000/v1
  api_key: EMPTY

# DeepSeek 保留作按需调用
providers:
  deepseek:
    base_url: https://api.deepseek.com/v1
    api_key: DEEPSEEK_API_KEY

# 自定义本地 provider
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

**cron job 模型覆盖规则：**
- `model: null, provider: null` → 继承全局默认（本地优先即全部走本地）
- `model: qwen..., provider: deepseek` → 模型名对但 provider 错误 → 空耗 API 费用
- 显式设 `provider: custom:amax` 确保走本地
- 需要 DeepSeek 时临时：`hermes config set model.provider deepseek` 或 job 单独指定

### Delivery 投递

- `deliver: "origin"` 会固化创建时的 receive_id，渠道变更后失效
- 显式指定：`deliver: feishu:yake_local`
- 脚本类 job（no_agent）用 `deliver: local`

## Reference Files

- `references/provider-setup.md` — 15+ provider configs + custom/local provider patterns
- `references/gateway-setup.md` — Gateway configuration
- `references/tui-commands.md` — TUI slash commands
- `references/agent-spawning.md` — Multi-agent spawning patterns
- `references/cron-setup.md` — Cron job creation, management, pitfalls
- `references/voice-setup.md` — Voice/text-to-speech setup
