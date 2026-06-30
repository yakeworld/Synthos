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

### 0. 上游动态前置检查（v0.24.0+ 关键）

在执行任何节点验证或配置检查前，**先检查 vLLM 上游是否有重大版本更新或 breaking changes**：
1. 访问 https://github.com/vllm-project/vllm/releases 确认最新版本
2. 重点关注：PyTorch 版本升级、`CUDA_VISIBLE_DEVICES` 弃用/移除、MRv2 行为变更、量化模型默认行为变更
- 如果有 pre-release，记录状态但**不建议生产环境直接使用**
- 使用 `curl` + GitHub API 获取 release data 时注意：curl 可能返回 exit code 28（timeout）但仍含完整数据，需用 bracket-matching 解析 JSON，不可直接 `pip | python3`（会被安全扫描拦截）
4. 将关键更新点存储为参考文件，供后续 session 查询

### 1. 节点连通性验证（诊断顺序：SSH → curl → 容器状态）

对每个新节点执行（**按此顺序**，任一失败即记录节点状态为不可达）：

```bash
# Step A: SSH 连通性（诊断层）
ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no root@<IP> "echo OK" 2>&1

# Step B: curl 端口探测（服务层 — 即使 SSH 失败也要测）
curl -s --connect-timeout 5 http://<IP>:8000/v1/models | python3 -m json.tool

# Step C: 容器状态（如果 SSH 或 curl 任一成功）
ssh root@<IP> "docker ps --filter 'name=vllm' --format '{{.Status}}'" 2>/dev/null
```

**关键规则**：
- SSH timeout ≠ 节点宕机 — 必须测 curl :8000 确认 vLLM 容器状态
- curl timeout + SSH timeout → 节点不可达，从 provider 列表移除或降级
- 全通后，确认所有节点返回**相同** model ID 和 max_model_len

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
  - name: amax-backup
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
- `auxiliary.vision` → **必须指向支持 vision 的节点**（当前为 `custom:amax`）。先运行 `scripts/test-vision-capability.py` 确认。

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

### 共享内存残留导致容器无限重启（关键）

vLLM 容器在 35B+ 模型、多 GPU 场景下会创建大量共享内存段（`/dev/shm/psm_*` 和 `sem.mp-*`）。旧容器异常退出后，这些残留会**阻止新容器启动**，报错 `RuntimeError: Engine core initialization failed` + `leaked shared_memory objects`。

**排查信号**：`docker logs` 看到 "leaked shared_memory objects" + "Engine core initialization failed" + 容器不断重启

**核心原因**：旧容器残留的共享内存段与新容器冲突。即使设置了 `--shm-size 128g` 也无法创建新段，因为旧的 `psm_*` 文件存在于 `/dev/shm/` 且被 Docker 守护进程锁定。

**解决步骤**：
1. `ipcs -m` 查看所有共享内存段，识别 `psm_*` 和 `sem.mp-*`
2. 需要 root 权限：`sudo ipcrm -M <shmid>` 清理所有 `psm_*` 段
3. `sudo ipcrm -s <sem_id>` 清理所有 `sem.mp-*` 信号量
4. **如果没有 root 权限，必须重启机器** 或切换到其他正常节点
5. 清理后重新启动容器，且必须带 `--shm-size 128g`

**预防措施**：
- 使用 `--restart=always` 而非 `--restart unless-stopped`（`unless-stopped` 会在 shm timeout 后无限重启循环）
- 部署后观察前 10 分钟日志，确认没有 `shm_broadcast.py` timeout 告警

### 节点网络不可达模式

某节点可能完全不可达（SSH timeout + ping 100% loss + curl timeout），但其他节点正常。这通常不是 vLLM 问题，而是：
- Tailscale 连接中断
- 网卡/电源问题
- 系统级故障

**排查步骤**：
1. `ping <IP>` 确认网络层连通性
2. `curl --connect-timeout 3 http://<IP>:8000/v1/models` 确认应用层
3. 如果 SSH 超时但 curl 正常 → 容器正常，仅 SSH 配置问题
4. 如果全不通 → 节点故障，从 provider 列表中移除或降级
5. **不要在完全不可达的节点上花调试时间**，先恢复服务再排查

### Tensor Parallel sizing 对 MoE 模型至关重要

对 35B MoE 模型（如 Qwen3.6-35B-A3B），**TP=4 的吞吐通常优于 TP=2**，但在实际环境中需要权衡：

| 场景 | 实测观察 | 关键因素 |
|------|---------|---------|
| 相同节点内 TP=4 vs TP=2 | TP=4 吞吐更高，但通信开销增加 | PCIe 带宽 vs 计算并行 |
| 跨节点比较 (4×4090 TP=4 vs 2×3090 TP=2) | 性能接近（差异<10%） | vLLM 配置（prefix_caching, max_model_len）比 TP 更重要 |
| 短输出场景 | TP=4 优势明显（33%） | 短上下文下计算并行优势大 |
| 长上下文场景 | TP=4 优势约21% | 长上下文下通信开销开始显现 |

**关键发现**：配置优化比硬件升级更关键。2×3090 TP=2 在启用 `prefix_caching=True` + `compile_range` 后，吞吐可达 200-240 tok/s，比 4×4090 TP=4 未优化配置更快。

**TP 选择建议**：
- 35B MoE + 4×4090：TP=4（充分利用所有GPU）
- 35B MoE + 2×4090：TP=2（避免通信开销）
- 35B MoE + 2×3090：TP=2（3090 无 NVLink，TP>2 通信开销大）
- 70B+ Dense：TP=4 起步
- 200B+ MoE：TP=8 或更高

**配置优先级**：
1. `prefix_caching=True` — 命中率通常 >80%，大幅提升吞吐
2. `max_model_len` — 设置为实际需求，过小会限制长文本
3. `compile_range` — 启用动态编译，短上下文场景提升显著
4. TP 选择 — 在配置优化的基础上再考虑

### 容器启动 shm-size 必须足够

35B+ 模型在 TP≥2 时，vLLM EngineCore 需要大量共享内存段。Docker 默认 `/dev/shm` 仅 64MB，不足以支撑。启动时必须设置：

```bash
--shm-size 128g
```

低于 128g 会导致 `RuntimeError: Engine core initialization failed`。

### 其他陷阱

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
- **`--distributed-executor-backend process` 不被 vLLM v0.23.0 支持**：不能作为共享内存问题的 workaround，容器会直接报错退出。
- **容器有 `--restart unless-stopped` 策略时，共享内存泄漏会导致容器不断重启**：因为 EngineCore 初始化失败后容器退出，自动重启策略立即再次启动，再次失败，形成死循环。排查时需先检查 `docker ps -a` 看是否频繁重启。

### Cronjob Provider 名称漂移（关键）

当节点从 `custom_providers` 中被移除时（如 `amax-1` 节点宕机后从 provider 列表删除并改名为 `amax`），**已创建的 cronjob 仍然指向旧的 provider 名称**（`custom:amax-1`），导致 cronjob 执行失败并报 `Unknown provider 'custom:amax-1'`。

**排查信号**：cronjob 失败日志中出现 `Unknown provider 'custom:<name>'`，而该 provider 在 config.yaml 中已不存在

**修复步骤**：
1. `cronjob list` 找到失败的 job_id
2. 查看当前 config.yaml 中 `custom_providers` 列表，确认正确的 provider 名称
3. **`cronjob update` 对 provider 的修改通常不生效**（工具限制）
4. **正确做法**：`cronjob remove` 旧 job → `cronjob create` 新 job，使用正确的 provider 名称
5. **预防**：移除节点时，同步检查所有 cronjob 是否引用了该节点的 provider

### Cronjob list 大列表超时（实用技巧）

当 cron 任务数量较多（>15个）时，`cronjob list` 可能因输出过长而超时（用户侧确认超时），导致诊断中断。

**规避策略**：
- 不直接运行 `cronjob list`，改用 `scripts/check-cron-providers.py` 脚本（已创建）
- 脚本通过解析 config.yaml 中的 custom_providers 列表，直接 grep 所有 cron job 配置中的 provider 引用，无需读取完整列表
- 如果必须用 `cronjob list`，先 `cronjob list | wc -l` 确认任务数量，超过20个时改用 provider-specific grep 而非全量检查

### 容器启动前必须验证镜像能力（关键）

使用非标准镜像（如 `my_pytorch`）启动 vLLM 容器时，**必须先验证镜像内是否包含 vllm 命令行工具**，否则容器启动后直接因入口点失败而退出。

**排查信号**：`docker logs` 显示 `/usr/local/bin/vllm: No such file or directory` 或类似路径不存在错误

**核心原因**：`my_pytorch` 是 NVIDIA PyTorch 基础镜像（含 CUDA 12.1 + PyTorch 2.1.1），但**未预装 vllm**。其他成功运行的容器使用 `vllm/vllm-openai:latest` 官方镜像。

**正确做法**：
1. **优先使用官方镜像** `vllm/vllm-openai:latest` — 已预装 vllm CLI 和所有依赖
2. **必须用自定义镜像时**：先验证 `docker run --rm <image> which vllm` 和 `pip list | grep vllm`
3. **如果镜像没有 vllm**：
   - 方案A：用 `--entrypoint ''` 覆盖默认 entrypoint，手动 `pip install vllm` 后启动
   - 方案B：直接用 `vllm/vllm-openai:latest` 镜像
4. **验证命令**：
```bash
# 快速验证
docker run --rm --gpus device=0 <image> which vllm 2>&1
docker run --rm <image> pip list 2>/dev/null | grep vllm
```

**预防**：在 `vllm/vllm-openai:latest` 镜像可用时，**不要**随意使用其他基础镜像启动 vLLM 容器。

### 容器启动前必须检查 GPU 占用和端口冲突（新）

启动新容器前，**必须确认目标 GPU 未被其他容器占用**，端口未被占用。

**排查信号**：`docker run` 报 `port is already allocated` 或 GPU 分配错误

**核心原因**：GPU 是独占资源，宿主机 GPU 6 可能被旧容器 `vllm-qwen3-nvfp4` 占用，即使容器名不同。必须通过 `nvidia-smi` 检查实际 GPU 内存占用。

**正确做法**：
1. `nvidia-smi --query-gpu=index,name,memory.used --format=csv,noheader` — 查看哪些 GPU 有内存占用
2. `docker ps --filter name=vllm --format '{{.Names}} {{.Status}}'` — 确认哪些容器在跑
3. 选择 **内存占用为 0 的 GPU** 启动新容器
4. 如果要用已占用的 GPU，必须先停掉旧容器：`docker rm -f <container>`
5. 容器内 GPU 编号从 0 开始，映射关系由 `--gpus device=X,Y` 决定。容器内看到的 GPU 0 对应宿主机的指定 GPU

### vLLM 版本升级安全清单（Breaking Changes 专项）

当上游发布新版本时，**不要直接升级**，按此清单逐项验证：

```
[ ] 阅读 release notes，识别 breaking changes 清单
[ ] 确认 CUDA_VISIBLE_DEVICES 是否被弃用 → 检查 Docker/systemd 启动脚本
[ ] 确认 PyTorch 版本是否升级 → 验证 CUDA/pytorch 二进制兼容层
[ ] 确认 MRv2 行为是否变更 → 验证当前模型（Qwen3 等）的量化行为一致性
[ ] 确认共享内存需求是否变化 → 验证 --shm-size 是否仍需 128g
[ ] 确认 API 端点兼容性 → 验证所有调用方（Codex/Hermes/cronjobs）正常工作
[ ] 确认 Starlette/CVE 修复紧迫性 → 安全漏洞需优先处理
```

**升级顺序**：
1. 单个节点灰度升级 → 观察 24 小时
2. 确认无异常后 → 滚动升级所有节点
3. 最后更新 provider 配置和 cronjob 引用

**升级前必查**：
- 备份 Docker 启动脚本和 systemd unit 文件
- 确认 `/dev/shm` 中残留的共享内存段已清理（防止升级后容器重启循环）
- 确认旧版本容器已完全停止（`docker stop` + `docker rm`），而非仅重启策略触发

**参考**: `references/v0.24.0-release-notes.md` — 包含 v0.23→v0.24 详细变更对照

## 参考文件

- `references/node-topology.md` — 标准三节点拓扑结构和路由策略
- `references/current-cluster-status.md` — 当前三节点集群实际状态快照（2026-06-30 更新）
- `references/verification-checklist.sh` — 节点验证脚本模板
- `references/tensor-parallel-sizing.md` — MoE模型多GPU TP sizing分析与实证数据（35B MoE TP=4优于TP=2）
- `references/shared-memory-cleanup.md` — vLLM容器共享内存泄漏诊断与清理指南（psm_*/sem.mp-*残留清理）
- `scripts/test-vision-capability.py` — 检测各节点是否支持 image_input（vision）
- `scripts/bench-throughput.py` — vLLM 吞吐量基准测试脚本（用于不同TP/节点间性能对比）
- `scripts/test-vision-capability.py` — 检测各节点是否支持 image_input（vision）
- `scripts/verify-vllm-nodes.py` — 验证所有节点模型一致性（max_model_len, model ID）
- `scripts/quick-node-check.sh` — 快速检查三节点集群状态（curl优先，不依赖SSH）
- `references/v0.23.0-baseline.md` — v0.23.0 当前部署版本基线，用于跨版本对比

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


## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。



# Vllm Cluster Management

