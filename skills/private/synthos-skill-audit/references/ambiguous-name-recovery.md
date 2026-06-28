# Ambiguous Name Recovery Protocol — 运行时别名冲突恢复

> 当 `skill_view()` / `skill_manage()` 因同名技能存在于两个目录而返回 AMBIGUOUS 错误时的恢复流程。

## 场景

两个目录包含同名技能（如 `paper-pipeline`、`quality-gate` 等）：
- `~/.hermes/skills/<name>/`
- `/media/yakeworld/sda2/Synthos/skills/<name>/`

`skill_view(name)` 拒绝加载，提示 "Ambiguous skill name"，即使两个副本内容完全一致。

## 恢复三步流程

### Step 1: 确认问题是名称冲突而非技能缺失

```python
# AMBIGUOUS 的典型特征：error 信息包含 "2 skills match"
error_msg  # → "Ambiguous skill name 'X': 2 skills match..."
# 而不是 "Skill not found" 或 "No such skill"
```

### Step 2: 确认两个副本内容是否一致

```bash
diff ~/.hermes/skills/<name>/SKILL.md /media/yakeworld/sda2/Synthos/skills/<name>/SKILL.md
# 无输出 = 一致；有差异 → 内容分叉，需先同步
```

### Step 3: 跳过 skill_view，直接读取 SKILL.md

```bash
# 从 Synthos 路径直接读取（Synthos 通常为最新）
cat /media/yakeworld/sda2/Synthos/skills/<name>/SKILL.md

# 或从 Hermes 路径
cat ~/.hermes/skills/<name>/SKILL.md
```

## 针对 paper-pipeline cron 的特殊恢复流程

当 paper-pipeline 和 quality-gate 都无法通过 skill_view 加载时：

### 1. 找到队列和状态文件

```bash
# paper-queue.json 通常在 Synthos 路径
cat /media/yakeworld/sda2/Synthos/paper-queue.json

# 每个论文有自己的 state.json
cat /media/yakeworld/sda2/Synthos/outputs/papers/<paper_id>/state.json
```

### 2. 确定权威来源

**state.json > paper-queue.json**

- state.json 是 steps_completed 的权威记录
- paper-queue.json 可能滞后（仅记录最新的 cron run 步骤）
- 如果不一致，以 state.json 为准

### 3. 执行步骤

即使无法通过 skill_view 加载 pipeline 技能，也可以：
1. 从 disk 直接读取 skill 内容（pip install 或 terminal cat）
2. 理解 pipeline 步骤顺序：gap_analysis → abstract → introduction → method → results → discussion → reference_check → quality_check → g1g7_gate_check → compile → publication
3. 执行当前步骤
4. 更新 state.json 和 paper-queue.json

### 4. 同步两个日志

每次步骤完成后，必须更新两个文件：
- **state.json**（论文目录下）— 精确记录所有已完成步骤
- **paper-queue.json**（Synthos 根目录）— cron 调度使用的概览

```json
// state.json — 权威源
{
  "steps_completed": ["gap_analysis", "abstract", "introduction", "method"],
  "current_step": "results",
  "quality_score": 75
}

// paper-queue.json — 从 state.json 同步
{
  "steps_completed": ["gap_analysis", "abstract", "introduction", "method"],
  "current_step": "results",
  "quality_score": 75
}
```

## 预写论文的处理

当论文已完整起草（paper.tex 含所有章节）但 state tracking 只显示部分步骤时：

1. **不要重写已有内容** — 剩余步骤应作为验证/对齐检查执行
2. **检查声明一致性** — Introduction 声称的方法特征是否在 Method 中实现（如 SO(3) 约束）
3. **验证编译** — pdflatex 编译确认零错误
4. **更新评分** — 每次对齐通过可提升 quality_score 2-5 分

## 陷阱

| 陷阱 | 表现 | 处理 |
|------|------|------|
| 认为 AMBIGUOUS = 技能不存在 | 跳过 pipeline 步骤 | 检查 error 信息：AMBIGUOUS ≠ NOT FOUND |
| 只读 SKILL.md 不读 references | 错过深度知识 | references/ 含详细协议和陷阱 |
| 双重反斜杠转义 | tex 文件出现 \\textbf 而非 \textbf | 用 write_file 写整个文件而非 patch |
| 先写 state.json 再写 queue | 两者不同步 | 两个文件必须同时更新 |
