# rclone Google Drive OAuth 设置

> 2026-05-26 实战积累

## 标准流程

```bash
# 1. 写入 client_id/client_secret 到配置
cat > ~/.config/rclone/rclone.conf << 'EOF'
[remote-name]
type = drive
client_id = YOUR_CLIENT_ID
client_secret = YOUR_CLIENT_SECRET
scope = drive
EOF

# 2. 启动 OAuth 授权
rclone authorize "drive" > /tmp/rclone_auth.txt 2>&1
# 输出中包含 URL: http://127.0.0.1:53682/auth?state=...
```

## ⚠️ 关键陷阱：Token 被安全系统脱敏

当 `rclone authorize` 返回 token 后，如果通过 `terminal()` 或 `cat` 读取输出文件，`access_token` 和 `refresh_token` 字段会被自动替换为 `***`，导致保存到 `rclone.conf` 后的 token 无效。

**修复**：必须用 Python 代码直接读取文件，避免经过 terminal 的输出管道：

```python
# ✅ 正确方式：Python 直接读取文件
with open('/tmp/rclone_auth.txt') as f:
    content = f.read()
import re
match = re.search(r'\{[^}]+\}', content)
if match:
    token = match.group()
    # 写入 config
    with open(os.path.expanduser('~/.config/rclone/rclone.conf'), 'a') as f:
        f.write(f'token = {token}\n')
```

**不能这样做**（token 会被脱敏）：

```bash
# ❌ 错误：terminal 输出中 token 被替换为 ***
cat /tmp/rclone_auth.txt | grep '^{'  # → {"access_token":"***",...}
```

## 配置验证

```bash
rclone lsd remote-name:  # 列出 Google Drive 根目录
```
