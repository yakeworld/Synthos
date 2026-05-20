---
name: paper-workflow
description: "Human-in-the-loop academic paper writing workflow. Bridges hypothesis-generation → argument-expression with a human review gate. Generates a paper framework (research gap, hypothesis, technical approach, experiment design, expected results, key conclusions), presents it for human confirmation, then executes full writing. Supports multi-variant exploration mode for competing hypothesis paths."
version: 1.0.0
author: Synthos Agent
license: MIT
metadata:
  synthos_atom_type: "workflow"
  synthos_version: "0.1.0"
  synthos_skill_md_hash: "pending"
  synthos_io_contract_ref: "references/IO_CONTRACT.md"
  synthos_asserted_compliance: "P0,P3,P4,P5"
  synthos_depends_on: "task-router, hypothesis-generation, argument-expression, viewpoint-verification, knowledge-acquisition, association-discovery"
  synthos_data_access_level: "raw"
  synthos_author: "Synthos Agent"
allowed-tools: delegate_task Read Write patch clarify terminal skill_view
---

# Paper Workflow — 人机互动论文撰写工作流

## 触发条件

加载此技能当用户：
- 请求撰写一篇完整的学术论文
- 希望在写作前先确认论文框架和方向
- 不确定研究方向，希望探索多种可能性
- 需要人机协同写作：人类确认方向后 AI 执行写作

不适用场景（请使用替代技能）：
- 用户已有完整框架，只需写作 → 直接用 argument-expression 原子
- 用户只需要假设生成 → 用 hypothesis-generation 原子
- 用户只需要文献检索 → 用 knowledge-acquisition 原子

## 验证清单

在执行此技能前，请确认以下条件已满足：

- [ ] 输入：已存在或可生成 hypothesis-generation 的输出（假设列表）
- [ ] 输入：明确用户写作需求（论文类型、目标期刊、篇幅）
- [ ] 工具可用：delegate_task（调用上下游原子）、Read（读取依赖输出）、Write（写入框架和输出）、clarify（用户确认交互）
- [ ] 依赖技能可用：task-router, hypothesis-generation, argument-expression, viewpoint-verification, knowledge-acquisition, association-discovery
- [ ] 数据访问级别：raw（允许引用原始文献和证据）
- [ ] 前置条件：clarify 工具有人机交互能力（非自动化管线）
- [ ] 宪法合规：P0（证据可溯性）、P3（人机分层）、P4（假说可证伪性）、P5（空白可追溯性）

## 1. 职责（Scope）

本工作流是连接知识获取→假设生成→论文写作的**人机互动门控层**。核心职责：

- 将上游原子（ACQ·EXT·ASC·HYP）的输出整合为结构化的**论文框架**
- 在**人类确认/选择**后再执行写作，避免无效产出
- 支持**多版本探索模式**，自动生成多个竞争假说路径供人类选择

本工作流**不做**假设生成（那是 HYP 的职责），**不做**论文写作（那是 ARG 的职责）。它只回答一个问题：**"在写论文之前，人类需要确认什么方向？"**

## 2. 工作模式

### 模式A（默认）：框架确认 → 写作

```
[HYP输出] → 生成论文框架 → clarify(展示给用户) → 用户确认 → [ARG+VER]
```

**流程**：
1. 检查上游 HYP 输出是否存在。若无，先运行 HYP（加载 hypothesis-generation SKILL.md 执行）
2. 从 HYP 输出提取假设列表，生成论文框架（见 §3 Schema）
3. 使用 `clarify` 工具展示框架，等待人类决策
4. 用户选择：确认（直接写）、修改（调整框架）、拒绝（重新生成）
5. 确认后，将框架+假设传递给 ARG → VER

### 模式C（探索）：多版本 → 人类选择 → 写作

```
[HYP多路径生成] → 框架N个变体 → clarify(展示选项) → 人类选择 → [ARG+VER]
```

**流程**：
1. 从 HYP 输出选取 2-3 个不同的假设路径（主假说、竞争假说、替代假说）
2. 为每个路径生成独立的完整框架变体（不同技术方案、不同实验设计）
3. 使用 `clarify` 工具展示变体供人类选择
4. 人类可选择单个变体，或指定混合方案
5. 将选中变体传递给 ARG → VER

## 3. Paper Framework Schema

每个论文框架是一个结构化的 JSON 文档，包含以下字段：

```yaml
paper_framework:
  title: "论文标题（建议）"
  
  research_gap:
    description: "清晰陈述研究空白"
    gap_type: "methodology_gap | contradiction | unanswered_question | outdated"
    supporting_refs: ["DOI列表，至少2篇"]
    significance: "P0 | P1 | P2 | P3"  # 空白重要性
  
  hypothesis:
    claim: "核心假说陈述"
    prediction: "可观测预测"
    falsification: "反证条件"
    supporting_evidence: ["DOI列表"]
  
  technical_approach:
    method: "核心方法学（如：XGBoost, 3D眼动追踪）"
    dataset: "数据集描述"
    variables: ["自变量", "因变量", "控制变量"]
    analysis_plan: "统计分析方法"
  
  experiment_design:
    design_type: "横断面 | 队列 | 病例对照 | 实验"
    population: "研究对象"
    sample_size: "样本量估计"
    primary_outcome: "主要结局指标"
    secondary_outcomes: ["次要结局指标"]
  
  expected_results:
    primary_finding: "预期主要发现"
    effect_size_estimate: "效应量估计"
    alternative_outcomes: ["替代结果1", "替代结果2"]
  
  key_conclusions:
    main_claim: "论文核心观点"
    significance: "科学意义"
    limitations: ["已知局限1", "已知局限2"]
    next_steps: ["后续研究方向"]
```

## 4. 执行流程

### Step 0：模式选择

| 用户查询特征 | 模式 | 说明 |
|:------------|:----|:-----|
| "写论文"、"写文章"、"写作" | 模式A | 默认框架→确认→写作 |
| "多版本"、"多种方案"、"探索"、"对比" | 模式C | 多版本探索模式 |
| 明确指定假设方向 | 模式A | 使用用户指定假设 |
| 无明确方向 | 模式C | 探索多种可能性 |

### Step 1：获取或运行 HYP

```python
# 检查上游输入
if not has_hypotheses:
    # 加载并运行 HYP 原子
    skill_view("hypothesis-generation")
    # 按照 HYP SKILL.md 执行
    # 输出保存为 hypotheses_output.json
    
# 若用户已提供假设，直接使用
```

### Step 2：生成论文框架

基于 HYP 输出，生成结构化的论文框架 JSON。关键原则：

- **P4 (假说可证伪性)**: 每个假设必须包含 `prediction` 和 `falsification`
- **P5 (空白可追溯性)**: 每个空白必须关联到具体文献引用
- **P0 (证据可溯性)**: 所有声称必须携带 provenance

### Step 3（模式A）：展示框架 + 人类确认

使用 `clarify` 工具展示框架：

```python
clarify(
    question="以下是为您生成的论文框架，请确认：\n\n"
             "📄 标题：[title]\n"
             "🔬 研究空白：[gap_description]\n"
             "🎯 科学假设：[hypothesis_claim]\n"
             "⚙️ 技术方案：[method]\n"
             "🧪 实验设计：[design_type] on [population]\n"
             "📊 预期结果：[primary_finding]\n"
             "💡 核心结论：[main_claim]\n\n"
             "请选择下一步操作：",
    choices=[
        "✅ 确认框架，开始写作",
        "✏️ 修改假设/方案",
        "🔄 重新生成",
        "🔀 切换探索模式（多版本）"
    ]
)
```

根据用户反馈：
- **确认** → 进入 Step 4
- **修改** → 根据用户指示调整框架 → 再次确认
- **重新生成** → 返回 Step 1 或 Step 2
- **切换探索模式** → 进入 Step 3C

### Step 3C（模式C）：生成多版本变体 + 人类选择

从 HYP 输出选取多个假设路径，为每个生成独立框架变体：

```python
clarify(
    question="已生成 [N] 个不同的论文框架方案，请选择：\n\n"
             "---\n"
             "方案1：[variant1_title]\n"
             "  假说：[variant1_hypothesis]\n"
             "  方案：[variant1_approach]\n"
             "---\n"
             "方案2：[variant2_title]\n"
             "  假说：[variant2_hypothesis]\n"
             "  方案：[variant2_approach]\n"
             "---\n"
             "方案3：[variant3_title]\n"
             "  假说：[variant3_hypothesis]\n"
             "  方案：[variant3_approach]\n"
             "---\n\n"
             "请选择：",
    choices=[
        "方案1",
        "方案2",
        "方案3",
        "混合方案（指定组合）"
    ]
)
```

### Step 4：执行写作管线

将确认的框架传递给下游原子：

```
confirmed_framework → ARG (加载 argument-expression SKILL.md)
                     → 生成论文段落
                     → VER (加载 viewpoint-verification SKILL.md)
                     → 验证置信度
                     → 输出 assembled_output.json
```

### Step 5：输出

输出文件：

```
outputs/runs/<run_id>/
├── paper_framework.json      # Step 2 生成的框架
├── human_decision.json       # 人类确认记录（P3追溯）
├── argument_output.json      # ARG 输出
├── verification_output.json  # VER 输出
└── assembled_output.json     # 最终论文
```

## 5. 边界判断

**什么时候用本工作流**：
- 用户需要写一篇完整学术论文
- 用户在撰写前希望确认方向
- 用户不确定研究方向，希望探索多种可能性

**什么时候不用**：
- 用户已有完整框架，只需写作 → 直接用 ARG 原子
- 用户只需要假设生成 → 用 HYP 原子
- 用户只需要文献检索 → 用 ACQ 原子

## 6. 已知陷阱

1. **clarify 工具不可自动化** — 本工作流依赖人类交互，不能用于自动化管线
2. **框架与最终论文可能不一致** — 人类确认框架后，ARG 写作时可能偏离。需在 ARG 执行前将框架作为硬约束注入
3. **多版本模式可能信息过载** — 建议最多生成 3 个变体，太多会让人类难以决策
4. **HYP 输出质量直接影响框架质量** — 如果上游 HYP 质量差，需要先强化 HYP 再进入本工作流
5. **ARG 的输出需要 VER 验证** — 不能跳过观点验证步骤

## 7. 宪法合规映射

| 原则 | 合规机制 |
|:-----|:---------|
| P0 证据可溯性 | 框架每个字段携带 provenance 引用 |
| P3 人机分层 | 核心决策点使用 clarify 等待人类决策 |
| P4 假说可证伪性 | 框架中 hypothesis 包含 prediction + falsification |
| P5 空白可追溯性 | 框架中 research_gap 包含 gap_type + supporting_refs |
