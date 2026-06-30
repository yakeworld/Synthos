# 当前三节点集群状态（2026-06-30 更新）

## 节点清单

| Provider | IP | GPU | 容器名 | 运行时间 | 角色 |
|----------|-----|-----|--------|---------|------|
| amax | 100.100.252.99 | 2× RTX 3090 | vllm-qwen3-nvfp4 | 27h+ | 主节点（交互/委托/压缩） |
| amax-backup | 100.125.10.93 | 8× RTX 4090 (用GPU 6,7) | vllm-qwen3-nvfp4 | 22h+ | 备用节点（主节点故障时） |
| amax-fallback | 100.82.27.51 | 2× RTX 3090 | vllm-qwen3-nvfp4 | 4天+ | session_search / 最终回退 |

## 验证时间线

- 2026-06-30 11:28: 全量检查通过，三节点 API 均返回 200
- 2026-06-30 11:28: 确认旧 provider `amax-1` 已从 config.yaml 中移除
- 2026-06-30 11:28: 确认旧 provider `amax-1` 已从 config.toml 中移除
- 2026-06-30 11:28: node-topology.md 已更新
- 2026-06-30 11:28: SKILL.md 中 `amax-1` 引用全部改为 `amax-backup`

## GPU 占用确认

```
100.125.10.93 (amax-backup):
  GPU 0-5: 空闲 (1 MiB)
  GPU 6-7: 占用 (22338 MiB each) - vllm-qwen3-nvfp4

100.100.252.99 (amax):
  GPU 0-1: 占用 (22813-23188 MiB each) - vllm-qwen3-nvfp4

100.82.27.51 (amax-fallback):
  GPU 0-1: 占用 (23195-23433 MiB each) - vllm-qwen3-nvfp4
```

## 注意事项

- 所有节点使用 `vllm/vllm-openai:latest` 镜像
- 所有节点运行 `qwen3.6-35b-nvfp4` 模型
- max_model_len = 262144
- prefix_caching = enabled
- TP = 2（所有节点）
- Cronjob 中如有 `amax-1` 引用需全部清除（参考 Cronjob Provider 名称漂移 pitfall）
