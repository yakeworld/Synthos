# Kuhn 范式评估 + Lakatos 研究纲领方法论

> 理论来源：Kuhn (1962) "The Structure of Scientific Revolutions"; Lakatos (1970) "Falsification and the Methodology of Scientific Research Programmes"

## Kuhn 范式评估

Kuhn 描述了科学发展的模式：常规科学 → 反常积累 → 危机 → 范式革命 → 新的常规科学。

### 范式状态评估

```
评估维度                    检查项                          评分
────────────────────────────────────────────────────────────────
当前领域共识度              主流方法/理论的一致性            0-1
反常现象数量               与现有理论矛盾的发现数量         0-1
危机严重程度               共识是否破裂                    0-1
替代方案的成熟度           是否有可行的替代理论            0-1
```

### 范式转换判定

```
Normal Science (常规科学):
  - 范式共识度 > 0.7
  - 反常现象 < 20%
  - 危机严重程度 < 0.3
  → 本假设在现有范式内工作

Paradigm Shift (范式转换):
  - 范式共识度 < 0.5
  - 反常现象 > 40%
  - 危机严重程度 > 0.6
  → 本假设挑战现有范式

处于过渡期:
  - 不满足上述任一条件
  → 需要更多证据判断
```

## Lakatos 研究纲领方法论

Lakatos 将科学理论组织为"研究纲领"，由 Hard Core (不可动摇的核心) 和 Protective Belt (可调整的辅助假设) 组成。

### 研究纲领识别

```
Hard Core (核心假设):
  - 不可妥协的基本原理
  - 例: "疾病由病原体引起" (医学)
  - 例: "物理规律在所有参考系中一致" (物理)

Protective Belt (辅助假设):
  - 可调整的细节
  - 例: 具体病原体识别
  - 例: 测量仪器的校准参数

Heuristics (启发式):
  - Positive Heuristic: 指导研究者如何扩展理论
  - Negative Heuristic: 保护 Hard Core 不被直接证伪
```

### 研究纲领健康度评估

```
Progressive Research Programme (进步型):
  - 预测新的可检验现象 ✓
  - 解释已有反常 ✓
  - 辅助假设有解释力 ✓
  - 新预测被验证 ✓
  → 健康: 评分 > 0.7

Declining Research Programme (衰退型):
  - 仅事后解释无反预测 ✗
  - 反常积累 ✗
  - 辅助假设特设化 (ad hoc) ✗
  - 新预测被证伪 ✗
  → 衰退: 评分 < 0.4

处于平衡:
  - 混合特征
  → 评分 0.4-0.7
```

### 健康度评分

```
评分维度:
  - 新预测能力        0-1 (能预测新现象? 权重 0.3)
  - 反常处理能力      0-1 (有效解释反常? 权重 0.25)
  - 辅助假设质量      0-1 (解释力 vs 特设性? 权重 0.25)
  - 经验验证          0-1 (新预测被验证比例? 权重 0.2)

health = Σ(weight_i × score_i)

verdict:
  health ≥ 0.7:   PROGRESSIVE (进步型 — 值得投入)
  0.4 ≤ health < 0.7:  MIXED (混合 — 谨慎)
  health < 0.4:   DECLINING (衰退型 — 避免)
```

## 与 Boden 创造力分类的关联

```
Boden Combinatorial  → 通常在 Normal Science 框架内
Boden Exploratory    → 可能在 Paradigm Shift 边缘
Boden Transformational → 对应 Paradigm Shift

本模块提供:
  - Kuhn: 判断假设是常规科学还是范式转换
  - Lakatos: 判断研究纲领是进步还是衰退
  - 组合 Boden: 形成完整的创新度评估
```

## 不合格标准

```
1. 声称 "Paradigm Shift" 但 Kuhn 评估显示领域共识度高 → WARNING
2. 研究纲领 health < 0.4 仍建议采用 → FAIL (避免投入衰退领域)
3. 无识别 Hard Core → WARNING
4. 辅助假设过度特设化 (ad hoc) → WARNING
```

## 理论来源

- Kuhn, T. S. (1962). *The Structure of Scientific Revolutions*. University of Chicago Press.
- Kuhn, T. S. (1970). "Postface to the 1970 edition." in *The Structure of Scientific Revolutions* (2nd ed.).
- Lakatos, I. (1970). "Falsification and the Methodology of Scientific Research Programmes." in Lakatos & Musgrave (eds.), *Criticism and the Growth of Knowledge*.
- Lakatos, I. (1978). *The Methodology of Scientific Research Programmes*. Cambridge University Press.
