---
name: vllm-cluster-management
description: "vLLM多节点集群部署与配置 — 在多个服务器节点上部署vLLM服务，统一配置Hermes/Codex的provider路由，实现负载均衡和故障转移。覆盖多节点vLLM实例的配置、验证、路由策略和故障切换。"
version: 1.0.0
triggers:
  - 需要在多个节点上配置vLLM模型服务
  - 为Hermes或Codex配置多节点base_url负载均衡
  - 添加/删除vLLM节点到provider路由
  - 多节点vLLM集群一致性检查
metadata:
  synthos:
    priority: P1
    atom_type: devops
    description: "vLLM多节点集群配置与路由管理"
    signature: 'vllm-cluster-mgmt → provision → verify → route → balance'

---

# vLLM 多节点集群管理

> 核心目标：在多节点上部署相同的vLLM模型，配置Hermes和Codex实现自动故障转移。

## 前置条件

- 所有节点运行相同模型（如 qwen3.6-35b-nvfp4）
- 所有节点端口一致（默认 8000）
- 所有节点可通过 Tailscale 网络访问
- 已配置 VLLM_API_KEY 环境变量

## 步骤

### 1. 节点连通性验证

对每个新节点执行：

```bash
# 基础连通性
curl -s http://<IP>:8000/v1/models | python3 -m json.tool

# 期望返回：
# {
#   "data": [{
#     "id": "qwen3.6-35b-nvfp4",
#     "object": "model",
#     "max_model_len": 262144
#   }]
# }
```

全部节点必须返回相同模型ID和相同 max_model_len。

### 2. 更新 Codex 配置

修改 `~/.codex/config.toml`，将新节点加入 `base_url`（逗号分隔）：

```toml
[model_providers.vllm]
base_url = "http://100.100.252.99:8000/v1,http://100.125.10.93:8000/v1,http://100.82.27.51:8000/v1"
```

顺序决定轮询优先级。将新节点放在列表最前作为首选。

### 3. 更新 Hermes config.yaml

修改 `~/.hermes/config.yaml`，在 `custom_providers` 中添加新节点：

```yaml
custom_providers:
  - name: amax
    base_url: "http://100.100.252.99:8000/v1"
    api_key: "EMPTY"
    model: "qwen3.6-35b-nvfp4"
  - name: amax-1
    base_url: "http://100.125.10.93:8000/v1"
    api_key: "EMPTY"
    model: "qwen3.6-35b-nvfp4"
  - name: amax-fallback
    base_url: "http://100.82.27.51:8000/v1"
    api_key: "EMPTY"
    model: "qwen3.6-35b-nvfp4"
```

同时更新：
- `model.provider` → 指向主节点（如 `custom:amax`）
- `delegation.provider` → 指向主节点
- `auxiliary.compression.provider` → 指向主节点
- `auxiliary.approval.provider` → 指向主节点
- `auxiliary.session_search.provider` → 备用节点（如 `custom:amax-fallback`）
- `auxiliary.vision` → **必须指向支持 vision 的节点**（当前为 `custom:amax-1`）。先运行 `scripts/test-vision-capability.py` 确认。

### 4. 路由策略（经验规则）

基于历史经验：

| 服务 | 推荐节点 | 理由 |
|---|---|---|
| 主交互 | 最新/最快节点 | 延迟敏感 |
| 子Agent委托 | 同主节点 | 一致性 |
| 压缩/审批 | 同主节点 | 一致性 |
| session_search | 备用节点 | 隔离、可并发 |
| Cron重度任务 | DeepSeek云端 | 不占用本地资源 |

### 5. 最终验证

```bash
# 所有节点模型一致
for ip in 100.100.252.99 100.125.10.93 100.82.27.51; do
  echo "=== $ip ==="
  curl -s http://$ip:8000/v1/models | python3 -c "
import json,sys; d=json.load(sys.stdin); 
m=d['data'][0]; print(f'{m[\"id\"]} ctx={m.get(\"max_model_len\",\"\")}')  "
done

# Codex配置检查
grep 'base_url' ~/.codex/config.toml

# Hermes配置检查
python3 -c "
import yaml; c=yaml.safe_load(open('/home/yakeworld/.hermes/config.yaml'))
for p in c['custom_providers']: print(f\"{p['name']}: {p['base_url']}\")"
```

## Pitfalls
## Pitfalls

- **模型版本不一致**：添加节点前必须验证模型ID和max_model_len与现有节点完全一致，否则Codex/Hermes可能路由到不兼容节点
- **base_url顺序**：Codex按顺序轮询，第一个节点故障后才会尝试下一个。确保主节点在最前
- **API Key统一**：所有节点使用相同的 VLLM_API_KEY 或 EMPTY（内部网络）
- **端口冲突**：确认各节点8000端口未被其他服务占用
- **Tailscale IP变更**：节点IP变更时，需要同步更新Codex和Hermes两处配置
- **Codex不自动重启**：更新config.toml后，需要用户手动重启Codex会话才能生效
- **Hermes配置热加载**：config.yaml更新后即时生效，无需重启
- **session_search应该隔离**：不要把session_search放在主节点，避免与交互流量竞争资源
- **三个节点是标准拓扑**：1主(最新)+1备用+1最终回退。不要超过3个节点增加维护复杂度
- **每个vLLM节点的模型能力可能不同**：部分节点可能运行不同模型（如支持vision vs 不支持）。使用前必须用 `curl $url/v1/models` 和 POST 测试图片输入确认能力。不要假设所有节点模型功能一致。`auxiliary.vision` 应指向有vision能力的节点，而非默认选择。
- **max_model_len 不一致是常见故障**：发现某节点 max_model_len 与其他节点不同时，该节点仍会返回200，不会报错。必须用 `verify-vllm-nodes.py` 脚本统一检测。修复步骤：①找到 vLLM 容器启动脚本（systemd service 或 shell 脚本）②修改 `--max-model-len` 参数③重启容器④重新验证。SSH 连接可能超时但 curl 正常（Tailscale 路由分层），遇到 SSH timeout 时不要放弃，先验证 curl 连通性再判断容器状态。

## 参考文件

- `references/node-topology.md` — 标准三节点拓扑结构和路由策略
- `references/verification-checklist.sh` — 节点验证脚本模板
- `scripts/test-vision-capability.py` — 检测各节点是否支持 image_input（vision）

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引


## 核心原则 · PRINCIPLES

1. **准确为先**: 所有输出必须经过事实核查，不编造数据
2. **证据驱动**: 每个结论必须可追溯到具体证据或数据源
3. **可复现性**: 每一步操作必须可重复，结果可验证

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
