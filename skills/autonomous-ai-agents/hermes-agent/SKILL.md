---
name: hermes-agent
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

## Reference Files

- `references/provider-setup.md` — 15+ provider configs
- `references/gateway-setup.md` — Gateway configuration
- `references/tui-commands.md` — TUI slash commands
- `references/agent-spawning.md` — Multi-agent spawning patterns
- `references/cron-setup.md` — Cron job creation and management
- `references/voice-setup.md` — Voice/text-to-speech setup
