# 标准三节点拓扑

## 拓扑结构

```
                 ┌─────────────────┐
                 │  Hermes/Codex   │
                 │  请求路由层     │
                 └─┬───┬───┬───────┘
                   │   │   │
          主节点   │   │   │  最终回退
       ┌───────────┘   │   └───────────┐
       │               │               │
  100.100.252.99  100.125.10.93  100.82.27.51
       │               │               │
   amax       amax-backup    amax-fallback
   qwen3.6-35b     qwen3.6-35b     qwen3.6-35b
   2×3090        8×4090 (TP2)   2×3090
   max_ctx=262K  max_ctx=262K   max_ctx=262K
```

## 节点详情

| Provider | IP | GPU | 运行时间 | 角色 |
|----------|-----|-----|---------|------|
| amax | 100.100.252.99 | 2× RTX 3090 | 27h | 主节点（交互/委托/压缩） |
| amax-backup | 100.125.10.93 | 8× RTX 4090 (TP2) | 22h | 备用节点（主节点故障时） |
| amax-fallback | 100.82.27.51 | 2× RTX 3090 | 4天 | session_search / 最终回退 |

## 路由决策树

```
请求到达
  │
  ├─ 交互请求 → amax (100.100.252.99)
  │   ├─ 成功 → 返回
  │   └─ 失败 → amax-backup
  │
  ├─ 子Agent委托 → amax (同主节点保持一致性)
  │   └─ 失败 → amax-backup → amax-fallback
  │
  ├─ 压缩/审批 → amax (同主节点)
  │   └─ 失败 → amax-backup
  │
  ├─ session_search → amax-fallback (隔离)
  │   └─ 失败 → amax
  │
  └─ Cron重度任务 → DeepSeek云端
      └─ 不占用本地资源
```

## 扩展规则

- 新增节点：放在 base_url 和 custom_providers 列表最前
- 移除节点：从两处同时删除
- 最多3个节点，超过则考虑分层（如按用途分离）
- 所有节点模型必须完全一致
