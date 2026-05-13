# Synthos 深层吸收主报告：5项目逐一对比

> 生成日期：2026-05-14 | 基于5次深度代码级分析 + 已有ARS吸收报告
> 方法论：逐一克隆→读全部核心源文件→理解设计哲学→对比思想→制定吸收策略

---

## 目录

1. [五项目全景定位](#1-五项目全景定位)
2. [逐一深度对比](#2-逐一深度对比)
   - 2.1 ResearcherSkill — 纯SKILL.md认知操作系统
   - 2.2 ARS — 32-Agent科研论文流水线
   - 2.3 NanoResearch — 端到端AI科研实验引擎
   - 2.4 KILO-KIT — Cognitive Flow Architecture
   - 2.5 Mimosa-AI — 达尔文进化+MC科研框架
3. [思想谱系图](#3-思想谱系图)
4. [吸收优先级矩阵](#4-吸收优先级矩阵)
5. [具体吸收方案](#5-具体吸收方案)
6. [反模式与风险](#6-反模式与风险)
7. [总结：哲学统一性](#7-总结哲学统一性)

---

## 1. 五项目全景定位

| 项目 | Stars | 范式 | 核心思想 | 哲学关键词 |
|:-----|:-----:|:-----|:---------|:----------|
| **ResearcherSkill** | 218⭐ | **纯SKILL.md** | 《把科学方法编码为306行指令》 | 自足性、元认知护栏、分支探索 |
| **ARS** | 6,358⭐ | SKILL.md + 32 Agent | 《AI是副驾驶不是飞行员》 | 反谄媚、完整性门控、碳硅协奏 |
| **NanoResearch** | 979⭐ | **Python CLI + SKILL.md** | 《真正跑GPU实验的端到端论文引擎》 | 实体验证、进化记忆、9阶段流水线 |
| **KILO-KIT** | 24⭐ | **CFA + 134 SKILL.md** | 《把认知建模为连续流而非离散任务》 | 预测性上下文引擎、可组合行为单元 |
| **Mimosa-AI** | 22⭐ | **Python沙箱 + MCP** | 《达尔文进化+MCP发现=自进化科研》 | 动态工作流综合、MCP工具发现、单居群进化 |

### 架构谱系

```
纯SKILL.md（零Python）<─────────────────────────────> Python框架（厚运行时）
    │                                                        │
    │ ResearcherSkill (306行, 1个文件)                         Mimosa-AI (51文件, Python沙箱)
    │   │                                                        │
    │   └─ Synthos（是, 同范式）                                   └─ NanoResearch (51K行Python)
    │        │                                                        │
    │        └─ ARS（SKILL.md + 32 Agent, 部分Python）               │
    │             │                                                   │
    │             └─ KILO-KIT（134 SKILL.md + CFA范式）              │
    │                                                                  │
    └─────── 认知层 ←────────────────→ 执行层 ────────────┘
           Synthos在此                         NanoResearch在此
```

---

## 2. 逐一深度对比

---

### 2.1 ResearcherSkill — 纯SKILL.md认知操作系统

**仓库**: krzysztofdudek/ResearcherSkill | **Stars**: 218 | **许可**: MIT
**架构**: 单文件 `skills/researcher/SKILL.md` (306行, ~22KB) | **零依赖**

#### 核心思想：「科学方法即指令」

ResearcherSkill最深刻的思想是：**科学方法论可以被形式化为一个Agent可执行的指令集，而不需要任何运行时系统。** 306行Markdown = 一个认知操作系统。

这种设计的底层假设是：
- **LLM本身是解释器** — Agent读取SKILL.md就像CPU读取指令
- **文件系统是状态** — `.lab/`目录是知识数据库，而不是代码状态
- **Git是版本控制** — 但仅用于代码，实验知识独立于代码

#### 架构核心机制

```
Phase 0: 设置（定义目标、指标、约束）
  ↓
Phase 1: 探索（THINK → TEST → REFLECT 循环）
  │           ↑                                  │
  └─────────── 迭代（非线性的分支图）────────────←┘
     · 从任意实验Fork
     · 基因谱系追踪（branches.md）
     · 停滞时翻转假设
```

**元认知护栏系统**（最值得吸收的部分）：

| 触发条件 | 强制动作 | 目的 |
|---------|---------|------|
| 连续3次丢弃 | STOP → 强制日志 | 防止盲目尝试 |
| 连续5次丢弃 | Fork默认 + 翻转假设 | 强制策略切换 |
| 最优8+轮未变 | Plateau → 基线Fork | 避免局部最优 |
| 每10次实验 | 重新验证当前最优 | 检测退化 |

#### 与Synthos的相通性

| 维度 | ResearcherSkill | Synthos |
|:-----|:---------------|:--------|
| 架构范式 | 纯SKILL.md零Python | 纯SKILL.md零Python |
| 状态持久化 | `.lab/`文件系统 | `evolution-state.json` |
| 元认知 | 护栏系统 | 进化引擎 |
| 分支逻辑 | 非线性Fork+Combine | 进化周期 |
| 粒度 | 单文件306行 | 7原子+路由器 |

#### 可吸收的核心哲学

1. **「代码状态 vs 知识状态分离」** — Git管理代码，`.lab/`管理知识。这是最优雅的架构分离原则。
2. **「元认知不是可选项」** — 护栏是强制性的（`<critical>`标签），不是推荐性的。
3. **「最小自足单元」** — 任何Agent应该能在只有这一个文件的情况下完成完整的研究循环。
4. **「定性指标的多评估者协议」** — 3个独立子Agent盲评 + 中位数聚合 + 分歧标记。

---

### 2.2 ARS (Academic Research Skills)

**仓库**: Imbad0202/academic-research-skills | **Stars**: 6,358 | **许可**: CC BY-NC 4.0
**架构**: 4个技能模块 × 32个Agent | 10阶段流水线 | **SKILL.md主导 + 部分Python**

#### 核心思想：「碳硅协奏的系统化」

ARS的核心贡献不在于「写论文」，而在于**系统化地处理AI固有的认知缺陷**：

- **谄媚** → 反谄媚协议（Concession Threshold Protocol）
- **幻觉** → 5分类法（TF/PAC/IH/PH/SH）
- **概念漂移** → Sprint Contract（先承诺后执行）
- **框架锁定** → 跨模型验证 + 思维框锁检测

这与Synthos的「碳硅共生」哲学完全一致。

#### 最值得吸收的5个机制

| # | 机制 | 独创性 | 可吸收性 |
|:-:|:-----|:------:|:--------:|
| 1 | **反谄媚协议** — 反驳打分制(1-5) + 连续让步检测 | ★★★★★ | ★★★★★ 已在Phase 1吸收 |
| 2 | **完整性门控** — 5阶段严查(引用/数据/独创性/声明) | ★★★★★ | ★★★★★ 已在Phase 1吸收 |
| 3 | **Material Passport** — 完整的数据溯源体系(13个Schema) | ★★★★ | ★★★★ Phase 2待定 |
| 4 | **Sprint Contract** — 先提交评分计划再看论文 | ★★★★★ | ★★★★ Phase 2待定 |
| 5 | **意图检测** — 区分探索模式vs目标模式 | ★★★★ | ★★★★ 路由器原子可用 |

#### ARS哲学的精髓

> 「AI处理苦力活，人定义问题。不隐藏AI痕迹，反而提供合规的AI披露声明。」

这个哲学与ResearcherSkill的「科学方法即指令」有本质区别：
- ResearcherSkill: **Agent是独立研究员**，人在设定目标后放手
- ARS: **Agent是研究助理**，人一直在回路中做决策

两者在「碳硅共生」的不同点上：ResearcherSkill偏向「硅主」，ARS偏向「碳主」。

---

### 2.3 NanoResearch — 端到端AI科研实验引擎

**仓库**: OpenRaiser/NanoResearch | **Stars**: 979 | **许可**: MIT
**架构**: 51K行Python + 16个SKILL.md | **9阶段流水线** | **GPU/SLURM执行**

#### 核心思想：「真正的实验，不是编造的论文」

NanoResearch的根本区别在于：**所有数据、图表、数字来自真实GPU实验的输出，不是LLM编造。** 它不是一个论文写作工具，而是一个执行引擎。

三个运行模式揭示哲学层次：

| 模式 | 阶段数 | 哲学含义 |
|:-----|:------:|:---------|
| STANDARD | 6 | 快速原型验证 |
| DEEP | 9 | 完整的实验→论文闭环 |
| EVO | 9 + 进化 | 从每次实验中学习→改进 |

#### 架构核心创新

```
进化引擎的三支柱（对Synthos最有价值的部分）:
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Skill Evolution │    │ Memory Evolution │    │   RAM 模型    │
│ 候选提取→评分→合并 │    │ 类型/范围/权重    │    │ 本地反思增强  │
│ SKILL.md输出格式  │    │ 标签检索+衰减     │    │ 诊断+提示+进化 │
└─────────────┘    └─────────────┘    └─────────────┘
```

**Pre/Post Router 架构**（最值得吸收的设计模式）:
```
输入 → Pre-Router(选择记忆+技能+生成policy) → 执行阶段 → Post-Router(反思+改进)
```

#### 与Synthos的映射关系

| NanoResearch概念 | Synthos等价 | 吸收策略 |
|:----------------|:-----------|:---------|
| 9阶段流水线 | 9原子编排链 | 建模为manifest中的原子工作流 |
| SkillEvolutionStore | 进化引擎 | **直接采用** candidate→review→lifecycle模式 |
| MemoryStore | 记忆原子 | **直接采用** type/scope/retrieval模型 |
| RouterPolicy | 元认知原子 | 实现pre/post router |
| Workspace + manifest | 会话状态原子 | 采用workspace目录约定 |
| 每阶段一个Agent | 每原子一skill | 天然1:1映射 |
| RAM模块 | 本地增强原子 | 实现为轻量级原子 |

#### 可吸收的5个SKILL.md（P0级别）

| SKILL.md | 行数 | 核心价值 | 吸收方式 |
|:---------|:----:|:---------|:---------|
| `brainstorming-research-ideas` | 384 | 10种创意框架 | 直接复制为Synthos原子 |
| `creative-thinking-for-research` | 366 | 8种认知框架 | 直接复制为Synthos原子 |
| `ml-training-recipes` | 319 | 实战PyTorch配方 | 复制为参考SKILL.md |
| `academic-plotting` | 479 | 4种视觉风格+图表类型 | 扩展figure-generation |
| `ml-paper-writing` | 1015 | 全论文写作+12个会议模板 | 扩展argument-expression |

---

### 2.4 KILO-KIT — Cognitive Flow Architecture

**仓库**: VoDaiLocz/KILO-KIT | **Stars**: 24 | **许可**: MIT
**架构**: 134个SKILL.md + 43个核心框架文件 | **CFA范式**

#### 核心思想：「认知是流，不是任务」

KILO-KIT的定义性洞察是：**把AI交互从「任务→处理→响应→结束」的离散模型转变为「输入→预测→执行→学习→更好」的连续流模型。**

这是与所有其他项目最根本的哲学差异——它不是描述「做什么」，而是描述「怎么想」。

#### 5大核心创新

| 创新 | 缩写 | 功能 | 对Synthos的价值 |
|:----|:----:|:-----|:---------------:|
| **可组合行为单元** | CBU | 3层(12原子+8复合+10元行为) | ★★★★★ 直接对应 |
| **预测性上下文引擎** | PCE | 在使用前预加载上下文 | ★★★★ 进化引擎可嵌入 |
| **技能有效性追踪器** | SET | 自改进技能系统 | ★★★★★ 直接对应进化引擎 |
| **Token经济管理器** | TEM | 4种预算模式 | ★★★ 可作为meta层 |
| **决策审计轨迹** | DAT | 完整可解释性 | ★★★ 可作为输出门控 |

**CBU体系**（最值得吸收）：

```
原子行为(12): parse_input, search_code, read_file, write_file, 
              run_command, reason, generate, analyze_data,
              verify, test, refactor, document

复合行为(8): trace_error, modify_safely, test_change, 
             investigate_codebase, design_solution, 
             review_changes, plan_implementation, analyze_impact

元行为(10): chain, parallel, conditional, loop, fallback, 
            retry, guard, pipeline, map, reduce
```

这套行为体系是**与Synthos原子直接对应**的概念模型——每个行为都是可组合的认知原子。

#### KILO-KIT vs Synthos

| 维度 | KILO-KIT | Synthos | 差异 |
|:-----|:---------|:--------|:-----|
| 原子粒度 | 12原子行为 | 7认知原子 | KILO-KIT更细粒度 |
| 行为层次 | 3层(原子/复合/元) | 平面结构 | KILO-KIT更结构化 |
| 路由机制 | 多因子评分(35%+25%+...) | 路由器原子 | KILO-KIT可量化的路由 |
| 上下文管理 | PCE(预测性预加载) | 无 | KILO-KIT独特优势 |
| 自改进 | SET(有效性追踪) | 进化引擎 | 理念相同实现不同 |
| 审计 | DAT(完整SQL) | evolution-state.json | KILO-KIT更系统化 |
| 规模 | 134 SKILL.md | 7原子 | KILO-KIT更庞大 |

---

### 2.5 Mimosa-AI — 达尔文进化+MCP科研框架

**仓库**: HolobiomicsLab/Mimosa-AI | **Stars**: 22 | **许可**: Apache-2.0

#### 核心思想：「通用进化>固定流水线」

Mimosa-AI的定义性哲学：**不要为每个任务设计Agent流水线——让LLM动态综合任意任务的Agent工作流，然后用达尔文进化选优。**

```
输入任务 → LLM综合工作流(代码) → 执行 → 评估 → 
          ↺ 改进(如果<0.9且<10次迭代) → 存储最优
```

#### 关键创新

| 机制 | 实现 | 独特性 |
|:-----|:-----|:-------|
| **动态工作流综合** | LLM生成LangGraph代码 | 不预设流水线，每次任务全新生成 |
| **单居群进化** | 仅最优工作流繁殖 | 简单但有效(5%改进门限) |
| **MCP工具发现** | 扫描5000-5200端口 | 自动发现本地可用工具 |
| **SmolAgent沙箱** | HuggingFace CodeAgent | 安全执行+超时保护 |

#### 为什么评分3.45/4.0（仅追踪）

Mimosa-AI虽然理念与Synthos高度一致（自进化、MCP集成），但有根本差异：

| Synthos | Mimosa-AI | 鸿沟 |
|:--------|:----------|:-----|
| 纯SKILL.md | Python沙箱(40+文件) | 范式不兼容 |
| 7固定原子 | 每任务动态综合工作流 | 静态vs动态 |
| 进化引擎驱动原子进化 | 达尔文迭代改进 | 进化层次不同 |
| 文件系统状态 | 内存/数据库状态 | 状态管理不同 |

**唯一值得吸收的**：MCP工具发现模式（扫描本地MCP服务器）和「workflow_v9.md」的多Agent编排提示工程。

---

## 3. 思想谱系图

### 碳硅共生程度

```
ResearcherSkill ────●─────── 硅主导（Agent独立跑实验，人在设定后放手）
                    │
Synthos ────────────●─────── 平衡（7原子+人在回路做决策）
                    │
ARS ────────────────●─────── 碳主导（每个阶段人都必须决策）
                    │
KILO-KIT ───────────●─────── 硅主导（Agent以流模式自主运行）
                    │
NanoResearch ───────●─────── 硅执行（9阶段全自动，GPU跑实验）
                    │
Mimosa-AI ──────────●─────── 硅进化（达尔文进化选择工作流）
```

### 形式化程度

```
# 执行 → 思考 → 反思

ResearcherSkill:  THINK → TEST → REFLECT
                        │
    NanoResearch:  IDEATION → PLANNING → SETUP → CODING → EXECUTION → ANALYSIS → FIGURE → WRITING → REVIEW
                        │
           ARS:   RESEARCH → WRITE → GATE → REVIEW → MODIFY → RE-REVIEW → GATE → FINALIZE → SUMMARY
                        │
       KILO-KIT:  INTAKE(PCE) → ROUTE → EXECUTE → LEARN
                        │
      Mimosa-AI:  PLAN → SYNTHESIZE(LLM) → EXECUTE → EVALUATE → EVOLVE
```

### 核心主张差异

| 项目 | 最强烈的信念 | 最弱的一环 |
|:-----|:------------|:----------|
| **ResearcherSkill** | 「一个文件就够了」 | 缺少多Agent协作 |
| **ARS** | 「系统化防治AI缺陷」 | 过度系统化(31个lint脚本) |
| **NanoResearch** | 「真实的实验才有价值」 | Python 51K行过于厚重 |
| **KILO-KIT** | 「认知是流不是任务」 | 实际代码实现有限 |
| **Mimosa-AI** | 「动态生成比固定流水线好」 | 成本高(34x单Agent) |

---

## 4. 吸收优先级矩阵

### P0 — 直接吸收（本周可完成）

| 源项目 | 吸收物 | 目标位置 | 价值 | 难度 |
|:-------|:-------|:---------|:----:|:----:|
| **NanoResearch** | `brainstorming-research-ideas` SKILL.md | 新原子 | 10种创意框架 | ★☆☆ |
| **NanoResearch** | `creative-thinking-for-research` SKILL.md | 新原子 | 8种认知框架 | ★☆☆ |
| **NanoResearch** | `ml-training-recipes` SKILL.md | reference | 实战配方参考 | ★☆☆ |
| **NanoResearch** | `academic-plotting` SKILL.md | 扩展figure-generation | 4种视觉风格 | ★☆☆ |
| **ResearcherSkill** | 「代码/知识状态分离」原则 | Synthos manifest设计 | 架构原则 | ★☆☆ |
| **ResearcherSkill** | 元认知护栏系统 | evolution engine | 防局部最优 | ★☆☆ |

### P1 — 适配吸收（本月可完成）

| 源项目 | 吸收物 | 目标位置 | 适配工作 | 价值 |
|:-------|:-------|:---------|:---------|:----:|
| **NanoResearch** | Skill Evolution Store | evolution engine | 适配为纯SKILL.md模式 | ★★★★ |
| **NanoResearch** | Memory Store (type/scope/weight) | 记忆原子 | 标签检索+衰减算法 | ★★★★ |
| **NanoResearch** | Pre/Post Router | task-router原子 | 两阶段路由模式 | ★★★ |
| **KILO-KIT** | CBU三层次原子模型 | 原子重组 | 从7原子→3层12+8+10 | ★★★★★ |
| **KILO-KIT** | PCE预测性上下文 | evolution engine | Pre-load上下文 | ★★★ |
| **ARS** | Material Passport | knowledge provenance | 完整溯源Schema | ★★★★ |
| **ARS** | Sprint Contract | task-router | 先合约后执行 | ★★★ |
| **ResearcherSkill** | 多评估者协议 | 质量门控 | 3子Agent盲评 | ★★★ |

### P2 — 架构级吸收（季度级别）

| 源项目 | 吸收物 | 目标位置 | 架构影响 | 价值 |
|:-------|:-------|:---------|:---------|:----:|
| **KILO-KIT** | TEM Token经济管理 | 全系统 meta层 | 中 | ★★★ |
| **KILO-KIT** | DAT决策审计轨迹 | evolution-state.json | 低 | ★★★ |
| **ARS** | 跨模型验证 | 全部原子 | 高（需多模型配置） | ★★★★ |
| **Mimosa-AI** | MCP工具发现模式 | 外部工具集成 | 中 | ★★★ |
| **NanoResearch** | 9阶段流水线manifest | 任务编排模式 | 中 | ★★★★ |
| **NanoResearch** | RAM本地增强模型 | 轻量级原子 | 高 | ★★★ |

### 不吸收（仅追踪）

| 项目 | 原因 |
|:-----|:-----|
| **Sakana AI Scientist** | Python框架+NOASSERTION许可 |
| **Mimosa-AI** (非MCP部分) | Python沙箱，范式不兼容 |
| **PaperForge** | Python框架，需要GPU环境 |

---

## 5. 具体吸收方案

### P0执行计划

#### 5.1 从NanoResearch吸收3个纯SKILL.md

**新原子1: `research-ideation`** (← `brainstorming-research-ideas`)
- 10种创意框架作为子skill
- 3阶段：Diverge → Converge → Refine
- 框架选择指南

**新原子2: `creative-cognition`** (← `creative-thinking-for-research`)
- 8种认知框架（Bisociation, Problem Reformulation, Analogical Reasoning...）
- 4阶段创意协议
- 结构类比深度量表（surface → relational → structural）

**新原子3: `experiment-recipes`** (← `ml-training-recipes`)
- PyTorch实战配方（优化器、LR调度、混合精度）
- 领域指南（LLM/视觉/扩散/生物医学）

#### 5.2 扩展现有原子

**扩展 `figure-generation`** (← `academic-plotting`)
- 4种视觉风格（Sketch, Modern Minimal, Illustrated Technical, Accent Bar）
- 图表类型决策指南
- 色板（Ocean Dusk, Ink & Wash, Nord, Okabe-Ito）

**扩展 `argument-expression`** (← `ml-paper-writing`)
- Narrative Principle + 5句摘要公式
- 12个会议模板（NeurIPS/ICML/ICLR/ACL...）
- 引用验证工作流

#### 5.3 从ResearcherSkill吸收哲学原则

**进化引擎增强：元认知护栏**
```
吸收 researcher_skill 的护栏系统到 evolution engine：

每轮进化周期检查:
1. 连续失败次数 ≥ 3 → 强制记录+暂停
2. 最优分N轮未变 → 标记plateau → 分支策略
3. 每N轮 → 重新验证最优
```

**.lab/目录模式 → 进化状态分离**
```
Synthos 当前: evolution-state.json（单一文件）
吸收后: .evolution/
  ├── state.json        # 当前状态
  ├── history/          # 历史周期完整记录
  ├── branches/         # 分叉路径（如果有）
  └── analysis/         # 每次进化的深入分析
```

---

### 6. 反模式与风险

#### 6.1 过度吸收风险

| 风险 | 来源 | 缓解 |
|:-----|:-----|:-----|
| 吸收NanoResearch的Python进化引擎 | NanoResearch | 只吸收设计模式，不复制Python代码 |
| KILO-KIT的134 SKILL.md过于庞大 | KILO-KIT | 只吸收CBU分层模型，不吸收具体技能 |
| ARS有31个CI脚本过于系统化 | ARS | 仅吸收关键检查，不追求完全等价 |

#### 6.2 哲学冲突

| 冲突 | 项目A | 项目B | 解决 |
|:-----|:------|:------|:-----|
| Agent独立性vs人在回路 | ResearcherSkill(硅主) | ARS(碳主) | Synthos保持平衡：碳决策+硅执行 |
| 动态vs静态原子 | Mimosa-AI(动态综合) | Synthos(固定7原子) | 保持7原子+可扩展框架 |
| 细粒度vs粗粒度 | KILO-KIT(12+8+10) | Synthos(7原子) | 引入3层模型不增加原子数 |

#### 6.3 维护债务

- 每吸收一个新原子 = 维护负担
- SKILL.md需要随LLM能力演化而更新
- 吸收的外部项目可能更新（需追踪）

---

## 7. 总结：哲学统一性

### 所有项目的共同点

```
1. 「Agent-native」是下一代范式
   ├── 不是Python框架封装Agent
   └── 而是直接写Agent能读的指令

2. 「自改进」是必要条件
   ├── ResearcherSkill: 护栏强制反思
   ├── ARS: 完整性门控
   ├── NanoResearch: 进化引擎
   ├── KILO-KIT: SET有效性追踪
   └── Mimosa-AI: 达尔文迭代

3. 「可组合」是架构核心
   ├── KILO-KIT: CBU 3层
   ├── ARS: 13个Schema
   └── Synthos: 7原子 → 可组合 = 所有可能
```

### 吸收的本质

吸收不是复制，是理解每个项目的**设计原理**后，用Synthos的架构重新实现。

**核心原则：**
1. **只吸设计模式，不吸代码** — 所有Python代码都不直接吸收，只吸收思想
2. **只吸哲学一致的模式** — 与「碳硅共生」一致的才吸收
3. **保持零Python范式** — 吸收物必须是纯SKILL.md形式
4. **每吸收一个，减重一个** — 维护债务必须可控

### 立即行动建议

```
本周（P0）:
  ✅ 创建 3 个新原子: research-ideation, creative-cognition, experiment-recipes
  ✅ 扩展 2 个现有原子: figure-generation, argument-expression
  ✅ 进化引擎增强: 元认知护栏系统
  ✅ 状态分离: .evolution/ 目录结构

本月（P1）:
  📋 Skill Evolution Store → 适配evolution engine
  📋 Memory Store → 标签检索+衰减
  📋 CBU 三层次模型 → 重组7原子
  📋 Material Passport → knowledge provenance增强

季度（P2）:
  📋 TEM Token经济 → meta层
  📋 DAT 审计轨迹 → evolution-state增强
  📋 跨模型验证 → 全部原子
  📋 MCP工具发现 → 外部集成
```
