# IO_CONTRACT.md — hypothesis-generation

> 对应原则：P2
> 权威来源：docs/atom-io-schemas.md

## 概述

原子类型：cognitive
上游依赖：association-discovery

## Schema: hypothesis_record

```yaml
hypothesis_record:
  id: \"HYP-YYYYMMDD-N\"
  
  # 来源
  source_gap: \"GAP-YYYYMMDD-M\"      # 源自哪个空白
  origin: enum[GAP_pipeline, user_input, mixed]
  
  # 核心
  title: string                      # 假说标题
  claim: string                      # 核心主张（精确到可检验）
  type: enum[primary, competing, null, auxiliary]
  
  # 认识论熵定位（Step 1.5）
  entropy_reduced:
    uncertainty_type: string         # 四选一：机制不明/效应方向不确定/边界条件模糊/测量效度存疑
    specificity: string              # 具体描述这个假设解决的不确定性
    baseline_entropy: string         # 当前不确定性程度评估
    reduction_gain: string           # 如果验证，不确定性降低多少
  
  # 模型假设清单（Step 2.5）
  model_assumptions:
    - assumption: string
      consequence_if_false: string
  
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
