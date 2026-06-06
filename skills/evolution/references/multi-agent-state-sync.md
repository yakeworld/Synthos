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
