# Codex 进程诊断

> 记录: 2026-06-21
> 场景: 用户问"codex现在在干什么" → 需要诊断运行中 Codex 进程在做什么

## 诊断流程

### Step 1: 找到进程

```bash
ps aux | grep -i codex | grep -v grep
# 列出所有 Codex 进程，记录 PID
```

### Step 2: 定位会话日志

```bash
# Codex 会话日志在 ~/.codex/sessions/YYYY/MM/DD/
ls -lt ~/.codex/sessions/$(date +%Y)/$(date +%m)/$(date +%d)/
# 按时间排序，最新的是当前会话
```

### Step 3: 提取用户任务/目标

```python
import json
# Codex JSONL 格式: {"timestamp": ..., "type": ..., "payload": {...}}
# 需要找 type=session_meta 获取 cwd (项目路径)
# 需要找 payload.message 包含中文任务的条目
# payload.message 字段直接包含用户输入的任务描述

# 关键: Codex JSONL 中 payload.message 包含原始用户消息
# 例如: "对本项目代码进行认真审查"
```

### Step 4: 输出报告

```
Codex 进程状态:
- PID: xxxxx, 项目: /path/to/project, 任务: "用户输入的任务描述"
- PID: xxxxx, 项目: /path/to/other, 任务: "另一个任务"
```

## 常见 Codex 任务类型

| 任务来源 | 示例 | 说明 |
|----------|------|------|
| codex-tui (用户直接) | "对本项目代码进行认真审查" | 用户在终端直接调用 Codex |
| codex_exec (脚本调用) | "论文全库 D8/D10a 扫描" | Cron 脚本调用 codex exec |
| background 任务 | 无明确 message | 可能后台持续运行 |

## JSONL 格式要点

- `type=session_meta` → `payload.cwd` 是工作目录，`payload.thread_source` 是来源(codex-tui/codex_exec)
- `type=event_msg` → `payload.message` 是用户消息
- 第一个非 session_meta 的 event_msg 通常就是用户任务

## 陷阱

1. **进程数不等于任务数**: 一个 long-running Codex session 会产生大量 JSONL 文件(每个 turn 一个)。`ls` 显示的是 turn 文件，不是会话文件。
2. **会话文件命名**: `rollout-YYYY-MM-DDTHH-MM-SS-UUID.jsonl` — 按日期排序最晚修改的是最新的 session。
3. **JSONL 格式**: Codex 输出不是简单的 role/content 格式，而是 `timestamp/type/payload` 结构。需要用 Python 解析，不能用 head/grep 直接看。
