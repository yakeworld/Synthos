# 贝叶斯假设评估器

> 理论来源：Jeffrey (1961); Kass & Raftery (1995); Gelman et al. (2013)

## 贝叶斯评估框架

贝叶斯方法是现代科学假设评估的标准概率框架。不同于传统频率学派的"接受/拒绝"二元判断，贝叶斯方法给出**假设成立的概率**。

### 核心公式

```
P(H|E) = P(E|H) × P(H) / P(E)

其中:
  P(H)       = Prior — 假设的先验概率（基于已有文献）
  P(E|H)     = Likelihood — 在假设成立前提下，观测到新证据的概率
  P(E)       = Marginal likelihood — 新证据出现的总概率
  P(H|E)     = Posterior — 结合新证据后，假设成立的后验概率
```

### 多级证据融合

```
证据等级                    权重 (w)   说明
─────────────────────────────────────────────────────────
直接实验证据 (RCT/模拟)       1.0       直接检验假设
间接证据 (关联/机制)          0.7       支撑同一机制但非直接检验
类比证据 (相似领域)           0.4       不同领域但逻辑相似
专家意见 / 理论推导           0.2       仅作为辅助支撑
```

### 先验概率 P(H) 评分规则

```
Prior 基于以下维度计算（加权平均）:

维度              权重   评分标准
─────────────────────────────────────────────────────────
文献支持度         0.35   已验证数量 / 总相关文献
效应一致性         0.25   支持 vs 反对文献的效应方向一致程度
方法质量           0.20   文献的平均方法学质量评分
样本规模           0.10   累计样本量的自然对数映射 (0-1)
时间新鲜度         0.10   5年内文献占比

Prior 分级:
  低 (0.0-0.3): 几乎无文献支持，或主要证据来自低质量研究
  中 (0.3-0.6): 有部分支持但存在矛盾或样本不足
  高 (0.6-1.0): 多项高质量研究一致支持
```

### 似然函数 P(E|H) 评分规则

```
Likelihood 基于以下证据源加权计算:

每个证据源 s 的强度 s_strength ∈ [0, 1]:
  - 效应量 (effect size): Cohen's d > 0.8 → 0.9, d > 0.5 → 0.7, d > 0.2 → 0.5
  - 统计显著性: p < 0.001 → 0.95, p < 0.01 → 0.85, p < 0.05 → 0.70, p > 0.05 → 0.20
  - 可复现性: 多研究复现 → 0.9, 单研究 → 0.5, 不可复现 → 0.1
  - 样本量: n > 500 → 0.9, n > 100 → 0.7, n > 30 → 0.5, n < 30 → 0.3

P(E|H) = Σ(w_s × s_strength) / Σ(w_s)

证据等级与权重:
  直接证据 (weight=3): 直接检验假设的实验/数据
  间接证据 (weight=2): 机制性支撑但非直接检验
  类比证据 (weight=1): 相似领域的间接支撑
```

### 后验概率 P(H|E) 计算

```
简化计算 (假设 E 为所有证据的集合):

P(H|E) = sigmoid(
  ln_prior + Σ_s (weight_s × ln_bf_s)
)

其中:
  ln_prior = ln(P(H) / (1 - P(H))) — log-odds 形式的先验
  ln_bf_s  = log(Bayes Factor) — 证据 s 的贝叶斯因子
  sigmoid(x) = 1 / (1 + exp(-x))

Bayes Factor 近似:
  BF ≈ exp(2 × Φ⁻¹(1 - p/2)²)  其中 p 为统计显著性 p-value
  Φ⁻¹ 为标准正态分布的分位数函数

Bayes Factor 解释 (Kass & Raftery, 1995):
  BF < 3     : 不支持 (barely worth mentioning)
  3 ≤ BF < 10: 中等支持 (substantial)
  10 ≤ BF < 30: 强支持 (strong)
  BF ≥ 30    : 非常强支持 (very strong)
```

### 敏感性分析

```
必须对 Prior 做敏感性分析:

vary_prior(P) = P(H|E) when Prior = P

输出:
  best_case:  vary_prior(0.9) = ?  (最优先验下的后验)
  worst_case: vary_prior(0.1) = ?  (最差先验下的后验)
  robust:     best_case - worst_case < 0.2 → 结果稳健
              best_case - worst_case >= 0.2 → 结果敏感，需谨慎

结论:
  robust AND posterior > 0.5 → 假设可信
  not robust AND posterior > 0.5 → 需要更多证据
  posterior < 0.5 → 假设不可信 (无论先验如何)
```

## 不合格标准

```
1. Prior 无文献支撑 → FAIL (不能凭空假设)
2. Likelihood < 0.5 且 Posterior < 0.5 → 假设不可信
3. Bayes Factor < 3 → 证据不足，需补充证据
4. 敏感性分析 not robust → 结论不可靠

必须检查:
- 每个概率值必须有 justification
- 必须包含敏感性分析
- 置信度上限为 0.95 (防止过度自信)
```

## 理论来源

- Jeffrey, R. C. (1961). *The Logic of Decision*. University of Chicago Press.
- Kass, R. E. & Raftery, A. E. (1995). "Bayes Factors". *Journal of the American Statistical Association*, 90(430), 773-795.
- Gelman, A., Carlin, J. B., Stern, H. S., Dunson, D. B., Vehtari, A., & Rubin, D. B. (2013). *Bayesian Data Analysis* (3rd ed.). CRC Press.
- Berger, J. O. (2013). *Statistical Decision Theory and Bayesian Analysis* (2nd ed.). Springer.
