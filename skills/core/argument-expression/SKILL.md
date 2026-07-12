---
name: argument-expression
category: core
signature: "argument-expression -> core: 将假设转化为结构化学术论证（论文章节+论据链），支持 Toulmin 模型、Hyland 修辞框架、IMRAD 验证。"
description: "将假设转化为结构化学术论证（论文章节+论据链），支持 Toulmin 模型、Hyland 修辞框架、IMRAD 验证。"
author: Synthos
license: MIT
version: 2.1.0
entrypoint_type: cognitive
entrypoint_cmd: "将假说展开为Toulmin结构化学术论证"
entrypoint_desc: "认知原子"
priority: P1
atom_type: cognitive-atom
allowed-tools: [terminal, read_file, write_file, session_search]
metadata:
  synthos:
    priority: P1
    atom_type: cognitive-atom
    description: "Academic argument construction from hypotheses — Toulmin model, Hyland rhetoric, IMRAD validation"
    signature: "claims: list[Claim], evidence: list[Evidence] -> argument_chain: ArgumentChain (structure, strengths, gaps, counterarguments)"
    related_skills: ['hypothesis-generation', 'viewpoint-verification', 'association-discovery']
---

# Argument Expression — 论证表达

> 将假设转化为结构化学术论证，确保每个论断有证据支撑、逻辑链完整。
> 立言必立据，立据必立源。言之无文，行而不远。
> 引经据典，层层递进。不破不立，不证不立。

## 原理层·文言

> **立言必立据，立据必立源。** 无据之言如无根之木，不推自倒。
>
> **三不原则：** 不自行发明论据（必须来自EXT/HYP）、不跳步（claim→evidence→inference→conclusion 四步不可缺）、不过度论证（只论证核心假设，不枝蔓）。
>
> **三步成文：** 一曰结构（Toulmin骨架），二曰修辞（Hyland润色），三曰验证（IMRAD检校）。

## 方法层·白话

论证表达是认知管道第 5 步（ACQ→EXT→ASC→HYP→**ARG**→VER）。
输入假设（HYP）+ 证据（EXT/ASC），输出结构化论据链 + 论文章节草案。

### 论证三引擎

| 引擎 | 用途 | 参考 |
|:-----|:-----|:-----|
| **Toulmin 模型** | 构建论据链骨架 | `references/toulmin-argument/` |
| **Hyland 修辞框架** | 选择学科适切的修辞策略 | `references/rhetoric-framework/` |
| **CARS 模型** | 构建引言叙事 | `references/cars-analysis/` |
| **IMRAD 验证** | 检查结构完整性 | `references/imrad-validator/` |
| **引用功能分类** | 标注引文的论证角色 | `references/citation-function-classifier/` |

---

## 触发条件

- HYP 产出可验证假设，需展开为论文论证
- VER 反馈了论证弱点，需补充论据或重新组织
- 用户要求"写论文/写引言/写讨论/构建论证"

---

## Step 1: 整理输入

从上游获取三类输入：

```bash
# 从 HYP 获取假设
cat outputs/{session}/hypotheses.json

# 从 EXT 获取证据
cat outputs/{session}/knowledge.json

# 从 ASC 获取关联信息
cat outputs/{session}/associations.json
```

### 输入检验清单
- [ ] 每个主张有至少1个直接证据引用
- [ ] 证据有 provenance（可追溯至原文位置）
- [ ] 假设有 falsifiability 标记（是否可以证伪）
- [ ] 关联有 confidence 评分

---

## Step 2: Toulmin 论据链

对每个核心主张构建完整的 Toulmin 六要素：

| 要素 | 定义 | 问题 | 示例 |
|:-----|:-----|:-----|:-----|
| **Claim (主张)** | 待论证的断言 | 要证明什么？ | "VOR增益随年龄下降" |
| **Data (数据)** | 支持主张的事实 | 基于什么？ | 50名受试者，20-80岁，r=-0.45,p<0.01 |
| **Warrant (理由)** | 从数据到主张的推理 | 数据如何支持主张？ | 年龄解释约20%的VOR增益变异 |
| **Backing (支撑)** | 理由的额外支持 | 理由本身可靠吗？ | 类似发现在3项独立研究中复现 |
| **Qualifier (限定)** | 主张的强度/范围 | 主张在什么条件下成立？ | 仅限水平VOR，旋转VOR未检验 |
| **Rebuttal (反驳)** | 例外条件 | 什么情况下主张不成立？ | 代偿性扫视可掩盖VOR增益下降 |

输出格式：
```json
{
  "claim_id": "arg-001",
  "claim": "VOR增益随年龄下降",
  "toulmin": {
    "data": "50名受试者(20-80岁), VOR增益r=-0.45,p<0.01 (Paper_A, Results §3.2)",
    "warrant": "年龄相关的前庭毛细胞丢失影响VOR弧",
    "backing": "Paper_B(2020), Paper_C(2022)独立复现",
    "qualifier": "仅限水平半规管VOR, 角速度<150°/s",
    "rebuttal": "代偿性扫视(compensatory saccade)可掩盖VOR增益测量值"
  },
  "evidence_refs": ["ext/001", "ext/003"],
  "provenance": "HYP-002 → ARG"
}
```

---

## Step 3: CARS 引言叙事

CARS（Create a Research Space）模型三步：

### Move 1: 建立研究领域
- **Claim 1A:** 该领域的中心地位/重要性（引用1-2篇权威综述）
- **Claim 1B:** 已有共识（引用该方向的代表性工作）

### Move 2: 确立研究缺口
- **Claim 2A:** 指出尚未解决的问题（引用ASC输出的gap）
- **Claim 2B:** 继续强调缺口的重要性（说明为什么需要解决）
- **Claim 2C:** 指出已有方法的局限（引用矛盾类关联）

### Move 3: 占据研究空间
- **Claim 3A:** 介绍本文方法/假设（"我们提出..."）
- **Claim 3B:** 说明方法的创新点（与已有工作的区别）
- **Claim 3C:** 预告主要发现和论文结构

---

## Step 4: Hyland 修辞框架

根据目标期刊/学科选择修辞策略：

| 学科文化 | 修辞策略 | 示例 |
|:---------|:---------|:-----|
| 硬科学（临床/生物学） | 直陈式，强调数据驱动 | "Data show...", "Results indicate..." |
| 软科学（方法论/综述） | 解释式，强调概念框架 | "We argue that...", "This framework suggests..." |
| 工程/计算 | 展示式，强调方法创新 | "We propose a novel...", "Our approach achieves..." |

**每个主张必须标注修辞策略**，确保学科一致性。

---

## Step 5: 引用功能分类

每篇引文标注在论证中的角色：

| 功能 | 说明 | 示例表达 |
|:-----|:-----|:---------|
| `support` | 支持本研究的假设/方法 | "As demonstrated by X (2023)..." |
| `contrast` | 对比/对照 | "In contrast to X (2022)..." |
| `gap` | 指出研究空白 | "However, X does not address..." |
| `method` | 方法引用 | "Following the protocol of X..." |
| `data_source` | 数据来源 | "Data from X (2021) database..." |
| `limitation` | 局限性 | "As noted by X (2020), this approach..." |

输出 `references/citation-function-classifier/` 下的完整分类。

---

## Step 6: IMRAD 结构验证

| 章节 | 必须包含 | 禁止包含 |
|:-----|:---------|:---------|
| **Introduction** | CARS三步骤清晰可辨 | 不出现方法细节、不出现结果 |
| **Methods** | 方法描述可复现 | 不出现结果讨论、不出现文献综述 |
| **Results** | 数据驱动，客观陈述 | 不出现解释、不出现与其他文献比较 |
| **Discussion** | 结果→文献→局限→展望 | 不出现新结果、不出现新方法 |

输出 `references/imrad-validator/` 下的I MRAD完整性检查报告。

---

## Step 7: 输出交付

```bash
mkdir -p outputs/{session}/
# 论据链JSON
python3 -c "import json; json.dump(arg_chain, open('outputs/{session}/arguments.json','w'), indent=2, ensure_ascii=False)"
# CARS引言草案
cat > outputs/{session}/introduction_draft.md << 'EOF'
... CARS 三步生成的引言 ...
EOF
# IMRAD验证报告
cat > outputs/{session}/imrad_report.md << 'EOF'
... IMRAD各节检查结果 ...
EOF
```

---

## 输入契约

| 字段 | 类型 | 必需 | 说明 |
|------|------|:----:|------|
| `claims` | list[Claim] | ✅ | 待论证的主张（HYP输出） |
| `evidence` | list[Evidence] | ✅ | 支持证据（EXT/ASC输出） |
| `context` | dict | ❌ | 论文类型、目标期刊、篇幅约束 |
| `mode` | string | ❌ | `full`（默认，含所有章节）或 `intro_only` |

## 输出契约

```json
{
  "meta": {
    "source_atoms": ["HYP-003", "EXT-001", "ASC-002"],
    "generated_at": "ISO时间戳",
    "mode": "full|intro_only"
  },
  "argument_chain": [
    {
      "claim_id": "arg-001",
      "claim": "...",
      "toulmin": {"data": "...", "warrant": "...", ...},
      "rhetoric_strategy": "data_driven|explanatory|demonstrative",
      "citation_functions": {"ref_doi": "support|contrast|gap|..."},
      "evidence_refs": ["ext/001"]
    }
  ],
  "sections": {
    "introduction": {"cars_moves": ["1A","1B","2A","2B","2C","3A","3B","3C"], "content": "..."},
    "methods": {"content": "..."},
    "results": {"content": "..."},
    "discussion": {"content": "..."}
  },
  "imrad_validation": {
    "passed": true,
    "issues": ["Discussion contains new results (line 47)"],
    "recommendations": ["Move lines 45-50 to Results section"]
  },
  "gaps": [],
  "counterarguments": [
    {"argument": "反驳内容", "response": "回应", "confidence": 0.7}
  ],
  "evidence_chain": [
    {"source_type": "atom_output", "source_ref": "hypothesis-generation", "note": "主张来源"},
    {"source_type": "atom_output", "source_ref": "knowledge-extraction", "note": "证据来源"}
  ]
}
```

---

## 陷阱（Pitfalls）

| # | 陷阱 | 正确做法 |
|:-:|:-----|:---------|
| 1 | **自造论据** — 论证中引入未在上游出现的证据 | 所有论据必须来自EXT/ASC，不可自行发明 |
| 2 | **跳步推理** — 从数据直接跳到结论，缺少 warrant | 必须完整四步：claim→evidence→warrant→conclusion |
| 3 | **过度论证** — 对非核心假设也展开完整Toulmin | 只论证核心假设（HYP标记为priority=H的） |
| 4 | **忽视反驳** — 论据链没有 rebuttal 要素 | 每条论据必须包含限定和反驳条件 |
| 5 | **单源依赖** — 所有论据来自同一篇论文 | 每个核心主张至少引用2篇独立来源 |
| 6 | **CARS错位** — 引言中混入方法/结果 | Move1-3严格分离，方法结果不进入引言 |
| 7 | **修辞不一致** — 同一篇论文在不同段落切换修辞策略 | 全篇统稿时统一修辞策略（数据驱动/解释/展示） |

---

## 验证清单

- [ ] 每个主张有完整Toulmin六要素（claim/data/warrant/backing/qualifier/rebuttal）
- [ ] 所有论据来自上游（EXT/HYP/ASC），无自造
- [ ] CARS三步骤在引言中清晰可辨
- [ ] 修辞策略全篇一致
- [ ] 每篇引文标注了论证功能
- [ ] IMRAD各节内容正确（无跨节内容）
- [ ] 包含反方观点及回应
- [ ] 已保存：arguments.json + introduction_draft.md + imrad_report.md

## 边界声明

- 本原子只做**论证构建**，不做假设生成（那是HYP）
- 不做观点验证（那是VER）
- 不做关联发现（那是ASC）
- 不自动写完整论文——输出是结构化论据链+章节草案，非最终稿件

## 相关文件

- `references/toulmin-argument/` — Toulmin论证模型完整参考
- `references/rhetoric-framework/` — Hyland学科修辞框架
- `references/cars-analysis/` — CARS引言模型
- `references/imrad-validator/` — IMRAD结构验证
- `references/citation-function-classifier/` — 引用功能分类体系
- `references/citation-chain/` — 引文链分析
- `references/gap-type-classifier/` — 研究空白分类
- `references/kuhn-lakatos/` — Kuhn/Lakatos科学哲学框架
- `references/litreview-quality-gate.md` — 文献综述质量门
- `references/quality-4d-gate/` — 四维质量闸门
- `references/BOUNDARY.md` — 边界声明
- `references/EVIDENCE_SCHEMA.md` — 证据链结构
- `references/IO_CONTRACT.md` — 输入输出契约
