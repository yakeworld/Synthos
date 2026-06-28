---

name: task-router
description: Synthos系统入口。路由用户查询到正确的认知原子链或执行模式。 四模式：标准链 / 探索循环 / 研究双循环 / 并行执行。 Agent-native执行，纯skill驱动零Python。
author: Synthos
license: MIT
version: 1.0.0
license: MIT
allowed-tools: shell (bash), Read (view), Write (write), task_delegation (agent, inline),
  skill_loader (view with file path)
metadata:
  synthos:
    priority: P0
    atom_type: parent-skill
    description: Synthos系统入口。路由用户查询到正确的认知原子链或执行模式。 四模式：标准链 / 探索循环 / 研究双循环 / 并行执行。
    signature: |
      query: str, context: dict -> route: str, atom_chain: list[str], execution_mode: str | route: str, atom_chain: list[str], execution_mode: str, pipeline_trace: pipeline_trace.json
    related_skills: [knowledge-acquisition, knowledge-extraction, association-discovery, hypothesis-generation, argument-expression, viewpoint-verification, evolution]


---


# Task Router — Synthos 系统入口

## IO_CONTRACT

- **input**: `query: str` — 用户原始查询
- **input**: `context: dict` — 当前会话上下文（含已执行原子、历史输出）
- **output**: `route: str` — 选择模式（standard_chain / exploration_loop / research_double_loop / parallel_execution）
- **output**: `atom_chain: list[str]` — 目标认知原子链（按依赖顺序）
- **output**: `execution_mode: str` — 具体执行模式描述
- **output**: `status: dict` — 路由决策日志（含 confidence, alternatives_considered）
> 对应原则：P2（机械原子暴露输入输出规范）
## 原理层·文言

> 路由者，问之所向也。问大则大行，问细则细究。
> 四维之径：一曰直行（标准链），二曰环探（探索），
> 三曰双环（研究），四曰并行（并进）。
> 路定则行，行必录迹。不轻问，不妄答。
> **链可接续，器可传参。AI为器，人为魂。**

## 方法层·白话

任务路由是Synthos的执行入口。分析用户查询，确定执行模式+原子链，调度执行，汇总输出。

## 触发条件

**始终加载** — 这是所有用户查询的第一个入口点。每次会话自动触发。

## 验证清单

- [ ] 查询已分析：模式确定 + 原子链确定
- [ ] 运行目录已创建
- [ ] 每步保存独立JSON文件
- [ ] 汇总输出包含所有原子结果
- [ ] 执行模式匹配查询复杂度

---

## 工作目录

```
/media/yakeworld/sda2/Synthos/
├── outputs/papers/          # 论文产出
├── outputs/evolution/       # 进化日志
├── evolution-log.md         # 进化链记录
└── skills/                  # 所有认知原子
```

## 执行流程

### 第0步：创建运行目录
每个执行会话创建唯一目录：`outputs/{session_id}/`，含 `pipeline_trace.json`

### 第1步：分析查询 → 确定执行模式

**四模式选择矩阵：**

| 模式 | 适用 | 原子链 | 行为 |
|:---
  io_contract: input: ['query: str, context: dict -> route: str, atom_chain: list[str], execution_mode: str', 'output: ['route: str, atom_chain: list[str], execution_mode: str, pipeline_trace: pipeline_trace.json']
--|:-----|:-------|:-----|
| **标准链** | 一次性查询：搜索文献/提取信息/写段文字 | ACQ→EXT→ARG 或 自定义短链 | 顺序执行，每步完报告 |
| **探索循环** | 需迭代优化的单一问题 | HYP→ARG→VER, 循环 | 提出→检验→修改, 循环≥2次 |
| **研究双循环** | 完整研究任务：文献+发现+假说+论文 | ACQ→EXT→ASC→GAP→HYP→ARG→VER | 外环(计划)+内环(执行) |
| **并行执行** | 独立子任务可并行 | 各子任务独立链 | 并行执行子任务 |

**查询→模式判断规则：**
- "搜索/查找/找文献" → 标准链(ACQ→EXT)
- "有什么关联/矛盾" → 标准链(ACQ→EXT→ASC)
- "写一段/分析" → 标准链(ACQ→EXT→ASC→ARG)
- "怎么优化/改进" → 探索循环(HYP→ARG→VER)
- "写论文/完整研究" → 研究双循环(全链)
- 包含"同时/分别" → 并行执行

### 第2-7步：标准执行

```
for each atom in chain:
  1. 加载技能：open skills/{atom}/SKILL.md
  2. 从上游JSON读取输入
  3. 执行原子任务
  4. 保存输出到 {atom}_{sequence}.json
  5. 报告简况
```

### 探索循环（exploratory_loop）

```
初始化: 定义目标+指标+基线
循环:
  1. 提出修改假说（HYP）
  2. 实施并生成论证（ARG）
  3. 验证结果（VER）
  4. 与基线对比
  5. 通过→keep，不通过→discard+改方向
  6. 检查退出条件
退出: 达目标 / 连续3次无进展 / 用户叫停
```

### 研究双循环（research_twoloop）

```
外循环(规划者):
  1. 宽搜索(ACQ) → 多源文献
  2. 跨域关联(ASC) → 发现矛盾/空白
  3. 锁定GAP → 定义研究缺口
  4. 生成假说(HYP) → 可证伪预测
  5. 计划子任务 → 交内循环

内循环(执行者):
  对每个子任务:
  1. 提取(EXT) → 精准信息
  2. 论证(ARG) → 结构化输出
  3. 验证(VER) → 多角度检查
  4. 反馈给外循环 → 调整计划
```

### 并行执行

```
子任务列表 → 并行执行子任务
汇总: 收集所有子任务输出 → 统一格式
注意: 子任务不可依赖彼此输出
```

### 链式组合（v1.8 — 吸收 Fabric Pattern Chaining）

支持管道式技能链：`技能A → 技能B → 技能C`，前者的输出自动成为后者的输入。

```yaml
chain_example:
  # 提炼论文摘要 → 提取洞见
  - skill: knowledge-acquisition
    args: {topic: "3D eye tracking"}
  - skill: knowledge-extraction
    args: {mode: "findings"}        # 自动接收上游 output.papers
  - skill: association-discovery
    args: {mode: "patterns"}        # 自动接收上游 output.knowledge_items
```

链式组合与标准链的区别：
- 标准链：Agent逐步骤解释+决策（适合有判断点的任务）
- 链式组合：数据按契约自动流转（适合无分支的流水线任务）

### 第11步：循环模式汇总

每次迭代后保存 checkpoint。会话恢复时从 checkpoint 读状态。

---

## 输出格式（pipeline_trace.json）

```json
{
  "session_id": "uuid",
  "query": "用户原始输入",
  "mode": "standard|exploratory|research_twoloop|parallel",
  "chain": ["knowledge-acquisition", "knowledge-extraction", ...],
  "atoms": {
    "knowledge-acquisition": {
      "input": "...",
      "output_file": "outputs/{session_id}/ka_01.json",
      "status": "completed|failed|skipped"
    }
  },
  "cycles": 1,
  "parallel": false
}
```

---

## 已知陷阱

1. **不要用旧Python代码** — Synthos是纯skill架构，别找core/下的Python文件
2. **输出目录不存在则创建** — 每步执行前确保目录存在
3. **上游输出未找到** — 读pipeline_trace.json确认上游已完成
4. **Agent是执行引擎** — 你(Agent)负责加载skill→理解→执行，不要写Python调度器
5. **执行完向用户报告** — 汇总+关键发现+文件路径
6. **双循环陷阱** — 外循环不执行具体任务(只是规划+分派)，内循环不修改计划(只执行+反馈)
7. **循环模式不适用一次性查询** — 搜索/提取类查询用标准链

---

## 命令层

- **Signature**: `query: str -> pipeline_trace.json + 汇总报告`
- **Allowed tools**: shell, Read, Write, task_delegation, skill_loader
- **Output**: 原子级JSON + pipeline_trace.json + 用户终报
- **Execution**: 每步独立JSON → 不拼接 → 汇总时引用文件路径
