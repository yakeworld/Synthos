---
name: docker-vllm-troubleshoot
description: "Docker vLLM多节点故障排查 — 容器内可访问但外部404、端口映射异常、MTU异常、端口冲突、Triton编译延迟。覆盖work1/work3多节点vLLM实例的稳定性诊断与修复。"
version: 1.0.0
triggers:
  - vLLM Docker容器状态Up但API返回404
  - 容器内curl localhost:8000正常但宿主机curl localhost:8000返回404
  - curl通过容器IP(172.17.x.x)访问返回404
  - vLLM容器启动后长时间无响应
  - Docker daemon.json中MTU异常值导致网络不稳定
  - 多个容器竞争同一端口
metadata:
  synthos:
    priority: P1
    atom_type: troubleshooting
    description: "Docker vLLM多节点故障排查 — 容器内正常/容器外404诊断与修复"
    signature: 'docker-vllm-troubleshoot → port-mapping-diag + mtu-check + port-conflict + startup-timing'

---

# Docker vLLM 多节点故障排查

> 核心场景：vLLM容器状态为Up，容器内curl localhost:8000正常，但宿主机curl localhost:8000或容器IP返回404。

## 诊断步骤

### 1. 快速连通性测试矩阵

```bash
# 容器内localhost（基准）
docker exec <container> curl -s http://localhost:8000/ping
# 期望: 200 OK (空body)
# 注意: vLLM 0.23.0的ping返回200空body，不是"pong"

# 容器内容器IP
docker exec <container> curl -s http://172.17.0.X:8000/ping

# 宿主机localhost
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8000/ping

# 宿主机直接容器IP
curl -s -o /dev/null -w '%{http_code}\n' http://172.17.0.X:8000/ping

# 外部Tailscale/IP
curl -s -o /dev/null -w '%{http_code}\n' http://<host-ip>:8000/ping
```

**判读规则：**
- 全部200 → 正常
- 容器内200但外部404 → **端口映射路由异常**（核心问题）
- 容器内404 → **容器内服务异常**
- 全部连接失败 → **容器未启动或端口未监听**

### 2. 端口映射路由异常诊断

当容器内正常但外部404时：

```bash
# 检查端口绑定是否真的生效
docker port <container>
# 期望: 8000/tcp -> 0.0.0.0:8000

# 检查监听进程（需root或sudo）
sudo ss -tlnp | grep 8000
# 确认是哪个进程监听了8000

# 检查iptables NAT规则（需root）
sudo iptables -t nat -L DOCKER -n -v

# 检查端口是否被其他进程抢占
ss -tlnp | grep 8000
# 如果有非docker的进程绑定8000，需要杀掉或换端口
```

### 3. MTU检查

```bash
# 检查docker0 MTU
ip addr show docker0 | grep mtu
# 检查daemon.json配置
cat /etc/docker/daemon.json | grep mtu

# 正常值: 1500
# work1问题值: 1300（异常值，导致大包静默丢弃）
# 修复: 删除daemon.json中的mtu配置，或删除该字段
```

**MTU问题影响：** 大包TCP段被静默丢弃，连接建立成功但数据传输异常。表现为间歇性404、超时、curl exit code 56。

### 4. 端口冲突检查

```bash
# 查看所有容器的端口映射
docker ps --format '{{.Names}} {{.Ports}}'

# 检查是否有其他容器内部占用相同端口
# 常见冲突: Portainer内部占用8000/tcp（Agent端口）
# 如果多个容器都映射到宿主8000，后启动的会覆盖前一个
```

**修复方案：** 给vLLM换到非冲突端口（如8060），修改docker-compose或启动参数。

### 5. Triton Kernel编译延迟

```bash
# 检查vLLM容器日志是否卡在编译阶段
docker logs <container> --tail 30

# sm_89 GPU (RTX 3090/4090) 编译Triton kernel需要60-120秒
# 期间容器看起来"挂了"，实际在加载模型

# 检查是否卡死（进程还在但长时间无新日志）
docker exec <container> ps aux | grep vllm
```

**处理：** 等待编译完成。如果超过5分钟无进展，检查是否有编译错误。

## Pitfalls

- **vLLM /ping 返回空body而非"pong"**：vLLM 0.23.0的ping是200空响应，不是传统"pong"字符串
- **curl exit code 0但HTTP 404**：`curl -s -o /dev/null -w '%{http_code}'` 即使404也返回exit code 0，不要误判
- **容器内curl localhost和容器IP可能指向不同服务**：如果容器内多个进程监听不同端口，localhost和IP可能路由到不同服务
- **Docker NAT规则可能被其他Docker容器破坏**：Portainer等容器内部端口占用可能干扰NAT表
- **MTU 1300不是bug**：某些网络环境（如跨云平台）需要低MTU，但单机环境1300通常是错误的
- **端口映射的[::] IPv6绑定可能与IPv4冲突**：检查docker port输出是否同时有0.0.0.0和::
- **Tailscale 路由分层**：SSH 连接可能因 Tailscale 路由问题失败但 curl 到 vLLM 端口（8000）正常。这是 Tailscale 的 MagicDNS 和 direct TCP 路由分层导致的——SSH 走不同路径。排查 vLLM 问题时，如果 SSH timeout 但 curl 正常，容器可能仍在线，不要直接判断节点故障。
- **Docker NAT规则可能被其他Docker容器破坏**：Portainer等容器内部端口占用可能干扰NAT表

vLLM 服务器在长时间运行后可能出现吞吐量下降（从 170+ tok/s 降到 30 tok/s 甚至超时），**不是端口问题而是 GPU 调度/OOM 问题**。

```bash
# 快速检测：发送一个简单请求测量吞吐
curl -s http://100.82.27.51:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen3.6-35b-nvfp4","messages":[{"role":"user","content":"Hi"}],"max_tokens":50,"temperature":0.1}' \
  -w "\nTIME:%{time_total}" 2>/dev/null | python3 -c "
import json,sys;
d=json.load(sys.stdin); 
u=d['usage']; 
print(f'tokens={u[\"completion_tokens\"]} time={u.get(\"total_tokens\",0)}')"
```

**判定标准：**
- > 150 tok/s: 正常
- 100-150 tok/s: 注意观察
- < 100 tok/s: 开始异常
- < 50 tok/s: 严重退化
- 超时: 服务器可能 OOM

**常见原因：**
1. GPU 显存碎片化（长时间处理长上下文后）
2. 其他用户请求抢占 GPU 资源
3. vLLM PTH 缓存满了需要重加载
4. 系统级别 OOM killer 介入

**修复方案：**
1. 重启 vLLM 容器（最快）：`docker restart <vllm-container>`
2. 检查 GPU 状态：`nvidia-smi`
3. 如果有备用服务器，切换到备用端点
4. 检查系统日志：`dmesg | tail -20` 看是否有 OOM

## 关联

- `references/work1-vllm-port-mapping-diagnosis.md` — work1端口映射404问题完整诊断记录
- `references/vllm-performance-benchmark.md` — vLLM吞吐量基准测试方法论和跨服务器切换决策
- `llm-model-selection` — Qwen型号辨析、多模态部署方案、显存估算

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。
## 验证清单 · VERIFICATION

1. **输入验证**: {输入条件是否完整}
2. **输出验证**: {输出格式是否符合预期}
3. **边界验证**: {边界条件是否处理}
4. **错误处理**: {异常场景是否覆盖}


## 核心原则 · PRINCIPLES

1. **准确为先**: 所有输出必须经过事实核查，不编造数据
2. **证据驱动**: 每个结论必须可追溯到具体证据或数据源
3. **可复现性**: 每一步操作必须可重复，结果可验证


## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每项验证必须可执行、可记录、可复现。




# Docker Vllm Troubleshoot

