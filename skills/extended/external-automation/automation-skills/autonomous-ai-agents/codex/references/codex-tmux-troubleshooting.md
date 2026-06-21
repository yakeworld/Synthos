# Codex tmux 交互与故障排查

## 核心规则

### tmux send-keys 必须分开
Codex TUI 需要 Enter 作为独立 keypress。`send-keys` 同一调用中混发指令+Enter，Enter 被当普通字符，Codex 不响应。

```bash
# 正确
tmux send-keys -t codex-session "指令内容"
sleep 0.5
tmux send-keys -t codex-session Enter

# 错误 — 会卡死
tmux send-keys -t codex-session "指令内容" Enter
```

### 卡死恢复
当 `tmux capture-pane` 看到 `›` 后指令显示但无响应：
1. 重新 `send-keys Enter` — 有时只是 Enter 没被处理
2. 如果无效，`send-keys /stop Enter` 停止当前会话
3. 如果仍然无效，`tmux kill-session -t codex-xxx` 杀掉重建

## 多节点路由

Codex 配置文件在 `~/.codex/`：

| 文件 | 节点 | 地址 | 用途 |
|:-----|:-----|:-----|:-----|
| `config.toml` | 默认 | 100.125.10.93:8000 | 主力 (amax) |
| `amax.config.toml` | amax | 100.125.10.93:8000 | amax 备用 |
| `deepseek.config.toml` | deepseek | api.deepseek.com | 云端 API |
| `fallback.config.toml` | fallback | — | 兜底 |

多节点 tmux 启动方式：

```bash
# 默认节点 (amax)
tmux new-session -d -s codex-default "cd /repo && codex --yolo"

# 指定 base_url
tmux new-session -d -s codex-alt "cd /repo && codex --yolo -c model_provider=vllm -c \"[model_providers.vllm].base_url=http://100.82.27.51:8000/v1\""

# deepseek API
tmux new-session -d -s codex-deepseek "cd /repo && codex --yolo -c model_provider=deepseek"
```

### 节点切换时机
- Codex 卡死 >30 秒无响应 → 检查是否是 vLLM 超时
- vLLM 响应慢 → 杀掉 tmux，用另一节点重建
- 观察：`tmux capture-pane -t codex-xxx -p | tail -20` 看最后输出时间

### tmux 会话管理

```bash
# 查看所有会话
tmux list-sessions

# 查看会话内容
tmux capture-pane -t codex-xxx -p | tail -40

# 发送指令（分两步）
tmux send-keys -t codex-xxx "指令"
sleep 0.5
tmux send-keys -t codex-xxx Enter

# 附着（不推荐，会中断当前 agent）
tmux attach-session -t codex-xxx

# 杀掉会话
tmux kill-session -t codex-xxx
```

## 故障信号

| 症状 | 原因 | 修复 |
|:-----|:-----|:-----|
| `›` 后指令显示但无响应 | Enter 没发 | 重新 send Enter |
| vLLM 404/超时 | 节点挂了/过载 | 切换节点 |
| Codex 一直 "Working" | vLLM 在推理 | 等或 /stop |
| SyntaxError 被捕获 | Codex 自己修 | 继续等 |
