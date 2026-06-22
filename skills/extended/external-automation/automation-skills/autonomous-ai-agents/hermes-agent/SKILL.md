---

name: hermes-agent
related_skills: []
description: Configure, extend, or contribute to Hermes Agent — the open-source AI agent framework by Nous Research.
version: 1.0.0
allowed-tools:
- terminal
- file
- web
license: MIT
author: Synthos
metadata:
  synthos:
    version: 2.1.0
    author: Synthos
    signature: 'query: str -> config_change: dict'


---


## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）



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

## Key Commands (v0.15.2)

| 功能 | 命令 |
|:-----|:------|
| 交互式运行 | `hermes` |
| 单次运行 | `echo "prompt" \| hermes chat`（管道模式） |
| 技能列表 | `hermes skills list` |
| 技能加载 | `hermes skills load <name>` |
| 技能创建 | `hermes skills create <name>` |
| 工具配置 | `hermes config set tools.<name> <value>` |
| Agent spawn | `hermes agent spawn <name> --provider ... --model ...` |
| Cron job | `hermes cron create --name "job" --prompt "..." --schedule "..."` |

**注意**: `hermes run` 在 v0.15.2 已移除。用 `echo "prompt" | hermes chat` 或 interactive 模式替代。

## Provider Config

```yaml
# ~/.hermes/config.yaml
# 本地 vLLM 配置（最常用）
model:
  default: qwen3.6-35b-nvfp4
  provider: custom:local

custom_providers:
- name: local
  base_url: http://localhost:8000/v1
  api_key: EMPTY
  model: qwen3.6-35b-nvfp4
```

远程 provider 见 `references/provider-setup.md`。

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

# DeepSeek 保留作按需调用 — ⚠️ api_key 必须用 ${} 包裹
providers:
  deepseek:
    base_url: https://api.deepseek.com/v1
    api_key: ${DEEPSEEK_API_KEY}

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

### Codex CLI 远程部署
远程部署 Codex CLI（如 work1 服务器）见 `codex-cli` 技能。关键要点：
- 环境变量必须放在 `~/.codex/.env`（codex exec 不 source .bashrc）
- SSH 传递敏感值用 base64 编码，避免引号嵌套破坏
- `codex exec --skip-git-repo-check` 用于非 git 目录执行
- 部署后用 `codex doctor` 验证，`codex exec "echo test"` 验证连通性

### Delivery 投递

- `deliver: "origin"` 会固化创建时的 receive_id，渠道变更后失效
- 显式指定：`deliver: feishu:yake_local`
- 脚本类 job（no_agent）用 `deliver: local`

## Reference Files

- `references/provider-setup.md` — 15+ provider configs + custom/local provider patterns + env-var-ref trap
- `references/env-var-ref-trap.md` — .env 环境变量引用陷阱：config.yaml 中 `api_key` 必须用 `${VAR}` 包裹，裸字符串不被 `_expand_env_vars()` 展开
- `references/gateway-setup.md` — Gateway configuration
- `references/tui-commands.md` — TUI slash commands
- `references/agent-spawning.md` — Multi-agent spawning patterns
- `references/cron-setup.md` — Cron job creation, management, pitfalls
- `references/voice-setup.md` — Voice/text-to-speech setup
