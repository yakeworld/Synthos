---
name: hypothesis-generation
description: "科学假设生成原子（HYP）—— 将研究空白转化为形式化可检验假说。接收GAP发现的研究空白和ACQ文献语料，生成包含预测、反证条件、竞争假说和实验设计的结构化假设。每个假设包含可检验性/新颖性/重要性/可行性评分。遵循7+1东西合参框架：观察者位置声明(Step0)→认识论熵定位(Step1.5)→模型假设清单(Step2.5)→日损检查点(Step5.5)。"
version: 1.4.0
author: Synthos Agent
license: MIT
allowed-tools: terminal Read Write
signature: "associations: list[Association], research_gaps: list[Gap] -> hypotheses: list[Hypothesis]"
metadata:
  synthos_atom_type: "cognitive"
  synthos_version: "1.1.0"
  synthos_skill_md_hash: "7a943ccfae503e3f92abeb87296b102e4a51b5c7bcce5fd1dd19d47db9d23e2d"
  synthos_model_tested_on: "2026-05-13T00:00:00Z"
  synthos_io_contract_ref: "references/IO_CONTRACT.md"
  synthos_evidence_schema_ref: "references/EVIDENCE_SCHEMA.md"
  synthos_golden_set_ref: "golden/GOLDEN_SET.md"
  synthos_golden_set_origin: "self_defined"
  synthos_pass_threshold: "0.80"
  synthos_boundary_proof_ref: "references/BOUNDARY.md"
  synthos_change_log_ref: "references/CHANGE_LOG.md"
  synthos_asserted_compliance: "P0,P4,P5"
  synthos_depends_on: "knowledge-extraction,association-discovery"
  synthos_author: "Synthos Agent (v4.3 evolution patch)"
  synthos_data_access_level: "verified_only"
---

# HYP — 科学假设生成原子 (Hypothesis Generation) - 认知原子 #4

## 原理层·文言

### 设言之法

> 空白之地，假设所生。有疑则有问，有问则有望。
> 凡立说必先有据，凡假设必可证伪。
> 主假说、竞争说、零假说，三者备而后可验。
> 不设虚言，不凭空想。每一问必有一答，每一答必可驳。
> 有可驳者存，科学乃立。

**核心理念**：假设生成是认知链的第四步。将关联发现中的研究空白转化为形式化可检验假说。每个假说必须包含可观测预测、反证条件、竞争假说、实验设计。没有反证条件的"假说"不是假说，是断言。遵循7+1东西合参框架——增加工程约束：观察者位置声明(Step0·天人合一)、认识论熵定位(Step1.5·熵减律)、模型假设清单(Step2.5·庄周观模)、日损检查点(Step5.5·大道至简)。

### 假说生成三要义

| 要义 | 文言释 | 含义 |
|:-----|:-------|:-----|
| 可检验 | 可测也 | 有明确的观测指标和统计阈值 |
| 可证伪 | 可驳也 | 有具体的反证条件 |
| 有竞争 | 有他也 | 至少1个竞争假说对抗确认偏差 |

## 方法层·白话

### Step 0: 观察者位置声明

原子在认知链中的位置声明，每次启动时嵌入输出：

```yaml
observer_standpoint:
  cognitive_chain_position: 4 (ACQ→EXT→ASC→HYP→ARG→VER)
  upstream_atoms: [knowledge-extraction, association-discovery]
  downstream_atoms: [argument-expression, viewpoint-verification]
  current_model_lens: "默认：提出最可能为真的假说；可选：提出最具有NSFC竞争力的假说"
```

**意图**：避免工具中立幻觉——明确HYP所在的位置决定它"从什么角度看世界"，从而约束假说生成的方向。如果用户指定 `model_lens` 为"NSFC竞争力模式"，所有评分权重和精简策略随之调整。

### 触发条件

在以下情况加载本技能：

- 上游 association-discovery 已产出 research_gaps，需要转化可检验假设
- 用户要求"生成假设/提出假说/找研究方向"
- 需要形式化假设（含预测、反证条件、评分）

### 验证清单

- [ ] Step 0: 声明观察者位置（cognitive_chain_position、upstream/downstream atoms）
- [ ] 每个假设包含 prediction（可观测预测）
- [ ] 每个假设包含 falsification_condition（至少一个反证条件）
- [ ] 每个假设包含 entropy_reduced（认识论熵定位，Step 1.5）
- [ ] 每个假设包含 model_assumptions（≥3条，每条带违反后果，Step 2.5）
- [ ] 每个假设包含可检验性/新颖性/重要性/可行性评分
- [ ] 假设来源的研究空白有文献定位
- [ ] 最终输出包含 pruned 记录（日损检查，Step 5.5）
- [ ] 精简后假说数量 ≥ 3（否则触发补充生成）
- [ ] 输出格式符合 _ok 信封结构
- [ ] 无 Python 代码生成

### 功能

HYP原子接收GAP发现的研究空白，将其转化为形式化的、可检验的科学假设。每个假说包含预测、反证条件、文献支撑、和实验设计建议。

```
GAP空白 ──→ HYP生成 ──→ 形式化假说列表
                         ├── 主假说
                         ├── 竞争假说
                         ├── 零假说
                         └── NSFC问题树
```

### 执行流程

#### Step 1: 空白→假说转换

对每个GAP空白生成至少一个假说：

| 空白类型 | 默认假说策略 | 示例 |
|:---------|:-------------|:-----|
| 结论矛盾 | "矛盾是由于X调节变量不同" | 效应量随年龄段变化 |
| 方法论缺口 | "新方法Y可以解决X限制" | 深度学习优于传统阈值 |
| 未答问题 | "X导致Y"的正向假设 | 前庭信号异常→ADHD平衡障碍 |
| 过时结论 | "新证据修正了旧结论" | 2025年meta分析推翻2010结论 |

#### Step 1.5: 认识论熵定位

对每个生成（或候选）假说，回到元认知层面追问：

> **"这个假设在降低哪部分认识论熵？"**

即：如果不回答这个假设，我们面对的是什么不确定性？这个假设摧毁的是什么未知？

```yaml
# 输出到每个假说的 entropy_reduced 字段
entropy_reduced:
  uncertainty_type: "机制不明 | 效应方向不确定 | 边界条件模糊 | 测量效度存疑"  # 四选一或多选
  specificity: "目前只知道X与Y相关，但不知道因果方向（反向因果 vs X→Y）"
  baseline_entropy: "高：已有3篇冲突文献，效应量从-0.2到0.8不等"
  reduction_gain: "如果验证，可将此问题的不确定性降低约60%（从5种解释→2种）"
```

**意图**：防止"假说多而空"——每个假说必须明确自己解决的是什么具体不确定性。没有这个回答的假说，在生成阶段就应该被质疑。

#### Step 2: 假说形式化

每个假说必须包含：

```yaml
hypothesis:
  # 核心
  claim: "X与Y呈正相关，且效应量≥0.5"
  
  # 可观测预测
  prediction: "在A人群中测量X和Y，Pearson r ≥ 0.5, p < 0.01"
  
  # 反证条件
  falsification: "如果r < 0.2或p ≥ 0.05，则假说不成立"
  
  # 证据基础
  supporting_evidence:
    - doi: "10.xxxx/xxxxx"
      role: "提供了X→Y的初步证据"
    - doi: "10.xxxx/xxxxy"  
      role: "提供了效应量估计"
  
  # 竞争假说
  competing_hypotheses:
    - claim: "Z是X和Y的混淆变量"
      distinguishing_test: "控制Z后检测X→Y的偏相关系数"
  
  # 实验设计
  suggested_design:
    type: "横断面相关性研究"
    population: "ADHD患儿（6-12岁）"
    sample_size_estimate: "基于效应量0.5, power=0.8, n=64"
    key_measurements: ["3D眼动仪", "ADHD-RS评分", "前庭功能测试"]
```

#### Step 2.5: 模型假设清单

每个假说输出时附带底层建模假设的显式清单——让隐式前提暴露在阳光下：

```yaml
model_assumptions:
  - assumption: "X的测量误差是随机的（同方差假定）"
    consequence_if_false: "效应量的置信区间可能被低估，假阳性风险上升"
  - assumption: "X与Y的关系在样本范围内是线性的"
    consequence_if_false: "非线性效应（如U型曲线、阈值效应）可能被遗漏"
  - assumption: "样本分组具有充分同质性（除主要变量外）"
    consequence_if_false: "未测量的混杂变量可能导致偏差"
```

每个假说至少列出 **3 条** 模型假设，每条附带「违反后果」。

**意图**：科学史表明，重大错误往往出在隐式前提而非显式逻辑上。显式化假设后，同行评审、实验设计、甚至假说自身都可能提前发现潜在漏洞。

#### Step 3.5: [反类比] 负面对齐 — Disanalogy Check

**当假说基于跨领域类比时，必须同时输出负面对齐清单**：

| 类比元素 | 正面相似 | 本质差异（负面对齐） |
|:---------|:---------|:--------------------|
| 源领域特征A | 目标领域也有A | 但在机制M上不同（见注） |
| 源领域关系R | 目标领域有类似关系 | 但R的因果方向可能相反 |

```yaml
analogy:
  source_domain: "变压器注意力机制"
  target_domain: "生物眼动注意力"
  positive: "两者都使用权重分配来聚焦关键信息"
  disanalogies:
    - aspect: "疲劳上限"
      why_different: "生物注意力有生理疲劳上限，变压器没有"
      consequence: "该类比在[长时间任务建模]场景无效"
    - aspect: "状态依赖性"
      why_different: "生物注意力受情绪/药物/昼夜节律影响"
      consequence: "该类比在[ADHD干预评估]场景需修正"
  boundary_condition: "仅适用于[信息选择过程的数学描述]，不适用于[生理机制的因果解释]"
```

#### Step 3: 竞争假说生成

对每个主假说，生成至少1个竞争假说（对抗确认偏差）：

| 竞争类型 | 含义 | 示例 |
|:---------|:-----|:-----|
| **混淆变量** | 第三变量导致假象关联 | Z→X且Z→Y |
| **反向因果** | Y→X而非X→Y | ADHD症状→异常眼动，而非反之 |
| **调节效应** | 只在特定条件下成立 | 仅男性患儿中显著 |
| **测量伪像** | 假象来自测量方法 | 眼动仪校准误差 |

#### Step 4: 假说评级

| 维度 | 评分标准 |
|:-----|:---------|
| 可检验性（0-1） | 是否有明确的观测指标和统计阈值 |
| 新颖性（0-1） | 与已有文献的差异度 |
| 重要性（0-1） | 验证后对领域的贡献 |
| 可行性（0-1） | 所需资源、时间、技术 |

综合分 = 可检验性 × 0.3 + 新颖性 × 0.25 + 重要性 × 0.25 + 可行性 × 0.2

#### Step 5: NSFC问题树

如果假说符合国家自然科学基金框架，生成问题树：

```
顶层问题：前庭功能障碍在ADHD中的致病机制？
 ├── 子问题1：ADHD患儿的前庭功能是否异常？
 │    └── 假说1.1：ADHD患儿的vHIT增益低于正常对照
 ├── 子问题2：前庭异常是否与ADHD核心症状相关？
 │    └── 假说2.1：vHIT增益与ADHD-RS多动评分呈负相关
 └── 子问题3：前庭训练是否能改善ADHD症状？
      └── 假说3.1：8周前庭训练降低ADHD-RS评分≥30%
```

#### Step 5.5: 日损检查点

在所有假说生成完毕后，执行一次**精简强制检查**：

> **问1：当前假设列表中，哪一个最没有区分度？**
> **问2：如果必须删一个假设，删哪个？为什么？**

```yaml
pruned:
  removed_id: "HYP-20260523-003"
  reason: "该假说与主假说HYP-20260523-001的预测空间重叠度>85%，在实际验证中无法提供独立信息增益。保留它增加了科学负载，但没有增加认识论熵减。"
  alternative: "将重合部分合并到假说001的讨论段中作为敏感性分析"
```

**精简准则**：
| 准则 | 判断 |
|:-----|:-----|
| 预测重叠度过高 | 两个假说的预测空间重叠 > 70%，实验设计无法区分 |
| 信息增益不足 | 该假说的 entropy_reduced 与同类假说相比 < 50% |
| 可行性过低 | 可行性评分 < 0.3 且无特殊理由 |
| 证据基础薄弱 | supporting_evidence < 2 篇|

如果精简后剩下的假说 < 3 个，自动触发**补充生成**（回到 Step 1），确保最终输出假说数量 ≥ 3。

**意图**：道家"日损"智慧——科学假说不是越多越好。"损之又损，以至于无为"——能用一个假说解释的，不用两个。

#### Step 6: 实验执行 — Execution Step

**已在 allowed-tools 中声明 terminal 权限。通过容器化环境执行实验代码，收集真实指标。**

**触发条件**：仅当假说已有明确可检验预测 + 用户批准 + 实验可 Python/Shell 实现时执行。

**执行流程**：
```
1. 生成实验代码 → /tmp/synthos_experiments/<hyp_id>/
2. docker run --rm -v /tmp/.../<hyp_id>/:/code python:3.11-slim python /code/run.py
3. 捕获 stdout + exit_code → 解析指标 → 写入 executed_results/
4. 标记假说状态为 executed / execution_failed
```

**安全约束**：必须容器化 | 无网络(--network none) | 超时≤30min | 自动清理(--rm) | 执行前审查代码

**不执行（仅出方案）**：需 GPU / 外部 API 密钥 / >30min / 涉及人或动物数据

### 验证标准

| 测试 | 通过条件 |
|:-----|:---------|
| 输入1个空白 | 生成≥1个假说 + ≥1个竞争假说 + 观察者位置声明 |
| 输入3个空白 | 所有空白都被覆盖 |
| 每个假说 | 有prediction和falsification字段 |
| 每个假说 | 有≥2篇文献支撑 |
| 每个假说 | 有entropy_reduced字段（Step 1.5定位） |
| 每个假说 | 有model_assumptions ≥ 3条（Step 2.5清单） |
| 最终输出 | 有pruned记录（Step 5.5日损检查） |
| 精简后 | 假说数量 ≥ 3（否则触发补充生成） |
| 无输入 | 返回 no_gaps_input 错误 |
| 完整Schema | references/IO_CONTRACT.md |
### 与下游原子的接口

```
HYP.hypotheses[] 
  ├──→ ASC (论证表达)：将假说展开为论文引言/讨论
  ├──→ NotebookLM/Notion：存入假说库
  └──→ EVA (质量评估)：假说质量纳入进化评分
```

### 错误处理

| 错误 | 处理 |
|:-----|:-----|
| 空白太模糊 | 提示用户补充具体矛盾点 |
| 证据不足以形成假说 | 触发ACQ补充检索 |
| 生成的假说与现有库重复 | 自动合并/标记为辅助假说 |

## 命令层·English

- **Signature**: `associations: list[Association], research_gaps: list[Gap] -> hypotheses: list[Hypothesis], observer_standpoint: ObserverStandpoint, pruned: list[PruneRecord]`
- **Allowed tools**: `terminal`, `Read`, `Write`
- **Input**: `associations` (list[Association]) + `research_gaps` (list[ResearchGap]) from upstream `association-discovery`
- **Output**: `hypotheses` (list[Hypothesis]) — each with prediction, falsification, competing hypotheses, evidence, scores, experimental design, entropy_reduced, model_assumptions; plus observer_standpoint declaration and pruned records
- **Required fields per hypothesis**: `prediction`, `falsification`, `supporting_evidence` (≥2), `competing_hypotheses` (≥1), `scores`, `entropy_reduced`, `model_assumptions` (≥3)
- **Competing types**: `confounding`, `reverse_causality`, `moderation`, `measurement_artifact`
- **Score weights**: testability×0.3 + novelty×0.25 + importance×0.25 + feasibility×0.2
- **NSFC mode**: optional, generates question tree when applicable
- **Pruning**: mandatory Step 5.5 — if hypotheses < 3 after pruning, trigger supplementary generation
- **Model lens**: default "most likely true"; optional "most competitive for NSFC"
- **Do NOT**: generate hypotheses without falsification conditions, skip competing hypotheses, fabricate evidence, skip the daily-loss pruning check
