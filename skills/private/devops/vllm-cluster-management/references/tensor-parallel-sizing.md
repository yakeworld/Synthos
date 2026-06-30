# Tensor Parallel Sizing for MoE Models

## Core Finding

For MoE models (如 Qwen3.6-35B-A3B), **TP=2 and TP=4 are comparable in throughput**, with TP=4 having a slight edge on medium/long contexts but TP=2 being more resilient to config differences.

## Why Performance is Similar

### 1. Memory-bound workload

Inference is **memory bandwidth limited**, not compute limited:
- 3090: 936 GB/s memory bandwidth
- 4090: 1008 GB/s memory bandwidth
- Only ~7.7% difference!

Theoretical compute doubled (41.5 → 82.5 TFLOPS), but throughput barely moves.

### 2. PCIe communication overhead

Both RTX 3090 and 4090 have **no NVLink**. Multi-GPU NCCL All-Reduce goes over PCIe 4.0 x16 (~64GB/s bidirectional). 4-card All-Reduce has higher latency and contention.

### 3. Low activation ratio

Qwen3.6-35B-A3B has 35B total params but ~33B activated per inference. With TP=4, each GPU processes ~8.25B of the active path — very small. GPU idle time waiting for NCCL All-Reduce dominates.

## Empirical Data (June 2026)

### 2×4090 TP=2 (100.125.10.93, vLLM v0.23.0)
| 场景 | 吞吐 (tok/s) | 延迟 (s) | 备注 |
|------|-------------|---------|------|
| 短→短 (32 tok) | 62-91 avg | 0.1-2.3 | 冷启动慢 |
| 短→中 (128 tok) | 159-174 | 0.7-0.8 | 稳定 |
| 中→中 (200 tok) | 157-164 | 0.8-0.8 | 稳定 |
| 长→中 (500 tok) | 65-162 | 0.8-2.0 | 不稳定 |

### 2×3090 TP=2 (100.100.252.99)
| 场景 | 吞吐 (tok/s) | 备注 |
|------|-------------|------|
| 短→中 | ~180-200 | 配置: max_model_len=262K, prefix_caching=True, compile=[4096] |
| 长→长 | ~200+ | 最高记录 240+ tok/s |

### 关键对比：2×4090 TP=2 vs 2×3090 TP=2

**2×4090 反而比 2×3090 慢 5-20%**。原因：
- 3090 节点配置了 `enable_prefix_caching=True`（前缀缓存命中率达 87%）
- 3090 节点有 `--compile range [4096]`（图编译优化）
- 3090 节点 `max_model_len=262K` vs 4090 节点实际被截断在 32K
- **配置差异大于硬件差异**

## TP 选择建议

| 场景 | 推荐 TP | 理由 |
|------|---------|------|
| 35B MoE, 4×4090 | TP=2 或 TP=4 | 性能差异 <10%，TP=2 更稳定 |
| 35B MoE, 2×4090 | TP=2 | 唯一选择 |
| 35B MoE, 2×3090 | TP=2 | 有 prefix caching 时性能接近 4090 |
| 70B Dense | TP=4 起步 | Compute dominates |
| 200B+ MoE | TP=8+ | 必须加载全部权重 |
| 3090+3090+4090+4090 混用 | 避免混 TP | 各卡能力不同，路由不稳定 |

## Debug Checklist

如果某节点 TP=2 表现异常差：
1. `enable_prefix_caching` 是否开启？（影响重复 prompt 场景）
2. `--compile range` 是否配置？（影响首 token 延迟）
3. `max_model_len` 是否被截断？（影响长上下文）
4. `gpu_memory_utilization` 是否过高导致 OOM？
5. 对比其他同配置节点，排除网络/硬件个体差异
