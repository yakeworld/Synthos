---
name: hypothesis-generation
description: "Generate falsifiable, prioritised research hypotheses from gap analysis — with falsifiability tests, evidence matrices, clinical translation assessment, and composite scoring."
version: 1.1.0
license: MIT
author: Synthos
priority: P1
atom_type: cognitive-atom
metadata:
  synthos:
    signature: "research_gap: str, domain_knowledge: str, constraints: dict -> hypotheses: list[Hypothesis]"
    related_skills:
      - knowledge-acquisition
      - knowledge-extraction
      - association-discovery
      - argument-expression
      - viewpoint-verification
---

# Hypothesis Generation

> 假说生于空白，立于可证伪，强于可检验。

## 原理层 · 文言

> 「假说者，探理之始也。无证则悬，有证则立。」
> 「可证伪者存，不可证伪者废。无检验之假设，犹无砭之弓矢。」
> 立意高远，证伪分明，验之有法，废之有理。

## 触发条件

- 研究空白（gap\_analysis 输出）待转化为可检验假设
- 用户输入"提出假设"、"hypothesize"、"formulate" 等指令
- 需要构建研究方案的假说框架

## 输入契约

| 字段 | 类型 | 必需 | 说明 |
|:-----|:-----|:----:|:-----|
| research_gap | str | ✅ | 研究空白描述（来自 gap_analysis 或文献扫描） |
| domain_knowledge | str | ✅ | 领域知识摘要（经典模型、已知约束、实验范式） |
| constraints | dict | ❌ | 实验约束（预算、时间、数据可得性、伦理限制） |
| prior_hypotheses | list | ❌ | 已有假说（避免重复） |

## 输出契约

```yaml
hypothesis_record:
  id: "HYP-YYYYMMDD-N"
  title: string                     # 假说标题
  statement: string                 # 核心主张（精确到可检验）
  rationale: string                 # 理论基础
  # --- 可检验性 ---
  falsifiability_test:
    experiment: string              # 关键实验设计
    subjects: string                # 受试者/样本要求
    measurements: string[]          # 关键测量指标
    rejection_criteria: string      # 定量反证条件（"H falsified if ..."）
  # --- 证据 ---
  supporting_evidence:
    - source: string                # 文献引用
      role: string                  # 证据角色（motivation / constraint / precedent）
      confidence: int               # 星级 (1-5)
  conflicting_evidence:
    - source: string
      role: string
  # --- 评分 ---
  scores:
    novelty: float                  # 0-1 新颖性
    plausibility: float             # 0-1 合理性
    testability: float              # 0-1 可检验性
    clinical_impact: float          # 0-1 临床转化潜力（仅生物医学领域）
    feasibility: float              # 0-1 实验可行性
    composite: float                # 加权综合
  priority: string                  # HIGHEST / HIGH / MEDIUM / LOW
  suggested_design:
    type: string                    # 实验设计类型
    population: string              # 目标人群
    sample_size: string             # 样本量估算
    duration: string                # 实验时长
```

## 执行步骤

### Step 1: 从 Gap 到假说种子

1. 读取 gap_analysis 输出，提取：
   - **白空间状态**（ABSOLUTE_WHITE / CONDITIONAL / OCCUPIED）
   - **空白类型**（方法空白 / 疾病空白 / 机制空白 / 生物标志物空白）
   - **竞争分析**（经典模型 vs PINN/ODE 模型区分）
   - **临床需求**（目标疾病、市场规模、未满足需求）
2. 从每个空白维度推导 1-2 个假说种子

### Step 2: 假说结构化

每个假说按五段式构建：

```
┌─────────────────────────────────────────┐
│  H: 假说标题                             │
│                                          │
│  ① Statement — One-line crystal-clear    │
│     claim.                               │
│                                          │
│  ② Rationale — Why this hypothesis       │
│     follows from domain knowledge.        │
│     Should cite 2-3 key foundational      │
│     references.                           │
│                                          │
│  ③ Falsifiability Test — The heart.      │
│     - Experiment design (what, who, how)  │
│     - Explicit quantitative rejection     │
│       criteria ("H falsified if RMSE >    │
│       X, R² < Y, AUC < Z")               │
│     - Statistical criterion (p, effect    │
│       size, confidence interval)          │
│                                          │
│  ④ Evidence Matrix                       │
│     - Supporting: source + role + conf    │
│     - Conflicting: source + role          │
│     - At least 3 supporting per H         │
│                                          │
│  ⑤ Counter Evidence & Limitations        │
│     - Confounding factors, boundary       │
│       conditions, known biases            │
│     - Cross-species / cross-paradigm      │
│       generalisability caveats            │
└─────────────────────────────────────────┘
```

### Step 3: 复合评分

| 维度 | 权重 | 评分标准 |
|:-----|:----:|:---------|
| Novelty | 0.20 | 0.0=已知答案, 0.5=已知领域的延伸, 1.0=全新空白 |
| Plausibility | 0.20 | 0.0=与已知规律矛盾, 0.5=合理但不显然, 1.0=经典理论的直接推论 |
| Testability | 0.20 | 0.0=无法检验, 0.5=需要新范式, 1.0=现有设备+现有数据即可检验 |
| Clinical Impact | 0.25 | 0.0=无临床价值, 0.5=间接价值, 1.0=直接影响诊断/治疗决策 |
| Feasibility | 0.15 | 0.0=不可行, 0.5=需要额外资源, 1.0=现有可能 |

**Composite** = Σ(score_i × weight_i)

| Composite | Priority |
|:----------|:---------|
| ≥ 0.80 | HIGHEST |
| ≥ 0.65 | HIGH |
| ≥ 0.50 | MEDIUM |
| < 0.50 | LOW |

### Step 4: 假说排序 & 推荐

- 输出假说的优先列表
- 标注 recommented_primary_hypothesis
- 给出区分各假说的判别实验

## 生物医学 PINN/ODE 假说模板

对于眼动/前庭/生物力学领域的 2-ODE + PINN 模型假说，推荐以下固定结构：

```
H{n}: [Variable] [Relationship] [Condition]

Statement: The [parameter/metric] [verb] [function/relationship] 
           that [PINN property] can [capability] from [data constraint].

Falsifiability example:
  - Falsified if: RMSE > X, R² < Y, AUC_diff < Z
  - Primary endpoint: [quantifiable metric]
```

**历史成功假说模式**：
1. **增益-频率假说** — OKR/VOR 增益是刺激频率的 S 形函数，PINN 可从稀疏数据学习
2. **对数缩放假说** — 小脑适应率与误差幅度呈对数关系（Weber-Fechner 定律）
3. **生物标志物假说** — 某时间常数是某疾病的比金标准更敏感的指标（ROC AUC 对比）
4. **集成/框架假说** — 将 gap_analysis 提出的多个独立候选假说整合为一个统一的多参数诊断框架。**为什么有效**: 单个生物标志物假说受限于单参数与单疾病的映射；集成假说提升维度的同时不增加检测成本（同一次检测提取全部参数）。**何时添加**: gap_analysis 提出 ≥3 个独立假说时，自动检查它们是否可合成一个统一框架。若各假说对应不同参数且源自同一次检测，则集成假说总是适用的。**验证案例**: caloric-test-response-ODE session (2026-06-21) — H4 multi-parameter framework scored 0.82 (HIGH) vs H1=0.84 (HIGHEST), but H4 novelty=0.95 vs H1=0.90. Integration hypothesis typically has lower feasibility but higher novelty + clinical impact.

## 已知陷阱

1. **假说不具可证伪性** — 每个假说必须有明确的定量拒绝标准，不能仅说"需要进一步研究"
2. **证据引用不足** — 每个假说至少需要 3 篇支撑文献，1 篇反例或边界条件文献
3. **忽略混杂因素** — 药物影响、年龄效应、跨物种差异必须列出
4. **同源假说簇** — 多个假说对应同一实验时，需要给出区分性实验设计
5. **PINN 假说特有问题** — 必须区分"先验模型空白"（differential equation 建模）和"数据驱动空白"（PINN learning），两者不同

## 性能特征：门控恢复

从 gap_analysis（通常 CONDITIONAL 0.65-0.78）到 hypothesis_generation 的过渡通常产生 +9 到 +15 分的提升，使候选者达到 PASS 状态。历史数据：

| Session | Gap Score | HG Score | Δ | Key Improvements |
|:--------|:---------:|:--------:|:-:|:----------------|
| vocal-fold-phonation-PINN (C164) | 0.78 CONDITIONAL | 0.87 PASS | +9 | Formalized 3 drafts + H4 integration + Pattern #5 |
| PupillaryLightReflex-PINN (C139) | 0.89 PASS | 0.87 PASS | -2 | Scores already high; no recovery needed |
| cardiac-autonomic (C141) | 0.88 PASS | 0.87 PASS | -1 | Already at PASS |
| caloric-test (C118) | 0.88 PASS | 0.84 PASS | -4 | Hypothesis formalization was valid |

**模式**: CONDITIONAL candidates (0.65-0.78) 在 hypothesis_generation 中通过以下方式获得最大的提升：(a) 将 gap_analysis 中的草稿假说正式化、(b) 在 ≥3 个独立假说时添加模式 #4 集成假说、(c) 添加模式 #5 判别设计、(d) 绘制完整的转化路径。已经处于 PASS 状态的候选者通常会保持或小幅下降（因为他们严格的 gap_analysis 已经有高分）。

## 假说模式 #5：判别性实验设计（Discriminative Experiment Design）

**当多个假说共享同一临床协议但探测不同时间相位时适用。**

### 模式描述

PINN/ODE 候选常产生 3-5 个假说，各对应不同的 ODE 参数（增益、时间常数、延迟、顺应性等）。若所有参数可从同一个临床扰动协议的不同时间相位提取，则无需为每个假说设计独立的实验。**单个协议 × 时间相位切分 = 同时检验所有假说。**

### 何时使用

- gap_analysis 提出了 ≥3 个独立参数，且每个参数主导不同的扰动时相
- 临床协议包含多个生理阶段（如 Valsalva 四相、头脉冲前/中/后、倾斜台测试不同角度）
- 每个时相有明确的起始/结束边界（可秒级分割）

### 实现步骤

1. **列出各假说的核心参数** — 哪个 ODE 参数决定哪个假说（如 G_BRS → 增益假说, τ_BR → 速度假说）
2. **分解临床协议为时间相位** — 记录每个时相的生理事件和持续时间
3. **建立相位→参数映射表** — 每个时相对应的主导参数（如 Valsalva 相 I → δ 延迟, 相 II_early → G_BRS 增益, 相 II_recovery → τ_BR 速度, 相 IV → C 顺应性）
4. **验证映射唯一性** — 避免两个参数在同一时相主导（若重叠则需分离实验或统计解耦）
5. **输出判别实验表格** — 格式：

| Phase | Physiology | Dominant Parameter | Hypothesis Tested | Rejection Criterion |
|:------|:-----------|:------------------:|:----------------:|:-------------------:|
| I (onset, 0-2s) | Mechanical BP surge | δ (conduction delay) | H4 | δ > 600ms |
| II_early (2-8s) | Venous return ↓ | G_BRS (baroreflex gain) | H1 | AUC < 0.70 |
| ... | ... | ... | ... | ... |

### 模式 #5 变体：内源周期分割（Intrinsic Cyclic Segmentation）

**当假说利用同一生理振荡的单周期内相位而非扰动协议的不同时相时适用。**

#### 何时使用

- 研究对象是持续振荡（心跳、呼吸、发声振荡、眼震慢相），而非单次扰动（Valsalva、头脉冲）
- 每个生理周期可分割为可辨识的子相位（打开/闭合/开放/恢复），且不同参数主导不同相位
- 单个"静止"记录（如持续元音、静息态ECG、静止凝视）即包含所有相位信息

#### 与经典 Pattern #5 的区别

| 维度 | 经典 Pattern #5（扰动分割） | 内源周期分割变体 |
|:-----|:--------------------------:|:---------------:|
| 时间分辨率 | 秒级（扰动相I→II→III→IV） | 毫秒级（周期内的打开/闭合/闭合/开放） |
| 记录类型 | 主动指令（"吹气"、"转头"） | 被动静止记录（"发元音"、"平视"） |
| 参数映射 | 每个扰动相位→1-2个参数 | 每个周期相位→1-2个参数 |
| 验证难度 | 需要精确的扰动时间戳 | 需要高采样率（≥10kHz）分割周期相位 |
| 边际数据成本 | 每个扰动增加额外数据 | 同一记录无额外数据成本 |

#### 验证案例

**vocal-fold-phonation-PINN (K-014, Cycle 164, 2026-06-22):** 一段 30s 持续元音 /a/ 的声门周期可分割为 6 个相位：Opening (0-1ms) → A_g0 主导；Maximum Opening (1-3ms) → P_sub, α 主导；Closing (3-4ms) → b 主导；Closed Phase (4-10ms) → K_c 主导；Sustained Oscillation (20-500ms) → k 主导；Phonatory Modulation (0.5-10s) → m, P_sub 主导。**结果**: 一段 30s 记录 = 4 个参数特定假说的同时检验。

### 与模式 #4（集成假说）的区别

| 维度 | 模式 #4 集成/框架假说 | 模式 #5 判别性实验设计 |
|:-----|:--------------------:|:---------------------:|
| 目标 | 组合参数 → 一个复合指数 | 区分竞争假说 → 检验优先级 |
| 输出 | 加权复合指标（BHI） | 相位→参数映射表 |
| 适用范围 | 所有假说可单向合并 | 假说对应不同主导时相 |
| 典型分数 | 高 Novelty, 中 Feasibility | 高 Testability + Feasibility |

## 质量检查清单

- [ ] 每个假说有明确的 statement（one-liner）
- [ ] 每个假说有 falsifiability test 和 rejection criteria
- [ ] 每个假说评分维度全（novelty, plausibility, testability, clinical_impact, feasibility）
- [ ] 至少 3 个支撑文献引用
- [ ] 列出反例/边界条件
- [ ] 输出优先排序
- [ ] 标记推荐 primary hypothesis
- [ ] 输出格式兼容下一原子（argument-expression）

## 支持文件

- `references/BOUNDARY.md` — 原子职责边界
- `references/IO_CONTRACT.md` — 输入输出 Schema（含 hypothesis_record 完整 YAML）
- `references/EVIDENCE_SCHEMA.md` — 证据链节点类型
- `references/CHANGE_LOG.md` — 版本变更
- `templates/hypothesis_output.md` — 假说输出文件模板（含评分表、证据矩阵）

## 执行示例

### 示例 1: OKR-adaptation-PINN (2026-06-20)

三人假说生成产物结构参见 `session-2026-06-20-OKR-adaptation-PINN.md`：
- H1: Gain-Frequency Sigmoid (0.74, HIGH)
- H2: Logarithmic Rate Scaling (0.74, HIGH)
- H3: Ataxia Biomarker τ_adapt (0.84, HIGHEST)
- 各假说含完整 falsifiability test + evidence matrix + counter-evidence + composite scoring

### 示例 2: vocal-fold-phonation-PINN (2026-06-22)

参见 `session-2026-06-22-vocal-fold-phonation-PINN.md` 完整会议记录：
- **领域**: Domain Expansion #6，首次应用于喉部/发声生物力学的PINN候选
- **输出**: 4 个假说（H1 0.866 HIGHEST, H2 0.794 HIGH, H3 0.748 HIGH, H4 0.762 HIGH）
- **新模式**: 首次将 Pattern #5 变体（内源周期分割）应用于声门周期相位分割
- **门控恢复**: CONDITIONAL 0.78 → PASS 0.87（+9分）
