# Cron Job 路由与模型分配

## 双节点负载均衡架构

两个推理端点 + Hermes 调度器（独立主机，跑 cron 脚本）：

```
                  ┌─────────────────┐
                  │  Hermes 主机    │
                  │  (调度 cron)    │
                  │                 │
                  │  no_agent:      │
                  │  gpu-heartbeat  │
                  │  paper-queue    │
                  └──┬────────┬────┘
                     │        │
              amax   │        │  amax-fallback
          (主节点)   │        │  (备节点)
              100.100.252.99   100.82.27.51
              :8000            :8000
              qwen3.6-35b      qwen3.6-35b
```

## Cron 任务路由表

### 主节点 (custom:amax)
| Job | 频率 | 负载 |
|:-----|:-----|:-----|
| 交互会话 | 随时 | 重 |
| autonomous-core-researcher | 每3h | 最重(带skill链) |
| papers-daily-scan | 每6h | 重 |
| synthos-evolution-full | 每天 | 重(11步) |
| synthos-github-discussion | 每月 | 轻 |
| context compression | 随时 | 中 |

### 备节点 (custom:amax-fallback)
| Job | 频率 | 负载 |
|:-----|:-----|:-----|
| literature-monitor | 每天08:00 | 中高 |
| bib-standardization | 每天05:00 | 中 |
| daily-papers-report | 每天07:00 | 中 |
| synthos-evolution-probe | 每6h | 轻 |
| session_search | 随时 | 轻 |

### 无Agent脚本 (不占LLM)
| Script | 频率 | 说明 |
|:--------|:-----|:-----|
| gpu-heartbeat.sh | 每30min | 节点心跳+GPU温度 |
| paper-queue-worker.sh | 每2h | 论文目录扫描 |

## 关键规则

1. **默认模型设为本地** → 所有 `model: null` 的 job 自动走本地，不空耗 API
2. **provider 必须匹配模型** → `model: qwen..., provider: deepseek` 是反模式
3. **显式指定 provider** → `custom:amax` 或 `custom:amax-fallback`
4. **cron 无 memory** → memory 工具在 cron 不可用，用 no_agent 脚本+文件替代
5. **deliver: "origin"** → 固化创建时的 receive_id，渠道变更后失效，需显式指定

## 常用操作

```bash
# 迁移 job 到备节点
hermes cron update <job_id> --provider custom:amax-fallback

# 迁移 job 到主节点
hermes cron update <job_id> --provider custom:amax

# 创建 no_agent 脚本 job
hermes cron create --name "my-worker" --script "my-worker.sh" \
  --schedule "every 60m" --deliver local --no-agent

# 验证脚本
bash ~/.hermes/scripts/gpu-heartbeat.sh
bash ~/.hermes/scripts/paper-queue-worker.sh
```
