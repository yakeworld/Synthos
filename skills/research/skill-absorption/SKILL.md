---
name: skill-absorption
description: "双循环进化：内部反思(P0) + 外部吸收(P1)。Cross-project absorption methodology — multi-round cross-project comparison across different paradigms, active project tracking, self-expanding keyword discovery, follow-up/revisit mechanism, and structured absorption proposals. Includes internal reflexive abstraction methodology (5-step capture→abstract→formalize→integrate→elevate cycle). Search GitHub/Hermes/arXiv for external capabilities, evaluate via 5-dimension scoring, generate proposals. Internal reflection (project-experience-distillation + reflexive abstraction) runs FIRST — external absorption fills gaps that internal reflection finds."
metadata:
  type: methodology
  version: "4.3.0"
  priority: P1
  status: active
  depends_on: [project-experience-distillation, quality-gate, evolution]
---

# Skill Absorption Engine v3.0 — Active Spiral Absorption

> 从被动等待变为主动追踪。项目DB + 自扩展关键词 + 定期随访 = 螺旋式吸收。

## 架构原则

1. **主动追踪**：不等待固定周期。每次进化轮次都执行扫描。
2. **看过的项目不丢**：项目追踪数据库记录所有发现，可随访。
3. **关键词自扩展**：从项目描述/标签中提取新关键词，持续扩大搜索面。
4. **从自身缺陷发现方向**：系统诊断结果（API失败、结构退化）自动生成新关键词。
5. **P2原则**：核心原子稳定，吸收目标永远是扩展层。

## 第一原则：动灵驱动吸收（Entelechy-Driven Absorption）（v4.3.0 新增）

> **吸收不是补短缺，是选营养。系统进化不来自匮乏，来自内在形式因的完满实现。**

### 核心转变：从"缺口驱动"到"营养评估"

| 方向变化 | 旧框架（缺口驱动） | 新框架（动灵/营养驱动） |
|:---------|:------------------|:----------------------|
| 搜索动因 | "我们缺什么功能" | "在这个生长方向上，哪些营养值得摄入" |
| 评估焦点 | 外部项目有而我们没有的东西 | 外部项目的哲学/思想/技能与我们的相容性和互补性 |
| 吸收后的自问 | "缺口填上了吗" | "这个营养被有效转化、融入系统的成长逻辑了吗" |
| 空吸收期的判断 | "我们还有缺口没补" | "没有高价值营养时，内部进化继续——动灵不需要外部输入也能生长" |

### 动门（Entelechy Gate）— 每次吸收前必须过的第一道门

吸收任何外部项目前，先自问三个问题：

1. **方向相容吗？** —— 这个项目的核心哲学与 Synthos 的 7+1 框架相容吗？如果方向不相容，即使功能再强也不摄入（如同营养相克的食物）
2. **我们能转化吗？** —— 这个项目的理论/思想/技能能否经过三语层级（文言→白话→英文）被分解重组？如果不能被文言提炼，说明还没真正理解
3. **为什么是这个方向？** —— 在当前进化阶段，这个方向的营养比另一个方向更有价值吗？（主动选择，不是被动接收）

**动门未过 → 不吸收。这不是"缺失"，是"营养不适合当前生长阶段"。**

### 动灵与已有吸收流程的融合

```
动门（新）：方向相容？能转化？为什么是这方向？
    ↓ 通过
L+0（来源标注门）——来源不变
L+1（适配改造门）——改造不变
L+2（五层验证门）——五层不变，但每层的评估标准多了"营养价值"维度
L+3（独立验证门）——独立不变
    ↓ 全部通过
吸收完成 → 更新 evolution-log，标注 "absorbed as nutrition [方向名]"
```

### 吸收评估标准中的动灵维度

在已有的 5 维度评估上，增加第 6 维度：

| 维度 | 权重 | 评估方法 | 原有 |
|:-----|:----:|:---------|:-----|
| 营养方向对齐 | 0.20 | 项目的核心哲学是否与当前生长方向一致？是否指向我们在 7+1 框架中选定的增强方向？ | **新增** |

调整后权重：

| 维度 | 权重 | 评估方法 |
|:-----|:----:|:---------|
| 营养方向对齐 | 0.20 | 项目哲学方向与当前生长路径的相容性 |
| 互补性 | 0.20 | 项目的理论/思想/技能是否补充了我们已有能力？ |
| 代码/文档质量 | 0.15 | README 完整？有示例？ |
| 社区活跃度 | 0.10 | Stars, PRs, Issues 响应 |
| 集成成本 | 0.20 | 是否容易整合到纯SKILL架构？ |
| 许可证兼容 | 0.15 | MIT/Apache/BSD 优先 |

### 吸收后的动灵验证

吸收完成后，额外检查两项：

- [ ] **原生感**：吸收后的新能力在系统中是否看起来像原生生长的？——不保留被吸收项目的名称、路径、文件结构特征
- [ ] **拆解感**：外部项目的原始形式能否被三语层级完全分解？——"文言提炼"不再是可选步骤，是验证吸收质量的强制标准

### 五层提取规范（v3.10 新增）

> 吸收自 project-experience-distillation v1.3。任何外部项目吸收必须按此五层提取。

| 层次 | 名称 | 提取内容 | 吸收方式 |
|:----:|:-----|:---------|:---------|
| 0 | **文言** (Classical Essence) | 3-5 条四字格言，压缩核心哲学 | **必选先导** — 只有能用文言表达，才算真正理解 |
| 1 | **思想** (Philosophy) | 核心信念、设计哲学 | 对比→参考，不相容则停止 |
| 2 | **规范** (Standard) | 格式、接口、质量标准 | 吸收到已有规范 |
| 3 | **规律** (Pattern) | 通用模式、设计原则 | 吸收到已有技能 |
| 4 | **能力** (Capability) | 功能、工具、技能 | 无重叠→吸收；有→跳过 |
| 5 | **任务规律** (Task Pattern) | 操作流程、执行步骤 | 参考级记录 |

> 完整规范见 project-experience-distillation §五层提取规范。

> 吸收不是"看到好项目就吸"。必须先评估自身，找出缺口，只为了补缺口而吸收。

### 营养评估流程（Entelechy-Driven Assessment）（v4.3.0 更新）

> 替换旧"正确流程"——不再问"缺什么"，而问"当前生长方向需要什么营养"和"这个项目能提供什么营养"。

```python
评估前先过动门（方向相容？能转化？为什么选此方向？）
  ↓ 通过后

1. 运行内部反思（project-experience-distillation）→ 了解当前进化状态
   └── 不是在找"缺口"，而是了解"当前生长重点"
   └── 内部反思发现实际工作中的不足 → 形成营养需求
   
2. 评估候选项目的营养价值：
   └── 哲学/思想贡献（方向对齐）
   └── 规范/方法论贡献（可标准化吸收）
   └── 技能/功能贡献（能力层补充）
   
3. 对比不同方向的候选 → 选择当前阶段营养价值最高的
4. 通过四道门吸收，最后验证"这个营养被有效转化了吗"（原生感 + 拆解感检查）
```

### 过往经验（从匮乏逻辑到动灵逻辑的演进）

以下案例展示了从旧"缺口驱动"逻辑到新"动灵驱动"逻辑的范式转换：

| 案例 | 旧逻辑（为什么当时觉得要吸收） | 新逻辑（用动灵视角重新评估） |
|:-----|:-----------------------------|:---------------------------|
| Sakana AI Scientist (13k⭐) | "我们没有自动跑实验的能力" → 分析：D1=94已健康 → 能补的功能分有限 | "我们当前生长阶段是从内部反思建立方法论深度的阶段。Sakana的黑盒调参会稀释认识论诚实原则。" → 🔵 动门未过——方向不相容，跳过 |
| Fabric (41k⭐) 吸收分=4.0 | "互补性高，代码质量好" → 但没对应缺口 → 设为tracking | "Fabric的核心哲学是'AI命令行工具集'，与我们的哲学体系无交集。高互补性≠高营养价值——它提供的是功能营养，不是思想营养。" → 记录为参考级，不作为吸收目标 |
| gpt-researcher (27k⭐) MCP集成 | "已经有S2/PubMed/OpenAlex了，吸收MCP边际收益低" | "MCP集成是工具层问题，不是生长方向问题。我们的生长重点在哲学框架的实现度和内部反思的深化。" → 方向优先级不匹配，跳过 |

**核心转变**：旧逻辑问的是"有什么功能我们没覆盖"；新逻辑先问"这个项目的哲学/思想与我们的生长方向一致吗"——方向不相容，即使功能再强也不摄入。

### 方向驱动的搜索策略

搜索关键词不应来自"什么项目火"，而应来自当前生长方向和内部反思发现的实际需求：

| 内部反思发现 | 搜索方向 | 示例命中 | 预期营养类型 |
|:------------|:---------|:---------|:-------------|
| "观点验证缺竞争性解释机制" | "adversarial verification multi-perspective" | ARS反谄媚协议 | 方法论/规范营养 |
| "假设生成的方法论模板不足" | "hypothesis generation CRISP-DM template" | KILO-KIT (CBU模式) | 技能营养 |
| "编排层的循环状态机不够灵活" | "agent state machine orchestration" | LangGraph | 架构营养 |
| "吸收哲学概念没有标准化流程" | "philosophical absorption methodology" | 本会话动灵吸收 | 方法论营养 |

**营养类型分类**：

| 营养类型 | 定义 | 吸收方式 | 优先级 |
|:---------|:-----|:---------|:------:|
| 🧠 思想营养 | 哲学、理论、核心信念 | 吸收到philosophical-foundations.md或宪法 | P0 |
| 📐 规范营养 | 格式、接口、质量标准 | 吸收到已有技能的方法层或references | P1 |
| 🔧 技能营养 | 功能、工具、具体能力 | 创建新原子或扩展已有原子 | P1-P2 |
| 🏗️ 架构营养 | 编排、状态机、数据流 | 吸收到task-router或evolution引擎 | P2 |

## 架构原则 6: 双循环进化（Dual-Loop Evolution）

> **最高优先级**: 外部吸收是第二循环。第一循环是内部反思——从自己的项目工作中提取规律、凝练技能。
> 凝练自 2026-05-16 对话: 自进化+规律提取被定为 Synthos 最高优先级任务。

### 第一循环：内部反思（P0）

```
项目工作 → quality-gate（达标检查）
    ├── 通过 → project-experience-distillation（规律提取→新skill/更新）
    ├── 通过 → conversation-to-memory（记忆同步）
    └── 不通过 → 修复 → 重检
```

内部反思比外部吸收优先级更高，因为：
- 从自己工作中提取的规律直接适用于自己的系统（零适配成本）
- 它训练"从经验中学习"的能力——这是认知操作系统的核心
- 它提升思想高度（不只是"学了什么"，是"为什么有效"）

### 第二循环：外部吸收（P1-P2）

```
评估框架 → 定位缺口 → 搜索外部项目 → 评估 → 吸收提议 → 用户确认 → 执行
```

### 双循环协作

外部吸收的分析，应由内部反思的结果驱动——但这是"问题发现→营养选择"的机制，不是"缺口→填补"：

```
内部反思发现: "我的观点验证原子缺少反谄媚协议——在真实使用中出现了谄媚输出"
    ↓ 这个来自真实使用经验的"问题"（不是理论推演的"缺口"）
外部吸收: "搜索 anti-sycophancy protocol"
    ↓ 找到 ARS → 评估动门（方向相容？能转化？）→ 吸收 → 验证
```

**规则：**
- 先跑内部反思，了解系统的真实工作状态
- 从内部反思中提取"实际遇到的困难"和"可以提升的方向"
- 再决定外部吸收——吸收什么、吸收哪个方向
- 如果内部反思没有发现值得关注的方向，外部吸收应该跳过（即使找到高分项目）
- **动灵驱动**：内部反思发现"问题"（工作不畅），外部吸收提供"营养"（能解决问题的方案）。问题不是"缺"，方向不是"补"，而是"当前生长遇到了什么障碍，什么营养能帮助生长"

### Internal Reflection Methodology: Reflexive Abstraction

> Absorbed from: `reflexive-abstraction` skill (archived)

The internal reflection loop uses a **five-step reflexive abstraction cycle** to extract patterns from project work and formalize them as skills.

#### The Five-Step Reflection Cycle

**Step 1 — Capture:** After complex tasks, scan for 5 signal types:
| Signal | Self-ask |
|:-------|:---------|
| Workflow | What was the step order? |
| Correction | Did the user say "don't do this" or "do it this way"? |
| Repetition | What pattern appeared multiple times? |
| Tacit knowledge | What was assumed but not stated? |
| Insight | Did the user share any deep observation? |

**Step 2 — Abstract:** Remove project-specific details (names, dates, paths). Keep the general structure.

**Laws:**
- Usable in 3+ scenarios → qualified abstraction
- Only 1 scenario useful → too narrow, needs further abstraction
- "Do A then B" is too obvious → needs more detail

**Step 3 — Formalize:** Write as SKILL.md following constitution principles (P1 reproducibility, P2 stable sink, P3 traceability). Separate method (SKILL.md) from examples (references/).

**Step 4 — Integrate:** Register in skill tree, update evolution-state.json, update related skills' `related_skills`.

**Step 5 — Elevate:** Ask "why did it work?" rather than just "what did we do?"

| Level | Question |
|:------|:---------|
| Operational | What did we do? |
| Pattern | What method is this? |
| Principle | Why did this method work? |
| Philosophy | What deeper belief does this reveal? |

#### Verification

- [ ] New skill loads with skill_view()
- [ ] Pattern is usable in ≥2 scenarios
- [ ] Has concrete steps (not abstract philosophy)
- [ ] Has pitfalls section (from real experience)
- [ ] Has a session case study in references/
- [ ] Does not overlap with existing skills

#### Pitfalls

1. **Over-abstraction** — Too general loses practical value
2. **Under-abstraction** — Just recording operations without extracting the pattern
3. **Skipping elevation** — Recording steps without asking "why it works" misses the point
4. **Direction confusion** — `reflexive-abstraction` = internal → skills; `skill-absorption` = external → internal
5. **One-shot extraction** — Extract only one pattern per cycle. Three patterns = three skills.
6. **Create without maintain** — In future similar scenarios, first load the existing skill to check if it needs updating.

**Relationship to skill-absorption:** Reflexive abstraction is the **internal reflection** component of the dual-loop evolution model. It runs before external absorption (P0 priority) and identifies gaps that external absorption then fills. Together they form the complete absorption cycle: internal reflection captures first-hand experience → external absorption imports third-party patterns.

## 与 evolution 引擎的协作

`evolution` 技能（Synthos 进化引擎）的 EXTERNAL 步骤执行本技能定义的全部吸收流程。两个技能应共同使用：`evolution` 负责编排和定期执行，`skill-absorption` 负责吸收方法论和评估标准。

**轮转集成**：evolution 引擎每轮调用本技能的搜索、评估和扩展方法，通过 absorption-tracked.json 共享数据库。evolution 的 DIAGNOSE 结果会通过 SELF_INSPECT 机制自动生成新的搜索关键词，反馈到本技能的搜索循环中。

**主动扫描**：每次进化循环都执行。每轮选 2-3 组关键词（8类别轮转），确保所有方向定期覆盖。

**定期随访**：对已追踪项目，至少每7轮重新检查一次（star变化、新release、新doc）。

## Deep Structural Absorption (3-Phase)

当 EXTERNAL 扫描发现高价值项目（评估分 ≥ 4.0）后，执行**深度结构吸收**，将项目机制真正嵌入目标系统。本会话对 ARS v3.7.0 的吸收演示了完整流程。

### Phase 0: Pre-Absorption — Full Project Reconnaissance

在动手吸收前，先用并行子任务完成全面侦查。**不要边读边实现** — 先完整理解再动手。

**并行探索矩阵**（使用 `delegate_task` 同时派出 3-5 个子Agent）：

| 子Agent | 探索方向 | 目标文件 |
|---------|---------|---------|
| **Pipeline & Gates** | 流水线编排器+状态机+质量门控 | orchestrator SKILL.md, state machine, integrity gates, performance docs |
| **Schemas & Contracts** | 共享Schema、handoff机制、数据访问层 | handoff_schemas.md, sprint_contracts, data access patterns |
| **Agents & Protocols** | Agent prompt细节 + 核心协议机制 | devil's advocate, socratic mentor, integrity agent, anti-sycophancy |

每个子Agent产出结构化摘要。主Agent汇总后决策吸收范围和优先级。

**⚠️ 子Agent搜索结果幻觉陷阱**（2026-05-17 实战发现）：

子Agent执行 GitHub 搜索时极可能**编造项目名称和星标数**。这不是偶发，是系统性风险。避免方法：

1. **子Agent只能探索已确定真实存在的项目** — 克隆传入的任务中应包含目标项目的 URL
2. **禁止子Agent自主搜索新项目** — 搜索由主Agent通过直接 GitHub API 调用完成
3. **搜索结果必须由主Agent直接验证** — 用 `curl https://api.github.com/repos/owner/repo` 确认项目存在
4. **任何项目名听起来太完美（VeriSci/LitSynth/KnowLoop）大概率是幻觉**
5. **子Agent返回的星标数、描述、日期必须经过交叉验证**

**验证协议示例**：
```bash
# 子Agent说找到"VeriSci (528⭐)" → 验证
curl -s "https://api.github.com/repos/owner/VeriSci" | python3 -c "import json,sys; d=json.load(sys.stdin); print('EXISTS' if 'id' in d else f'HALLUCINATED: {d.get(\"message\",\"\")}')"
# 如果返回 "Not Found"，就是幻觉。所有项目在做任何报告之前都必须过此验证。
```

**输出**：吸收分析报告（含架构对比、机制映射表、吸收优先级矩阵）

**参考案例**：`references/p0-deep-analysis-storm-sci-skills-ars.md` — STORM/scientific-agent-skills/AI-Research-SKILLs 的3层深度分析完整示范。  
**五层提取案例**：`references/claude-code-5-layer-case-study.md` — Claude Code按思想→规范→规律→能力→任务五层提取的完整实践，含每层决策、吸收统计和关键发现。  
**编排协议注入案例**：`references/two-loop-orchestration-absorption.md` — AI-Research-SKILLs双循环编排→ROUTE v1.2.0的完整吸收记录，含实施步骤和陷阱清单。  
**管线执行协议**：`references/synthos-pipeline-execution-protocol.md` — SynthOS写作端到端管线执行规范（2026-05-18写作闭环审计驱动）。含11条核心规则（严禁模拟输出、多关键词搜索、PDF/BibTeX命名、40篇质量门槛、速率限制等），8项常见陷阱。

### Phase 1: Core Mechanism Injection（立即吸收）

针对小型、自包含、可直接嵌入目标原子的机制。

**典型特征**：
- 不改变目标原子的I/O合约
- 作为新步骤/子协议注入现有推理流程
- 可通过 frontmatter + reference 文件实现

**实现模式**：

| 机制类型 | 注入方式 | 示例 |
|---------|---------|------|
| 反谄媚协议 | 在原子SKILL.md的推理流程中新增Step，含表格+规则+反模式 | ARS反谄媚门控 → viewpoint-verification |
| 分类法/检测模板 | 增强已有reference文件，或新建reference | 5-type citation hallucination taxonomy → CITATION_VERIFICATION.md |
| 宪法原则 | 在宪法条文中声明，更新宪法映射表 | P6 数据访问分级 → CONSTITUTION.md |
| 元数据字段 | 在所有原子frontmatter中添加新字段 | synthos_data_access_level: raw/redacted/verified_only |
| **编排协议** | 在编排层（ROUTE）SKILL.md中新增执行模式+循环状态机+退出条件；更新I/O合约和边界文档 | **Autoresearch双循环 → task-router v1.2.0** |

**验证方式**：逐个检查注入后的原子 — 加载SKILL.md确认语法正确、reference文件存在、frontmatter合法。

### Phase 2: Schema & Contract Integration（近期整合）

针对需要新I/O合约或新数据协议的机制。

**典型特征**：
- 需要建立新的原子间数据契约
- 可能涉及新原子或新的编排模式
- 需要更新 task-router 的路由逻辑

**待吸收方向**（从ARS提取）：
| 机制 | 目标 | 实现方式 |
|------|------|---------|
| Material Passport | 知识溯源增强 | 在 knowledge-acquisition 和 viewpoint-verification 之间建立 Schema 9 产地证 |
| Sprint Contract | 任务路由可靠性 | task-router 在分发任务前建立 pre-commit 合约 |
| Generator-Evaluator | 验证/生成原子编排 | 确保 hypothesis-generation 和 viewpoint-verification 之间的 blind pre-commit |

### Phase 3: Meta-Cognition & Observers（中期参考）

针对跨原子、系统级的元认知机制。

**待吸收方向**：
| 机制 | 目标原子 | 说明 |
|------|---------|------|
| 协作深度观察 | evolution engine | 衡量碳硅协作质量的4维评分 |
| 对话健康指标 | task-router | 检测探索模式下的过早收敛 |
| 跨模型验证 | 全部原子 | 利用模型无关性做多模型交叉验证 |

### Phase Flow Control

```
发现项目 → 评估 ≥ 4.0? → 是 → Phase 0: 并行侦查
                               → 产出吸收分析报告（含哲学对比）
                               → 用户确认 → P0: 吸收执行
                               → 验证: 各原子健康检查+注册表完整
                               → Phase 2: Schema整合（月级别完成）
                               → Phase 3: Meta吸收（季度级别完成）
                               → 记录: evolution-state.json更新
```

#### P0: Absorption Execution（执行层）

当用户批准吸收后，执行阶段负责将被吸收的技能实际写入目标系统。这是一个**多原子并行任务**，不应线串行执行。

**并行执行矩阵**（使用 `delegate_task` 同时派出多个子Agent）：

| 子Agent角色 | 产出 | 典型数量 |
|------------|------|:--------:|
| **Create atom** | 纯SKILL.md原子（cognitive_atom/reference），含完整frontmatter+流程 | 2-3个新原子 |
| **Extend existing** | 向现有原子的SKILL.md追加新章节（不修改已有内容） | 1-2个扩展 |
| **Infrastructure** | 目录结构、状态分离、registry更新脚本 | 1-2个基础设施任务 |

**P0执行原则**：
1. **先在独立子Agent中创建** — 每个新原子由独立的delegate_task子Agent创建，避免跨文件上下文污染
2. **扩展使用补丁** — 对现有原子的扩展优先用 `patch`（追加新章节），而非重写整个文件
3. **最后统一注册** — 所有原子创建完成后，更新 skill_registry.json + skill_tree.json + task-router SKILL.md
4. **P0不涉及Schema变更** — Schema变更属于Phase 2

**P0完成检查清单**：
- [ ] 所有新SKILL.md文件存在且格式正确（frontmatter + body）
- [ ] 所有扩展段落已追加（不破坏原内容）
- [ ] skill_registry.json已添加新条目
- [ ] skill_tree.json已更新count和拓扑
- [ ] task-router已更新路由关键词+原子映射+DAG
- [ ] 基础设施（如.evolution/)已创建

**边界规则**：
- **Phase 1 不依赖 Phase 2**：可以单独执行和验证
- **Phase 2 可以跳过**：如果项目没有新Schema需求
- **Phase 3 是可选**：只有高价值项目值得元认知增强
- **P0 执行需用户批准，除非自主执行阈值适用**：默认需要用户明确批准（"开始吸收"或类似指令）。但如果符合自主执行条件（推测置信度≥80%、不触及核心哲学/外部费用/不可逆操作），可自主执行。执行后附推理链解释"为什么推测用户会同意"。

#### Multi-Project Philosophy Comparison（v3.5.0 新增）

当同时发现多个高价值项目（≥4.0评分）时，执行多项目哲学对比，而不是逐项目吸收。

**适用场景**：多个项目在同一维度或同一范式上各有优势，需要理解它们的哲学差异后再决定吸收策略。

#### 3-Layer Deep Analysis Pattern（v3.8.0 新增）

对于 P0 级项目，执行 **3层深度分析**（哲学→架构→可吸收模式），而不是浅层特征对比：

```
Layer 1: Philosophy（思想）
  └── 项目最核心的信念是什么？（e.g., STORM: "最难的是问对问题"）
  └── 解决什么问题？用什么思路解决？
  └── 碳硅比例如何？（全自动 vs 人在回路）

Layer 2: Architecture（架构）
  └── 管线结构（流程图梳理）
  └── 关键模块/组件（PersonaGenerator, ConvSimulator 等）
  └── 数据流（输入→处理→输出路径）
  └── 哪些依赖是项目自有的 vs 生态通用的？

Layer 3: Absorbable Patterns（可吸收模式）
  └── 每个核心机制分类：
      ├── ✅ 可吸收：可直接注入 Synthos 原子的模式
      └── ❌ 不可吸收：Python 强依赖/专有API/框架锁定
  └── 为每个可吸收模式标注目标原子（ACQ/EXT/ASC/HYP/ARG/VER/ROUTE）
  └── 吸收优先级：P0（核心机制）→ P1（增强机制）→ P2（参考模式）
```

**输出格式**：每个项目产出一张 3×3 吸收映射表：

| 模式 | 目标原子 | 优先级 | 是否直接可迁移 |
|:----:|:--------:|:------:|:--------------:|
| 多视角Persona生成 | ACQ+EXT+ASC | P0 | 🔄 需改DSPy→SKILL.md |
| Co-STORM对话协议 | ROUTE | P1 | 🔄 协议可迁移 |
| ... | ... | ... | ... |

**关键发现提炼**：分析完成后，提炼一个跨项目的 critical finding，揭示它们的互补关系——例如本会话发现 STORM 擅长问问题、scientific-agent-skills 擅长访问数据源、AI-Research-SKILLs 擅长编排——三者互补而非竞争，各自填不同的原子缺口。

**对比维度**：

| 维度 | 问题 | 判断方法 |
|:-----|:------|:---------|
| **范式** | 纯SKILL.md vs Python运行时 vs 混合？ | 读项目结构：有无Python/JS文件依赖 |
| **碳硅比例** | Agent独立vs人在回路？ | 读AGENTS.md/README，看每步需不需要人决策 |
| **原子粒度** | 细粒度(12+原子) vs 粗粒度(7原子)？ | 统计SKILL.md数量和行为分类 |
| **核心主张** | 项目最坚信的信念是什么？ | 读README第一段+哲学声明段落 |
| **最弱一环** | 项目最明显的局限 | 读CHANGELOG/Issues/FAQ |

**并行侦察策略**：同时派出3-5个子Agent，每个克隆并深度分析一个项目。每个子Agent产出一份结构化摘要（哲学+架构+核心机制+可吸收点）。主Agent汇总后形成对比矩阵。

**输出格式**：对比表（项目×维度）+ 思想谱系图 + 吸收优先级矩阵

**边界规则**：如果只发现1个高价值项目，不需要多项目对比，走标准吸收流程。

### 吸收报告模板

每次深度吸收后，在 `Synthos/docs/` 下保存吸收报告。模板参见 `docs/ars_absorption_report.md`（ARS吸收实作范例）。

---


## 核心流程

### 1. 项目追踪数据库

所有发现的项目存储在 `outputs/evolution/absorption-tracked.json`：

```json
{
  "id": "gh:owner/repo",
  "source": "github | hermes_skill | paper",
  "name": "项目名称",
  "url": "https://...",
  "stars": 12000,
  "description": "项目描述",
  "first_seen": "2026-05-08",
  "last_checked": "2026-05-11",
  "status": "tracking | evaluating | absorbed | deferred | archived",
  "absorption_score": 4.2,
  "absorbed_skills": [],
  "tags": ["cognitive-flow", "skill-md"],
  "notes": "评估笔记"
}
```

状态生命周期：tracking → evaluating → absorbed | deferred → archived

### 2. 关键词轮转策略

关键词库按类别组织，每轮选2-3组未使用/久未使用的关键词：

| 类别 | 示例关键词 | 轮流节奏 |
|------|-----------|---------|
| research_agent | AI research assistant, scientific discovery agent | 每2轮 |
| architecture | cognitive skill framework, agent orchestration | 每3轮 |
| literature | academic literature automation, paper search agent | 每3轮 |
| knowledge | knowledge graph extraction, structured knowledge | 每3轮 |
| reasoning | hypothesis generation AI, argumentation framework | 每4轮 |
| pipeline | research paper agent LLM pipeline | 每4轮 |
| evaluation | benchmark research agent, scientific claim verification | 每4轮 |
| self_discovered | 从关键词扩展中动态生成的词 | 每2轮 |
| **industry_leaders** | **claude-code, cursor, copilot, aider** | **每4轮** |

> 2026-05-16: 新增 industry_leaders 类别。用于定期扫描业界领头羊（Claude Code 123K⭐, Cursor, etc.），不为了吸收而吸收，而是为了哲学对比和架构参考。从Claude Code的Hook系统吸收已验证此模式的价值：只吸了Hook事件系统，其他都是参考级。

### 3. 关键词自我扩展

从新发现项目的 topics/description 中自动提取新关键词：

1. 提取 project.topics → 所有标签
2. 提取 project.description → 核心名词短语（3-5个词的领域术语）
3. 过滤：已在关键词库中、过于通用（python/ai/llm）、非英文
4. 价值评估：
   - 在 >=2 个不同项目出现 → **high value**，立即加入
   - 与已有关键词强相关 → **medium value**，加入下一轮候选
   - 全新领域词 → **low value**，加入自发现池，每3轮重评估
5. 新关键词加入 `self_discovered` 类别，标记来源

**示例**：从 AutoResearchClaw 发现 "citation graph analysis" → 追加到关键词库 → 下一轮搜这个方向 → 发现更多引用验证项目。

### 4. 自检关键词生成

从系统自检结果（PROBE/DIAGNOSE）自动生成新搜索方向：

| 发现 | 生成的关键词方向 |
|------|----------------|
| 某个原子结构分 < 0.7 | [原子功能] improvement / alternative |
| 某 API 连续失败 | [API名] replacement / alternative |
| 技能树覆盖率 < 0.5 | skill framework, cognitive architecture |
| golden 测试缺失 | 从 golden_set 提取相关领域关键词 |
| 历史 lesson 提示特定缺陷 | lesson issue 相关的搜索词 |

### 5维度+1 营养评估标准（v4.3.0 更新：增加了"营养方向对齐"维度）

每个候选项目按以下维度打分（0-5），先过动门后评估：

| 维度 | 权重 | 评估方法 |
|------|:----:|---------|
| 营养方向对齐 | 0.20 | 项目哲学方向与当前生长路径的相容性？是否指向7+1框架的增强方向？ |
| 互补性 | 0.20 | 项目的理论/思想/技能是否补充了我们的能力？ |
| 代码/文档质量 | 0.15 | README 完整？有示例？ |
| 社区活跃度 | 0.10 | Stars, PRs, Issues 响应 |
| 集成成本 | 0.20 | 是否容易整合到纯SKILL架构？ |
| 许可证兼容 | 0.15 | MIT/Apache/BSD 优先 |

综合分 = Σ(维度分 × 权重)

| 综合分 | 决策 |
|--------|------|
| >= 4.0 | 🔥 强烈建议吸收，生成提议 |
| 3.0-3.9 | 👍 设为 evaluating 状态 |
| < 3.0 | ⏭️ 设为 archived 状态 |

#### 6.2 学术论文/概念性项目评估（5维度·动灵版）

当目标为arXiv论文、概念性框架、思想性博客等非GitHub项目时，使用以下维度：

| 维度 | 权重 | 评估方法 |
|------|:----:|---------|
| 哲学对齐 (Philosophical Alignment) | 0.20 | 核心信念与设计哲学是否与目标系统相容？不相容则停止 |
| 营养互补 (Nutritional Complement) | 0.25 | 概念/理论/思想在当前生长方向上的营养价值？ |
| 生态影响 (Ecosystem Impact) | 0.15 | 吸收后能带来长期生态价值（引用/合作/范式定位）？ |
| 可转化性 (Transformability) | 0.25 | 概念是否可经过三语层级被分解重组为可执行技能/流程？|
| 内容质量 (Content Quality) | 0.15 | 论证是否完整、证据充分、引用可靠？ |

综合分 = Σ(维度分 × 权重)

| 综合分 | 决策 |
|--------|------|
| >= 4.0 | 🔥 强烈建议吸收，产出吸收记录+技能更新 |
| 3.0-3.9 | 👍 记录为 reference（只记录不修改系统） |
| < 3.0 | ⏭️ 跳过，记录理由 |

## Local Project Absorption (from adjacent file systems)

Not all absorption targets are on GitHub — some are **local projects** sharing the same filesystem. The academic_writer → Synthos pattern demonstrates this.

### When Local Absorption Applies

- A project on the same machine has capabilities that complement Synthos's atoms
- The external project is NOT a GitHub repo but a local development directory
- Integration cost is low because both projects share the same Agent runtime environment

### Assessment Criteria for Local Projects

| Criterion | Weight | Definition |
|-----------|--------|-----------|
| Nutritional Value | 0.30 | Does it provide valuable theory/methodology/skill nutrition for our current growth direction? |
| Content Quality | 0.25 | Density of validated, structured information (e.g., 126-node knowledge graph vs scattered notes) |
| Integration Cost | 0.25 | Can it be absorbed as pure SKILL.md files? (NO Python dependencies) |
| Maintenance Burden | 0.20 | Will the source project drift without active maintenance? |

### Workflow

1. **Inventory** — list all directories/subdirectories, identify what each contains
2. **Extract candidate skills** — which knowledge domains or tool capabilities are self-contained?
3. **Assess** — score each candidate on the 4 criteria
4. **Create extended skills** — write SKILL.md files in Synthos/skills/<name>/ with clear "Origin: absorbed from ..." header
5. **Register** — update skill_registry.json + skill_tree.json + evolution-state.json
6. **Verify** — load the new skill with `skill_view(name)` to confirm it's accessible

### Concrete Example: AKNE → Synthos (2026-05-12)

Source: `/media/yakeworld/sda2/academic_writer/yakeworld/.knowledge/` — 126 nodes, 137 edges, BPPV knowledge + research methodology concepts.

**Candidates created:**
- `bppv-expert` — BPPV diagnosis, repositioning maneuvers, nystagmus interpretation, 3D biomechanical simulation
- `research-thinking-framework` — Five-principle reasoning: First Principles, Bayesian, Falsificationism, Model-Dependent Realism, Free Energy

**Scoring:**
- Complementarity: 4.5/5 (Synthos lacked structured medical domain knowledge)
- Content Quality: 4.0/5 (60+ papers compiled, wiki-structured, falsification-tested)
- Integration Cost: 5.0/5 (pure SKILL.md, zero dependencies)
- Maintenance: 3.5/5 (AKNE is actively maintained, but may diverge)

**Total: 4.0/5 → STRONG ABSORB**

### Pitfall: Overlapping Capabilities

In this session, `academic_writer/work/src/` multi-source search tool was assessed but NOT absorbed because: (a) Synthos `knowledge-acquisition` atom already covers S2/PubMed/OpenAlex/arXiv/Crossref, and (b) the overlap was too large to justify absorption. The unique value (PDF download strategy + BibTeX generation) was noted for future evaluation.

**Rule**: If 60%+ of a project's capabilities already exist in Synthos, don't absorb the whole project — extract only the unique 40% as a focused extension.

## Registration After Absorption

After creating the SKILL.md files in Synthos/skills/<name>/, register them across three data stores:

### 1. skill_registry.json
Add a top-level entry with the skill's metadata (name, type, version, status, source, absorption_date, synthos_dimensions, depends_on, files). This is a dict, not an array — add as `"skill-name": { ... }`.

### 2. skill_tree.json
Update `total_skills`, `extended_skills`, and `last_absorption` with the date, source project, and skills absorbed.

### 3. evolution-state.json
Update the `skill_tree` subsection (same fields as skill_tree.json plus `external_absorptions` counter). Append to the `absorptions` array with date, source, skills, evaluation_score, and notes.

### 4. absorption-tracked.json  \
Update the source project's entry: change status from "evaluating" to "absorbed", add absorbed_skills list, update last_checked.

### ⚠️ JSON Key Collision Pitfall

Same key name must not appear as BOTH a dict and a scalar in the same JSON object. For example, `extended_skills` used as the skills dict AND as a counter integer (`"extended_skills": 3`) causes Python's `json.load()` to return the **last occurrence** (the integer), silently losing the dict. The counter field must use a **different name** like `extended_count`.

```jsonc
// ❌ WRONG — extended_skills appears both as dict (line N) and int (line M):
{
  "extended_skills": {   // ← parsed, then overwritten
    "foo-skill": { ... },
    "bar-skill": { ... }
  },
  "total_skills": 13,
  "extended_skills": 3,  // ← overwrites the dict above!
}

// ✅ CORRECT — use distinct key for the counter:
{
  "extended_skills": {
    "foo-skill": { ... },
    "bar-skill": { ... }
  },
  "total_skills": 13,
  "extended_count": 3,  // ← different key, no collision
}
```

This applies to any registry/state JSON that carries both skill objects and summary counts (skill_registry.json, skill_tree.json, evolution-state.json).

### Registration Example (from AKNE absorption, 2026-05-12)

```json
// skill_registry.json entry
"bppv-expert": {
  "name": "bppv-expert",
  "type": "extended",
  "version": "1.0.0",
  "status": "active",
  "category": "medical",
  "source": "akne-absorption",
  "absorption_date": "2026-05-12"
}

// evolution-state.json absorption record
{
  "date": "2026-05-12",
  "source": "AKNE (yakeworld/.knowledge/)",
  "skills": ["bppv-expert", "research-thinking-framework"],
  "type": "extended_knowledge",
  "evaluation_score": 4.0
}
```

### External Skill Adaptation Checklist

When absorbing a skill from another project (GitHub repo, Hermes skill, local project), the source SKILL.md will contain project-specific assumptions that must be adapted before integrating into the target system. This is NOT optional — an unmodified copy will have stale path references, privacy rules, and backend defaults that don't apply.

| Adaptation | What to check | Example from nature-figure → Synthos figure-generation |
|------------|---------------|-------------------------------------------------------|
| **Remove backend-choice gates** | Does the skill force a language choice (Python/R)? The target system may have a fixed default. Remove the blocking gate and set the default. | nature-figure had a blocking "Python or R?" gate. Synthos default: Python only. Gate removed. |
| **Remove privacy rules** | Does the skill mention hidden local paths, template collections, or provenance-protection rules? These reference the source author's filesystem. Delete all privacy directives. | nature-figure had 3 privacy rules (don't reveal template path, don't expose private dirs). All removed. |
| **Add IO contracts** | Does the skill define what input it expects and what output it produces? The target pipeline needs explicit contracts for upstream/downstream atom integration. | Added Input: {claim, data, target, panel_count}. Output: {SVG asset, figure_legend, pipeline_meta}. |
| **Adapt frontmatter** | Does the skill's `---` frontmatter match the target project's schema? Add `allowed-tools`, `meta.archetype`, `inherits`, `version`, and remove source-project specific fields. | Renamed `inherits: nature-figure (absorbed ...)`, added `layer: extended`, added allowed-tools. |
| **Create reference files** | Does the source have rich `references/` content? Copy and condense the most valuable ones into the target's `references/` directory. Don't mirror everything — keep what's actionable for future execution. | nature-figure had 11 reference files → kept 6 (figure-contract, api, design-theory, common-patterns, qa-contract, nature-2026-observations). |
| **Update skill description** | Rewrite the description to describe what the skill DOES for the target system, not what the source project was. Use active verb + domain context. | From "Submission-grade Nature figure workflow" to "发表级科研图表创建——Figure契约方法论..." |
| **Verify pipeline integration** | If the target has a task router / orchestration layer, add a `pipeline_integrated` field and note which upstream skill feeds into this one. | figure-generation receives claim from argument-expression, returns SVG asset for latex-output. |

### 5. 搜索渠道

### 1. GitHub 搜索
- Star >= 50
- 最近 1 年内有更新
- 有 README 和文档

### 2. Hermes 技能库

用 `skills_list` 扫描所有可用技能，评估互补性。

### 3. 学术论文/博客

搜索 "AI agent for scientific research", "autonomous literature review system", "knowledge-driven research assistant" 等。

### 4. 社交媒体推送（小红书/微信公众号/推特）

用户可能分享 **Xiaohongshu (小红书)** 等社交媒体的链接。这些链接指向的不是直接目标，而是**线索**：

| 渠道 | 提取方式 | 跟进动作 |
|:-----|:---------|:---------|
| Xiaohongshu | 解析HTML中的`<meta name=\"description\">`或JSON中的`\"desc\"`字段；通过`curl -sL`获取页面→`python3 -c`提取描述 | 提取文末的GitHub/arXiv/DOI链接 → 进入标准评估流程 |
| 微信公众号 | 通常需要浏览器渲染，用`browser_navigate`获取全文 | 提取文中提及的工具/论文名称 → 搜索确认 |
| Twitter/X | 通过xurl CLI或API获取tweet内容 | 提取链接或工具名 |

**关键规则**：社交媒体帖子是**诱发源（trigger）**，不是**吸收目标**。帖子中的链接才是目标。不要直接吸收帖子内容——永远追到GitHub/arXiv/DOI链接后再评估。

**执行示例**（2026-05-21 实战）：
```
用户分享: xhslink.com/o/4AikVtTUgr2 (Agent4S)
步骤1: curl获取页面 → 提取<meta name="description">
步骤2: 提取 arxiv.org/abs/2506.23692
步骤3: 运行学术论文评估标准（见§6.2）
步骤4: 创建吸收记录 + 更新目标技能
```

### 6. 评估标准

评估标准根据目标类型不同而分化：

#### 6.1 GitHub项目评估（5维度·原版）

| 维度 | 权重 | 评估方法 |

## 吸收提议格式

```json
{
  "id": "ABS-001",
  "source_type": "github | hermes_skill | paper",
  "name": "项目名称",
  "url": "https://...",
  "complementarity_score": 4.2,
  "nutrition_type": "思想 | 规范 | 技能 | 架构",
  "nutrition_rationale": "为什么这个营养在当前生长方向上有价值",
  "proposed_action": "创建新技能 or 增强已有原子",
  "integration_effort": "low | medium | high",
  "rationale": "为什么吸收..."
}
```

## 吸收后的验证

吸收新技能后，需要：
1. **文言提炼（必选）**：吸收完成后，先在原理层加入 3-5 条文言四字格言，压缩核心思想。文言是对吸收内容的最高层次抽象——只有真正理解了原理，才能用文言表达。具体遵循三语层级原则：原理层·文言（先）→ 方法层·白话 → 命令层·英文。
2. **吸收五层验证**：按思想→规范→规律→能力→任务规律五层逐层验证，确保每一层都有实质吸收而非表面搬运。
3. 集成到技能树（更新 skill_count）
4. 下一轮 BENCHMARK 测试新能力
5. 记录到 evolution-log.md
6. 如果新技能包含 golden 测试 → 验证测试通过

## Pitfalls

- **关键词死的**：如果持续搜不到新项目，说明关键词需要更具体或换方向
- **不要只看star数**：小团队项目（如KILO-KIT仅24⭐）可能比大项目更有架构借鉴价值
- **忽略已吸收项目**：即使吸收了，仍要继续随访——上游可能有新功能
- **Python代码不能复制**：转写为Agent原生指令
- **只提议不执行**：等待用户批准
- **Entelechy-driven, not opportunity-driven**：高分项目 ≠ 应该吸收。先过动门（方向相容？能转化？为什么选这个方向？）。如果方向不相容，即使见到 50k⭐ 的项目也仅记录为 reference。只有动门通过后才进入四道门评估框架。**不过动门就吸收 = 盲目功能堆积 = 聚集而非生化**。
- **`patch` 与部分读取的冲突**：absorption-tracked.json 随项目增多可达数百行。如果用 offset/limit 部分读取（如"前500行"），随后用 `patch` 操作会触发"部分读取→潜在覆盖"警告。**安全做法**：对需要 patch 的文件，始终全量读取后再应用 patch。ex. 用 `cat` 一次性读取整个 JSON 而非片段。
#### `patch` 转义陷阱（v3.6.0 新增）

`skill_manage(action='patch')` 和 `patch` 工具中，new_string 里的 `\n` 是**文字字符**，不是换行符。以下写法会写出字面字符串 `\n`：

```
# ❌ 错误 — 写出 literal '\n'
patch(old_string="xxx", new_string="line1\n\nline2")

# ✅ 正确 — 使用真实换行
patch(old_string="xxx", new_string="line1

line2")
```

**检测方法**：patch 后立即 `skill_view(name)` 检查目标行——如果看到 `\n` 文本出现，说明转义失败。修复方法：重新 patch，将 `\n` 替换为编辑器中的真实换行。

#### 吸收后四重同步检查（v3.6.0 新增）

吸收完成后，执行以下**强制同步检查**，防止边界文档与 SKILL.md 不一致：

| 检查项 | 文件 | 验证内容 | 失败后果 |
|:-------|:-----|:---------|:---------|
| SKILL.md §4 | skills/<atom>/SKILL.md | 边界声明覆盖新能力归属？ | Agent不知谁负责 |
| BOUNDARY.md | skills/<atom>/references/BOUNDARY.md | 有 pwbench/新能力边界行？ | 文档与代码不一致 |
| CHANGE_LOG.md | skills/<atom>/references/CHANGE_LOG.md | 版本+日期+类型+审批人齐全？ | P3留痕缺失 |
| references 索引 | skills/<atom>/SKILL.md 末段 | 新 reference 在索引中？ | Agent找不到文件 |

**P0要求**：四重同步是刚性的，不是可选的。任何一项失败，吸收不算完成。
- **Local project JSON with partial read**：`absorption-tracked.json` 和 `evolution-state.json` 是 Synthos 项目本地文件（位于 /media/yakeworld/sda2/Synthos/outputs/evolution/），不在 Hermes 技能存储中。如果用 `read_file` 的 offset/limit 参数部分读取它们（如前500行），随后任何写入操作（`patch`、`write_file`）都会触发"部分读取→潜在覆盖"警告。**安全做法**：始终用 `cat` 或全量 `read_file` 读取整个文件后再修改。读取 JSON 时用 `python3 -c "import json; print(json.dumps(json.load(open(...)), indent=2))"` 确保完整内容可见。

## Awesome List Cascading — 生态扫描加速器（v3.7.0 新增）

> 不使用逐关键词搜索，而是利用社区精选的 Awesome List 作为一站式生态扫描捷径。一次 README 阅读即可获取 30+ 项目线索。

### 动机

传统关键词搜索（GitHub搜 `auto research agent`）每次返回 10-30 个项目，但搜索词有限且容易遗漏跨类别项目。Awesome List 是社区经过筛选的**生态全景图**——一次扫描即可覆盖完整生命周期的所有主流项目。

### 工作流

```
1. 找 Awesome List
   └── GitHub 搜 "awesome auto research", "awesome research agent", "awesome-ai-for-science"
2. 级联扫描
   └── 一次 README 阅读 → 30+ 项目线索（已按类别/星标/描述组织好）
3. 交叉比对
   └── 每个项目对照 absorption-tracked.json:
       ├── 已存在且状态不变 → 跳过
       ├── 已存在但 star/status 变化 → 更新 last_checked
       └── 全新项目 → 进入评估流水线
4. 批量评估
   └── 对全部新项目用 5 维度打分法一次性评估
       ├── ≥4.0 → 🔥 高价值候选
       ├── 3.0-3.9 → tracking
       └── <3.0 → deferred
5. 分类归档
   └── 将生态快照保存为 reference 文件（含项目名称/类目/评分）
```

### 与 Keyword Search 的对比

| 维度 | Keyword Search | Awesome List Cascading |
|:-----|:---------------|:----------------------|
| 单次覆盖率 | 10-30 个项目 | 30-50+ 个项目 |
| 分类质量 | 需自行分类 | 社区已分类 |
| 时效性 | 实时 | 可能滞后 1-3 月 |
| 偏差风险 | 搜索词偏差 | 策展人视角偏差 |
| 最佳用途 | 补充最新项目 | 建立生态全局认知 |

### 执行示例（2026-05-15）：Awesome-Auto-Research-Tools

来源: https://github.com/handsome-rich/Awesome-Auto-Research-Tools ⭐427

| 类别 | 项目数 | 代表性项目 |
|:-----|:------:|:----------|
| 端到端自主研究系统 | 13 | karpathy/autoresearch, SakanaAI/AI-Scientist, RD-Agent, AutoResearchClaw, ARIS, AI-Scientist-v2, Agent Laboratory, AI-Researcher, claude-scholar, Biomni, DeepScientist, DATAGEN, Idea2Paper, InternAgent |
| 深度调研与文献综合 | 12 | DeerFlow, STORM, GPT Researcher, ChatPaper, 通义DeepResearch, Open Deep Research, PaperQA2, DeepResearchAgent, Auto-Deep-Research, OpenScholar, ChatReviewer, OpenResearcher |
| 自动化实验与代码智能体 | 7 | AutoGPT, OpenHands, Aider, SWE-agent, PaperBanana, MLE-agent, AIDE |
| 研究 Skills 与插件合集 | 2 | scientific-agent-skills (133 skills), AI-Research-SKILLs (86 skills) |
| Awesome Lists | 3 | awesome-ai-for-science, Autonomous-Agents, Awesome-Deep-Research |

**发现的新高价值候选**（不在现有 absorption-tracked.json 中）：
- DeepScientist — Findings Memory + Bayesian optimization 架构
- AI-Scientist-v2 — BFTS agentic tree search
- OpenResearcher — 完全开源 deep research 模型 30B-A3B
- PaperBanana — 多智能体学术插图生成

**边界规则**：
- Awesome List 是**索引**，不是购物车。不因项目在列表中就自动吸收。
- 每个项目仍需独立评估互补性和缺口匹配。
- 优先检查哪些项目已存在于 absorption-tracked.json，避免重复录入。
- Awesome List 可能遗漏最新（<1月）的项目，仍需 Keyword Search 补充。

### 维护

- 每 30 天重新扫描已知 Awesome List 的 star 变化和新条目
- 新发现的 Awesome List 加入 `absorption-tracked.json` 的 tracking 集合
- 生态快照 reference 文件保持更新

## 跨项目多轮吸收方法论（Multi-Round Cross-Project Absorption）— v4.0 新增

> 凝练自 2026-05-16 跨 3 个项目（Claude Code → DSPy → LangGraph）的系统性对比吸收实践。
> 每次吸收迭代，s 选定一个**不同范式**的外部项目，系统性对比、提取缺口、吸收模式。

### 核心理念：范式分化

不是连续吸收多个同类项目（如 3 个 AI 编码 Agent），而是每次选择**完全不同的范式**：

| 轮次 | 参考项目 | 范式 | 吸收要点 |
|:----:|:---------|:-----|:---------|
| 1-2 | Claude Code | CLI 终端 Agent | 哲学免疫系统/漂移检测/渐进披露/响应质量门 |
| 3 | DSPy | 声明式编程框架 | 类型签名/自动优化器 |
| 4 | LangGraph | 有状态图执行 | 持久执行/条件分支/拦截点/追踪 |

**原则**：每轮选上个轮次**不同**的范式。如果上轮看了 Agent 平台，这轮看声明式框架，下轮看状态机。不同范式暴露不同缺口。

### 标准流程

```
┌────────────────────────────────────────────────────┐
│  Round N: Pick Next Paradigm                      │
│  └── 列举候选方向（Agent/框架/图谱/生态/...）      │
│  └── 选与已吸收项目最不同的范式                     │
├────────────────────────────────────────────────────┤
│  1. RESEARCH — 研究参考项目核心特征                 │
│     └── 用 README / 架构文档 / API 做快速侦察        │
│     └── 产出: 4-6 个可吸收模式候选项                 │
├────────────────────────────────────────────────────┤\n│  2. NUTRITION ANALYSIS — 对照现有系统评估营养价值  │\n│     └── 表格格式: 项目特征 | Synthos现状 | 营养价值 | 营养类型 |\n│     └── 区分: 思想/规范/技能/架构 四种营养类型      │\n│     └── 产出: 营养评估矩阵（含优先级）               │
├────────────────────────────────────────────────────┤
│  3. PLAN — 选定吸收项                              │
│     └── 排优先级：P0 核心模式 → P1 增强 → P2 参考   │
│     └── 每个吸收项标注目标技能/文件                   │
│     └── 产出: task list + 每项预计 tool calls        │
├────────────────────────────────────────────────────┤
│  4. EXECUTE — 逐项吸收（一次一件事）                 │
│     └── 更新 SKILL.md / 创建新文件                   │
│     └── 每项完成后立即验证                            │
├────────────────────────────────────────────────────┤
│  5. VERIFY — 全量验证                              │
│     └── 所有修改的文件可加载                          │
│     └── L1 格式门通过：frontmatter + 触发条件 + 验证  │
│     └── 吸收记录 updated                             │
├────────────────────────────────────────────────────┤
│  6. RECORD — 记录本轮吸收                          │
│     └── memory 更新吸收记录                          │
│     └── 更新 absorption-tracked.json                 │
│     └── 更新 changelog                               │
└────────────────────────────────────────────────────┘
```

### 营养评估表格式

每轮使用的标准表格（从"缺口分析"升级为"营养评估"）：

| 外部项目特征 | Synthos 当前状态 | 营养类型 | 营养价值 | 吸收位置 | 状态 |
|:------------|:----------------|:--------:|:--------:|:---------|:----:|
| ARS 反谄媚协议 | VER 无系统性反谄媚门控 | 🧠 思想 + 📐 规范 | P0 核心 | VER技能 §4 | ✅ |
| LangGraph 条件分支 | evolution 简单if/else | 🏗️ 架构 | P1 增强 | evolution §8 | ⏳ |
| Claude Code Hook系统 | evolution 无事件驱动 | 📐 规范 | P1 增强 | evolution §Hook | ✅ |

优先级规则：🧠 P0（思想营养，必须吸收）> 📐 P1（规范营养，推荐吸收）> 🔧 P1-P2（技能营养）> 🏗️ P2（架构营养，参考）

### 验证清单（每轮吸收后执行）

- [ ] 所有修改的技能：`skill_view()` 可加载，无YAML错误
- [ ] frontmatter signature 字段存在（v2.6+ 要求）
- [ ] L1 格式门通过（触发条件 + 验证清单 + 签名）
- [ ] 吸收报告已更新（若适用）
- [ ] memory 已更新吸收记录
- [ ] 无回退（已通过的测试仍然通过）

### 陷阱

#### ⚠️ 轮次疲劳
连续多轮吸收后，边际收益递减 → 每轮完成后评估"还有未覆盖的范式吗？"如果只剩下同质化的项目，停止吸收。

#### ⚠️ 只吸收不反思
吸收外部模式后，没有更新内部技能的反省机制 → 每轮吸收后运行一次 project-experience-distillation，从吸收过程本身提取规律。

#### ⚠️ 忽略范式重叠
两个不同范式但功能重叠（如 DSPy 的签名 和 TypeScript 的类型系统都有类型声明但用途不同）→ 在对比表中明确标注重叠部分，避免"这我早有了"的误判。

---

## 变更日志

2026-05-23: v4.3.0 — 动灵驱动吸收（范式转换: 缺口驱动→营养驱动）[本会话用户哲学澄清]
  新增: 「第一原则：动灵驱动吸收」——新增动门(Entelechy Gate)三道问、营养方向对齐第6维度、吸收后的原生感+拆解感验证
  更新: 所有旧"缺口驱动"语言替换为"营养/动灵"语言——正确流程→营养评估流程、反例→过往经验(动灵视角重评)、缺口驱动的搜索策略→方向驱动的搜索策略(营养类型分类法)、双循环协作语言、Gap-driven pitfall→Entelechy-driven、缺口分析表格式→营养评估表格式、5维度→5+1维度、学术论文空白填补→营养互补、Local Project fill gap→Nutritional Value、吸收提议格式synthos_gap→nutrition_type+nutrition_rationale
  新增: 营养类型分类表（🧠思想/📐规范/🔧技能/🏗️架构）

2026-05-22: v4.2.0 — 新增文言层作为五层提取的第0层（必选先导）。吸收后验证增加文言提炼步骤。
  新增: 五层提取规范增加 Layer 0 文言（Classical Essence）— 3-5条四字格言压缩核心哲学，为必选先导
  新增: 吸收后验证第1步 — 文言提炼（必选），原理层·文言先于方法层·白话先于命令层·英文
  原则: 任何吸收必须先过文言层——只有能用文言表达，才算真正理解
  触发: 用户纠正"吸收应先做文言加工，理论和思想提取优先"
  影响: 所有未来吸收必须包含文言蒸馏步骤

2026-05-18: v4.1.0 — 新增编排协议注入模式 + 自主执行阈值兼容性。
  新增: Phase 1 注入模式第5类「编排协议注入」（含案例：双循环编排→ROUTE v1.2.0）
  新增: references/two-loop-orchestration-absorption.md 案例参考
  更新: P0用户批准门控 → 自主执行阈值例外（≥80%置信度可直接执行）
  原则: 编排协议注入更新4文件（SKILL+IO+BOUNDARY+CHANGE_LOG）是强制要求

2026-05-16: v4.0.0 — 跨项目多轮吸收方法论。凝练自 Claude Code → DSPy → LangGraph 三轮对比吸收实践。
  新增: §「跨项目多轮吸收方法论」— 范式分化原则、标准6步流程、缺口分析表格式、验证清单
  新增: 陷阱×3（轮次疲劳/只吸收不反思/范式重叠误判）
  原则: 每轮选不同范式（Agent→声明式→状态机→...），不是连续同类吸收

2026-05-16: v3.10.0 — 新增五层提取规范（思想→规范→规律→能力→任务）。
  新增: §「五层提取规范」作为所有外部吸收项目的最低方法论要求
  新增: references/claude-code-5-layer-case-study.md — 五层提取在Claude Code分析中的完整实践案例
  注意: 第1-3层（思想/规范/规律）是必选项，第4-5层（能力/任务规律）是推荐项
  原则: 第一次就按五层提取，避免「只看了能力层就决定是否吸收」的片面判断

2026-05-16: v3.9.0 — 新增industry_leaders关键词类别 + Claude Code 3层分析参考。
  新增: industry_leaders 类别（每4轮扫描Claude Code/Cursor/Copilot等）
  新增: references/claude-code-analysis-2026-05-16.md — 3层深度分析完整记录
  经验: 业界领头羊分析哲学和架构，不为了吸收而吸收。Claude Code只吸了Hook系统。
  更新: 双循环进化中明确P0内部反思 > P1外部吸收

2026-05-15: v3.8.0 — 新增 3-Layer Deep Analysis Pattern (思想→架构→可吸收模式) 作为 Multi-Project Philosophy Comparison 的增强方法。新增参考案例文件 references/p0-deep-analysis-storm-sci-skills-ars.md（STORM/scientific-agent-skills/AI-Research-SKILLs 完整3层分析）。关键发现提炼：三个项目互补而非竞争，各自填不同的原子缺口。
2026-05-15: v3.7.0 — 新增 Awesome List Cascading 方法论，用于高效生态扫描。添加执行示例（Awesome-Auto-Research-Tools 扫描）。新增 reference 文件 awesome-auto-research-ecosystem-2026-05.md。
2026-05-14: v3.6.0 — 修复 absorption-tracked.json 和 evolution-state.json 部分读取问题。新增 `patch` 转义陷阱（`\\n` → 真实换行）。新增吸收后四重同步检查（SKILL.md §4 + BOUNDARY.md + CHANGE_LOG.md + references 索引）。
  新增: "P0: Absorption Execution（执行层）" — 并行子Agent创建原子+扩展+注册的完整流程
  新增: "Multi-Project Philosophy Comparison" — 5维度哲学对比表+并行侦察+输出格式
  新增: P0完成检查清单（6项）
  更新: 并行探索矩阵 3→5 子Agent
  更新: Phase Flow Control 增加P0节点和用户批准门控

2026-05-13: v3.4.0 — 新增Deep Structural Absorption方法论（3-Phase）+ ARS案例研究参考。
  新增: "Deep Structural Absorption (3-Phase)" 节 — Phase 0并行侦查/Phase 1核心注入/Phase 2 Schema整合/Phase 3 Meta吸收边界规则
  新增: 4种核心注入模式表（反谄媚/分类法/宪法原则/元数据字段）
  新增: 吸收报告模板 → 引用 Synthos/docs/ars_absorption_report.md 作范例
  新增: references/ars-case-study-deep-structural-absorption.md — ARS吸收完整回顾

2026-05-11: v3.3.0 — 新增JSON Key Collision Pitfall（同名key作为dict和int的覆盖问题），新增External Skill Adaptation Checklist（7项外部技能适应性改造清单：删除后端选择闸门、删除隐私规则、添加IO契约、适配前导格式、创建参考文件、改写描述、验证流水线集成）。强调必须先运行评估框架(synthos-evaluation-framework.md)定位D1-D6缺口，只吸收能填补缺口(<70)的项目。新增gap-driven vs opportunity-driven pitfall。新增缺口驱动的搜索策略表。

2026-05-11: v3.1.0 — Evolution 集成文档 + 操作陷阱。新增与 evolution 引擎协作指引（轮转集成、SELF_INSPECT 反馈循环）。新增 pitfalls: patch与部分读取冲突（全量读取再patch）、GitHub API搜索结果稀疏时的应对策略。
2026-05-11: v3.0.0 — 主动螺旋吸收。项目追踪DB、自扩展关键词、随访机制、自检生成。
2026-05-10: v2.0.0 — 六步吸收法（AutoResearchClaw验证）。GitHub/Hermes/论文搜索。
2026-05-08: v1.0.0 — 初始版本。
