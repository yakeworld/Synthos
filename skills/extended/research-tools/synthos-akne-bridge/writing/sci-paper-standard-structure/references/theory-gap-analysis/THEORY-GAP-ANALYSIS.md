# 理论缺口分析 — Synthos 学术理论体系审计

> 审计日期: 2026-06-19
> 审计范围: 全部认知原子 + 论文管线 + 哲学文档
> 审计目标: 识别已实现/已提及/完全缺失的理论框架，为后续补充提供路线图

---

## 一、已有理论（已实现）

| # | 理论 | 状态 | 位置 | 理论来源 |
|---|------|------|------|----------|
| 1 | **CARS 模型** | ✅ 已实现 | `argument-expression/references/cars-analysis/` | Swales (1990) |
| 2 | **引用功能分类** | ✅ 已实现 | `argument-expression/references/citation-function-classifier/` | Meyer (2010) |
| 3 | **研究空白类型分类** | ✅ 已实现 | `argument-expression/references/gap-type-classifier/` | Blessing & Chakraborti (2003) |
| 4 | **四维质量门控** | ✅ 已实现 | `argument-expression/references/quality-4d-gate/` | Popper + Kuhn + Lakatos (引用) |
| 5 | **文献综述 6 轴质量门** | ✅ 已实现 | `argument-expression/references/litreview-quality-gate.md` | PaperOrchestra |
| 6 | **引用 F1** | ✅ 已实现 | `viewpoint-verification/references/citation-f1-methodology.md` | PaperOrchestra |
| 7 | **伦理筛查** | ✅ 已实现 | `viewpoint-verification/references/ETHICS_SCREENING.md` | 通用伦理准则 |
| 8 | **哲学框架（三翼+铁律）** | ✅ 已实现 | `docs/synthos-philosophy.md` + `AGENTS.md` | 东西方融合 |
| 9 | **6 认知原子 DAG** | ✅ 已实现 | `AGENTS.md` | 原创 |
| 10 | **CRISP-DM 实验流** | ✅ 已实现 | `paper-pipeline/references/crispdm-helix-experiment-workflow.md` | CRISP-DM 标准 |
| 11 | **论文结构映射** | ✅ 已实现 | `akne-bridge/.../system-description-paper-structure.md` | 原创 |
| 12 | **写作前 IMRaD Gap 映射** | ✅ 已实现 | `akne-bridge/.../prewriting-gap-analysis.md` | 原创 |
| 13 | **创新思维框架（L1/L2/L3）** | 🟡 仅描述 | `skill_tree.json` | 创意理论综合 |

---

## 二、已提及但未实现（半缺失）

### H1: 图尔敏论证模型 (Toulmin's Argument Model) — 高优先级

**当前状态**:
- `system-description-paper-structure.md:102` 有一张映射表
- 但 **没有实际的 Toulmin 分析器代码/模块**
- ARG 原子输出 "claims" 但没有将其结构化

**需要实现**:
```
Data（数据/证据）
  → Warrant（推理规则）
    → Claim（主张/结论）
  ↑
Backing（支撑）
Qualifier（限定词）
Reservation（例外）
```

**影响**: Discussion 部分缺乏严谨的论证结构。每个主张应该有 Data -> Warrant -> Claim 完整链路。

**理论来源**: Toulmin (1958) "The Uses of Argument"

---

### H2: SPICE/SPIRIT 研究问题框架 — 中优先级

**当前状态**: 完全不存在

**需要实现**:
```
SPICE:
  Setting（场景）+ Perspective（视角）+ Intervention（干预）
  + Comparison（对照）+ Evaluation（评估）+ Context（背景）

SPIRIT:
  Source + Phenomenon of Interest + Research design
  + Intervention/Exposure + Types of outcome + Timing
```

**影响**: Gap 到 Hypothesis 的转换是黑箱，缺少结构化框架。

**理论来源**: Thompson (2004); Richardson (1999)

---

### H3: Boden 创造力分类 — 中优先级

**当前状态**: skill_tree.json 中提到 "Boden约束" 但无实现代码

**需要实现**:
```
Combinatorial (组合创新):     已有空间内新概念的组合
Exploration (探索创新):       扩展已有空间的边界
Transformational (转换创新):  改变空间本身的规则/约束
```

**影响**: 所有 gap 被同等对待，无法区分渐进式创新 vs 范式级创新。

**理论来源**: Boden (1991) "The creative mind: Myths and mechanisms"

---

### H4: Kuhn 范式评估 + Lakatos 研究纲领 — 中优先级

**当前状态**: 在 4D 门控中作为"理论来源"引用，但从未真正使用

**需要实现**:
```
Kuhn:   当前范式状态? 是 anomaly 内修补还是范式改变?
Lakatos: Hard Core + Protective Belt? 研究纲领 progress 还是 decline?
```

**理论来源**: Kuhn (1962); Lakatos (1970)

---

### H5: 引文链分析 — 中优先级

**当前状态**: 有 citation_count 和 6 种引用功能，但无方向性分析

**需要实现**:
```
Forward:  后续文献引用情况（正面/负面）
Backward: 核心网络覆盖度
Context:  每篇文献的引用上下文深度分析
```

---

### H6: IMRaD 结构自动验证器 — 中优先级

**当前状态**: 有映射概念但无自动检查器

**需要实现**: 验证论文各 section 是否包含 IMRaD 要求的核心要素

---

## 三、完全缺失理论

### M1: 贝叶斯假设评估 — 高优先级

**为什么重要**: VER 原子置信度计算是确定性的，没有概率框架。贝叶斯是现代科学假设评估的标准方法。

**需要实现**:
```
P(H|E) = P(E|H) × P(H) / P(E)
Prior → Likelihood → Posterior → Bayes Factor
```

**理论来源**: Jeffrey (1961); Kass & Raftery (1995); Gelman et al. (2013)

---

### M2: 实验设计方法论 — 高优先级

**需要实现**:
```
- 样本量计算 (power analysis)
- 随机化/盲法设计
- PICOS/PIOS 框架
- RCT (CONSORT) / 观察性 (CASP) / 质性 (COREQ)
```

**理论来源**: CONSORT; STROBE; CASP; COREQ; PICOS

---

### M3: 系统评价/Meta-分析方法论 — 中优先级

**需要实现**: PRISMA 流程图 + 质量评估 (Cochrane RoB 2.0 / ROBINS-I / NOS)

**理论来源**: PRISMA 2020; Cochrane Handbook

---

### M4: 科学写作的修辞学框架 — 低优先级

**需要实现**: Hyland 学术写作五维度 + Swales & Feak 风格矩阵

**理论来源**: Hyland (2000); Swales & Feak (2012)

---

### M5: 可重复性/开放科学框架 — 中优先级

**需要实现**: 数据/代码可用性声明 + 预注册 + 报告指南符合度 + Effect Size

**理论来源**: Ioannidis (2005); Open Science Framework

---

### M6: 同行评审模拟 — 中优先级

**需要实现**: 多角色评审模拟 (方法学/领域/统计/主编)，模拟真实审稿

**理论来源**: Nature/Science 审稿标准; Bédard et al. (2020)

---

## 四、补充优先级矩阵

| 编号 | 理论 | 优先级 | 估计工作量 | 依赖 |
|------|------|--------|-----------|------|
| H1 | Toulmin 论证模型 | 高 | 小 (50-80行) | 无 |
| M1 | 贝叶斯假设评估 | 高 | 中 (100-150行) | 无 |
| M2 | 实验设计方法论 | 高 | 中 (80-120行) | 无 |
| H2 | SPICE/SPIRIT | 中 | 中 (60-100行) | 无 |
| H3 | Boden 创造力分类 | 中 | 小 (30-50行) | 无 |
| H4 | Kuhn/Lakatos 评估 | 中 | 中 (80-120行) | H3 |
| H5 | 引用链分析 | 中 | 大 (200+行) | 现有citation |
| H6 | IMRaD 验证器 | 中 | 中 (60-100行) | 无 |
| M3 | Meta-分析方法论 | 中 | 大 (150+行) | M2 |
| M5 | 可重复性框架 | 中 | 小 (40-60行) | 无 |
| M6 | 评审模拟 | 低 | 大 (200+行) | M1, M2 |
| M4 | 写作修辞学 | 低 | 中 (80-120行) | H1 |

---

## 五、理论关系图

```
                    +---------------------+
                    |   科学哲学基础       |
                    | (Popper/Kuhn/Lakatos)|
                    +----------+----------+
                               |
          +--------------------+--------------------+
          |                    |                    |
    +-----+-----+      +------+-------+     +------+-------+
    | 假设评估   |      | 创新评估     |     | 质量门控     |
    | (Bayesian) |      | (Boden)      |     | (4D/6轴)     |
    +-----+-----+      +------+-------+     +------+-------+
          |                    |                    |
    +-----+--------------------+--------------------+-----+
    |                 研究生命周期                         |
    |                                                      |
    |  Gap --SPICE--> Hypothesis --Toulmin--> Argument     |
    |     |              |              |                 |
    |  Boden          Design          CARS                |
    |     |              |              |                 |
    |  Hypothesis --M2--> Experiment --> Results          |
    |                                                    |
    |  Citation --H5--> Writing --M4--> Peer Review --M6|
    +----------------------------------------------------+
```

---

## 六、架构决策建议

**问题**: 这些模块是合并为单一"论文质量分析器"还是保持独立？

**建议**: **保持独立**，通过 ORCHESTRATOR 模式组合。

理由:
1. P2 原则"稳定下沉/演化上浮" — 每个理论模块作为独立技能，可独立升级
2. P3 原则"人机分层" — 路由器负责路由，原子负责执行
3. 单一分析器违背"原子边界精确"原则
4. 推荐: paper-pipeline (编排层) -> 各独立分析模块，互不依赖可替换

---

*Synthos 理论审计 v1.0 — 动灵在内，不假外求*

---

## 实现状态追踪 (2026-06-19 更新)

| 编号 | 理论 | 计划 | 状态 | 位置 |
|------|------|------|------|------|
| H1 | Toulmin 论证模型 | 高 | ✅ 完成 | argument-expression/references/toulmin-argument/ |
| H2 | SPICE/SPIRIT | 中 | ✅ 完成 | hypothesis-generation/references/spice-framework/ |
| H3 | Boden 创造力分类 | 中 | ✅ 完成 | association-discovery/references/boden-creativity/ |
| H4 | Kuhn/Lakatos | 中 | ✅ 完成 | argument-expression/references/kuhn-lakatos/ |
| H5 | 引用链分析 | 中 | ✅ 完成 | argument-expression/references/citation-chain/ |
| H6 | IMRaD 验证器 | 中 | ✅ 完成 | argument-expression/references/imrad-validator/ |
| M1 | 贝叶斯假设评估 | 高 | ✅ 完成 | viewpoint-verification/references/bayesian-hypothesis/ |
| M2 | 实验设计方法论 | 高 | ✅ 完成 | knowledge-acquisition/references/experimental-design/ |
| M3 | Meta-分析方法论 | 中 | ✅ 完成 | knowledge-acquisition/references/meta-methodology/ |
| M4 | 科学写作修辞学 | 低 | ✅ 完成 | argument-expression/references/rhetoric-framework/ |
| M5 | 可重复性框架 | 中 | ✅ 完成 | viewpoint-verification/references/reproducibility/ |
| M6 | 同行评审模拟 | 中 | ✅ 完成 | viewpoint-verification/references/review-simulation/ |

## 完成率

```
已实现理论: 13 (原有) + 12 (新增) = 25
理论缺口: 0/12 = 0%
完整度: 100%
```

## 架构最终状态

```
认知原子理论模块分布:
  ACQ (格物):       文献检索 + CRISP-DM + 实验设计 + Meta-分析
  EXT (通理):       (无独立理论模块 — 依赖 ACQ 输出)
  ASC (取象):       空白类型分类 + Boden 创造力
  HYP (通变):       SPICE/SPIRIT + 贝叶斯评估
  ARG (立言):       CARS + 4D + 6轴 + Toulmin + IMRaD + 修辞学 + 引用链 + Kuhn/Lakatos
  VER (正观):       Citation F1 + 伦理筛查 + 可重复性 + 同行评审模拟 + 贝叶斯

论文管线理论模块:
  paper-pipeline/  → CRISP-DM 实验流 + 批量QC + NotebookLM 5门
  prewriting/      → IMRaD Gap Mapping
  structure/       → 系统论文结构 + 论文模板

哲学理论模块:
  docs/            → 三翼+铁律 + 五经据典 + 三层文言
  AGENTS.md        → 宪法 + 哲学免疫系统 + 六认知原子DAG
  evolution-*      → 进化状态 + 进化日志
```
