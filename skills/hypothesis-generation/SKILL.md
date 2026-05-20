---
name: hypothesis-generation
description: "科学假设生成原子（HYP）—— 将研究空白转化为形式化可检验假说。接收GAP发现的研究空白和ACQ文献语料，生成包含预测、反证条件、竞争假说和实验设计的结构化假设。每个假设包含可检验性/新颖性/重要性/可行性评分。"
version: 1.2.0
author: Synthos Agent
license: MIT
allowed-tools: terminal Read Write
signature: "associations: list[Association], research_gaps: list[Gap] -> hypotheses: list[Hypothesis]"
metadata:
  synthos_atom_type: "cognitive"
  synthos_version: "1.1.0"
  synthos_skill_md_hash: "pending"
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

# HYP — 科学假设生成原子

## 触发条件

在以下情况加载本技能：

- 上游 association-discovery 已产出 research_gaps，需要转化可检验假设
- 用户要求"生成假设/提出假说/找研究方向"
- 需要形式化假设（含预测、反证条件、评分）

## 验证清单

- [ ] 每个假设包含 prediction（可观测预测）
- [ ] 每个假设包含 falsification_condition（至少一个反证条件）
- [ ] 每个假设包含可检验性/新颖性/重要性/可行性评分
- [ ] 假设来源的研究空白有文献定位
- [ ] 输出格式符合 _ok 信封结构
- [ ] 无 Python 代码生成

## 功能

HYP原子接收GAP发现的研究空白，将其转化为形式化的、可检验的科学假设。每个假说包含预测、反证条件、文献支撑、和实验设计建议。

```
GAP空白 ──→ HYP生成 ──→ 形式化假说列表
                         ├── 主假说
                         ├── 竞争假说
                         ├── 零假说
                         └── NSFC问题树
```

## 执行流程

### Step 1: 空白→假说转换

对每个GAP空白生成至少一个假说：

| 空白类型 | 默认假说策略 | 示例 |
|:---------|:-------------|:-----|
| 结论矛盾 | "矛盾是由于X调节变量不同" | 效应量随年龄段变化 |
| 方法论缺口 | "新方法Y可以解决X限制" | 深度学习优于传统阈值 |
| 未答问题 | "X导致Y"的正向假设 | 前庭信号异常→ADHD平衡障碍 |
| 过时结论 | "新证据修正了旧结论" | 2025年meta分析推翻2010结论 |

### Step 2: 假说形式化

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

### Step 3.5: [反类比] 负面对齐 — Disanalogy Check

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

### Step 3: 竞争假说生成

对每个主假说，生成至少1个竞争假说（对抗确认偏差）：

| 竞争类型 | 含义 | 示例 |
|:---------|:-----|:-----|
| **混淆变量** | 第三变量导致假象关联 | Z→X且Z→Y |
| **反向因果** | Y→X而非X→Y | ADHD症状→异常眼动，而非反之 |
| **调节效应** | 只在特定条件下成立 | 仅男性患儿中显著 |
| **测量伪像** | 假象来自测量方法 | 眼动仪校准误差 |

### Step 4: 假说评级

| 维度 | 评分标准 |
|:-----|:---------|
| 可检验性（0-1） | 是否有明确的观测指标和统计阈值 |
| 新颖性（0-1） | 与已有文献的差异度 |
| 重要性（0-1） | 验证后对领域的贡献 |
| 可行性（0-1） | 所需资源、时间、技术 |

综合分 = 可检验性 × 0.3 + 新颖性 × 0.25 + 重要性 × 0.25 + 可行性 × 0.2

### Step 5: NSFC问题树

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

## Schema: hypothesis_record

```yaml
hypothesis_record:
  id: "HYP-YYYYMMDD-N"
  
  # 来源
  source_gap: "GAP-YYYYMMDD-M"      # 源自哪个空白
  origin: enum[GAP_pipeline, user_input, mixed]
  
  # 核心
  title: string                      # 假说标题
  claim: string                      # 核心主张（精确到可检验）
  type: enum[primary, competing, null, auxiliary]
  
  # 可检验性
  prediction: string                 # 可观测预测
  falsification: string              # 反证条件
  statistical_criterion: string      # 统计阈值（如 p<0.05, effect>0.5）
  
  # 证据
  supporting_evidence:               # 至少2篇
    - doi: string
      role: string
  conflicting_evidence:              # 如果有
    - doi: string
      role: string
  
  # 竞争关系
  competes_with: string[]            # 竞争假说ID
  distinguishing_test: string        # 区分性实验
  
  # 评分
  scores:
    testability: float               # 0-1
    novelty: float
    importance: float
    feasibility: float
    overall: float
  
  # 实验设计
  suggested_design:
    type: string
    population: string
    sample_size: string
    duration: string
    key_measurements: string[]
  
  # NSFC（如果适用）
  nsfc:
    applicable: boolean
    question_tree: object
    funding_category: string
  
  # 状态
  status: enum[proposed, in_review, accepted, rejected, tested, validated, falsified]
  created_at: timestamp
  last_updated: timestamp
```

## Schema: hypothesis_graph

```yaml
hypothesis_graph:
  nodes:
    - id: string
      title: string
      type: enum[primary, competing, null]
      status: string
  edges:
    - source: string
      target: string
      relationship: enum[competes_with, supports, contradicts, generalizes, specializes]
  gaps_addressed: string[]          # 覆盖的空白ID列表
```

## 验证标准

| 测试 | 通过条件 |
|:-----|:---------|
| 输入1个空白 | 生成≥1个假说 + ≥1个竞争假说 |
| 输入3个空白 | 所有空白都被覆盖 |
| 每个假说 | 有prediction和falsification字段 |
| 每个假说 | 有≥2篇文献支撑 |
| 无输入 | 返回 no_gaps_input 错误 |

## 与下游原子的接口

```
HYP.hypotheses[] 
  ├──→ ASC (论证表达)：将假说展开为论文引言/讨论
  ├──→ NotebookLM/Notion：存入假说库
  └──→ EVA (质量评估)：假说质量纳入进化评分
```

## 错误处理

| 错误 | 处理 |
|:-----|:-----|
| 空白太模糊 | 提示用户补充具体矛盾点 |
| 证据不足以形成假说 | 触发ACQ补充检索 |
| 生成的假说与现有库重复 | 自动合并/标记为辅助假说 |
