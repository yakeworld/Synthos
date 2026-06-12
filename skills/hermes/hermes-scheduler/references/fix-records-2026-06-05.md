# 实战修复记录：2026-06-05

## 问题1: memory-consolidation空跑

**症状：** 每2小时运行一次，输出"内存不可用（此环境未启用持久记忆存储）"，跳过所有步骤。

**根因：** cron环境无memory后端（`enabled_toolsets: ["memory"]`无效），memory工具在cron会话中不可达。

**诊断：**
```bash
hermes cron list 2>/dev/null | grep -A15 "memory-consolidation"
# 发现：enabled_toolsets包含memory，但cron环境不支持
```

**修复：** 直接移除。非配置问题，是架构限制。

```bash
hermes cron remove 9926ae23cdbc
```

**教训：** cron任务中涉及memory操作的都需要检查环境是否支持。`memory`工具只在交互会话可用。

## 问题2: evolution-probe/full投递失败

**症状：** `delivery error: Feishu send failed: [230001] Your request contains an invalid request parameter, ext=invalid receive_id`

**根因：** `deliver: "origin"` 固化了创建时的receive_id，但该ID已失效（可能因workspace变更）。

**修复：**
```bash
# 先确认当前channel
# 当前Home Channel ID: yake_local

# 显式指定当前channel
hermes cron update e2ced0c400ad --deliver feishu:yake_local
hermes cron update 99afed190353 --deliver feishu:yake_local
```

**注意：** 仅设置`deliver: origin`不会刷新，必须显式指定`feishu:<channel-id>`。

## 问题3: 全量迁移到本地模型

**症状：** 8个cron jobs + 默认模型都走DeepSeek API（付费），两个本地节点（amax/amax-fallback）空闲。

**诊断：**
```bash
cat ~/.hermes/config.yaml | grep -A5 "^model:"
# 发现：默认模型为deepseek-v4-flash on deepseek provider

# 检查本地节点可用性
curl -s http://100.100.252.99:8000/v1/models  # ✓ qwen3.6-35b-nvfp4
curl -s http://100.82.27.51:8000/v1/models     # ✓ qwen3.6-35b-nvfp4
```

**修复步骤：**

```bash
# 1. 修改默认模型（交互会话）
patch ~/.hermes/config.yaml:
  model:
    default: qwen3.6-35b-nvfp4
    provider: custom:amax
    base_url: http://100.100.252.99:8000/v1
    api_key: EMPTY

# 2. 修改压缩模型
patch ~/.hermes/config.yaml compression:
    provider: custom:amax
    model: qwen3.6-35b-nvfp4
    base_url: http://100.100.252.99:8000/v1
    api_key: EMPTY

# 3. 迁移cron jobs（逐个更新）
# 8个jobs全部切到custom:amax（主节点）
for job_id in ff134d00da00 63bd3bc7ee08 579cf863a4e6 9bf24f47487c; do
  hermes cron update $job_id \
    --model '{"model": "qwen3.6-35b-nvfp4", "provider": "custom:amax"}'
done

# 4. 负载均衡：4个jobs切到备节点
for job_id in e75667c2351f a8c95de4bb2e e2ced0c400ad 99afed190353; do
  hermes cron update $job_id \
    --model '{"model": "qwen3.6-35b-nvfp4", "provider": "custom:amax-fallback"}'
done
```

**最终分布：**
- 主节点(amax): 交互会话 + autonomous-core-researcher + papers-daily-scan + synthos-evolution-full
- 备节点(amax-fallback): literature-monitor + bib-standardization + daily-papers-report + synthos-evolution-probe + session_search

## 问题4: cron→持续运行转换

**症状：** 论文管线改进工作是定时触发的（cron），不是持续运行的。每次cron触发=全新会话=有状态丢失风险。

**需求：** 论文处理应该是持续运行的流水线，按IMRaD结构逐步推进。

**实现：**

```bash
# 1. 写常驻后台脚本
cat > /home/yakeworld/.hermes/scripts/paper-orchestrator.py << 'PYEOF'
#!/usr/bin/env python3
# (完整脚本见templates/paper-orchestrator.py)
# 核心：持续扫描论文队列，按步骤依次处理，LLM调用后自动推进
PYEOF
chmod +x /home/yakeworld/.hermes/scripts/paper-orchestrator.py

# 2. 用tmux托管
tmux new-session -d -s paper-orch -n worker
tmux send-keys -t paper-orch:worker "cd /home/yakeworld/.hermes/scripts && python3 paper-orchestrator.py" Enter

# 3. 验证
sleep 5 && tail -f /home/yakeworld/.hermes/cron/logs/paper-orchestrator.log
# 输出: "✓ 3d-iris-normalization 处理完成，等待新任务..."

# 4. 移除被替代的cron任务
hermes cron remove fb6221e7b255  # paper-queue-worker

# 5. 管理命令
python3 /home/yakeworld/.hermes/scripts/paper-orchestrator.py status
python3 /home/yakeworld/.hermes/scripts/paper-orchestrator.py tail
python3 /home/yakeworld/.hermes/scripts/paper-orchestrator.py stop
```

**验证输出：**
```
2026-06-05 09:55:41 [INFO] ✓ 3d-iris-normalization 处理完成
2026-06-05 09:56:08 [INFO] ✓ 3wd-framework-trustworthy-clinical-ai 处理完成
```

## 关键发现

1. **两个节点各有一块Quadro RTX 4000 (8GB)**，都加载了qwen3.6-35b-nvfp4，温度51°C
2. **GPU心跳监测**已创建（gpu-heartbeat.sh, 每30分钟cron），但实际节点一直在线
3. **62篇论文目录**中10篇有内容，52篇为空等待内容
4. **cron环境不支持的tools：** memory、可能还有skill相关的交互式操作
