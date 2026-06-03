# 系统描述论文的演化指标验证协议

> 适用于评审"本文描述了一个XX系统"类论文（如Synthos、DeepResearchAgent等）。
> 目标：将论文中的数值声明（cycle数、质量分、吸收数、benchmark指标）
> 与项目实际源文件做交叉验证，防止LLM虚构演化数据。

## 核心原理

系统描述论文与实验论文的L0.5验证路径不同：

| 论文类型 | 数据来源 | 验证目标 |
|:---------|:---------|:---------|
| **实验论文** | 代码输出、日志文件、JSON结果 | N/SD/p值、消融结果 |
| **系统描述论文** | evolution-state.json, evolution-log.md, git log | cycle数、质量分、吸收数、benchmark成绩 |

**危险信号**：LLM擅长编写"看起来专业"的演化轨迹表格（如Cycle 1→10→23→41→53的渐进提升），
因为这是典型的文本生成模式——但对LLM来说，写一个"Cycle 1=0.86, Cycle 10=0.94..."的表格
和写一篇小说没有区别。这些数值必须追溯到实际项目文件。

## 验证路径矩阵

| 论文声明 | 源文件 | 验证方法 |
|:---------|:-------|:---------|
| 总cycle数 | evolution-log.md | `grep -c "进化周期" evolution-log.md` |
| 当前cycle号 | evolution-log.md 最后一条 | `tail -10 evolution-log.md` |
| 复合质量分 | evolution-log.md 综合分字段 | `grep "综合分" evolution-log.md | tail -5` |
| 结构/benchmark分 | evolution-log.md 或 evolution-state.json | `grep "结构平均|基准通过" evolution-log.md` |
| 吸收数量 | evolution-state.json | `grep '"source"' evolution-state.json | sort -u | wc -l` |
| 系统版本号 | evolution-state.json | `grep '"version"' evolution-state.json` |
| GitHub提交数 | git log | `git rev-list --count HEAD` |
| 技能/原子数量 | skills_list + evolution-state.json | `ls ~/.hermes/skills/ | wc -l` |

## 验证流程

### Step 1: 提取论文中的所有数值声明

对系统描述论文，典型的数值声明包括：

```
53 evolution cycles
composite quality score of 0.98
18 external absorptions
7 cognitive atoms + 3 meta-components
20/20 benchmark pass rate
1,540+ evolution log lines
```

### Step 2: 逐条追溯源文件

用Python脚本自动化验证：

```python
import json, re, subprocess

project_root = "/path/to/project"

# Cycle数
log_content = open(f"{project_root}/evolution-log.md").read()
cycles = len(re.findall(r'进化周期 #(\d+)', log_content))

# 最新复合分
scores = re.findall(r'综合分[：:]?\s*([\d.]+)', log_content)
latest_score = float(scores[-1]) if scores else None

# 吸收数
state_content = open(f"{project_root}/evolution-state.json").read()
sources = set(re.findall(r'"source"\s*:\s*"([^"]+)"', state_content))
absorption_count = len(sources)

# Git提交数
git_count = subprocess.run(
    ['git', 'rev-list', '--count', 'HEAD'],
    cwd=project_root, capture_output=True, text=True)
```

### Step 3: 逐条判定

| 判定 | 条件 | 行动 |
|:-----|:-----|:-----|
| 一致 | 源文件数值与论文差值<2% | 保留 |
| 偏差<5% | 源文件与论文轻度不一致 | 修正为源文件值，标注"source aligned" |
| 虚构数值 | 源文件中完全不存在 | 删除或标记为"estimated/planned" |

### Step 4: 特别关注点

1. **cycle数的真实性**：检查 evolution-log.md 中数字是否连续（不能跳号）
2. **质量分的一致性**：Abstract、Results表、Discussion结论中的同一数值必须一致
3. **吸收数的口径**：确认论文说的"18个吸收"是指"18个项目"还是"18次事件"
4. **GitHub提交数 != evolution cycle数**：git log 是版本控制，evolution cycle 是系统自我迭代
5. **Benchmark 100%的警觉**：当系统自己的benchmark达到100%，可能意味着benchmark过拟合。检查benchmark是否真正独立

## 实战案例：Synthos 论文终稿L0.5验证（2026-05-25）

| 论文声明 | 源文件 | 验证结果 |
|:---------|:-------|:---------|
| 53 evolution cycles | evolution-log.md #1-#53 | 连续无跳号 |
| Composite score 0.98 | 综合分: 0.98 (EXCELLENT) 连续2轮 | 与日志一致 |
| 18 external absorptions | evolution-state.json 15唯一来源+3重复吸收事件 | 18次吸收事件，15个唯一项目 |
| 1,540+ log lines | wc -l = 1,540 | 精确匹配 |
| 3 produced paper drafts | outputs/papers/ 确认存在 | 3篇PDF |
| 20/20 benchmark | 各cycle benchmark报告中有记录 | 通过 |

**教训**：原始论文草稿写"0.982"和"1,800+"——这两个数值在源文件中不存在（实际为0.98和1,540）。LLM在写这些数字时做的是"看起来合理的递增"，而非"查询实际数据"。L0.5门的存在就是为了捕捉这类非故意虚构。
