---
name: association-discovery
category: core
signature: "association-discovery -> core: 跨论文识别知识关联（矛盾、补充、演进、空白），构建知识图谱。基于 Boden 创造力理论分类关联类型。"
description: "跨论文识别知识关联（矛盾、补充、演进、空白），构建知识图谱。基于 Boden 创造力理论分类关联类型。"
author: Synthos
license: MIT
version: 2.1.0
entrypoint_type: cognitive
entrypoint_cmd: "从知识条目中识别矛盾/补充/演进/空白四类关联"
entrypoint_desc: "认知原子"
priority: P1
atom_type: cognitive-atom
allowed-tools: [terminal, read_file, write_file, session_search]
metadata:
  synthos:
    priority: P1
    atom_type: cognitive-atom
    description: "Cross-paper association discovery — identify contradictions, complements, evolution, gaps. Boden creativity theory."
    signature: "knowledge_base: dict, query: str -> associations: list[Association] (type, strength, confidence, source)"
    related_skills: ['knowledge-extraction', 'hypothesis-generation', 'viewpoint-verification']
---

# Association Discovery — 关联发现

> 跨论文识别知识项之间的关联，输出结构化关联报告与研究空白。
> 万物互联，非孤立存在。知同知异，知缺知全。不执一端，不蔽于片。

## 原理层·文言

> **观其会通，明其异同。** 不观其通，则见木不见林。不明其异，则混为一谈。
>
> **七类关系：** 矛盾（Contradiction）、补充（Complement）、演进（Evolution）、
> 空白（Gap）、因果（Causation）、并行（Parallel）、依赖（Dependency）。
>
> **三不原则：** 不比无关项（知识不在同一粒度不比较）、不跨域自洽检查（那是VER的职责）、
> 不编造关联（无证据则标 confidence=0，不沉默忽略）。

## 方法层·白话

关联发现是认知管道第 3 步（ACQ → EXT → **ASC** → HYP → ARG → VER）。
输入多篇论文的 KnowledgeItem JSON（来自 EXT），输出结构化关联 + 研究空白。

### 核心流程

```
EXT的KnowledgeItem JSON
        ↓
  Step 1: 知识项对齐（归一化实体名/概念）
        ↓
  Step 2: 两两配对 → 检查7类关系
        ↓
  Step 3: 每对关系标注confidence(0-1) + 证据引用
        ↓
  Step 4: 按confidence排序，分组聚合
        ↓
  Step 5: 识别研究空白 → 标记为HYP输入
        ↓
  Step 6: 保存 outputs/{session}/associations.json
```

---

## 触发条件

- EXT 产出 ≥2 篇论文的 KnowledgeItem，需要发现跨论文关联
- 用户要求"找矛盾/找补充/找研究空白/写文献综述"
- 上游 `knowledge-extraction` 产出多篇知识，等待关联

---

## Step 1: 知识项对齐

不同论文对同一概念可能使用不同术语，必须先归一化：

```python
# 实体对齐策略：
# 1. 同义词映射（BPPV = benign paroxysmal positional vertigo = 良性阵发性位置性眩晕）
# 2. 缩写展开（VOR → vestibulo-ocular reflex）
# 3. 粒度匹配（"瞳孔直径" 与 "pupil diameter" 视为同一实体）
# 4. 层级归并（"眼震" 包含 "水平眼震"、"垂直眼震"、"旋转眼震"）
```

**对齐输出**：`entity_alias_map.json`，记录同组实体的别名 + 来源。

---

## Step 2: 七类关系检查

每一对知识项按以下7类逐一检查，不可跳过：

### 1. 矛盾（Contradiction）

同一问题的不同论文得出相悖结论。

| 条件 | confidence |
|:-----|:----------:|
| 明确统计矛盾（如 p<0.05 对 p>0.05，同一指标） | 0.8-1.0 |
| 趋势矛盾（A论文说上升，B论文说下降，但无统计对比） | 0.5-0.7 |
| 隐含矛盾（A的假设前提与B的发现不一致） | 0.3-0.5 |

输出格式：
```json
{
  "type": "contradiction",
  "item_a": {"knowledge_id": "ext/001", "paper": "doi:10.xxx1"},
  "item_b": {"knowledge_id": "ext/003", "paper": "doi:10.xxx2"},
  "aspect": "VOR增益与年龄的相关性方向",
  "claim_a": "VOR增益随年龄下降(p<0.01)",
  "claim_b": "VOR增益随年龄增加(p<0.05)",
  "confidence": 0.85,
  "evidence": "item_a claims[0] vs item_b claims[1]: 相反的相关性方向",
  "resolvable": true
}
```

### 2. 补充（Complement）

不同论文从不同角度研究同一问题，结论可互补。

| 条件 | confidence |
|:-----|:----------:|
| 同一系统，不同环节（如输入侧 vs 输出侧） | 0.7-1.0 |
| 同一问题，不同方法（如 ODE 建模 vs PINN 拟合） | 0.5-0.7 |
| 同一领域，不同人群（如成人 vs 儿童数据） | 0.4-0.6 |

### 3. 演进（Evolution）

后一篇论文在前一篇的基础上推进。

- A 提出了方法 → B 改进了该方法
- A 发现了现象 → B 解释了该现象
- A 做了横断面 → B 做了纵向

**判断标准**：B 论文引用了 A 论文，并且在 A 的基础上有明确的增量贡献。

### 4. 空白（Gap）

某方向有充足的知识，但关键环节缺失。

| 类型 | 说明 | 示例 |
|:-----|:-----|:-----|
| `方法空白` | 有模型无数据验证 | 多个ODE模型提出但无人实测 |
| `人群空白` | 只研究了某个亚群 | 只有成人数据，无儿童/老人 |
| `机制空白` | 发现现象但无机制解释 | 观察到了某种眼震但原因不明 |
| `方法学空白` | 有临床需求无定量工具 | BPPV诊断靠主观判断，无定量方法 |

**空白必须标注"为什么是空白"的具体证据**（哪些论文覆盖了什么，缺什么）。

### 5. 因果（Causation）

A论文的发现可能是B论文发现的原因或结果。

- A 发现前庭功能下降 → B 发现平衡能力下降 → 因果关系
- A 发现眼震模式 → B 发现特定半规管阻塞 → 因果关系

### 6. 并行（Parallel）

两篇论文同时独立研究了同一问题，结论一致或互补。

**判断标准**：未互相引用，但研究问题和方法高度相似，时间接近。

### 7. 依赖（Dependency）

A论文的方法/数据是B论文方法的前提或基础。

**判断标准**：B 方法明确需要 A 的输出作为输入，或 B 的数据集包含 A 的方法产出。

---

## Step 3: Confidence 评分

每对关联标注 0-1 的置信度：

| 分数 | 含义 | 证据要求 |
|:----:|:-----|:---------|
| 0.8-1.0 | 高置信度 | 有明确的统计/引用/数据支撑 |
| 0.5-0.7 | 中置信度 | 有趋势或逻辑支撑，但无直接统计 |
| 0.2-0.4 | 低置信度 | 有暗示但证据不足（仍输出，标记为"需验证"） |
| 0.0-0.1 | 推测 | 无明显证据，仅基于逻辑推理 |

**纪律**：低 confidence 关联不跳过——它们常常是创新发现的来源。

---

## Step 4: 跨领域关联

> 不要只找同领域关联。跨领域关联更有价值。

强制检查 **3类跨域关联**：
1. **方法迁移** — 领域 A 的方法能否用于领域 B 的问题（如 PINN 从力学→眼动）
2. **现象类比** — 领域 A 的已知现象是否在领域 B 有类似表现
3. **数据复用** — 领域 A 的数据集是否可用于回答领域 B 的问题

---

## Step 5: 研究空白 → HYP 输入

将识别到的研究空白标记为 `gap` 类型，包含：
- `gap_statement`: 一句话描述空白
- `evidence`: 为什么判定为空白（哪些论文覆盖了什么，缺什么）
- `filled_by?:` 可能的填补方向（输出给 HYP 作为起点）
- `priority`: H/M/L 优先级

保存至 `outputs/{session}/gaps.json`，作为 HYP 的输入。

---

## 输入契约

| 字段 | 类型 | 必需 | 默认 | 说明 |
|------|------|:----:|------|------|
| `knowledge_base` | list[KnowledgeItem] | ✅ | — | 多篇论文的结构化知识（EXT输出） |
| `query` | str | ❌ | 全量 | 分析焦点（缩小关联范围） |
| `min_confidence` | float | ❌ | 0.0 | 最低confidence过滤 |
| `cross_domain` | bool | ❌ | true | 是否检查跨领域关联 |

## 输出契约

```json
{
  "meta": {
    "source_count": 5,
    "pair_count": 10,
    "analyzed_at": "ISO时间戳"
  },
  "associations": [
    {
      "id": "asc-001",
      "type": "contradiction|complement|evolution|gap|causation|parallel|dependency",
      "sources": ["ext/001", "ext/003"],
      "papers": [{"doi": "10.xxx1"}, {"doi": "10.xxx2"}],
      "aspect": "关联的具体方面",
      "confidence": 0.85,
      "evidence": "证据引用",
      "resolvable": true,
      "cross_domain": false
    }
  ],
  "gaps": [
    {
      "gap_statement": "...",
      "evidence": "...",
      "filled_by": "可能填补方向",
      "priority": "H|M|L",
      "related_papers": ["doi:xxx", "doi:yyy"]
    }
  ],
  "summary": {
    "total_associations": 10,
    "by_type": {"contradiction": 2, "complement": 3, ...},
    "high_confidence": 5,
    "gaps_found": 3
  },
  "evidence_chain": [
    {"source_type": "atom_output", "source_ref": "extracted_knowledge", "note": "引用 KnowledgeItem.id=ext/001, ext/003"}
  ]
}
```

---

## 陷阱（Pitfalls）

| # | 陷阱 | 正确做法 |
|:-:|:-----|:---------|
| 1 | **跳过低 confidence 关联** — 只报告高置信度，丢弃低分关联 | 低分关联往往是创新发现的前兆——输出但标记"需验证" |
| 2 | **只找同领域关联** — 只比较相同方向的论文 | 强制检查方法迁移/现象类比/数据复用三类跨域关联 |
| 3 | **跳过7类关系中的某些类** — 只检查矛盾/补充/演进 | 7类必须全部检查，用 checklist 确保无遗漏 |
| 4 | **关联无双向引用** — 只记录 A→B 不记录 B→A | 每条关联必须有双向引用，否则不对称信息丢失 |
| 5 | **空白无证据** — 说"存在空白"但不说明为何是空白 | 空白必须标注：哪些论文覆盖了X、缺了什么Y |
| 6 | **实体未对齐直接比较** — "瞳孔" vs "pupil" 直接比较 | 必须先归一化实体名（同义词/缩写/层级） |
| 7 | **忽略论文本身的局限性** — 未利用 EXT 提取的局限性信息 | 局限性是发现空白最有价值的输入之一 |

---

## 验证清单

- [ ] 7类关系均已检查（contradiction/complement/evolution/gap/causation/parallel/dependency）
- [ ] 实体已对齐：同义词/缩写/层级归一化
- [ ] 跨领域关联已检查（方法迁移/现象类比/数据复用）
- [ ] 每条关联有双向引用（不丢失信息）
- [ ] 每条关联有 confidence 评分（0-1）
- [ ] 研究空白有具体证据（为什么是空白）
- [ ] 按 confidence 排序输出
- [ ] 低 confidence 关联已保留（标记为"需验证"）
- [ ] 已保存：associations.json + gaps.json
- [ ] 空白已标记为 HYP 输入

## 边界声明

- 本原子只做 **跨论文** 关联发现，不做单论文提取（那是 EXT）
- 不做假设生成（那是 HYP）
- 不做观点验证（那是 VER）
- 不评估关联的价值/可靠性（那是 VER 在需要时的扩展职责）
- PW-Bench 逆向工程不在本原子范围内

## 相关文件

- `references/BOUNDARY.md` — 边界声明
- `references/EVIDENCE_SCHEMA.md` — 证据链结构
- `references/IO_CONTRACT.md` — 输入输出契约
- `references/boden-creativity/` — Boden 创造力理论参考
- `references/CHANGE_LOG.md` — 变更记录
