---
name: task-router
version: 1.2.0
entrypoint_type: cognitive
entrypoint_cmd: 分析查询→选模式→定原子链→建pipeline_trace→调度
entrypoint_desc: '系统入口。输入: query(str), 输出: pipeline_trace.json'
category: core
description: Synthos系统入口。分析查询→选执行模式→定原子链→调度执行→汇总输出。
signature: 'query: str, context: dict -> route: str, atom_chain: list[str], execution_mode: str, pipeline_trace: pipeline_trace.json'
allowed-tools:
- shell (bash)
- Read (view)
- Write (write)
- task_delegation (agent
- inline)
- skill_loader (view with file path)
metadata:
  synthos:
    priority: P0
    atom_type: router
    synthos_version: 1.2.0
    synthos_model_version_pin: anthropic/claude-4-opus-max@latest
    synthos_model_tested_on: '2026-07-01T00:00:00Z'
    synthos_asserted_compliance: P0,P1,P2
    synthos_mechanical_atoms: ''
    synthos_io_contract_ref: references/IO_CONTRACT.md
    synthos_evidence_schema_ref: references/EVIDENCE_SCHEMA.md
    synthos_boundary_proof_ref: references/BOUNDARY.md
    synthos_change_log_ref: references/CHANGE_LOG.md
    synthos_golden_set_ref: golden/GOLDEN_SET.md
    synthos_golden_set_origin: self_defined
    synthos_pass_threshold: '0.85'
    description: Synthos系统入口。分析查询→选执行模式→定原子链→调度执行→汇总输出。
    signature: 'query: str, context: dict -> route: str, atom_chain: list[str], execution_mode: str, pipeline_trace: pipeline_trace.json'
license: MIT
---


# Task Router — Synthos 系统入口

## IO_CONTRACT

- **input**: `query: str` — 用户原始查询
- **input**: `context: dict` — 当前会话上下文（含已执行原子、历史输出）
- **output**: `route: str` — 选择模式
- **output**: `atom_chain: list[str]` — 目标认知原子链
- **output**: `execution_mode: str` — 具体执行模式描述
- **output**: `status: dict` — 路由决策日志

## Entrypoint 调度机制

从 2026-07 起，所有 core skill 声明了 entrypoint 元数据。task-router 按以下规则自动调度：

### exec 类型（有脚本）

```yaml
entrypoint_type: exec
entrypoint: /path/to/script.py
entrypoint_cmd: script "$var1" --param "$var2"
```

1. 读 entrypoint_cmd，替换 $变量
2. 执行命令
3. 捕获输出
4. 输出给下一原子

### cognitive 类型（推理）

```yaml
entrypoint_type: cognitive
entrypoint_cmd: "从输入中提取四域"
```

1. 加载 skill → 读 entrypoint_cmd
2. Agent 按描述执行推理
3. 输出结构化 JSON
4. 更新 pipeline_trace

### 回退策略

- `skill_view(name)` 失败 → 检查 standalone-* 类 skill
- standalone skill 应优先检查 `which literature` 等 CLI
- 都不存在时 → 直接提示用户配置

## 原理层·文言

> 路由者，问之所向也。问大则大行，问细则细究。
> 四维之径：一曰直行（标准链），二曰环探（探索），
> 三曰双环（研究），四曰并行（并进）。
> 路定则行，行必录迹。不轻问，不妄答。
> AI为器，人为魂。


## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考上方完整文档。

- **[TR-001]** 路由决策 → 分析查询→选模式(单原子/管道/进化)→定原子链→调度。pipeline_trace 记录全程
- **[TR-002]** 原子链选择 → ACQ→EXT→ASC→HYP→ARG→VER 是完整链。单步任务只调所需原子。不越级
- **[TR-003]** 执行模式 → exec(有脚本)→直接执行; cognitive(推理)→agent推理; 回退→手动
- **[TR-004]** 上下文传递 → 每原子输出→下原子输入。pipeline_trace 记录每步状态。断链即停

## 方法层·白话

任务路由是Synthos的执行入口。分析用户查询，确定执行模式+原子链，调度执行，汇总输出。

## 触发条件

**始终加载** — 这是所有用户查询的第一个入口点。每次会话自动触发。

## 执行流程

### 第0步：创建运行目录

```
outputs/{session_id}/
  └── pipeline_trace.json
```

### 第1步：分析查询 → 确定执行模式

| 模式 | 适用 | 原子链 |
|:-----|:-----|:-------|
| **标准链** | 搜索/提取/写段文字 | ACQ→EXT→ARG |
| **探索循环** | 需迭代优化的单一问题 | HYP→ARG→VER, 循环≥2次 |
| **研究双循环** | 完整研究任务 | ACQ→EXT→ASC→GAP→HYP→ARG→VER |
| **并行执行** | 独立子任务可并行 | 各子任务独立链 |

**查询→模式判断规则：**
- "搜索/查找/找文献" → 标准链(ACQ→EXT)
- "有什么关联/矛盾" → 标准链(ACQ→EXT→ASC)
- "写一段/分析" → 标准链(ACQ→EXT→ASC→ARG)
- "怎么优化/改进" → 探索循环(HYP→ARG→VER)
- "写论文/完整研究" → 研究双循环(全链)
- 包含"同时/分别" → 并行执行

### 第2-7步：执行原子链 — 通过 delegate_task 派发

每个原子不应由 task-router 直接执行，而是通过 `delegate_task` 派发给子 Agent。这是2026-07-11实测验证的正确模式。

**正确的派发方式：**
```
# ✅ 正确：传用户原话
delegate_task(
    context="",                    # 空！不微操
    goal="搜索3D nystagmus文献",    # 用户原话
    toolsets=["terminal","file","web","skills"]
)
```

**错误的派发方式（本会话踩过的坑）：**
```
# ❌ 错误：写满微操指令
delegate_task(
    context="先加载knowledge-acquisition技能，会redirect到literature，
            然后调literature.py成熟脚本，不要自己写API...",
    goal="搜索...返回前8篇..."
)
```

**关键原则：**
- **context 留空或极简** — 子 Agent 自己有 SOUL.md（task-router first、skill-first、调成熟脚本）
- **goal 就是用户原话** — 不要转写，不要加步骤说明
- **toolsets 给 terminal+file+web+skills** 让子 Agent 自己选择
- **不要微操** — 告诉它"做什么"而不是"怎么做"

**验证子 Agent 行为的标准（2026-07-11实测方法）：**
1. 它加载了 skill 吗？（tool_trace 中 skill_view 调用）
2. 它调了成熟脚本还是自己写实现？（看 tool_trace 中 terminal 是否执行了 literature.py 等）
3. 执行成功吗？（看 summary 中的结果）
4. 耗时是否合理？（看 duration_seconds）

**批量子任务陷阱（2026-07-11实测）：**
- 不要试图让一个子 Agent 处理 >10 篇论文——子 Agent 有超时限制
- 批量处理不应写 Python 脚本调 literature.py——每篇独立调 API 太慢
- 正确做法：让子 Agent 直接用 Sci-Hub CDN 批量下载已知 DOI（快，0.7s/篇）

### 输出格式（pipeline_trace.json）

```json
{
  "session_id": "uuid",
  "query": "用户原始输入",
  "mode": "standard|exploratory|research_twoloop|parallel",
  "chain": ["knowledge-acquisition", "knowledge-extraction"],
  "atoms": {
    "knowledge-acquisition": {
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
8. **子Agent context 陷阱** — 不要在 delegate_task 的 context 里写详细步骤。子Agent有自己的SOUL.md。context 写越多，子Agent越倾向于"理解后再实现"而非"直接调用成熟脚本"
9. **批量任务陷阱** — 不要试图让一个子Agent处理大量论文（>10篇）。每个子Agent有超时限制。大任务应拆成多个并行子任务
10. **文献检索：jabkit-rs 优先，literature.py 仅下载** — 搜索学术文献用 `jabkit-rs fetch`（26 源，S2 已修复），`literature.py` 仅用于 PDF 下载和管线编排

---


## Golden 集合 · GOLDEN SET

- **Golden Input**: `query: "搜索3D nystagmus文献"`, `context: {已执行原子: []}`
- **Golden Output**: `route: "standard"`, `atom_chain: ["knowledge-acquisition", "knowledge-extraction"]`；创建 `outputs/{session_id}/pipeline_trace.json`（含 session_id/mode/chain/atoms 字段），delegate_task 仅传 goal（用户原话）+ 空 context
- **Golden Error**: delegate_task 的 context 写入微操指令（如"先加载skill A再调脚本B"）→ 子 Agent 实测中断（微操版 interrupted）；或 >10 篇论文派给单个子 Agent → 超时，应拆为并行子任务

## 架构参考：deer-flow 模式 (bytedance/deer-flow)

2026年最活跃的开源Super Agent框架（78.7k stars, 2898 commits, 2026-02登顶GitHub Trending #1）。

### 与Synthos的架构对比

| 模式 | Synthos | deer-flow | 借鉴价值 |
|------|---------|-----------|----------|
| 技能加载 | 始终加载 skill_view | Progressive (按需加载) | ⚠️ 大skill（paper-writing, devops）可考虑按需加载 |
| 技能激活 | auto-trigger | Slash-activation (`/skill-name`) | ✅ 精准控制单轮工具集 |
| 沙箱隔离 | 无 | E2B沙箱 per subagent | ✅ subagent隔离执行，防越权 |
| 记忆管理 | 无持久化 | Long-term Memory | ✅ 跨会话记忆增强 |
| 工具权限 | 全局 allowed-tools | Skill-level allowed-tools (slash-activation后生效) | ✅ 更精细的权限控制 |
| 子任务派发 | delegate_task | Subagent orchestration + Session Goals | ✅ 长程任务分解范式 |

### 关键洞察

1. **Progressive Skill Loading**: 技能只在需要时加载，保持上下文窗口精简。Synthos的skill-first架构可借鉴：大技能包不是一次性全部加载。

2. **Slash-Activation**: `/skill-name` 激活特定技能，该技能的`allowed-tools`策略在此轮生效。这是精准控制工具集的有效方式。

3. **Sandbox Isolation**: 每个Subagent在独立沙箱中运行，有独立的文件系统、进程空间。Synthos的delegate_task可借鉴此隔离思想。

4. **Session Goals**: 长程任务分解为明确的session goals，每个goal有明确的输入/输出契约。

### 对Synthos的启示

- delegate_task的context留空是正确的 — 与deer-flow的渐进式技能加载理念一致
- skill_view按需加载可进一步优化上下文窗口利用率
- subagent隔离可考虑通过独立tmux会话实现

---

## delegate_task 铁律

子任务派发时，遵循以下原则：

```python
# ✅ 正确
delegate_task(goal="用户的原话描述")

# ❌ 错误：加 context 微操
delegate_task(goal="...", context="先加载skill A, 再调脚本B, 然后...")
```

**规则：**
- `context` 参数传空串 `""` — 不加微操指令
- `goal` 传用户原话或极简描述
- 子 Agent 有自己的 SOUL.md + 技能库，信任它自行决策
- 子 Agent 找不到 ACQ skill 时，会 fallback 到 `literature search` CLI 命令
- 本会话实测：微操版 interrupted，信任版 5 篇 PDF ✅

执行任何任务前，按优先级检查：

### L0：不重新造轮子
- **先查 skill 库** — skills_list 看有没有现成技能
- **再查成熟脚本** — literature.py、paper-manager/download_one.py 等
- **最后查成功案例** — 之前怎么做的（如 dual-ellipse 处理流程）
- **只有以上都不存在时**，才自己写实现

### L1：能调用
- skill_view(name) 能加载 → 内容非空
- 不是 redirect stub（knowledge-acquisition 指向 literature，必须跟下去）
- 脚本路径存在、CLI 参数正确

### L2：执行稳定
- 步骤可复现，参数已验证
- pitfall 覆盖已知坑
- 同一输入 → 同一输出

### L3：成功优先
- 调成熟脚本 > 读代码后再实现 > 自己从头写
- 先调通一个最小用例 → 再扩展

### 常见违规模式（此会话发现）
- ❌ 写了 batch_pipeline_v1~v5 系列，每次都在重新实现下载逻辑。应有：直接调 literature.py
- ❌ 子任务读了现有脚本但没调用，自己写 wget。应：直接 python3 existing_script.py
- ❌ 7 源检索写成自定义 API 调用。应：直接用 literature.py --sources ...
- ❌ 只查 .bbl 不查内联 thebibliography。应：同时处理两种引用格式

### 用户风格偏好
- 简短直接，数据优先
- 要做就直接做完，不用先问"要不要"
- 做错了直接说错在哪
- 每次执行后给可验证的结果，不是描述

## 示例 · EXAMPLES

**输入**：`query: "搜索3D nystagmus文献"`, `context: {已执行原子: []}`
**输出**：`route: "standard"`, `atom_chain: ["knowledge-acquisition", "knowledge-extraction"]`；创建 `pipeline_trace.json`；delegate_task(goal="搜索3D nystagmus文献", context="")

**输入**：`query: "同时搜索VOR和BPPV两个方向的文献并分析矛盾"`
**输出**：`route: "parallel"`，拆为 2 个独立子任务（各 ACQ→EXT→ASC），并行执行后汇总关联对比

## Verification

- [ ] 查询已分析：模式确定 + 原子链确定
- [ ] 运行目录已创建
- [ ] 每步保存独立JSON文件
- [ ] pipeline_trace.json 完整
- [ ] 已向用户报告
