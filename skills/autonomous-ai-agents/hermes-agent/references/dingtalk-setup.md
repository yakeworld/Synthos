# DingTalk (钉钉) Setup Guide

## Prerequisites

### 1. Install Dependencies

```bash
pip3 install --break-system-packages "dingtalk-stream>=0.20"
# httpx should already be installed
```

Verify:
```bash
python3 -c "import dingtalk_stream; print('dingtalk-stream OK')"
python3 -c "import httpx; print('httpx OK')"
```

### 2. Create DingTalk Enterprise Application

1. Log in to [DingTalk Open Platform](https://open-dev.dingtalk.com/) (requires DingTalk admin account)
2. Go to "App Development" → "Enterprise Internal Development" → "Create App"
3. Select "Robot" type
4. In the app's "Credentials & Basic Info" page, get **Client ID** and **Client Secret**
5. In "Messages & Permissions", ensure "Receive Messages" is enabled
6. Publish the app

### 3. Configure Hermes

Set env vars in `~/.hermes/.env`:
```bash
DINGTALK_CLIENT_ID=your-app-key
DINGTALK_CLIENT_SECRET=your-secret
```

Optional config in `~/.hermes/config.yaml`:
```yaml
platforms:
  dingtalk:
    enabled: true
    extra:
      client_id: "your-app-key"
      client_secret: "your-secret"
      # Optional group-chat gating:
      require_mention: true        # bot only responds in groups when @mentioned
      # free_response_chats:       # conversations that skip require_mention
      #   - chat_id_here
      # mention_patterns:          # regex wake-words for group triggers
      #   - "^小马"
      # allowed_users:             # staff_id or sender_id list; "*" = any
      #   - manager1234
      # Card SDK (optional, for AI Cards):
      # card_template_id: "your-template-id"
      # robot_code: "your-robot-code"
```

### 4. Start Gateway

```bash
hermes gateway run        # foreground
hermes gateway install    # install as background service
hermes gateway start      # start if installed
hermes gateway status     # check status
```

## Group Chat Gating (Recommended)

DingTalk adapter supports three levels of group chat filtering:

1. **`allowed_chats`** — Hard whitelist. Only these group chat IDs get processed.
2. **`free_response_chats`** — These chats respond to any message (no @mention needed).
3. **`require_mention`** — Bot only responds when @mentioned (default: true).

When `require_mention: true`, the bot checks `is_in_at_list` on incoming messages (set by dingtalk-stream SDK).

Mention patterns (`mention_patterns`) use regex to match wake-words in message text (fallback if `is_in_at_list` is not set).

## Known Issues

- **Webhook-only DingTalk**: Without Card SDK (`card_template_id` not set), streaming/edited responses are not supported. Only markdown text replies via session webhook.
- **Card SDK packages**: `alibabacloud-dingtalk-card-1_0` and `alibabacloud-dingtalk-robot-1_0` may not be on PyPI. Check [Alibaba Cloud SDK registry](https://github.com/alibabacloud/) for correct package names. If unavailable, Card SDK features are gracefully disabled.
- **`hermes config` doesn't show DingTalk status** by default — check `hermes gateway status` instead.

## Session Webhook Cache

DingTalk's stream mode sends messages with a `session_webhook` URL. The adapter caches these URLs per chat_id (max 500) with expiry tracking to ensure replies go to the correct destination. Stale webhooks are cleaned up on first use.
