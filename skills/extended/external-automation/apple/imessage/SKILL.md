---
name: imessage
description: "Use `imsg` to read and send iMessage/SMS via macOS Messages.app."
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "task_desc: str, params: dict -> result: dict"
    atom_type: skill
    priority: P2
    related_skills: []

---




## IO_CONTRACT

- **input**: `recipient: str, message: str` — 用户请求描述、上下文信息
- **output**: `sent_status: dict — iMessage`

> 对应原则：P2（机械原子暴露输入输出规范）


# iMessage

Use `imsg` to read and send iMessage/SMS via macOS Messages.app.

## Prerequisites

- **macOS** with Messages.app signed in
- Install: `brew install steipete/tap/imsg`
- Grant Full Disk Access for terminal (System Settings → Privacy → Full Disk Access)
- Grant Automation permission for Messages.app when prompted

## When to Use

- User asks to send an iMessage or text message
- Reading iMessage conversation history
- Checking recent Messages.app chats
- Sending to phone numbers or Apple IDs

## When NOT to Use

- Telegram/Discord/Slack/WhatsApp messages → use the appropriate gateway channel
- Group chat management (adding/removing members) → not supported
- Bulk/mass messaging → always confirm with user first

## Quick Reference

### List Chats

```bash
imsg chats --limit 10 --json
```

### View History

```bash
# By chat ID
imsg history --chat-id 1 --limit 20 --json

# With attachments info
imsg history --chat-id 1 --limit 20 --attachments --json
```

### Send Messages

```bash
# Text only
imsg send --to "+14155551212" --text "Hello!"

# With attachment
imsg send --to "+14155551212" --text "Check this out" --file /path/to/image.jpg

# Force iMessage or SMS
imsg send --to "+14155551212" --text "Hi" --service imessage
imsg send --to "+14155551212" --text "Hi" --service sms
```

### Watch for New Messages

```bash
imsg watch --chat-id 1 --attachments
```

## Service Options

- `--service imessage` — Force iMessage (requires recipient has iMessage)
- `--service sms` — Force SMS (green bubble)
- `--service auto` — Let Messages.app decide (default)

## Rules

1. **Always confirm recipient and message content** before sending
2. **Never send to unknown numbers** without explicit user approval
3. **Verify file paths** exist before attaching
4. **Don't spam** — rate-limit yourself

## Example Workflow

User: "Text mom that I'll be late"


## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引


## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

```bash
# 1. Find mom's chat
imsg chats --limit 20 --json | jq '.[] | select(.displayName | contains("Mom"))'

# 2. Confirm with user: "Found Mom at +1555123456. Send 'I'll be late' via iMessage?"

# 3. Send after confirmation
imsg send --to "+1555123456" --text "I'll be late"
```
