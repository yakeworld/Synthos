---
name: synthos
description: 自主进化科研教学认知操作系统 — 6认知原子 × 3元组件完整Research Pipeline
version: 1.0.0
compatibility: opencode
metadata:
  audience: researchers
  workflow: full-research-pipeline
  version: "2.20"
  source: /media/yakeworld/sda2/Synthos

---


# Synthos — 自主进化科研教学认知操作系统

> **核心编排 100% SKILL.md；无核心 Python 代码**
> 6 认知原子 × 3 元组件 × 10 个输出技能
>
> **愿景**: 一个可计算的、协作的、持续进化的公共认知操作系统，用于科学研究。
> *"A computable, collaborative, and evolving public cognitive operating system for science."*

## 架构概览

### 6 认知原子 DAG

```
[1] 知识获取 → [2] 知识提取 → [3] 关联发现 → [4] 假设生成
                                                    ↓
                                            [5] 论证表达
                                                    ↓
                                            [6] 观点验证 ↺
```

### 三层架构

```
┌─────────────────────────────────────────────────────┐
│                  Research Ideation                   │
│                    (启发动机)                         │
├─────────────────────────────────────────────────────┤
│                  Task Router (v1.8.0)                 │
│   standard │ exploratory │ dual-loop │ parallel      │
├─────────────────────────────────────────────────────┤
│ ACQ │ EXT │ ASC │ HYP │ ARG │ VER                   │
│ (认知原子 6 层)                                      │
├─────────────────────────────────────────────────────┤
│ evolution │ quality-gate                             │
│ (元组件 2 层)                                        │
└─────────────────────────────────────────────────────┘

输入流:
Query → [1] raw_papers, pdfs
      → [2] extracted_knowledge
      → [3] associations, knowledge_graph, research_gaps
      → [4] hypotheses, rationale, novelty_score
      → [5] sections, arguments, references
      → [6] verification_results, weaknesses, confidence

输出流: [6] → feedback → [4] (闭环迭代)
```

### 认知原子详情

| # | 中文名 | 英文名 | 能力 | 调用类别 |
|---|--------|--------|------|----------|
| 1 | 知识获取 | knowledge-acquisition (ACQ) | 多源学术文献检索与下载 (S2/PubMed/arXiv/Crossref/OpenAlex) | quick |
| 2 | 知识提取 | knowledge-extraction (EXT) | 从检索到的文献中结构化提取知识 | quick |
| 3 | 关联发现 | association-discovery (ASC) | 识别知识实体间关系，构建 7 类边关系 | ultrabrain / deep |
| 4 | 假设生成 | hypothesis-generation (HYP) | 基于文献分析生成创新假设 (7+1 框架) | ultrabrain |
| 5 | 论证表达 | argument-expression (ARG) | 构建学术论证链，生成论文结构 | writing |
| 6 | 观点验证 | viewpoint-verification (VER) | 多角度验证假设，Bayesian 评分 | ultrabrain |

### Synthos 八维认知框架

| 维度 | 覆盖原子 | 实现度 |
|------|----------|--------|
| 第一性原理 | 1, 2, 4, 5 | 95% |
| 系统思维 | 1, 3, 5 | 95% |
| 贝叶斯思维 | 4, 6 | 90% |
| 类比 | 4 | 70% |
| 奥卡姆剃刀 | 2, 5 | 80% |
| 证伪主义 | 6 | 60% |
| 模型依赖实在论 | 3 | 40% |
| 自由能原理 | 6 | 30% |

**综合实现度: 68%**

## 1. 认知原子 (Cognitive Atoms)

### 1.1 知识获取 (knowledge-acquisition — ACQ)

**路径**: `skills/knowledge-acquisition/SKILL.md` (v1.7.0)
**调用类别**: `quick`

**能力**: 多源学术文献检索与下载 — Semantic Scholar / PubMed / Crossref / OpenAlex / arXiv / bioRxiv
Agent-native 执行，纯 skill + curl 零 Python。含 API 弹性层、本地缓存、自动回退链。
宁无所得，不取伪术。

**输入契约**:

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| topic | string | ✅ | 研究主题 / 关键问题 |
| keywords | list[str] | ❌ | 具体关键词（自动生成） |
| source_priority | list[str] | ❌ | 优先级: S2→PubMed→arXiv→OpenAlex→Crossref→bioRxiv |
| max_papers | int | ❌ | 最大返回数（默认 15） |
| year_range | list[int] | ❌ | 年份范围 |

**输出契约**: JSON 列表，每项含 title, authors, year, source, DOI, abstract, url, pdf_url, citation_count, relevance_score, provenance

**调用方式**:

```bash
# 搜索学术文献
python3 tools/paper-manager/main.py search "[topic]" --output ./literature

# PDF 下载 + 三级验证
python3 tools/paper-manager/main.py download [paper_id]
```

```python
# 多源检索 (Semantic Scholar + Google Scholar + MedData + Web)
task(category="quick", prompt="检索 '[topic]' 相关文献，优先 Semantic Scholar")
```

**验证规则**:
- 所有 PDF 必须通过三级验证: `%PDF-` + `%%EOF` + ≥1000B
- 无硬编码凭据，全部从环境变量读取

**文言**:
> 「致知在格物。物格而后知至。」多源求索，博观约取。
> 宁缺毋滥，求真为要。

---

### 1.2 知识提取 (knowledge-extraction — EXT)

**路径**: `skills/knowledge-extraction/SKILL.md` (v1.1.0)
**调用类别**: `quick`

**能力**: 从检索到的文献中结构化提取知识

**调用方式**:

```python
# 提取文献结构
read filePath: "./literature/pdfs/[paper].pdf"
# goal: "提取摘要、主要贡献、实验方法、结论"

# 结构化知识卡
task(category="quick", prompt="将以下文献提取为结构化知识卡片: <content>")
```

---

### 1.3 关联发现 (association-discovery — ASC)

**路径**: `skills/association-discovery/SKILL.md` (v1.3.0)
**调用类别**: `ultrabrain` / `deep`

**能力**: 识别知识实体间关系，构建 7 类边关系

**7 类关系**: 因果、对比、补充、矛盾、扩展、应用、演化

**调用方式**:

```python
# 发现关联
task(category="ultrabrain", prompt="分析以下文献网络中的关联关系，输出7类边: 因果、对比、补充、矛盾、扩展、应用、演化")

# 构建知识图谱关系
task(category="deep", prompt="基于以下知识集构建图谱: <knowledge_set>")
```

---

### 1.4 假设生成 (hypothesis-generation — HYP)

**路径**: `skills/hypothesis-generation/SKILL.md` (v1.4.0)
**调用类别**: `ultrabrain`

**能力**: 基于文献分析生成创新假设 (7+1 框架)

**7+1 框架**: 机制假设、方法假设、参数假设、场景假设、评估假设、比较假设、理论假设 + 元假设

**调用方式**:

```python
# 生成假设
task(category="ultrabrain", prompt="生成3个创新假设 (7+1框架: 机制假设、方法假设、参数假设、场景假设、评估假设、比较假设、理论假设)")

# 假设优先级排序
task(category="ultrabrain", prompt="对假设进行可行性-创新性排序")
```

---

### 1.5 论证表达 (argument-expression — ARG)

**路径**: `skills/argument-expression/SKILL.md` (v1.1.0)
**调用类别**: `writing`

**能力**: 构建学术论证链，生成论文结构

**调用方式**:

```python
# 构建论证链
task(category="writing", prompt="基于以下内容构建学术论证链: <evidence>")

# 生成论文大纲
task(category="writing", prompt="设计论文结构: 引言→方法→实验→分析→结论")
```

---

### 1.6 观点验证 (viewpoint-verification — VER)

**路径**: `skills/viewpoint-verification/SKILL.md` (v1.3.0)
**调用类别**: `ultrabrain`

**能力**: 多角度验证假设，Bayesian 评分

**调用方式**:

```python
# 多角验证
task(category="ultrabrain", prompt="对以下假设进行多角验证: <hypothesis>")

# Bayesian 更新
task(category="ultrabrain", prompt="基于新证据更新假设的Bayesian得分")
```

## 2. 元组件 (Meta-Components)

### 2.1 路由分发 (task-router)

**路径**: `skills/task-router/SKILL.md` (v1.8.0)

**能力**: 查询分析 + 4 种执行模式

**路由类型**:

| 类型 | 说明 | 适用场景 |
|------|------|----------|
| standard | 单步执行 | 简单检索/提取 |
| exploratory | 探索式多轮 | 分析型任务 |
| dual-loop | 分析+执行双循环 | 复杂研究任务 |
| parallel | 多Agent并行 | 大规模并行处理 |

**复杂度判断规则**:

| 类型 | 示例 | 路径 | 原子数 |
|------|------|------|--------|
| 极简 | 找3篇ADHD论文 | 知识获取 | 1 |
| 短链 | 找论文+提取方法 | 知识获取 → 知识提取 | 2 |
| 短链 | 提出假设+验证 | 假设生成 → 观点验证 | 2 |
| 中长 | 分析XX领域现状 | 知识获取 → 知识提取 → 关联发现 | 3 |
| 中长 | 生成假设+写论证 | 假设生成 → 论证表达 | 2 |
| 完整 | 写综述/基金申请 | 完整链 | 5-6 |

**调用方式** (由 OpenCode 自动使用):

```
# 路由类型:
- standard:      单步执行
- exploratory:   探索式多轮
- dual-loop:     分析+执行双循环
- parallel:      多Agent并行
```

### 2.2 进化引擎 (evolution)

**路径**: `skills/evolution/SKILL.md` (v2.20.0)

**能力**: 11步状态机进化，SEPL回滚，Git-as-Memory，四态决策，Pareto优化

**核心流程**:

```
DIAGNOSE → 结构探查 + 功能基准 + Pareto多维优化
  ↓
OPTIMIZE → GEPA反射式分析 + 自动数据集
  ↓
VERIFY → 黄金验证 + 收敛检查
  ↓
CRYSTALLIZE → 技能结晶 + 教训学习
  ↓
PUBLISH → 发布 + Git记录
```

**调用方式**:

```bash
# 查看进化状态
read filePath: "/media/yakeworld/sda2/Synthos/evolution-state.json"

# 进化循环触发
bash: bash scripts/enhance-notebook.sh
bash: bash scripts/enhance-notebook-r2.sh
```

**外部吸收记录**:
- autocontext (3.9) → absorbed — improvement-loop + knowledge-inheritance + trace-continuity
- PaperDebugger (3.3) → absorbed_methodology — Research→Critique→Revision + conference-style review
- 724-office (3.8) → absorbed_methodology — Nudge Registry + Trigger Functions + Auto-Inject Hints
- Claude Code (4.5) → absorbed_methodology — Hooks + Confidence Scoring + Parallel Agents + Session Start Context

### 2.3 质量闸门 (quality-gate)

**路径**: `skills/quality-gate/SKILL.md` (v2.9.0)

**能力**: 四层质量架构，L0-L4 递进评审 + G1-G7 原子闸门 + SCI 7维评审

**五层架构**:

| 层 | 范围 | 触发 | 说明 |
|----|------|------|------|
| L0 动灵层 | 交付物/技能的方向与系统生长路径一致性 | 每次评估前 | 方向不对不进入技术检查 |
| L0.5 数据诚实门 | 可验证数据声明是否有源文件支撑 | 每次论文评审前 | 无源文件的数据声明必须删除 |
| L1 响应级 | 当前会话输出质量 | PreResponse Hook | 单次响应质量 |
| L2 项目级 | 交付物D1-D6 | 项目阶段完成 | 项目交付质量 |
| L3 管线级 | 论文G1-G7原子闸门 | 写作管线每阶段切换 | 管线流程质量 |
| L4 内容级 | SCI 7维评审 | G7通过后自动 | 内容深度质量 |

**核心铁律**:

| 白话 | 文言 | 含义 |
|------|------|------|
| 无记录=门不通过 | **无录不过** | 无skill_view记录视为未执行 |
| G5引用质量最关键 | **引质为要，G5最重** | 论文质量上限=引用质量 |
| 一次一个维度 | **一维一渡** | 每次只聚焦一个等级，不跳步 |
| 方向不对等于白做 | **向不正则功废** | 质量不只是技术合格，方向一致 |
| 论文数据必须可追溯 | **凡数必源，不源不取** | 无实验记录=编造，不得进评审 |

**通用铁律**: 任务完成→质量评估→不达标→循环执行。无skill_view记录=门不通过。

## 3. 输出技能 (Output Skills)

### 3.1 LaTeX 输出
```python
task(category="writing", prompt="生成LaTeX论文，遵循D1-D10质量门标准")
```

### 3.2 图表生成 (figure-generation)
```python
task(category="visual-engineering", prompt="生成Nature风格对比图表")
```

### 3.3 论文转PPT (nature-paper2ppt)
```bash
ls skills/nature-paper2ppt/SKILL.md  # Nature风格中文PPTX生成
```

### 3.4 医学专家 (bppv-expert)
```python
task(category="quick", prompt="查询BPPV相关医学知识与诊断方案")
```

### 3.5 NSFC 基金审计 (nsfc-grant-audit)
```python
# 8维度评估报告
task(category="quick", prompt="评审以下NSFC基金标书，输出8维度评估报告: <proposal>")

# 标书重构
task(category="quick", prompt="基于文献增强重构基金申请书: <outline>")
```

### 3.6 专利披露 (patent-disclosure)
```python
# 专利挖掘 (3-5个专利点)
task(category="quick", prompt="扫描项目文档，挖掘3-5个专利点: <docs>")

# 技术交底书 (三性论证+查新)
task(category="writing", prompt="脱敏后生成技术交底书: <invention>")
```

### 3.7 实验配方 (experiment-recipes)
```python
# ML实验设计
task(category="quick", prompt="设计训练配方: 架构选择、优化器、调度器、混合精度")

# OOM排障/Karpathy调试清单
task(category="quick", prompt="按Karpathy调试清单排障: <error_logs>")
```

## 4. 完整 Research Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│ Phase 1: 文献发现                                                │
│   ├─ websearch / librarian → 发现相关论文                        │
│   └─ paper-manager search → 自动化检索+下载                      │
│                                                                  │
│ Phase 2: 知识提取                                                │
│   ├─ read (PDF) → look_at → 提取结构                             │
│   └─ EXT (knowledge-extraction) → 知识卡片                       │
│                                                                  │
│ Phase 3: 关联分析                                                │
│   ├─ ASC 发现7类边关系                                           │
│   └─ 构建知识图谱                                                │
│                                                                  │
│ Phase 4: 假设生成                                                │
│   ├─ HYP 7+1框架生成                                             │
│   └─ ultrabrain 排序可行性-创新性                                │
│                                                                  │
│ Phase 5: 实验与实现                                              │
│   ├─ ultrabrain 设计+实现实验                                    │
│   └─ 执行代码 + 收集结果                                         │
│                                                                  │
│ Phase 6: 论证与写作                                              │
│   ├─ ARG 构建论证链                                               │
│   ├─ writing 生成LaTeX                                             │
│   └─ pdflatex → PDF                                              │
│                                                                  │
│ Phase 7: 质量门验证                                              │
│   ├─ VER 多角Bayesian验证                                        │
│   ├─ NotebookLM/Gemini review (D1-D7)                           │
│   └─ 参考文献≥30篇 (D8)                                          │
│                                                                  │
│ Phase 8: 进化                                                    │
│   └─ evolution 状态机 + SEPL回滚 + 质量门                         │
└─────────────────────────────────────────────────────────────────┘
```

## 5. 宪法规则 (Constitutional Rules)

**不可违反的六条铁律**:

1. **宪临万法** — 宪法条款在任何情况下不可修改
2. **一维一修** — 标准先行，逐一修复
3. **技能边界** — 技能之间功能不得重叠，重叠即合并
4. **凭据管理** — 禁止硬编码，从环境变量读取
5. **质量门** — D1-D10 ≥0.85 质量门限
6. **参考文献** — 引用 ≥30 篇

## 6. 环境变量配置

```bash
# 必需
export SEMANTIC_SCHOLAR_API_KEY="your_key"
export MEDDATA_USERNAME="your_username"
export MEDDATA_PASSWORD="your_password"
export MEDDATA_TOKEN="your_token"

# 可选
export ANTHROPIC_API_KEY="your_key"
export OPENAI_API_KEY="your_key"
```

## 7. 文件导航

**Synthos 仓库路径**: `/media/yakeworld/sda2/Synthos/`

| 文件 | 路径 | 说明 |
|------|------|------|
| SKILL.md (本文件) | 根目录 | 认知操作系统总编排 |
| README.md | 根目录 | 架构总览 |
| CONSTITUTION.md | 根目录 | 宪法 |
| evolution-state.json | 根目录 | 进化状态 (v2.20, cycle 72) |
| SKILL-evolution-engine.md | 根目录 | 进化引擎 |
| SKILL-autonomy.md | 根目录 | 自主性 |
| VERIFICATION_GATES.md | 根目录 | 验证门 |
| evolution-log.md | 根目录 | 进化日志 |
| skills/knowledge-acquisition/SKILL.md | skills/ | Atom 1 — 知识获取 |
| skills/knowledge-extraction/SKILL.md | skills/ | Atom 2 — 知识提取 |
| skills/association-discovery/SKILL.md | skills/ | Atom 3 — 关联发现 |
| skills/hypothesis-generation/SKILL.md | skills/ | Atom 4 — 假设生成 |
| skills/argument-expression/SKILL.md | skills/ | Atom 5 — 论证表达 |
| skills/viewpoint-verification/SKILL.md | skills/ | Atom 6 — 观点验证 |
| skills/task-router/SKILL.md | skills/ | 路由分发 (v1.8.0) |
| skills/research-paper-search/SKILL.md | skills/ | 主编排器 (v2.3.0) |
| skills/evolution/SKILL.md | skills/ | 进化引擎 (v2.20.0) |
| skills/quality-gate/SKILL.md | skills/ | 质量闸门 (v2.9.0) |
| skills/nature-paper2ppt/SKILL.md | skills/ | 论文转PPT |
| skills/SKILL_TREE.md | skills/ | 技能树总览 |
| skills/skill_tree.json | skills/ | 技能树 JSON |
| tools/paper-manager/main.py | tools/ | 论文管理器 |
| .evolution/legacy/scripts/enhance-notebook.sh | .evolution/legacy/scripts/ | 进化脚本 (V1) |
| .evolution/legacy/scripts/enhance-notebook-r2.sh | .evolution/legacy/scripts/ | 进化脚本 (R2) |
| docs/synthos-philosophy.md | docs/ | 哲学文档 |

## 8. 技能统计

- **总技能数**: 194 (git-tracked 187, 96.4%)
- **进化周期**: 72 completed, 0 failures, 7 rejected
- **版本**: v2.20 (当前进化状态 v2.19.0 → 2.20.0)
- **质量得分**: 0.8475 (overall_score)
- **质量协议覆盖率**: 4.12% (IO_CONTRACT)
- **版本签名覆盖率**: 1.03%

---

> **动灵在内，不假外求 — 主动发现，不等人说**
> **主动探索，主动发现，主动执行 — 禁止等待用户指示**
