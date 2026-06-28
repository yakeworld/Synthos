# 错误模式速查表

## 模式 1: vLLM 节点 404
```
ERROR agent.conversation_loop: API call failed after 3 retries. 
HTTP 404: Not found | provider=custom base_url=http://100.125.10.93:8000/v1 model=qwen3.6-35b-nvfp4
```
- **根因**：节点模型不存在
- **验证**：`curl -s http://<ip>:8000/v1/models`
- **修复**：从 config.toml/config.yaml 移除节点或修正模型名

## 模式 2: DeepSeek 认证失败
```
ERROR agent.conversation_loop: API call failed (attempt 1/3) 
error_type=AuthenticationError ... provider=deepseek ... 
summary=HTTP 401: Authentication Fails, Your api key: ****_KEY is invalid
```
- **根因**：API Key 无效
- **修复**：检查 `~/.hermes/.env` 中 DEEPSEEK_API_KEY

## 模式 3: 飞书 DNS 解析失败
```
ERROR gateway.platforms.feishu: HTTPSConnectionPool(host='open.feishu.cn', port=443): 
Max retries exceeded ... NameResolutionError("Failed to resolve 'open.feishu.cn'")
```
- **根因**：DNS 不可用 / Tailscale 未配置
- **验证**：`nslookup open.feishu.cn` / `curl -s https://open.feishu.cn`
- **修复**：配置 Tailscale Exit Node 或修复 DNS

## 模式 4: Stream 断开 (HTTP 200 但零内容)
```
WARNING agent.stream_diag: Stream drop on attempt 2/3 — retrying. 
http_status=200 bytes=0 chunks=0 elapsed=180.07s
```
- **根因**：vLLM 服务端超时或断开
- **修复**：检查 GPU 负载 / 增加超时 / 切换节点

## 模式 5: execute_code 超时
```
WARNING tools.code_execution_tool: execute_code timed out after 300.18s
```
- **根因**：代码执行超过 300s 限制
- **修复**：优化代码 / 减少数据集 / 增加超时

## 模式 6: 无报错但无响应
- 检查 Gateway 进程是否存在
- 检查 WebSocket 是否连接 (`grep "connected" gateway.log`)
- 检查 Agent session 是否被缓存驱逐 (`grep "evict" gateway.log`)
