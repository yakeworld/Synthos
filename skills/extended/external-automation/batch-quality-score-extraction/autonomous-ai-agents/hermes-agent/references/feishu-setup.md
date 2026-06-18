# Feishu / Lark Gateway — Quick Setup

## Local Docs (when website is unreachable)

```bash
~/.hermes/hermes-agent/website/docs/user-guide/messaging/feishu.md
```

## Prerequisites

1. A Feishu/Lark app from the developer console:
   - Feishu China: https://open.feishu.cn/
   - Lark International: https://open.larksuite.com/
2. **App ID** (cli_xxx) and **App Secret** (secret_xxx) from Credentials & Basic Info
3. Enable the **Bot** capability

## Install Dependency (if missing)

Hermes venv may not have lark-oapi installed:

```bash
source ~/.hermes/hermes-agent/venv/bin/activate
pip install --break-system-packages lark-oapi qrcode
```

## Manual Configuration (env vars)

Add to `~/.hermes/.env`:

```bash
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=secret_xxx
FEISHU_DOMAIN=feishu            # feishu (China) or lark (international)
FEISHU_CONNECTION_MODE=websocket   # websocket (default) or webhook

# Optional but recommended
FEISHU_ALLOWED_USERS=ou_xxx,ou_yyy   # comma-separated open_id allowlist
FEISHU_HOME_CHANNEL=oc_xxx            # chat ID for cron/notification output
```

## Config Section (auto-created from env)

The `platform_toolsets.telegram` in `config.yaml` already includes feishu tools. No YAML edits needed if env vars are set.

## Start Gateway

```bash
hermes gateway run        # foreground (test/debug)
hermes gateway install    # systemd user service (persistent)
hermes gateway start
```

Test by messaging the bot in Feishu.

## Common Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| `check_feishu_requirements()` fails | lark-oapi not installed | Run `pip install lark-oapi` in hermes venv |
| Bot doesn't respond in groups | Bot not @-mentioned | Ensure @mention or set `FEISHU_REQUIRE_MENTION=false` |
| `hermes gateway setup` can't be automated | TUI wizard uses prompt_toolkit | Use manual env config instead |
| 200340 on card button clicks | Missing card action event subscription | Subscribe to `card.action.trigger` in Event Subscriptions |

## Gateway is TUI Interactive

`hermes gateway setup` launches a prompt_toolkit wizard — cannot be driven from non-interactive shell (`terminal()` tool). **Always use manual env var config** when setting up via agent tool calls.
