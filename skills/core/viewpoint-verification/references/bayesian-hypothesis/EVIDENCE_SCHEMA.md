# 贝叶斯假设评估 — EVIDENCE_SCHEMA.md

> 对应原则：P0
> 理论来源：Jeffrey (1961); Kass & Raftery (1995); Gelman et al. (2013)

## 证据链节点类型

| source_type | 何时产生 |
|------------|----------|
| `bayesian_evaluation` | 为每个假设计算先验/似然/后验概率时 |

## 节点结构

```json
{
  "source_type": "bayesian_evaluation",
  "source_ref": "hypothesis_id_or_paper_id",
  "hypothesis": "string — H₁: ...",
  "prior": {
    "value": "float 0.0-1.0 — 先验概率",
    "justification": "string — 为什么这个先验是合理的",
    "evidence_count": "int — 支撑先验的文献数量",
    "source_quality_avg": "float — 文献平均方法学质量"
  },
  "likelihood": {
    "value": "float 0.0-1.0 — 综合似然值",
    "evidence_sources": [
      {
        "id": "string — 证据标识",
        "strength": "float 0.0-1.0 — 证据强度",
        "type": "direct|indirect|analogy",
        "source": "string — 来源",
        "weight": "float — 在综合计算中的权重"
      }
    ]
  },
  "posterior": {
    "value": "float 0.0-0.95 — 后验概率 (上限防止过度自信)",
    "calculation": "string — 计算过程简述"
  },
  "bayes_factor": {
    "value": "float — H₁ vs H₀ 的贝叶斯因子",
    "interpretation": "string — 解释 (支持/中等/强/非常强)"
  },
  "confidence": "float 0.0-0.95 — 最终置信度 = min(Posterior, 0.95)",
  "sensitivity_analysis": {
    "prior_range": [0.0, 1.0],
    "posterior_range": [float, float],
    "robust": "bool — 波动 < 0.2 则为稳健"
  },
  "verdict": "string —可信|需更多证据|不可信",
  "required_actions": ["string — 需补充的证据或分析"]
}
```

## 传递规则

每个贝叶斯评估节点必须:
1. 引用具体的 hypothesis_id 或 paper_id 作为 source_ref
2. 所有概率值必须有 justification (不能凭空赋值)
3. 必须包含敏感性分析 (防止单一先验偏差)
4. confidence > 0.7 才视为"可信"
