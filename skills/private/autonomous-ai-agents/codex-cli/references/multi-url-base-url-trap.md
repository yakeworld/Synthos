# Codex `base_url` 多 URL 逗号分隔陷阱（2026-06-21）

**问题**: `~/.codex/config.toml` 中 `[model_providers.vllm].base_url` 若设为逗号分隔的多 URL（如 `http://a/v1,http://b/v1`），Codex 不会轮询，而是将整个字符串当作一个 URL 发送请求，导致 **HTTP 404**。

**症状**:
```
codex doctor:
  ✗ reachability provider base URL route returned 404
  vllm API base URL: http://100.100.252.99:8000/v1,http:/<redacted>
```

**修复**: base_url 必须为单 URL。多节点负载均衡应通过以下方式实现：
1. 设置 `base_url` 为单节点（首选节点）
2. 需要切换时修改 `~/.codex/config.toml` 或环境变量
3. 代码层通过环境变量/自定义逻辑做负载均衡

**验证**: `codex doctor` 中 `reachability` 行应显示 `✓`，`17 ok · 0 fail`。

**本次会话修复记录**: base_url 从 `100.100.252.99:8000/v1,100.125.10.93:8000/v1,100.82.27.51:8000/v1` → `100.125.10.93:8000/v1`。三节点 curl 全部可达，仅 Codex 自身不处理多 URL。
