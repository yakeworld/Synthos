# Tailscale Exit Node — NotebookLM 连通性修复

## 场景
NotebookLM CLI 返回超时/网络错误。Google 服务被本地网络限制（如校园网/医院内网）。

## 修复命令

```bash
# 1. 查看可用 exit node
tailscale status | grep "exit node"

# 2. 启用 exit node（需要 sudo）
sudo tailscale set --exit-node=<exit-node-ip>

# 3. 验证连通性
curl -s -o /dev/null -w "%{http_code}" https://www.google.com
# 应返回 200

# 4. 验证 NotebookLM
notebooklm list
# 应返回笔记本列表

# 5. 关闭 exit node（用完可关）
sudo tailscale set --exit-node=
```

## 注意事项
- 需要 `sudo` 权限（或 `sudo tailscale set --operator=$USER`）
- Exit node 需要在线（`tailscale status` 显示 `active`）
- 启用后所有外网流量走 exit node，可能比直连慢
- `notebooklm login --browser-cookies` 也需要外网连通性
