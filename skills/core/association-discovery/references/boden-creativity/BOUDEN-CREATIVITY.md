# Boden 创造力分类器

> 理论来源：Boden, M. A. (1991). "The Creative Mind: Myths and Mechanisms". MIT Press.

## Boden 创造力三分类

Boden 提出创造力的三个基本类型。每个研究空白/假设按其创新程度分类：

### 类型 A: 组合创新 (Combinatorial Creativity)

```
定义: 将已有概念/方法/领域以新的方式组合在一起。
空间: 已有概念空间内的新组合。

特征:
- 所有组成元素都是已知的
- 组合方式是新的
- 创新来自"连接"而非"发明"

示例:
- 用机器学习方法分析传统 BPPV 数据
- 将眼动追踪从心理学扩展到神经病学

创新度: 中 (3.0/5.0)
```

### 类型 B: 探索创新 (Exploratory Creativity)

```
定义: 在已有概念空间内，通过探索边界发现新的可能性。
空间: 扩展已有空间的边界。

特征:
- 探索空间中新区域 (之前未被探索的)
- 空间本身不变，但内容扩展
- 需要系统地遍历空间

示例:
- 在已有 VOR 模型基础上扩展到 3D 空间
- 将已有算法在更多人群/条件上验证

创新度: 高 (4.0/5.0)
```

### 类型 C: 转换创新 (Transformational Creativity)

```
定义: 改变概念空间本身的规则/结构/约束。
空间: 空间本身的 transformation。

特征:
- 不是空间内的新发现，而是空间的重构
- 旧空间中的"不可能"变为"可能"
- 最罕见也最具突破性

示例:
- 从"眼动是结果"到"眼动是信号" (范式反转)
- 从"临床诊断靠经验"到"临床诊断靠算法" (方法论重构)
- 从"单一模态"到"多模态融合" (框架重构)

创新度: 极高 (5.0/5.0)
```

## 自动化分类规则

```
分类步骤:

1. 检查是否改变了已有框架的约束/规则 → 是则 Transformational
2. 检查是否扩展到已知空间的新区域 → 是则 Exploratory
3. 检查是否为已有元素的新组合 → 是则 Combinatorial

分类依据:
- 元素新? (所有元素已知 → Combinatorial)
- 空间新? (在新空间 → Transformational)
- 组合新? (新组合 → Exploratory 或 Combinatorial)
- 约束变化? (约束改变 → Transformational)
```

## 创新度评分

```
combinatorial:   novelty = 3.0 (中)
exploratory:     novelty = 4.0 (高)
transformational: novelty = 5.0 (极高)

影响:
- novelty_score 作为 hypothesis-generation 的输入
- 不同创新度对应不同期刊目标:
  - Combinatorial → Q2-Q3 (专业期刊)
  - Exploratory   → Q1-Q2 (领域顶刊)
  - Transformational → T1 (Nature/Science/Cell 子刊)
```

## 不合格标准

```
1. 无法分类 → WARNING (需要更多领域知识)
2. 声称 "Transformational" 但实际为 Combinatorial → WARNING (过度宣称)
3. 所有提出的假设都是 Combinatorial → INFO (创新度偏低，建议探索更高创新)
```

## 理论来源

- Boden, M. A. (1991). "The Creative Mind: Myths and Mechanisms". MIT Press.
- Boden, M. A. (2004). "The creative process: A topographical review." *The Journal of Creative Behavior*, 38(2), 85-94.
