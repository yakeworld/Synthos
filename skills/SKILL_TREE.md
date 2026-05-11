# Synthos 技能树 v3.1

## 架构概览

```
                    ┌─────────────────────────┐
                    │  Layer 0: 任务编排 (Router) │
                    │  atom0_task_router.py    │
                    │  trust: 0.90  ✅         │
                    └───────────┬─────────────┘
                                │ 奥卡姆剃刀: 最短路径
            ┌───────────────────┼───────────────────┐
            ▼                   ▼                   ▼
┌───────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Layer 1: 知识获取  │ │  Layer 2: 知识提取│ │  Layer 3: 关联发现│
│  atom1 (S2→PM→CR→AR)│ │  atom2 (NLP提取) │ │  atom3 (成对比较) │
│  trust: 0.85  ✅   │ │  trust: 0.80  ✅ │ │  trust: 0.55  ⚠️ │
└───────┬───────────┘ └───────┬─────────┘ └───────┬─────────┘
        │                     │                   │
        └─────────────────────┼───────────────────┘
                              ▼
                    ┌─────────────────────────┐
                    │  Layer 4: 观点生成        │
                    │  atom4 (缺口→假设)        │
                    │  trust: 0.55  ⚠️        │
                    └───────────┬─────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼                               ▼
    ┌───────────────────┐         ┌───────────────────┐
    │  Layer 5: 论证表达  │         │  Layer 5: 观点验证  │
    │  atom5 (IMRaD输出) │         │  atom6 (证伪+反方)  │
    │  trust: 0.75  ✅   │         │  trust: 0.75  ✅   │
    └───────────────────┘         └───────────────────┘
```

## 技能详情

| 层级 | 目录 | Atom | 实现 | 信任度 | 检验 | 状态 |
|------|------|------|------|--------|------|------|
| 0 | task-router | 0 | atom0_task_router.py | 0.90 | ✅ | 生产就绪 |
| 1 | knowledge-acquisition | 1 | atom1_knowledge_acquisition.py | 0.85 | ✅ | 生产就绪 |
| 2 | knowledge-extraction | 2 | atom2_knowledge_extraction.py | 0.80 | ✅ | 生产就绪 |
| 3 | association-discovery | 3 | atom3_association_discovery.py | 0.55 | ⚠️ | 需LLM增强 |
| 4 | hypothesis-generation | 4 | atom4_hypothesis_generation.py | 0.55 | ⚠️ | 需LLM增强 |
| 5 | argument-expression | 5 | atom5_argument_expression.py | 0.75 | ✅ | 生产就绪 |
| 5 | viewpoint-verification | 6 | atom6_viewpoint_verification.py | 0.75 | ✅ | 生产就绪 |

## DAG依赖关系

```
1 (知识获取) ──→ 2 (知识提取) ──→ 3 (关联发现) ──→ 4 (观点生成) ──┬──→ 5 (论证表达)
                                                                    └──→ 6 (观点验证)
```

- **原子1**: 无上游，下游为2、3（直接供给）
- **原子2**: 上游1，下游3
- **原子3**: 上游2，下游4
- **原子4**: 上游3，下游5、6
- **原子5**: 上游4+1（可回取原文），下游无
- **原子6**: 上游4+5（同时需要假设和论证），下游无

## 数据流

```
用户查询 → Router (复杂度判定)
              ↓
         Pipeline执行 atom_chain
              ↓
    accumulated_dict 在各原子间传递
              ↓
    atomX.run(accumulated) → {status, output}
              ↓
    output合并回accumulated → 下一个原子
              ↓
    最终输出: {sections, arguments, references, verification_results}
```

## Synthos 八维覆盖

| 维度 | 覆盖原子 | 评分 | 趋势 |
|------|----------|------|------|
| 第一性原理 | 1, 2, 4, 5 | 95% | → |
| 系统思维 | 1, 3, 5 | 95% | → |
| 贝叶斯思维 | 4, 6 | 90% | → |
| 类比 | 4 | 70% | → |
| 奥卡姆剃刀 | 2, 5, 0 | 80% | → |
| 证伪主义 | 6 | 70% | ↑+10 |
| 模型依赖实在论 | 3 | 50% | ↑+10 |
| 自由能原理 | 6 | 40% | ↑+10 |
| **综合** | | **75%** | ↑+7 |

## 已知局限与增强方向

### 高优先级 (影响检验结果)
1. **原子3 (关联发现)**: 小语料(<5篇)时关联为0，需LLM-based语义关联
2. **原子4 (观点生成)**: 模板假设缺乏可检验性，需LLM生成
3. **S2 API**: key过期，依赖PubMed+arXiv fallback

### 中优先级 (增强鲁棒性)
4. **原子2**: 仅基于摘要，未使用PDF全文
5. **原子6**: 可集成cross_model_review.py的多模型评审
6. **aiohttp会话管理**: academic_writer导入导致未关闭连接

### 低优先级 (扩展功能)
7. **知识图谱持久化**: 跨会话知识积累
8. **多语言**: 原子5的中文论证表达
9. **流式输出**: 长链任务的实时进度

## 使用方式

```bash
# 简单搜索
python3 run_pipeline.py 'find papers about ADHD eye-tracking'

# 领域分析
python3 run_pipeline.py 'analyze recent ML research on transformers'

# 论文写作
python3 run_pipeline.py 'write a survey on ADHD biomarkers'

# 假设验证
python3 run_pipeline.py 'evaluate my hypothesis about eye-tracking diagnosis'
```

## 版本历史

- v3.1 (2026-05-09): 6原子+路由器全部Python实现，pipeline可运行
- v3.0 (2026-05-09): 认知原子架构重构，7→6原子
- v2.x: hermes-scientist工作流架构
