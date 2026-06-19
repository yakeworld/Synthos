# EVIDENCE_SCHEMA.md — Research Gap Type Classifier

> 对应原则：P0（证据可溯性）
> 理论来源：Blessing & Chakraborti (2003) "Reductive Design" gap types; Krippendorff (2018) "Semantic Shifts in Research"

## 研究空白分类体系（4 类 12 子类）

每一处 identified gap 必须属于以下类别之一。空白分类的**精确度**直接影响后续假设生成的质量。

### 类型 A：方法空白（Methodological Gap）

空白特征：已有研究使用了不合适的方法，或新方法未被应用到该领域。

| 子类 | 说明 | 关键词 |
|------|------|--------|
| A1. 方法不适用 | 已有方法不适合当前研究问题 | "not suitable for", "inadequate for" |
| A2. 新方法未应用 | 已有方法未应用于该领域 | "has not been applied to", "has never been used" |
| A3. 方法对比缺失 | 不同方法的比较研究缺失 | "no comparative study", "unclear whether" |

### 类型 B：理论空白（Theoretical Gap）

空白特征：已有研究发现无法用现有理论解释，或新现象未被理论覆盖。

| 子类 | 说明 | 关键词 |
|------|------|--------|
| B1. 理论不适用 | 现有理论无法解释新发现 | "challenges existing theory", "inconsistent with" |
| B2. 理论缺失 | 新现象无理论框架 | "no theoretical framework exists", "theoretical explanation lacking" |
| B3. 理论冲突 | 不同理论的矛盾无法调和 | "conflicting theories", "contradictory findings" |

### 类型 C：实证空白（Empirical Gap）

空白特征：已有研究缺少实证证据，或实证结果不一致。

| 子类 | 说明 | 关键词 |
|------|------|--------|
| C1. 数据缺失 | 缺少必要的数据 | "data is lacking", "no empirical evidence" |
| C2. 结果不一致 | 已有研究发现相互矛盾 | "conflicting results", "inconsistent findings" |
| C3. 样本局限 | 已有研究样本代表性不足 | "limited to", "only in Western contexts", "small sample" |

### 类型 D：应用空白（Application Gap）

空白特征：理论/方法未在实际场景验证，或新场景未被探索。

| 子类 | 说明 | 关键词 |
|------|------|--------|
| D1. 场景迁移 | 理论/方法未迁移到新场景 | "has not been tested in", "remains unexplored in" |
| D2. 实践差距 | 理论与实践之间存在差距 | "practice remains", "implementation challenges" |
| D3. 跨域整合 | 不同领域的知识未整合 | "few studies integrate", "limited cross-domain" |

## 空白的优先级矩阵

| 类型 | 创新性潜力 | 可行性 | 优先级 |
|------|-----------|--------|--------|
| A（方法） | 高 | 中 | **高** |
| B（理论） | 极高 | 低 | **高** |
| C（实证） | 中 | 高 | **中** |
| D（应用） | 低 | 极高 | **中** |

## 传递规则

每个 Gap 的 evidence 标注其类型和子类：
```json
{"source_type": "gap_classification", "source_ref": "literature_analysis", "note": "gap_id=001, type=A, subtype=A2, priority=high, confidence=0.85"}
```
