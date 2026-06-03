# Cron Execution Reference — Cycle 59 (2026-06-03)

> 实战记录：首次 DeepSeek Chat 通过 cron 完整执行 11 步进化循环。

## 执行环境

| 参数 | 值 |
|:-----|:---|
| Provider | deepseek-chat (DeepSeek Chat) |
| Host | Linux 6.8.0-117-generic |
| Working dir | /media/yakeworld/sda2/Synthos |
| Git state | Detached HEAD (cron default) |
| State files | `evolution-state.json`, `evolution-log.md` — both in `.gitignore` |

## 关键发现

### 1. Gitignored state files

`.gitignore` 中有：
```
/evolution-state.json
/evolution-log.md
/outputs/
```

这意味着所有 state/log/report 文件必须用 `git add -f` 强制添加。

**行动模式：**
```bash
# RECORD 步骤末尾：
git add -f evolution-state.json evolution-log.md
git commit -m "[evolution] cycle-N: state+log update"
git add -f outputs/evolution/cycle-N-report.md
git commit -m "[evolution] cycle-N: report"
```

**不要用 `git add .` 或 `git add -A`** — 它们会尊重 .gitignore，漏掉 state 文件。

### 2. Detached HEAD

Cron 执行时 HEAD 可能指向某个 commit 而非分支。需要手动 checkout main 再 merge：

```bash
git checkout main
git merge <last-hash>
# 通常是 fast-forward，安全
```

如果 merge 时出现冲突（极罕见），说明 cron 外有人修改了 main。此时中断 cycle，不覆盖。

### 3. Push failure（预期行为）

Cron 进程没有 GitHub 凭据：
```
remote: Invalid username or token.
fatal: 'https://github.com/yakeworld/Synthos.git/' 鉴权失败
```

**这不影响 cycle 完成** — 所有 commit 已经在本地 main 分支上。Push 在有用户交互时手动执行。

### 4. Flat-level duplicate detection

`skills/` 根目录的扁平 `.md` 文件可能与子目录 SKILL.md 形成 name 重复。例如 cycle-59 发现：
- `skills/pdf-download-racing.md` (flat, untracked)
- `skills/research/pdf-download-racing/SKILL.md` (tracked, canonical version)

两者 name 字段都是 `pdf-download-racing`，导致 Hermes agent 报告 121 个技能（实际唯一 120 个）。

**检测脚本：** 见 evolution SKILL.md 陷阱6。

## 时间线

| 时间 | 事件 |
|:-----|:-----|
| 03:00 | Cron 触发 — `synthos-evolution-full` |
| 03:01 | DRIFT_CHECK → 🟢 无漂移 |
| 03:02 | PROBE → 7/7 atoms pass, 121 flat count noted |
| 03:04 | BENCHMARK → all 1.0, duplicate pdf-download-racing.md found |
| 03:05 | DIAGNOSE → all dimensions 1.0 |
| 03:06 | IMPROVE → removed duplicate, cleaned .git-rewrite, committed dual-quality-check-v2 improvement |
| 03:07 | VERIFY → clean |
| 03:08 | RECORD → state/log/report committed, main merged |

## Lessons Applied to evolution SKILL.md

| Lesson | Trap # | 新增于 |
|:-------|:-------|:-------|
| State files gitignored → use `git add -f` | Trap 4 | 2026-06-03 |
| Cron detached HEAD → checkout main + merge | Trap 5 | 2026-06-03 |
| Flat-level skill duplicates | Trap 6 | 2026-06-03 |
| Push failure expected in cron | Trap 7 | 2026-06-03 |
