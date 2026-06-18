# 论文管线持续运行Worker模板

## 架构概述

`paper-orchestrator.py` 是一个常驻后台的Python进程，持续扫描论文队列并按IMRaD结构逐步处理每篇论文。

## 核心设计原则

1. **持续运行** — 不是cron触发，而是tmux托管的常驻进程
2. **增量处理** — 每篇论文只处理"缺失"的步骤，完成后自动推进
3. **优雅停止** — SIGTERM捕获，PID文件管理
4. **异常重试** — LLM调用失败最多重试3次
5. **状态持久化** — state.json记录每篇论文的完成进度

## 论文管线步骤（IMRaD标准）

```python
STEPS = {
    "gap_analysis":     "研究空白分析",
    "abstract":         "摘要生成/优化",
    "introduction":     "引言扩写",
    "method":           "方法描述",
    "results":          "结果分析",
    "discussion":       "讨论与结论",
    "reference_check":  "引用完整性检查",
    "quality_check":    "质量检查",
}
```

## 文件结构

```
~/.hermes/scripts/paper-orchestrator.py   # 主脚本
~/.hermes/cron/logs/paper-orchestrator.log  # 日志文件
~/.hermes/cron/logs/paper-orchestrator.pid  # PID文件
media/yakeworld/sda2/Synthos/outputs/papers/<paper>/
    state.json                              # 每篇论文的状态
    01-manuscript/step_<step>.md            # 每步处理结果
```

## 使用方式

```bash
# 启动（tmux后台）
tmux new-session -d -s paper-orch -n worker
tmux send-keys -t paper-orch:worker "cd /home/yakeworld/.hermes/scripts && python3 paper-orchestrator.py" Enter

# 管理命令
python3 paper-orchestrator.py status   # 查看论文队列状态
python3 paper-orchestrator.py tail     # 查看实时日志
python3 paper-orchestrator.py stop     # 优雅停止

# tmux会话管理
tmux list-sessions          # 查看会话
tmux attach -t paper-orch   # 附加到会话
tmux kill-session -t paper-orch  # 强制关闭
```

## LLM API配置

```python
API_URL = "http://100.100.252.99:8000/v1/chat/completions"
API_KEY = "EMPTY"  # 本地vLLM节点无需API key

# 调用参数
{
    "model": "qwen3.6-35b-nvfp4",
    "temperature": 0.3,
    "max_tokens": 4096,
    "top_p": 0.9,
}
```

## 注意事项

1. **脚本路径** — 必须放在`~/.hermes/scripts/`目录下
2. **执行权限** — `chmod +x` 脚本
3. **日志路径** — 确保日志目录存在（`os.makedirs`）
4. **PID管理** — 启动时写PID文件，停止时删除
5. **tmux会话名** — 固定使用`paper-orch`，避免冲突
6. **GPU喘息** — 每步完成后sleep(5)，避免GPU过热
7. **异常不崩溃** — 工作循环包裹在try/except中

## 从cron迁移到持续运行的检查清单

- [ ] 脚本有完整的信号处理（SIGTERM/SIGINT）
- [ ] 脚本有PID文件管理
- [ ] 日志写到固定文件而非stdout
- [ ] tmux session名固定
- [ ] 已移除对应的cron任务
- [ ] 已验证脚本能正常启动和停止
- [ ] 已验证日志能正常输出
