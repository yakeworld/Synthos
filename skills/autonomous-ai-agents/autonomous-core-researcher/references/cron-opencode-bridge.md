# Cron → OpenCode Bridge 模式

> cron 触发 bash 脚本 → 脚本前置检测（零 LLM）→ 有工作时调 `opencode run`
> 参考实现：`~/.hermes/scripts/autonomous-core-researcher.sh`

## 架构

```
┌─────────────────────────────────┐
│        Hermes Cron Scheduler    │
│  (Holds schedule + script ref)  │
└──────────┬──────────────────────┘
           │ every run
           ▼
┌─────────────────────────────────┐
│     Bash Script (no_agent)      │
│  ├─ 读 tracker/state 文件        │
│  ├─ 终端状态检测 → 跳过 (0元)     │
│  ├─ 有工作 → 环境准备             │
│  └─ 调 opencode run "..."       │
└──────────┬──────────────────────┘
           │ (only when needed)
           ▼
┌─────────────────────────────────┐
│        OpenCode / LLM           │
│  (本地模型，100% 执行工作)        │
└─────────────────────────────────┘
```

## 配置模板

### 1. 创建脚本

`~/.hermes/scripts/my-task.sh`:
```bash
#!/bin/bash
SYNTHOS_DIR="/media/yakeworld/sda2/Synthos"
# 前置检测（零 LLM）
python3 -c "..."  # 判断是否需要执行
if [ "$NEED_WORK" = "false" ]; then
    echo "跳过本周期"
    exit 0
fi
cd "$SYNTHOS_DIR"
opencode run "任务描述" --model hermes/qwen3.6-35b-nvfp4
```

### 2. 配置 cron

```bash
hermes cron create "0 */2 * * *" \
  --name my-task \
  --no-agent \
  --script my-task.sh
```

## 使用场景

| 场景 | 前置检测 | 触发条件 |
|:-----|:---------|:---------|
| 论文研究管道 | agent-tracker 终端状态 | phase=working 或新空白 | 
| 批量质检 | last_run 与文件修改时间 | 有新论文完成 |
| 同步任务 | 文件变化检测 | 源目录有变化 |

## 优势

- **零 LLM 成本** — 终端状态检测由 bash/Python 完成，不调推理
- **防空转** — 脚本前置检测保证 cron 不会浪费 API token
- **恢复简单** — 改 tracker/state 参数 → 下周期自动激活
- **可组合** — 一个 cron 可调多个 opencode run（不同任务链）

## 已知陷阱

### 120s 超时
`no_agent=true` 脚本默认超时 **120 秒**。若前置检测后调 `opencode run` 跑本地模型（如 qwen3.6-35b），推理耗时远超此限制。

**解决**：前置检测逻辑必须在 `opencode run` 前完成。检测到无工作→立即 `exit 0`（<1s）。有工作才调 `opencode run`（此时即使超时，也输出了有意义的 agent-tracker 日志）。

### 前置检测必须零模型
前置检测只用 bash/Python 读本地文件（JSON/DB），不能调任何 LLM。否则每次 cron 触发都消耗 token。

### 脚本去重
若 cron 每整点触发而任务需要 >1h，前置检测应加时间锁：
```bash
# 防止并发（可选）
LOCKFILE=\"/tmp/my-task.lock\"
if [ -f \"$LOCKFILE\" ] && [ \"$(($(date +%s) - $(stat -c %Y \"$LOCKFILE\")))\" -lt 3000 ]; then
    exit 0  # 距离上次<50分钟，跳过
fi
touch \"$LOCKFILE\"
```
