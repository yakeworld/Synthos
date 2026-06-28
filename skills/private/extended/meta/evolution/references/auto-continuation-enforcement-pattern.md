# Auto-Continuation Enforcement Pattern

> 2026-06-28 Cycle 189-190 批量自动循环实战提炼
> 核心教训：自动持续迭代不是"diagnose.py里写个条件判断"就能工作的——必须在每次诊断后主动检查条件并触发下一轮。

## 实际工作流

正确的自动循环执行顺序（非诊断脚本内部逻辑，而是 agent 执行协议）：

```
每次会话/周期：
  1. 加载 state.json
  2. 运行 diagnose.py → 获取诊断结果
  3. 检查 auto-continuation 条件:
     - score >= 0.85?
     - status == healthy?
     - no rejected buffer?
     - consecutive_healthy < 20?
  4. 如果全部满足 → 立即进入下一 cycle（不等待用户输入）
  5. 执行优化（本次轮次的具体改进操作）
  6. 提交所有变更 (git add + commit)
  7. 确认 git clean (git status --porcelain 返回空)
  8. 再次运行 diagnose.py（干净状态下获取真实分数）
  9. 更新 state.json（精确计算，不可估算）
  10. 写入 evolution-log.md
  11. commit state + log
  12. 回到步骤 2（如果条件仍然满足，继续下一轮）
```

## 关键发现

### 1. Auto-continuation 是 agent 层面的决策，不是 diagnose.py 内部的逻辑

diagnose.py 只做一件事：输出六维评分。它不应该包含"自动进入下一轮"的代码。
自动循环的检查由 agent 在每次 diagnose 后执行。

### 2. "继续" = 自动触发

用户说"继续"时，如果 auto-continuation 条件满足，应该直接执行下一个 cycle，不需要询问。
用户说"继续循环进化5个周期"时，应该批量执行 5 轮。

### 3. 批量循环中每轮之间不需要状态隔离

批量循环（5 个周期连续执行）中，每轮的 commit 都是累积的，不需要回滚。
每轮之间的 dirty 文件必须立即提交，否则会影响下一轮 diagnose 的 structural 分数。

### 4. 验证清单注入的分阶段策略

| 阶段 | 目标 | 操作 | 效果 |
|:---|:---|:---|:---|
| 阶段1 | 验证清单 | 191/191 技能 → 添加 5 点验证 | optimize +0.22 (0.65→0.87) |
| 阶段2 | 示例章节 | 约 120 个技能 → 添加示例 | optimize +0.01 (per 35 skills) |
| 阶段3 | 规则/原则 | 约 80 个技能 → 添加规则 | optimize +0.04 (per 35 skills) |
| 阶段4 | Golden | 约 180 个技能 → 添加 golden 集合 | optimize +0.002 (per 35 skills) |

### 5. dirty 文件必须在每轮 commit

每轮修改 35 个文件后，必须：
1. 立即 git add + commit
2. 检查 git status --porcelain 返回空
3. 再运行 diagnose（确保 dirty=0）

否则 dirty count 会污染 structural 分数。

## 陷阱

| # | 陷阱 | 正确做法 |
|:-:|:-----|:---------|
| 1 | 忘记检查 auto-continuation 条件 → 手动干预代替了自动执行 | 每次 diagnose 后立即检查，条件满足则自动继续 |
| 2 | 批量循环中不 commit → dirty 累积影响后续 diagnose | 每轮修改后立即 commit，确保 git clean |
| 3 | diagnose 在 dirty 状态下运行 → structural 分数被污染 | 先 commit，再 diagnose（clean state） |
| 4 | 状态分数估算而非精确计算 | 用公式精确计算：`overall = sum(diagnostics[k] * weights[k])` |
| 5 | 批量循环超过 20 轮不自动停止 → burnout | consecutive_healthy >= 20 时自动停止 |
