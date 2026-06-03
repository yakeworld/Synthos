---
name: hypothesis-generation
description: "科学假设生成原子（HYP）—— 将研究空白转化为形式化可检验假说。接收GAP发现的研究空白和ACQ文献语料，生成包含预测、反证条件、竞争假说和实验设计的结构化假设。每个假设包含可检验性/新颖性/重要性/可行性/可验证性/冲突度六维评分及验证方案草案。遵循7+1东西合参框架：观察者位置声明(Step0)→认识论熵定位(Step1.5)→模型假设清单(Step2.5)→日损检查点(Step5.5)。v1.6新增：两轨执行决策（Fast-Track / Plan-Track）"
version: 1.6.0
author: Synthos Agent + 用户杨晓凯
license: MIT
related_skills: [argument-expression, association-discovery, ai-outreach, autonomous-core-researcher, claude-code]
allowed-tools: terminal Read Write
signature: "associations: list[Association], research_gaps: list[Gap] -> hypotheses: list[Hypothesis]"
metadata:
  synthos_atom_type: "cognitive"
  synthos_version: "1.1.0"
  synthos_skill_md_hash: "hypothesis-generation-v1.6.0"
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

> 「穷则变，变则通，通则久。」假说者，可证可伪。
> 「或也者，不尽也。」不立不可证之论，不放无据之言。
> 有破有立，有竞有择。大道至简。

### 设言之法

> 空白之地，假设所生。有疑则有问，有问则有望。
> 凡立说必先有据，凡假设必可证伪。
> 主假说、竞争说、零假说，三者备而后可验。
> 不设虚言，不凭空想。每一问必有一答，每一答必可驳。
> 有可驳者存，科学乃立。

**核心理念**：假设生成是认知链的第四步。将关联发现中的研究空白转化为形式化可检验假说。每个假说必须包含可观测预测、反证条件、竞争假说、实验设计。没有反证条件的"假说"不是假说，是断言。遵循7+1东西合参框架——增加工程约束：观察者位置声明(Step0·天人合一)、认识论熵定位(Step1.5·熵减律)、模型假设清单(Step2.5·庄周观模)、日损检查点(Step5.5·大道至简)。v1.6新增两轨执行决策：Fast-Track（≥0.70直接执行）vs Plan-Track（<0.50列计划等人批）。

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
- [ ] 每个假设包含可检验性/新颖性/重要性/可行性/可验证性/冲突度六维评分
- [ ] 每个假设附带 verification_plan（含验证路径、数据需求、计算成本、风险因素）
- [ ] 每个假设包含 track 字段（fast/plan），且符合可验证性阈值映射
- [ ] 假设来源的研究空白有文献定位
- [ ] 最终输出包含 pruned 记录（日损检查，Step 5.5）
- [ ] 精简后假说数量 ≥ 3（否则触发补充生成）
- [ ] 输出格式符合 _ok 信封结构

### 功能

HYP原子接收GAP发现的研究空白，将其转化为形式化的、可检验的科学假设。每个假说包含预测、反证条件、文献支撑、和实验设计建议。

```
GAP空白 ──→ HYP生成 ──→ 形式化假说列表
                         ├── 主假说 / 竞争假说 / 零假说
                         ├── track: fast | plan（自动路由）
                         ├── verification_record（快验后）
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
entropy_reduced:
  uncertainty_type: "机制不明 | 效应方向不确定 | 边界条件模糊 | 测量效度存疑"
  specificity: "目前只知道X与Y相关，但不知道因果方向（反向因果 vs X→Y）"
  baseline_entropy: "高：已有3篇冲突文献，效应量从-0.2到0.8不等"
  reduction_gain: "如果验证，可将此问题的不确定性降低约60%（从5种解释→2种）"
```

#### Step 2: 假说形式化

```yaml
hypothesis:
  claim: "X与Y呈正相关，且效应量≥0.5"
  prediction: "在A人群中测量X和Y，Pearson r ≥ 0.5, p < 0.01"
  falsification: "如果r < 0.2或p ≥ 0.05，则假说不成立"
  supporting_evidence:
    - doi: "10.xxxx/xxxxx"
      role: "提供了X→Y的初步证据"
  competing_hypotheses:
    - claim: "Z是X和Y的混淆变量"
      distinguishing_test: "控制Z后检测X→Y的偏相关系数"
  suggested_design:
    type: "横断面相关性研究"
    population: "ADHD患儿（6-12岁）"
    sample_size_estimate: "基于效应量0.5, power=0.8, n=64"
    key_measurements: ["3D眼动仪", "ADHD-RS评分", "前庭功能测试"]
```

#### Step 2.5: 模型假设清单

每个假说至少列出 **3 条** 模型假设，每条附带「违反后果」。

```yaml
model_assumptions:
  - assumption: "X的测量误差是随机的（同方差假定）"
    consequence_if_false: "效应量的置信区间可能被低估，假阳性风险上升"
  - assumption: "X与Y的关系在样本范围内是线性的"
    consequence_if_false: "非线性效应（如U型曲线、阈值效应）可能被遗漏"
  - assumption: "样本分组具有充分同质性（除主要变量外）"
    consequence_if_false: "未测量的混杂变量可能导致偏差"
```

#### Step 3: 竞争假说生成 + Step 3.5 负面对齐

对每个主假说，生成至少1个竞争假说。如果假说基于跨领域类比，同步输出负面对齐清单（见原版SKILL.md）。

| 竞争类型 | 含义 | 示例 |
|:---------|:-----|:-----|
| **混淆变量** | 第三变量导致假象关联 | Z→X且Z→Y |
| **反向因果** | Y→X而非X→Y | ADHD症状→异常眼动，而非反之 |
| **调节效应** | 只在特定条件下成立 | 仅男性患儿中显著 |
| **测量伪像** | 假象来自测量方法 | 眼动仪校准误差 |

#### Step 4: 假说评级 — 双轨评分体系

| 维度 | 评分标准 | 权重 |
|:-----|:---------|:----:|
| **可检验性**（0-1） | 是否有明确的观测指标和统计阈值 | 0.20 |
| **新颖性**（0-1） | 与已有文献的差异度 | 0.20 |
| **重要性**（0-1） | 验证后对领域的贡献 | 0.15 |
| **可行性**（0-1） | 所需资源、时间、技术 | 0.15 |
| **可验证性**（0-1） | 验证路径是否清晰完整 | 0.20 |
| **冲突度**（0-1） | 与现有知识的冲突程度 | 0.10 |

综合分 = 可检验性×0.20 + 新颖性×0.20 + 重要性×0.15 + 可行性×0.15 + 可验证性×0.20 + 冲突度×0.10

##### 可验证性评分细则

| 分值 | 含义 | 示例 |
|:---:|:-----|:-----|
| 0.9-1.0 | 有公开数据集/代码可直接运行验证 | 用PhysioNet数据验证PD眼动分类假说 |
| 0.7-0.9 | 可通过虚拟仿真或数值实验验证 | 用PINN模拟VOR增益变化假说 |
| 0.5-0.7 | 需要收集新数据但方案清晰可行 | 临床横断面研究，已有人群可招募 |
| 0.3-0.5 | 验证方案可行但成本高（>1月/>10万） | 纵向队列研究，需随访1年 |
| 0.0-0.3 | 验证方案模糊或当前不可行 | 需新硬件开发/伦理审批/国际合作 |

#### Step 5: NSFC问题树 & Step 5.5: 日损检查点

如果假说符合国家自然科学基金框架，生成问题树。之后执行精简强制检查（见原版SKILL.md）。

#### Step 6: 两轨执行决策 — Two-Track Triage

**核心原则**：基于可验证性评分，将每个假说自动路由到对应执行通道。不等用户确认每个步骤，猜对了继续，猜错了纠正。这是v1.6的新增功能，替代原Step 6的单一容器化执行模式。

**可验证性评分 → 执行通道映射**：

| 可验证性分 | 通道 | 行为 | 示例 |
|:----------:|:-----|:-----|:-----|
| **≥0.70** | 🔥 **Fast-Track** | 直接生成验证代码并执行 | 计算仿真/公开数据/已有代码可复现 |
| **0.50-0.69** | 🟡 **Fast-Track with Report** | 执行后附推理链+假设验证置信度 | 需小量数据预处理的数值实验 |
| **<0.50** | 📋 **Plan-Track** | 生成验证计划+资源估算+风险分析，标记为`awaiting_approval` | 临床实验/新数据采集/需硬件开发 |

#### 🔥 Fast-Track (可快验) — 直接执行

**触发条件**：可验证性 ≥ 0.70 且验证路径是"公开数据分析"或"虚拟仿真"或"算法对比"

**执行流程**：
```
1. 生成验证代码 → /tmp/synthos_verify/<hyp_id>/
2. 直接执行（python shell或terminal）
3. 捕获 stdout + exit_code → 解析指标
4. 输出结构化验证报告：
   ├── 假说置信度（支持/部分支持/不支持）
   ├── 效应量/相关度
   ├── falsification check (是否符合反证条件)
   └── 局限性说明
5. 标记假说状态 executed / execution_failed
```

**常用验证模式**：

| 模式 | 适用场景 | 典型代码结构 |
|:-----|:---------|:-------------|
| **几何仿真** | 解剖形态→功能预测（如SCC形态→复位轨迹） | numpy 3D坐标变换+重力投影+路径积分，scipy相关性分析 |
| **数值模拟** | 物理模型验证（如PINN替代传统求解器） | PINN/DeepONet训练+收敛性分析 |
| **公开数据分析** | 已有数据集的统计验证 | pandas读取+sklearn建模+统计检验 |
| **算法对比** | 新方法 vs 基线（如眼动分类） | 交叉验证+ROC/AUC+配对t检验 |

**Fast-Track 示例（2026-05-29 SCC-BPPV验证）**：
```python
# 验证：SCC形态参数(b)是否影响标准化复位手法耳石轨迹
# 1. 加载已有3标本18条中心线数据
# 2. 拟合3D对数螺旋参数
# 3. 模拟Epley手法4个标准位置的重力方向变化
# 4. 计算每个SCC中耳石的有效位移
# 5. 相关性分析：b值×总行程 r=-0.536, AC变异 CV=18.5%
# 结果：部分支持H1 — 形态影响中等程度，需160例CT批量验证
```

验证代码通用框架：
```python
# fast-track通用模式
data = load_existing_data()
results = compute_hypothesis_metric(data)
corr = pearsonr(x_vals, y_vals)
falsified = abs(corr[0]) < threshold
print(json.dumps({
    "hypothesis_id": "...", "track": "fast",
    "effect_size": float(corr[0]), "p_value": float(corr[1]),
    "falsification_check": "..." ,
    "verdict": "supported" if abs(corr[0])>0.5 else "...",
    "limitations": ["样本量小(n=N)", "简化模型未考虑X因素"]
}))
```

#### 📋 Plan-Track (计划-批准) — 列计划等人批

**触发条件**：可验证性 < 0.50，或涉及以下任一：
- 需人类受试者/伦理审批
- 需新数据采集（>1周收集期）
- 需外部资源（GPU > 4小时/API付费/设备采购）
- 需跨机构合作

**输出格式**：
```yaml
verification_plan:
  track: "plan"
  hypothesis_id: "HYP-xxx"
  claim: "..."

  quick_feasibility_check:
    can_i_verify_with_existing_data: false
    existing_data_gap: "需BPPV患者CT+12月随访数据"
    estimated_effort: "3-6月", estimated_cost: "约5-10万"

  proposed_design:
    type: "回顾性队列研究"
    population: "BPPV患者 ≥60例"
    key_measurements: ["CT半规管形态参数", "复位疗效", "12月复发率"]

  required_resources: ["伦理审批（IRB）: 约1-2月", "..."]
  risk_factors: ["高: 失访率可能 >20%", "..."]
  status: "awaiting_approval"
```

#### Step 6.5: 验证结果记录

```yaml
verification_record:
  hypothesis_id: "HYP-xxx"
  track: "fast | plan"
  executed_at: "2026-05-29T06:30:00Z"
  code_path: "/tmp/synthos_verify/HYP-xxx/"
  execution_time_seconds: 45
  results:
    effect_size: -0.536
    falsification_check: "未违反反证条件（r=-0.536 > 假说阈值r<0.2）"
    verdict: "partially_supported"
  confidence_update: "先验0.70 → 后验0.55（部分支持，效应量中等但样本小）"
  next_action: "批量验证160例CT数据 | 转为Plan-Track等待伦理审批"
```

### 验证标准 — 新增v1.6条目

| 测试 | 通过条件 |
|:-----|:---------|
| 输入1个空白 | 生成≥1个假说 + ≥1个竞争假说 + 观察者位置声明 |
| 每个假说 | 有track字段（fast/plan），且符合可验证性阈值映射 |
| 每个假说 | 有prediction和falsification字段 |
| 每个假说 | 有≥2篇文献支撑 |
| fast-track假说 | 输出包含verification_record |
| 精简后 | 假说数量 ≥ 3 |

### 错误处理

| 错误 | 处理 |
|:-----|:-----|
| 空白太模糊 | 提示用户补充具体矛盾点 |
| 证据不足以形成假说 | 触发ACQ补充检索 |
| fast-track验证失败 | 标记execution_failed + 记录失败原因，自动转为plan-track |
