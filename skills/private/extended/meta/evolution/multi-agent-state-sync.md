# Multi-Agent State Synchronization

> Cycle 65 发现：当多个 Agent 运行进化循环时，state.json 会落后于 git commit。

## 问题

Cycle 64 由一个 Agent 提交到 git（`5fc3831 [evolution] cycle-64: OpenClaw absorption merge`），
但 state.json 仍显示 cycle 63。Cycle 65 启动时，state.json 基于过时数据执行 PROBE 和 DIAGNOSE，
导致评分不准确、改进方向偏差。

## 症状

- `git log --oneline | grep "evolution"` 显示 cycle N
- `evolution-state.json` 中 `cycle` 字段为 N-1
- 50+ 个未提交文件堆积（前一个 cycle 的改进未记录到 state）

## 修复：LOAD_STATE 增强

在 Cycle 65 中实施的修复：

```bash
# LOAD_STATE 增强：检查 state lag
git_last_cycle=$(git log --oneline | grep '\[evolution\]' | head -1 | grep -o 'cycle-[0-9]*' | grep -o '[0-9]*')
state_cycle=$(python3 -c "import json; print(json.load(open('evolution-state.json'))['cycle'])")

if [ "$git_last_cycle" -gt "$state_cycle" ]; then
    echo "⚠️ State lag detected: git=$git_last_cycle, state=$state_cycle"
    echo "Syncing state to cycle $git_last_cycle before proceeding..."
    # Update state.json to match git
fi
```

## Cycle 65 实际应用

1. 检测到 state lag: git cycle-64, state cycle-63
2. 在 LOAD_STATE 后将 state 同步到 65（+1 for current cycle）
3. 将 50 个未提交文件与 state 一起提交
4. 后续 PROBE/DIAGNOSE/IMPROVE 基于正确数据

## Lesson

> 心随境转，先对齐后行动。状态同步是进化的第一步。

### Git 路径陷阱（ls-files 返回相对路径）

> **陷阱：`git ls-files` 和 `git status --porcelain` 返回相对路径，`os.path.exists()` 需要绝对路径。**
>
> Cycle 68 发现：`git ls-files` 返回 110 行相对路径。这些路径在 `/tmp/hermes_sandbox`
> CWD 下全部 `os.path.exists()` → False，导致误判 110 文件"缺失"。实际文件全在。
>
> **修复规则**: 1) `git ls-files` 仅用于数量统计。2) `os.path.join(WORKDIR, path)` 构建绝对路径。
> 3) `os.walk()` 统计磁盘 SKILL.md 数量。4) `git status --porcelain` 结果同样需 WORKDIR 前缀。
>
> 文言: 名同实异，路不同基

### Paper-Pipeline 删除未追踪陷阱

> **陷阱：删除 SKILL.md 后 git status 标记 "D"，但 state.json 不更新。**
>
> Cycle 68：paper-pipeline/SKILL.md 被删除后 git status 显示 "D"，state.json 仍 110 tracked。
> PROBE 用 git ls-files 得 110，os.walk 得 109，产生不一致。
>
> **修复规则**: 1) "D " 行 = 已删除的 SKILL.md。2) 删除后必须 git add rm + commit + 更新 state.json。
> 3) 批量删除时在 IMPROVE 步骤一次性处理（git add -A + commit）。
>
> 文言: 删必录，录必同步
