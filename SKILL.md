---
name: synthos
description: "认知操作系统 — Agent4S第五科学范式L3-L4具体实现框架。6认知原子DAG编排+八维思维框架+技能进化引擎 | A computable, collaborative, and evolving cognitive operating system for science — the implementation of Agent4S L3-L4."
version: 1.2.0
author: Synthos Agent (Yakeworld Lab)
tags: [synthos, cognitive-os, agent4s, fifth-paradigm, research-automation]
---

# Synthos — Agent4S 认知操作系统

> **理论锚点**：Agent4S (Zheng et al. 2025, arXiv:2506.23692) — 第五科学范式
> Synthos 填补了 Agent4S L3-L4 "尚无清晰模式" (No Clear Pattern Established) 的空白

---

## 原理层 · 文言

### 总纲

系统之立，以认知为本。六原子为基，八维为纲，循DAG之序而作。上承假说，下出文章，中贯证伪。自L3单流程智能体至L4全流程闭环，乃第五范式之具象。

### 认知原子论

学问之道，始于搜罗，终于论证。六原子各司其职，互为输入输出，不可逆序：

| 序 | 名 | 义 |
|:--:|:---|:---|
| 一 | 知识获取 | 广搜博采，以充粮草 |
| 二 | 知识提取 | 去粗取精，以得骨干 |
| 三 | 关联发现 | 比同辨异，以见空白 |
| 四 | 观点生成 | 因空白而立假说，须可证伪 |
| 五 | 论证表达 | 依假说而构文章，须有据 |
| 六 | 观点验证 | 反方驳之，以验坚瑕 |

### 思维八维论

八维者，思辨之利器也。一事当前，八维齐举，则所见无遗：

| 维 | 用 | 联 |
|:--|:---|:----|
| 第一性原理 | 归元至不可分，则真伪自现 | 原子一、二、四、五 |
| 系统思维 | 整体观之，不囿于一隅 | 原子一、三、五 |
| 贝叶斯思维 | 先验加新证，后验逐次更新 | 原子四、六 |
| 类比 | 以彼之理，推此之事 | 原子四 |
| 奥卡姆剃刀 | 如无必要，勿增实体 | 原子二、五、编排层 |
| 证伪主义 | 不证其真，但求其不可伪 | 原子六 |
| 模型依赖实在论 | 模型即世界，世界即模型 | 原子三 |
| 自由能原理 | 系统自趋于最小自由能 | 原子六 |

> **综合实现度：68%** — 优先补自由能原理与模型依赖实在论

### 进化之道

进化引擎 v2.11，每轮只修一维，每次必有假说。败则回滚，成则铭记。外部吸收须经L+0~L+3四门：来源标注→七项改造→五层验证→独立验证。

### 质量之规

四层闸门，层层不可越过。自响应级漂移检测，至项目级L1-L4交付门，至原子级闸门，至论文级G1-G7闸门。不合格者自动循环，不问用户。

---

## 方法层 · 白话

### 触发条件

本OS在以下场景自动启用：
- 用户发起科研全流程任务（写论文·审标书·挖专利·找文献）
- 用户请求多skill组合的复杂任务（delegate_task跨skill编排）
- 用户加载任一原子skill时，编排层（task-router）自行启动

### Agent4S 层级映射

| 级别 | Agent4S定义 | Synthos对应 | 状态 |
|:----:|:------------|:------------|:----:|
| **L1** | 单一工具自动化 | tools/Python脚本（文献检索、PDF下载、CNIPA查新） | ✅ 成熟 |
| **L2** | 复杂流程编排 | 多步管线（论文8步、专利8步、Grant审计8步） | ✅ 成熟 |
| **L3** | 单流程智能体 | skill自主运行：规划→工具→迭代→自检→交付（专利交底书为验证案例） | ✅ **已实现** |
| **L4** | 单实验室全流程闭环 | 三管一硬：论文+专利+Grant管线 + 3D眼动硬件；skill间通过`delegate_task`+`session_search`协同 | ⚡ 构建中 |
| **L5** | 跨实验室多智能体协作 | `delegate_task`对等扩展 + 技能共享机制 | 🔮 愿景 |

**L3技术栈对齐**：`Reasoning`(LLM推理) + `Context Engineering`(skill_view+memory+session_search) + `MCP`(Hermes原生MCP客户端+s tools/)

### 6原子DAG编排

```
层0: task-router (编排层 — 奥卡姆剃刀)
  │
  ├──→ 层1: knowledge-acquisition
  │        │
  │        └──→ 层2: knowledge-extraction
  │                 │
  │                 └──→ 层3: association-discovery
  │                          │
  │                          └──→ 层4: hypothesis-generation
  │                                   │
  │                                   ├──→ 层5: argument-expression
  │                                   └──→ 层5: viewpoint-verification
```

#### 任务复杂度→最短原子链

| 复杂度 | 示例 | 路径 | 原子数 |
|:------|:-----|:------|:------:|
| 极简 | 找3篇论文 | 知识获取 | 1 |
| 短链 | 找论文+提取方法 | 获取→提取 | 2 |
| 短链 | 提出假设+验证 | 观点生成→观点验证 | 2 |
| 中长 | 分析领域现状 | 获取→提取→关联发现 | 3 |
| 中长 | 生成假设+写论证 | 观点生成→论证表达 | 2 |
| 完整 | 写综述/基金申请 | 完整链 | 5-6 |

### 外部吸收流程

```
发现外部技能 → 语义匹配 → 5维评分 (架构·哲学·空白·生态·质量)
  → 评分≥4.0 → 吸收 (L+0~L+3四门)
  → 评分<4.0 → 存档备查
```

**吸收四门**：
- L+0：来源标注（仓库+版本+License）
- L+1：七项改造（命名·触发·路径·工具·输出·文档·测试）
- L+2：五层验证（结构·功能·语义·漂移·宪法）
- L+3：独立验证（用户确认或测试通过）

### 进化引擎触发

| 模式 | 触发 | 周期 |
|:-----|:-----|:-----|
| ⏱ Timer | cron定时 | 每日/每周 |
| ⚡ Event | Hook事件 | 任务完成/会话结束 |

**质量控制**：
- 结构测试（YAML·命名·描述）
- 功能测试（端到端·错误处理）
- 质量评估（语义·重复检测）
- 生命周期：`DRAFT → TESTING → VALIDATED → ACTIVE → DEPRECATED`

### 当前度量

| 指标 | 值 |
|:-----|:---|
| 总技能数 | 17（7核心原子+7扩展+2基础+1新增nature-paper2ppt）|
| 通过测试 | 8/8 (100%, Cycle 24) |
| 平均质量 | 0.970 (EXCELLENT) |
| 进化轮次 | 37 |
| 综合实现度 | 68% |

---

## 命令层 · English

### Quick Start

```bash
# Load any core atom
skill_view("knowledge-acquisition")
skill_view("paper-workflow")
skill_view("patent-disclosure")

# Run evolution cycle
skill_view("evolution")

# Delegate cross-skill tasks
delegate_task(goal="...", toolsets=["terminal","web","skills"])
```

### Directory Structure

```
Synthos/
├── SKILL.md                    # This file — OS orchestrator
├── CONSTITUTION.md             # Philosophical immune system
├── PROJECT_QUALITY.md          # Quality gates
├── evolution-state.json        # Evolution state
├── skills/
│   ├── knowledge-acquisition/  # Atom 1
│   ├── knowledge-extraction/   # Atom 2
│   ├── association-discovery/  # Atom 3
│   ├── hypothesis-generation/  # Atom 4
│   ├── argument-expression/    # Atom 5
│   ├── viewpoint-verification/ # Atom 6
│   ├── task-router/            # Orchestration layer
│   ├── evolution/              # Evolution engine v2.11
│   ├── paper-workflow/         # Paper pipeline (PaperSpine-absorbed)
│   ├── patent-disclosure/      # Patent pipeline (handsomestWei-absorbed)
│   ├── nature-paper2ppt/      # Paper → Nature-style PPTX (GARCH-QUANT-absorbed)
│   └── [7 others]              # Domain extensions
├── archive/                    # Historical snapshots
└── docs/                       # Philosophy & design docs
```

### Absorbed External Skills

| Skill | Source | Score |
|:------|:-------|:-----:|
| patent-disclosure | handsomestWei/patent-disclosure-skill v1.8.5 | 4.6 |
| nature-paper2ppt | GARCH-QUANT/garch-nature-paper2ppt | 4.6 |
| — (theory) | Agent4S (Zheng et al. 2025, arXiv:2506.23692) | 4.6 |
| — (writing) | PaperSpine V2 (WUBING2023) | 4.6 |
