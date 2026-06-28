---

name: feishu-gateway-debug
related_skills:
- hermes-agent
- github
description: 飞书 Gateway 消息流诊断与排障 — 从用户消息到 agent 响应的全链路追踪。覆盖 404 根因、消息流路径、agent session 分离、日志定位。
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
    signature: 'query: str -> debug_trace: dict'


---

## IO_CONTRACT

- **input**: `error_msg: str, session_id: str, platform: str` — 用户报告的错误、会话ID、平台
- **output**: `diagnosis: str` — 问题根因 + 修复建议

## 触发条件

用户报告飞书消息无响应 / 报错 / API call failed / 404 / 发送失败。

## 诊断流程

### Step 1: 区分错误来源

**关键认知：Gateway 处理两种独立 session：**
- **CLI 会话**：`agent:main:cli:xxx` — 直接通过 `hermes` 命令行启动
- **飞书会话**：`agent:main:feishu:dm:<chat_id>` — 通过飞书 WebSocket 接收

两种 session 完全隔离，CLI 报错不影响飞书，反之亦然。

**错误来源判断：**
```
api call failed + 模型名 + base_url=http://X.X.X.X:8000  → vLLM 节点问题，非飞书
api call failed + open.feishu.cn  → 飞书 API 网络问题
api call failed + api.deepseek.com → DeepSeek API 问题
```

### Step 2: 追踪完整消息流

按时间顺序检查以下三处日志：

**1. Gateway 日志（入口→出口）：**
```bash
tail -50 ~/.hermes/logs/gateway.log | grep -E "2026-06-20 21:2[5-9]|21:3"
```
关键行：
- `Received raw message` — 飞书收到消息
- `Inbound dm message received` — 消息解析完成
- `Flushing text batch agent:main:feishu:dm:...` — 提交 agent 会话
- `inbound message: platform=feishu` — Gateway 确认收到
- `response ready: platform=feishu time=X.Xs api_calls=N` — 响应生成
- `Sending response (X chars) to <chat_id>` — 推送飞书

**一条成功消息的完整时间线：**
```
21:25:25 Received raw message → 飞书收到
21:25:32 Flushing text batch → 提交 agent (7s)
21:25:37 inbound message → 确认 (5s)
21:25:38 response ready time=1.2s → 模型响应 (0.6s)
21:25:39 Sending response → 推送飞书 (0.1s)
总耗时: ~14s (含网络延迟和模型推理)
```

**2. Agent 日志（模型调用细节）：**
```bash
grep "<session_id>" ~/.hermes/logs/agent.log | grep "2026-06-20 <time>"
```
关键行：
- `conversation turn: session=<id> model=<model> provider=<provider> platform=feishu` — 会话开始
- `API call #N: model=<model> provider=<provider> in=<tokens> out=<tokens> latency=<X>s` — 模型调用
- `Turn ended: reason=text_response(finish_reason=stop)` — 成功结束
- `API call failed (attempt N/3)` — 失败重试
- `Non-retryable client error` — 不可恢复错误

**3. Errors 日志（所有警告/错误汇总）：**
```bash
tail -30 ~/.hermes/logs/errors.log
```

### Step 3: 常见错误根因

#### vLLM 404 (最常见)
```
HTTP 404: Not found
provider=custom base_url=http://100.125.10.93:8000/v1 model=qwen3.6-35b-nvfp4
```
- 模型在该节点不存在（已删除/改名）
- 检查节点：`curl -s http://<ip>:8000/v1/models`
- 修复：从轮询配置移除该节点或修正模型名

#### DeepSeek 401
```
HTTP 401: Authentication Fails / Invalid API key
provider=deepseek base_url=https://api.deepseek.com/v1
```
- API Key 过期或错误
- 检查 `.env` 中 `DEEPSEEK_API_KEY`

#### 网络问题
```
NameResolutionError: Failed to resolve 'open.feishu.cn'
HTTPSConnectionPool(host='open.feishu.cn', port=443): Max retries exceeded
```
- DNS 解析失败
- 检查 Tailscale / 网络路由
- 验证：`curl -s -o /dev/null -w "%{http_code}" https://open.feishu.cn`

#### Stream 断开
```
RemoteProtocolError: peer closed connection without sending complete message body
http_status=200 bytes=0 chunks=0 elapsed=180.07s
```
- vLLM 服务超时（默认 180s）
- 模型响应过长或节点负载高

#### execute_code 超时
```
Script timed out after 300s and was killed
```
- 代码执行超时（默认 300s）
- 检查是否有阻塞操作

### Step 4: 报告成功消息的典型响应

成功处理飞书消息时，响应通常是简洁的（50-182 chars），如：
- "Hello, I'm here. How can I help you today?"
- "Hello, what's up?"

如果用户报告的 "api call failed" 不是来自日志，请确认：
1. 是在 CLI 还是飞书看到的？
2. 是哪条消息报的错？
3. 错误是立即出现还是延迟后出现？

## 排障清单

- [ ] Gateway 是否在运行？`ps aux | grep hermes-gateway`
- [ ] WebSocket 是否连接？`tail ~/.hermes/logs/gateway.log | grep "connected"`
- [ ] 飞书消息是否到达 Gateway？`tail ~/.hermes/logs/gateway.log | grep "Received raw message"`
- [ ] 是否提交到 agent session？`tail ~/.hermes/logs/gateway.log | grep "Flushing text batch"`
- [ ] Agent session 是否创建/恢复？`grep "conversation turn" ~/.hermes/logs/agent.log | tail`
- [ ] 模型调用是否成功？`grep "API call" ~/.hermes/logs/agent.log | tail`
- [ ] 响应是否返回 Gateway？`grep "response ready" ~/.hermes/logs/gateway.log | tail`
- [ ] 响应是否发送到飞书？`grep "Sending response" ~/.hermes/logs/gateway.log | tail`

## 关键发现（2026-06-20）

1. **Gateway 日志是最高优先级**：Gateway 完整记录了消息从接收→处理→回复的全链路，且只记录成功消息。失败会被捕获在 errors.log。
2. **404 多数来自 vLLM 而非飞书**：用户报告的 "404" 多数是模型节点返回的，不是飞书 API。需先检查 `base_url` 指向哪个服务。
3. **CLI 和飞书 session 隔离**：CLI 的 `execute_code` 超时不会阻塞飞书会话。两个平台各自维护独立 session。


## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

### MEDIA 文件附件发送（Feishu 交付模式）

完整的 MD→PDF→Feishu 管线见 `references/pdf-delivery-pipeline.md`。

### 发送格式
在响应文本中直接包含 `MEDIA:/absolute/path/to/file`，运行时自动上传为附件。每行一个文件。

### 铁律
1. **路径验证优先**：发送前务必 `ls -la /path/to/file` 确认文件真实存在。路径错误=静默失败。
2. **避开 /tmp/**：Hermes MEDIA 处理器可能无法访问 /tmp/ 目录。文件放 ~/ 或 /media/ 等稳定路径。
3. **先回应再发**：用户下达命令后，先回复「收到」确认，再执行操作。不无声执行。
4. **复用成功案例**：同类型任务（如发送PDF）的交付模式与之前成功案例一致的，直接照搬，不猜新花样。失败排查路径：用 search_files 查正确路径→确认文件存在→用已验证路径重发。

### 文件大小限制
**飞书 MEDIA 附件 >10MB 会静默失败**（不显示附件、不报错）。PPTX 转 PDF 后通常 30-80MB，必须压缩。

**压缩流程**（Ghostscript）：
```bash
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/screen -dNOPAUSE -dQUIET -dBATCH -sOutputFile=/path/to/output.pdf /path/to/input.pdf
```
典型效果：33MB → 2.4MB（screen 质量对文档可读性足够，图片/扫描件可能偏模糊）。

**其他 PDFSETTINGS 级别**：
- `/screen` — 72dpi，最小文件（适合文档）
- `/ebook` — 150dpi，平衡质量
- `/prepress` — 300dpi，最大文件

### 排查流程
用户反馈没收到附件时：
1. `ls -la <路径>` 确认文件存在
2. 检查文件大小 — 超过 10MB → 用 gs 压缩
3. 压缩后确认新文件 ≤10MB
4. 用新路径重新发送
5. 若不存在 → `search_files(pattern='*文件名*', target='files')` 找正确路径
6. 修正路径后重发
