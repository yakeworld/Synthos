---
name: task-router
description: Synthos system entry point. Routes user queries to the correct cognitive atom chain and orchestrates execution. Agent-native — no Python code, all atoms executed by Agent loading SKILL.md files. Supports three execution modes: simple chain (linear), exploratory loop (inner loop only), and research two-loop (inner+outer).
version: 1.2.0
author: Synthos Agent + AI-Research-SKILLs (Orchestra Research) absorption
license: MIT
allowed-tools: terminal web delegate_task Read Write skill_view browser_console
signature: "query: str -> mode: str, chain: list[str], loop_state: dict"
metadata:
  synthos_atom_type: "router"
  synthos_version: "1.2.0"
  synthos_skill_md_hash: "4a8d1f6e2c9b3a7e5d0f8c2a4b6e0d1f3a5c7b9e2d4f6a8c0b1e3d5f7a9c2b"
  synthos_model_tested_on: "2026-05-18T00:00:00Z"
  synthos_io_contract_ref: "references/IO_CONTRACT.md"
  synthos_change_log_ref: "references/CHANGE_LOG.md"
  synthos_asserted_compliance: "P0,P2,P3"
  synthos_depends_on: "knowledge-acquisition, knowledge-extraction, association-discovery, hypothesis-generation, argument-expression, viewpoint-verification"
  synthos_author: "Synthos Agent (v1.2.0 — 双循环编排吸收自 AI-Research-SKILLs)"
  synthos_data_access_level: "redacted"
---

## 原理层·文言

```
路由之道，统合诸子。
以问定向，以能授命。
分而治之，合而成之。
知人善任，因材施教。
```

**核心理念**：任务路由器是Synthos系统的唯一中枢，其职责不是代替各认知原子执行任务，而是理解用户问题、判断复杂度、选择最合适的执行路径，并将任务精准分派给对应的原子链。简单任务走线性速通，复杂任务进入探索循环，系统研究启用双循环架构。路由器本身不产生知识，但让知识的产生路径最优。

## 方法层·白话

# Synthos 任务路由器 (Task Router) — 技能驱动入口

## 触发条件

**本技能是 Synthos 系统的唯一入口。每次用户提问时自动加载。**

在以下情况加载：
- 每次用户与 Synthos 交互时——判断任务复杂度→选择模式→执行
- 用户明确指定原子时（如"帮我搜论文"→ACQ、"验证这个假设"→VER）
- evolution 引擎触发任务时

## 验证清单

- [ ] 用户意图已正确分类（检索/综述/假设/写作/验证/进化/研究）
- [ ] 选择的执行模式（简单链/内循环/双循环）与查询复杂度匹配
- [ ] 循环模式中：内循环每次迭代都调用了正确的原子
- [ ] 循环模式中：退出条件（收敛/最大迭代/转向）清晰记录
- [ ] 每个被调用的原子已加载其 SKILL.md
- [ ] 原子间 I/O 契约匹配
- [ ] 无 Python 代码生成（纯技能驱动）
- [ ] 输出写入 outputs/runs/ 目录 + loops/ 子目录（循环模式）

## 概述
本 SKILL.md 是 Synthos 系统的**唯一入口**。所有用户请求都通过本文件定义的流程路由到正确的认知原子链。Agent 读取本文件后，自主推理、编排和执行，不需要任何 Python 代码。

支持**四种执行模式**：
1. **简单链**（simple_chain）：线性执行选定原子，一次性完成
2. **探索循环**（exploratory_loop）：重复内循环直到收敛——适用于假设验证、实验迭代
3. **研究双循环**（research_twoloop）：内循环重复探索 + 外循环定期复盘——适用于完整研究项目
4. **并行模式**（parallel）：将可并行的子任务通过 `delegate_task` 分发到子 Agent 并发执行——适用于多库检索、多假设验证、多实验并行

双循环编排协议吸收自 **AI-Research-SKILLs (Orchestra Research)** 的 Autoresearch 架构。
并行模式利用 Hermes 内置的 `delegate_task` 工具实现子 Agent 并发。

## 工作目录
所有输出写入 Synthos 项目的 `outputs/runs/` 目录：
```
/media/yakeworld/sda2/Synthos/outputs/runs/<run_id>/
```
每次运行创建一个以时间戳命名的子目录，例如 `outputs/runs/20260518_080000/`。

循环模式中，每次迭代的子目录为：`outputs/runs/<run_id>/loops/inner_<N>/` 和 `loops/outer_<N>/`

Atom 输出文件命名规则：`<atom-name>_output.json`

## 执行流程

### 第 0 步：创建运行目录
```
run_id = 当前时间戳 (YYYYMMDD_HHMMSS)
mkdir -p /media/yakeworld/sda2/Synthos/outputs/runs/<run_id>
如果循环模式：
  mkdir -p /media/yakeworld/sda2/Synthos/outputs/runs/<run_id>/loops
```

### 第 1 步：分析查询 → 确定执行模式 + 原子链

分析用户查询，按关键词匹配确定复杂度和执行模式：

| 关键词类别 | 标记 | 示例关键词 |
|-----------|------|-----------|
| 创意 | `needs_ideation` | 创意、新想法、研究方向、brainstorm、ideation、探索 |
| 论文写作 | `needs_writing` | 写论文、写文章、学术写作、write paper、draft、投稿、撰写、IMRaD、paper framework |
| 多版本 | `needs_exploration` | 多版本、多种方案、对比、competing、alternative、变体、versus |
| 认知 | `needs_creativity` | 创造性思维、打破框架、跨领域、analogy、类比 |
| 检索 | `needs_acquisition` | 找论文、搜索、文献、find papers、search |
| 分析 | `needs_extraction` | 分析、综述、现状、趋势、analyze、review |
| 关联 | `needs_association` | 比较、对比、关系、矛盾、compare、contradiction |
| 假设 | `needs_hypothesis` | 提出、假设、新方向、hypothesis、propose |
| 写作 | `needs_expression` | 写论文、起草、撰写、write、draft |
| 验证 | `needs_verification` | 评估、检验、可行性、verify、validate |
| **研究** | **`needs_research`** | **研究、实验、迭代、优化、反复、experiment、iterate、converge** |
| **并行** | **`needs_parallel`** | **并行、并发、同时、多路、parallel、concurrent、simultaneous** |
| **双循环** | **`needs_twoloop`** | **双循环、内外、系统研究、full research、complete study、深入系统** |

**执行模式确定**：

| 条件 | 模式 | 说明 |
|------|------|------|
| 无特殊标记，简单任务 | `simple_chain` | 线性执行，一次性完成 |
| 含 `needs_exploration` 或 `needs_hypothesis` + `needs_verification` | `exploratory_loop` | 内循环：HYP→VER→ASC→重复 |
| 含 `needs_research` | `exploratory_loop` | 同上 |
| 含 `needs_parallel` 或 `needs_twoloop` + 多个独立子目标 | `parallel` | 并行分发子任务 |
| 含 `needs_twoloop` | `research_twoloop` | 内循环 + 外循环复盘 |
| `mode_hint` 明确指定则覆盖自动判断 | 按指定执行 |

**复杂度确定**（基于标记数量）：
- `simple` (1个标记)：极简链，1个原子
- `medium` (2个标记)：短链，2个原子
- `complex` (3-4个标记)：中长链，3-4个原子
- `full` (5+个标记)：完整链，5-6个原子
- `creative` (含 `needs_ideation` 或 `needs_creativity`)：创意链，前置 research-ideation 原子
- `research` (含 `needs_research` 或 `needs_twoloop`)：循环模式，不走线性链

**原子链定义**——新原子在DAG中的位置：
```
# 创意链（creative-cognition已合并入research-ideation作为Layer2）
research-ideation → [标准原子链]

# 标准原子链
knowledge-acquisition → knowledge-extraction → association-discovery → hypothesis-generation → argument-expression → viewpoint-verification
```

**输出**：写入 `<run_dir>/pipeline_trace.json` 的 `routing` 字段。

### 第 2-7 步：标准原子链执行（非循环模式）

对原子链中的每个原子，按顺序执行：

```
for each atom_name in atom_chain:
    1. 用 skill_view(name=atom_name) 加载对应的 SKILL.md
    2. 读取上游原子输出（如果有的话）
       - 从 <run_dir>/<上游atom名>_output.json 读取
    3. 按 SKILL.md 中的指令执行
       - 使用 terminal、web、delegate_task 等工具
    4. 保存输出到 <run_dir>/<atom_name>_output.json
    5. P0: 在执行记录中附 evidence_chain（引用上游数据源）
```

**对应关系**（atom 名称 → skill 名称）：
| Atom 名 | Skill 名 | 功能 |
|---------|----------|------|
| `research-ideation` | `research-ideation` | 研究创意发散与认知引擎（L1:10框架+L2:8引擎+L3:组合协议） |
| `knowledge-acquisition` | `knowledge-acquisition` | 多源文献检索 |
| `knowledge-extraction` | `knowledge-extraction` | 结构化知识提取 |
| `association-discovery` | `association-discovery` | 关联发现与分析 |
| `hypothesis-generation` | `hypothesis-generation` | 假设生成 |
| `paper-workflow` | `paper-workflow` | 人机互动论文撰写工作流（框架确认/多版本探索→写作） |
| `argument-expression` | `argument-expression` | 论证写作 |
| `viewpoint-verification` | `viewpoint-verification` | 观点验证 |

### 第 8 步：汇总输出（非循环模式）

读取所有已执行原子的输出文件，组装最终结果：
```
assembled_output.json
├── run_id
├── query
├── mode: "simple_chain"
├── routing (原子链、复杂度、跳过理由)
├── short_circuit (如有)
├── outputs: {
      "research-ideation": { ... },  (如有)
      "knowledge-acquisition": { ... },
      "knowledge-extraction": { ... },  (如有)
      ...
    }
```

### 第 9 步：探索模式（exploratory_loop — 仅内循环）

当执行模式为 `exploratory_loop` 时，不执行标准链，而是进入内循环。

#### 初始化
```
# Bootstrap：先跑一次 ACQ → EXT 获取初始信息
1. 加载 knowledge-acquisition → 获取初始数据
2. 加载 knowledge-extraction → 提取结构化信息
3. 初始化循环状态：
   {
     "inner_iterations": 0,
     "max_inner_iterations": 10,
     "exit_reason": null,
     "accumulated_results": [],
     "last_hypothesis": null,
     "last_verification": null
   }
```

#### 内循环协议（从 AI-Research-SKILLs Autoresearch 吸收）

每次迭代执行以下循环体：

```
inner_loop_iteration(N):
  1. 加载 hypothesis-generation (HYP)
     输入：累积结果 + (首次迭代为 bootstrap 数据)
     输出：{hypotheses: [...], selected_hypothesis: {...}, prediction: str}
     保存到 loops/inner_<N>/hypothesis-generation_output.json
  
  2. 加载 viewpoint-verification (VER)
     输入：selected_hypothesis, prediction
     输出：{verification_result: {confidence, evidence, gaps, contradictions}, 
            verdict: "supported|refuted|inconclusive"}
     保存到 loops/inner_<N>/viewpoint-verification_output.json
  
  3. 加载 association-discovery (ASC)
     输入：本轮的 verification_result + 历史 accumulated_results
     输出：{patterns: [...], lessons: [...], convergence_signal: boolean}
     保存到 loops/inner_<N>/association-discovery_output.json
  
  4. 更新循环状态：
     accumulated_results.append({
       iteration: N,
       hypothesis: selected_hypothesis,
       verdict: verification_result.verdict,
       confidence: verification_result.confidence,
       lessons: patterns,
       convergence: convergence_signal
     })
     inner_iterations += 1
```

#### 退出条件检查（每次迭代后）

检查以下退出条件，**优先级从高到低**：

| 条件 | 检查方式 | 退出原因 |
|------|----------|---------|
| **收敛** | ASC 输出的 `convergence_signal == true` | `converged` |
| **最大迭代** | `inner_iterations >= max_inner_iterations` | `max_iterations` |
| **用户中断** | 用户明确要求停止 | `user_interrupt` |
| **结果足够** | 3次连续验证置信度 > 0.85 | `converged` |

不满足以上条件 → 继续下一次迭代。

### 第 10 步：研究模式（research_twoloop — 双循环）

当执行模式为 `research_twoloop` 时，在内循环基础上增加外循环复盘机制。

#### 初始化
```
同 exploratory_loop 的 bootstrap + 额外初始化：
{
  "outer_iterations": 0,
  "max_outer_iterations": 5,
  "outer_reviews": [],
  "inner_iterations_in_current_outer": 0
}
```

#### 外循环协议（从 AI-Research-SKILLs Autoresearch 吸收）

外循环每 **5 次内循环迭代**后执行一次：

```
outer_loop_review(N):
  1. 读取所有内循环累积结果
  2. 加载 association-discovery (ASC)
     输入：全部 accumulated_results
     任务：识别全局模式、矛盾、缺口
     输出：{global_patterns: [...], contradictions: [...], gaps: [...], 
            narrative_update: str, direction_decision: "continue|pivot|finalize"}
     保存到 loops/outer_<N>/association-discovery_output.json
  
  3. 加载 hypothesis-generation (HYP)
     输入：ASC 的 direction_decision + narrative_update
     任务：根据复盘结果生成新方向性假设
     输出：{new_hypotheses: [...], pivot_recommendation: str, 
            is_pivot: boolean}
     保存到 loops/outer_<N>/hypothesis-generation_output.json
  
  4. 更新循环状态：
     outer_reviews.append({
       review_number: N,
       global_patterns: global_patterns,
       gaps: gaps,
       direction: direction_decision,
       pivot: is_pivot,
       new_hypotheses: new_hypotheses
     })
     outer_iterations += 1
     inner_iterations_in_current_outer = 0
```

#### 外循环退出决策

| direction_decision | 动作 |
|-------------------|------|
| `continue` | 继续内循环（重置内循环计数器） |
| `pivot` | 将新方向注入内循环的 HYP 输入 |
| `finalize` | 退出双循环，进入第 11 步汇总 |
| 达 max_outer_iterations | 强制退出 |

### 第 10b 步：并行模式（Parallel Execution）

**利用 Hermes `delegate_task` 将可独立的子任务分发到子 Agent 并发执行，大幅缩短总执行时间。**

**触发条件**：当前查询包含多个彼此独立的子目标（如同时检索3个数据库、同时验证3个假设、同时运行3个实验）

**并行协议**：

```
parallel_execute(tasks):
  1. 识别可并行执行的子任务列表
  2. 对每个子任务，构造自包含的 goal + context
  3. 通过 delegate_task(tasks=[...]) 并行分发
     - 每个子任务获得独立的上下文和终端会话
     - 最多支持 Hermes 配置的 max_concurrent_children 个并发
  4. 等待所有子任务完成
  5. 收集所有子任务的 summary
  6. 进入第 11 步汇总
```

**并行分派示例**：

```yaml
parallel_acquisition:
  description: "并行检索三个数据库"
  tasks:
    - goal: "检索PubMed: ADHD eye-tracking 2020-2025"
      context: "关键词: ADHD, eye tracking, saccade"
      toolsets: ["web"]
    - goal: "检索Semantic Scholar: ADHD eye-tracking deep learning"
      context: "关键词: ADHD, eye tracking, deep learning, CNN"
      toolsets: ["web"]
    - goal: "检索arXiv: eye movement ADHD classification"
      context: "关键词: eye movement, ADHD, classification, transformer"
      toolsets: ["web"]
```

**适用场景**：

| 场景 | 串行时间 | 并行时间 | 加速比 |
|:-----|:--------:|:--------:|:------:|
| 3数据库并行检索 | ~90s | ~35s | ~2.6x |
| 3假设同时验证 | ~180s | ~70s | ~2.6x |
| 3实验同时执行 | ~300s | ~120s | ~2.5x |

**安全约束**：
| 规则 | 说明 |
|:-----|:------|
| 子任务必须独立 | 无共享状态或数据依赖 |
| 结果需汇总校验 | 并行结果中的矛盾点须由主 Agent 仲裁 |
| 不可嵌套并行 | 子 Agent 不能再起并行（受 Hermes max_spawn_depth=1 限制） |

**意图**：填补 Synthos"单线程顺序执行"的性能短板。利用 Hermes 已有的 delegate_task 能力，对可独立的任务实现 2-3 倍的加速，使大规模文献检索和多方验证变得实用。

### 第 11 步：循环模式汇总

```
assembled_output.json
├── run_id
├── query
├── mode: "exploratory_loop" | "research_twoloop"
├── routing.complexity: "research"
├── loop_state: {
      "inner_iterations": N,
      "outer_iterations": M,  (仅 research_twoloop)
      "exit_reason": "converged|max_iterations|pivot|user_interrupt",
      "accumulated_results": [...],
      "outer_reviews": [...]  (仅 research_twoloop)
    }
├── outputs: {
      "initial_acquisition": { ... },
      "initial_extraction": { ... },
    }
```

## 输出格式（pipeline_trace.json）

写入 `<run_dir>/pipeline_trace.json`：

```json
{
  "run_id": "20260518_080000",
  "query": "用户原始查询",
  "mode": "simple_chain | exploratory_loop | research_twoloop",
  "status": "completed | short_circuited | error | loop_exited",
  "routing": {
    "complexity": "simple | medium | complex | full | research",
    "atom_chain": ["knowledge-acquisition", "knowledge-extraction"],
    "mode": "simple_chain | exploratory_loop | research_twoloop",
    "loops_executed": 5,
    "skip_reasons": ["..."]
  },
  "loop_state": {
    "inner_iterations": 7,
    "outer_iterations": 1,
    "exit_reason": "converged",
    "accumulated_results": [
      {"iteration": 1, "hypothesis": "...", "verdict": "supported", "confidence": 0.82},
      {"iteration": 2, "hypothesis": "...", "verdict": "refuted", "confidence": 0.91}
    ],
    "outer_reviews": [
      {"review_number": 1, "global_patterns": ["..."], "gaps": ["..."], "direction": "continue"}
    ]
  },
  "short_circuit": {
    "at_atom": "knowledge-acquisition",
    "reason": "Search returned zero papers across all sources",
    "executed_count": 1,
    "skipped_count": 4
  },
  "atoms_executed": ["knowledge-acquisition", "knowledge-extraction"],
  "output_dir": "outputs/runs/20260518_080000",
  "started_at": "2026-05-18T08:00:00Z",
  "completed_at": "2026-05-18T08:01:30Z"
}
```

## 动态环境调试（ENV-Debug）[吸收自 Claude Code]

**当执行报错时，自动查日志→分析失败原因→修复→重试。不再是一次失败就回滚。**

### 触发条件

执行任何原子后 exit_code ≠ 0 或输出包含 ERROR/Exception/Traceback：

### 调试协议

```
env_debug(step_name, error):
  1. 捕获完整错误输出（stdout + stderr）
  2. 分析错误类型：
     - ImportError/ModuleNotFoundError → pip install 缺失包后重试
     - FileNotFoundError → 检查路径/创建目录后重试
     - TimeoutError → 增加 timeout 后重试
     - PermissionError → 检查权限后重试
     - ValueError/TypeError → 检查参数格式后重试
  3. 执行修复操作（通过 terminal）
  4. 重新执行失败的步骤
  5. 如果重试仍失败 → 完整错误报告 + 建议替代方案
  6. 如果重试成功 → 记录修复方案到 lessons.jsonl
```

**边界**：最多重试 2 次；连续 2 次失败则停止调试并回滚。

## 动态 MCP 工具发现 [吸收自 MCP 生态]

**运行时动态发现可用工具，不硬编码 allowed-tools。**

### 发现协议

```
mcp_discover():
  1. 检查 Hermes 配置中是否启用了 native-mcp
  2. 如果已配置 MCP servers：
     - 读取 mcp_servers 列表
     - 对每个 server 发送 tools/list 请求
     - 将返回的工具合并到当前 allowed-tools
  3. 如果未配置 MCP：
     - 扫描本地 ~/.hermes/tools/ 目录下的 tool 定义
     - 加载可用工具列表
  4. 将发现的工具注册到当前会话的 tool registry
  5. 标记来源: "mcp" | "local_tool" | "built_in"
```

**意图**：不把 allowed-tools 写死。运行时发现新能力——吸收自 MCP 协议的动态工具发现机制。

## 短时情景记忆缓冲（Episodic Memory）[吸收自 Reflexion]

**在单次任务执行中维护一个短时错误缓冲区，遇到失败时立即语言反思并重试。**

### 执行协议

```
in each inner iteration:
  1. 执行当前原子
  2. 如果成功 → 清除失败计数
  3. 如果失败 → 
     a. 将错误写入 episodic_buffer[]（上限 3 条）
     b. 用自然语言反思：\"为什么这次失败？和之前类似吗？\"
     c. 如果 episodic_buffer 中已有 ≥ 2 条同类错误 → 调用 env_debug()
     d. 如果 ≥ 3 条不同错误 → 停止当前操作，建议更换策略
  4. 迭代结束时，将 episodic_buffer 清空或摘要写入 long_term_memory
```

**适用场景**：单次文献检索失败 → 反思"是不是关键词太宽泛？" → 调整后重试。
**与 Nudge 的区别**：Nudge 是进化引擎维度的宏观引导；Episodic Memory 是任务执行中的微观试错缓冲。

### 1. 不要用旧 Python 代码
`core/` 目录下的 Python 代码已经全部删除。不要尝试 import 或运行它们。所有功能通过 SKILL.md + Agent 工具实现。

### 2. 输出目录不存在则创建
`mkdir -p` 确保目录树存在。不要在运行目录不存在时报错。

### 3. 上游输出未找到
如果某原子需要读取上游输出但文件不存在：
- 第一个原子（knowledge-acquisition）不需要上游输出，这是正常的
- 后续原子如果找不到上游输出 → 记录错误到 `pipeline_trace.json` 并终止

### 4. Agent 是执行引擎
- 本 SKILL.md 由 Agent 读取并执行。Agent 的 terminal、web、delegate_task、read_file、write_file 工具即是执行手段。
- 不需要也**不应当**创建任何 Python 脚本来执行原子。

### 5. 执行完向用户报告
每个原子执行完后，向用户简要报告结果（找到 N 篇论文 / 提取了 N 条知识 / 内循环第 N 轮等）。

### 6. 双循环陷阱（v1.2.0新增）

| 陷阱 | 说明 | 避免方法 |
|------|------|---------|
| **无限循环** | 内循环未设退出条件 | 始终设 max_inner_iterations=10，永不超出 |
| **外循环过慢** | 用户等待外循环复盘 | 外循环复盘时主动向用户报告"正在复盘第 N 轮" |
| **收敛误判** | ASC 报告的 convergence_signal 不准 | 连续 2 轮收敛信号才视为真收敛 |
| **方向漂移** | 外循环 pivot 太频繁 | 至少 5 次内循环后才允许 pivot |
| **上下文膨胀** | accumulated_results 越长越长 | 每次外循环后压缩历史：保留摘要 + 最近 3 轮详细记录 |

### 7. 循环模式不适用于一次性查询
"帮我找一篇论文"、"搜索 BPPV 文献"等一次性查询不应进入循环模式。只有模棱两可的标记时才触发循环。

## 变更日志
2026-05-18: v1.2.0 — 双循环编排吸收（AI-Research-SKILLs Autoresearch）
  新增: 三种执行模式（simple_chain/exploratory_loop/research_twoloop）
  新增: 内循环协议（HYP→VER→ASC 迭代）
  新增: 外循环协议（每5轮复盘 + 全局模式识别 + 方向决策）
  新增: 循环状态追踪（loop_state schema + 退出条件）
  新增: 训练陷阱×5（循环中断/外循环过慢/收敛误判/漂移/膨胀）
  更新: frontmatter → v1.2.0, 新IO_CONTRACT, 新BOUNDARY

2026-05-10: v1.0.0 — 从 Python pipeline 重构为纯技能驱动入口。
  移除: core/atom_pipeline.py (188行), core/context.py (341行), core/agent_atom.py (180行),
        core/trust.py (156行), run_pipeline.py (207行), 所有 core/atoms/atom*.py (3,027行)
  移除: scripts/ 中依赖 Python 核心的脚本
  新增: Agent 直接编排所有原子，读取 SKILL.md 执行
  影响: Synthos 实现零 Python 代码，全部技能驱动

## 命令层·English

### Core Command: Route & Execute
```
Route the user query through Synthos cognitive atoms.
1. Classify intent and determine complexity (simple/medium/complex/full/creative/research)
2. Select execution mode (simple_chain / exploratory_loop / research_twoloop)
3. For simple_chain: load atoms in sequence, each reads upstream output from <run_dir>/<atom>_output.json
4. For exploratory_loop: inner loop of HYP→VER→ASC until convergence or max 10 iterations
5. For research_twoloop: inner loop + outer review every 5 iterations, pivot/continue/finalize
6. Write pipeline_trace.json and assembled_output.json to run directory
```

### Key Constraints
```
- No Python code generation: all atoms execute by Agent loading SKILL.md files
- Output directory: /media/yakeworld/sda2/Synthos/outputs/runs/<run_id>/
- Loop state tracked in pipeline_trace.json.loop_state
- Never exceed max_inner_iterations=10 or max_outer_iterations=5
- Report progress to user after each atom/iteration
```
