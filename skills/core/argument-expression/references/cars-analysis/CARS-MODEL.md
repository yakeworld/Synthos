# CARS 模型分析器

> 理论来源：John Swales (1990) "Genre Analysis"; Swales (2004) "Research Genres"

## CARS 模型定义

CARS (Create a Research Space) 是 Swales 提出的学术论文 Introduction 结构的理论模型。它定义了学术写作的三个核心步骤：

```
Move 1: Establish a territory    → 建立研究领域
    ├─ 1a. 宣布领域重要性
    └─ 1b. 综述前人研究（提供背景）

Move 2: Establish a niche       → 定位研究空白
    ├─ 2a. 指出空白/局限
    ├─ 2b. 提出问题
    └─ 2c. 否定前人或提出反面证据

Move 3: Occupy the niche        → 占领研究空白
    ├─ 3a. 概述本文目的
    ├─ 3b. 列举本文贡献
    └─ 3c. 概述论文结构
```

## 自动化分析规则

### Move 1 检测规则

**必须包含**：
1. 领域重要性声明（至少 1 个陈述）
2. 前人研究的引用（至少 3 篇，不同来源）
3. 领域范围的明确定义

**检测模式**：
- 重要性关键词："important", "critical", "essential", "significant"
- 引用模式："(Author, Year)", "Author (Year) showed"
- 范围模式："in the field of", "in recent years", "a growing body of research"

### Move 2 检测规则

**必须包含**：
1. 转折词/标记词（至少 1 个）
2. 明确的空白描述（不能是"许多研究尚未"）
3. 空白的具体定位（谁没做什么）

**检测模式**：
- 转折词："However", "Although", "Yet", "Despite", "Nevertheless"
- 空白标记："remains unclear", "has not been studied", "little attention", 
  "No study has", "few studies have examined", "limited research on"
- 空白类型：方法/理论/实证/应用（必须明确）

**不合格**：无转折词 → Move 2 失败
**不合格**：空白描述模糊 → Move 2 扣分
**不合格**：仅描述无批判 → Move 2 扣分

### Move 3 检测规则

**必须包含**：
1. 本文目的声明（至少 1 个）
2. 与 Move 2 空白的直接对应
3. 方法简述

**检测模式**：
- 目的标记："This paper proposes", "In this study, we", "we aim to",
  "Our goal is", "This research investigates"
- 对应标记："addresses", "overcomes", "fills", "responds to"

## 输出格式

```json
{
  "cars_analysis": {
    "move1": {
      "complete": true,
      "score": 24,
      "max": 30,
      "key_papers_cited": ["Author1", "Author2", "Author3"],
      "importance_statement": true,
      "literature_review": true
    },
    "move2": {
      "complete": true,
      "score": 32,
      "max": 40,
      "gap_type": "A2",
      "gap_description": "No study has applied method X to domain Y",
      "transition_words": ["However"],
      "specificity": "high",
      "falsifiable": true
    },
    "move3": {
      "complete": true,
      "score": 27,
      "max": 30,
      "objective_statement": "This paper proposes...",
      "corresponds_to_gap": true,
      "method_overview": "brief"
    },
    "total_score": 83,
    "total_max": 100,
    "result": "pass"
  }
}
```
