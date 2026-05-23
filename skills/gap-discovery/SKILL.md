---
name: gap-discovery
description: "[⚠️ ABSORBED into association-discovery v1.1.0] 研究空白发现功能已合并至ASC原子。本原子保留为引用参考。"
version: 1.0.0
author: Synthos Agent
license: MIT
status: absorbed
allowed-tools: Read Write
metadata:
  synthos_atom_type: "cognitive"
  synthos_version: "1.0.0"
  synthos_depends_on: "association-discovery"
  synthos_author: "Synthos Agent"
  synthos_data_access_level: "redacted"
---

## 原理层·文言

『空白之道，见所未见。检测四类矛盾，识别五型缺口。有缺则有向，有向则有问。』

> 研究空白即是方向。发现文献间的矛盾之处，识别方法论上的系统性缺口——有了缺口就有了方向，有了方向就有了可检验的科学问题。

## 方法层·白话

本技能已合并入 association-discovery（v1.1.0），此处保留为独立入口引用。核心逻辑：

1. **文献聚类**：将文献按主题/方法/结论聚类，每簇至少2篇
2. **矛盾检测**：检测四类矛盾——结论矛盾、方法矛盾、假设矛盾、时间矛盾
3. **缺口识别**：识别五型缺口——样本缺口、技术缺口、纵向缺口、机制缺口、验证缺口
4. **未答问题提取**：从文献的"未来工作"和"局限性"部分提取显式/隐式问题
5. **空白评级**：按重要性(P0-P3)、时效性、可行性、证据基础四维度评级

关键约束：
- 输入<5篇文献直接返回 insufficient_literature 错误
- 每个空白至少需要2篇文献引用支撑
- 每个空白必须附带 falsification_condition（可证伪条件）
- 与existing_gaps对比，不返回重复空白

# GAP — 研究空白发现原子

## 触发条件

本原子已合并入 association-discovery（§4 空白发现）。在以下情况加载：

- 作为独立入口，仅需空白检测，不需要完整关联链路
- 用户明确要求"找研究空白/知识缺口"
- 引用 association-discovery 的空白发现方法时

## 验证清单

- [ ] 空白按 P0-P3 评级
- [ ] 每个空白附带 falsification_condition（可证伪条件）
- [ ] 空白有明确的文献引用支撑
- [ ] 功能与 association-discovery §4 一致

## 功能

GAP原子接收ACQ检索的文献集合，通过系统性分析提取三个维度的研究空白：

```
ACQ文献 ──→ GAP分析 ──→ 空白列表
                      ├── 文献矛盾 (contradiction)
                      ├── 方法论缺口 (methodology_gap)
                      ├── 未答问题 (unanswered_question)
                      └── 过时结论 (outdated_conclusion)
```

## 执行流程

### Step 1: 文献聚类

将输入文献按主题/方法/结论聚类：
- 每个聚类至少2篇文献
- 聚类间有明确的边界定义
- 记录聚类依据

### Step 2: 矛盾检测

对每个聚类内部和跨聚类检测矛盾：

| 矛盾类型 | 检测条件 | 示例 |
|:---------|:---------|:-----|
| **结论矛盾** | A报告正向结果，B报告负向结果 | 药物A有效 vs 无效 |
| **方法矛盾** | 相似方法得出不同结论 | 样本量/人群差异 |
| **假设矛盾** | 不同的底层假设导致冲突 | 机制解释不同 |
| **时间矛盾** | 早期结论被后期证据推翻 | 2020 vs 2025结论 |

### Step 3: 缺口识别

检测方法论层面的系统性缺口：

- **样本缺口**：所有研究集中在特定人群（如汉族），缺少其他人群
- **技术缺口**：现有方法无法测量关键变量
- **纵向缺口**：只有横断面研究，缺少纵向追踪
- **机制缺口**：观察到现象但机制不明
- **验证缺口**：模型/算法未在独立数据集验证

### Step 4: 未答问题提取

从文献的"未来工作"、"局限性"部分提取显式和隐式问题：

- **显式**：作者明确说"需要进一步研究..."
- **隐式**：从局限性推断出的延伸问题

### Step 5: 空白评级

每个空白按以下维度评级：

| 维度 | P0 | P1 | P2 | P3 |
|:-----|:---|:---|:---|:---|
| 重要性 | 影响领域核心范式 | 影响重要子领域 | 有价值但非核心 | 边缘增量 |
| 时效性 | 亟需解决 | 1-2年内 | 2-5年 | 长期 |
| 可行性 | 现有技术可解 | 需适度努力 | 需重大突破 | 理论尚不成熟 |
| 证据基础 | ≥5篇矛盾文献 | 3-4篇 | 1-2篇 | 单篇或推测 |

## Schema: gap_record

```yaml
gap_record:
  id: "GAP-YYYYMMDD-N"
  title: string               # 空白的简洁标题
  description: string         # 详细描述
  type: enum[contradiction, methodology_gap, unanswered_question, outdated_conclusion]
  priority: enum[P0, P1, P2, P3]
  
  # 来源定位
  source_refs:                # 至少2篇文献
    - doi: string
      claim: string           # 该文献的主张
      lines: string           # 来源位置
  contradiction_ref: string   # 矛盾的另一方（矛盾类型时）
  
  # 可检验性
  falsification_condition: string  # "如果X成立，则此空白不存在"
  
  # 元数据
  discovered_by: string       # "ACQ/GAP pipeline"
  discovered_at: timestamp
  stability: enum[proposal, validated, accepted]
  
  # 关联
  related_gaps: string[]      # 关联空白ID
  related_hypotheses: string[] # 由此引发的假说ID（由HYP原子填充）
```

## Schema: contradiction_map

```yaml
contradiction_map:
  nodes:
    - id: string
      doi: string
      title: string
      conclusion_summary: string
  edges:
    - source: string          # 节点ID
      target: string
      type: enum[conclusion, method, assumption, temporal]
      strength: enum[strong, moderate, weak]
      description: string
```

## 验证标准

| 测试 | 通过条件 |
|:-----|:---------|
| 输入<5篇文献 | 返回 insufficient_literature 错误 |
| 输入5-10篇文献 | 至少发现1个合理空白 |
| 输入>10篇文献 | 空白分类覆盖≥3种类型 |
| 每个空白 | 至少有2篇文献引用 |
| 重复检测 | 与existing_gaps对比，不返回重复 |

## 与HYP原子的接口

GAP的输出直接输入到HYP原子：

```
GAP.gaps[] → HYP (空白→假说生成)
     ↓                      ↓
 空白库（Notion/NotebookLM）  假说库（Notion/NotebookLM）
```

## 错误处理

| 错误 | 处理 |
|:-----|:-----|
| ACQ返回空列表 | 触发ACQ重试，附带更宽检索词 |
| 所有文献同质无矛盾 | 输出 "no contradictions found" + 方法论缺口分析 |
| 焦点过宽 | 提示用户缩小范围，重新聚类 |

## 命令层·English

### Signature
```
signature: "literature_set: list[dict] -> gaps: list[dict], contradiction_map: dict"
```

### Allowed Tools
- `Read` — read ACQ (knowledge-acquisition) output, prior gap records
- `Write` — write gap records and contradiction maps to output files

### Input Format
```json
{
  "literature_set": [
    {
      "doi": "string",
      "title": "string",
      "abstract": "string",
      "conclusions": "string",
      "methods": "string",
      "limitations": ["string"],
      "future_work": ["string"],
      "year": "int"
    }
  ],
  "existing_gaps": ["GAP-IDs to exclude from duplicate detection"],
  "min_cluster_size": "int (default: 2)"
}
```

### Output Format
```json
{
  "gaps": [
    {
      "id": "GAP-YYYYMMDD-N",
      "title": "string",
      "description": "string",
      "type": "contradiction|methodology_gap|unanswered_question|outdated_conclusion",
      "priority": "P0|P1|P2|P3",
      "source_refs": [
        {"doi": "string", "claim": "string", "lines": "string"}
      ],
      "falsification_condition": "string",
      "stability": "proposal|validated|accepted"
    }
  ],
  "contradiction_map": {
    "nodes": [{"id": "string", "doi": "string", "title": "string", "conclusion_summary": "string"}],
    "edges": [{"source": "string", "target": "string", "type": "string", "strength": "string", "description": "string"}]
  },
  "clusters": [
    {"name": "string", "papers": ["doi list"], "basis": "string"}
  ]
}
```

### Error Handling
| Condition | Action |
|:----------|:-------|
| <5 papers in input | Return error: insufficient_literature, minimum 5 papers required |
| All papers homogeneous, no contradictions | Return "no_contradictions_found" + methodology gap analysis |
| Focus too broad (too many clusters) | Prompt user to narrow scope, re-cluster |
| ACQ returns empty list | Trigger ACQ retry with broader search terms |
