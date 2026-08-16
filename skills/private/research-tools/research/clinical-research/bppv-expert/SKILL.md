---
name: bppv-expert
description: 1. 确认输入参数完整
signature: 'bppv-expert -> clinical-research: synthetic skill for bppv expert'
allowed-tools:
- terminal
- read_file
- write_file
- session_search
version: 1.0.0
license: MIT
metadata:
  synthos:
    atom_type: mechanical
    description: 1. 确认输入参数完整
    signature: 'bppv-expert -> clinical-research: synthetic skill for bppv expert'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
category: research-tools
author: Synthos
---


## Operational Steps
1. 确认输入参数完整
2. 执行核心操作（参考本目录下的 scripts/ 或 references/）
3. 验证输出符合契约
4. 保存结果并报告

## Pitfalls
- 
- 

## Verification
- 
- 
- 
- 
1. 
2. 
3. 

## IO_CONTRACT

- **input**: `patient_data: dict, symptoms: str` — 用户请求描述、上下文信息
- **output**: `treatment_plan: dict — BPPV专家系统`

> 对应原则：P2（机械原子暴露输入输出规范）

# BPPV Expert — Extended Skill for Synthos

## 原理层·文言

『眩晕之道，定位为先。BPPV虽常见，误诊亦频。手法复位，精准则效。复位手法有七，辨认路径有图。』

## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[BPPV-001]** 当需要确定受累半规管时 → 根据眼震方向与模式（如后规管为上跳+扭转，水平规管为水平，前规管为下跳+扭转）精准识别解剖位置
- **[BPPV-002]** 当选择诊断试验时 → 依据怀疑的半规管类型匹配特定检查（后/前规管用 Dix-Hallpike，水平规管用仰卧翻滚试验）
- **[BPPV-003]** 当区分病理机制时 → 基于眼震持续时间特征区分管石症（短暂）与壶腹嵴顶结石症（持续）
- **[BPPV-004]** 当描述复位手法时 → 必须完整包含患者体位、头转方向/角度、操作时机及预期眼震反应四个核心要素
- **[BPPV-005]** 当提供临床建议时 → 严格标注“仅作教育用途，临床决策需面诊评估”的医学警告以规避医疗风险
- **[BPPV-006]** 当输出任何医学论断时 → 引用具体的 AKNE wiki 页面来源以确保证据链的可追溯性与准确性
- **[BPPV-007]** 当设计或验证新手法时 → 利用 3D 生物力学模拟预测耳石运动路径及管石转换机制，以指导临床前的手法优化

## 方法层·白话

## 触发条件

在以下情况加载本技能：

- 用户询问 BPPV 诊断、治疗或耳石复位操作
- 用户需要根据眼震模式判断受累半规管（后/水平/前半规管）
- 用户需要 BPPV 三维生物力学模拟指导
- 用户询问半规管和耳石器解剖知识
- 用户需要进行位置性眩晕的鉴别诊断
- 患者表现包括：特定头位诱发的短暂眩晕、位置性眼震、恶心/呕吐

## 验证清单

运行本技能后，确认以下检查项：

- [ ] 已根据眼震方向/模式正确识别受累半规管
- [ ] 推荐的诊断试验（Dix-Hallpike/仰卧翻滚试验/俯屈仰头试验）与怀疑的半规管匹配
- [ ] 复位手法（Epley/Gufoni/Semont/Barbecue/roll-over）包含患者体位、头转方向/角度、时机和预期眼震反应
- [ ] 已区分管石症 vs 壶腹嵴顶结石症（基于眼震持续时间）
- [ ] 已标注医学警告："此知识仅作教育用途，临床决策需面诊评估"
- [ ] 每个论断引用了具体的 AKNE wiki 页面来源

## Trigger
- User asks about BPPV diagnosis, treatment, or canalith repositioning
- User needs to interpret nystagmus patterns for canal involvement (posterior/horizontal/anterior)
- User asks about 3D biomechanical simulation of BPPV
- User asks about the anatomy of the semicircular canals and otolith organs
- User asks about differential diagnosis of positional vertigo

## Knowledge Sources
Absorbed from AKNE knowledge graph (yakeworld → .knowledge/wiki/):
- `bppv.md` — Disease overview (epidemiology, etiology, clinical presentation)
- `dix-hallpike.md` — Dix-Hallpike diagnostic maneuver
- `ear-stone-repositioning.md` — Repositioning maneuvers (Epley, Gufoni, Semont, Barbecue)
- `supine-head-flexion-test.md` — Supine head flexion test (俯屈仰头试验)
- `skyward-head-lift.md` — Skyward head lift method (仰天叩地法)
- `posterior-canal-new-repositioning.md` — New repositioning method for posterior canal (低头80°+后仰140°)
- `canalith-conversion.md` — Canalith conversion mechanisms between canals
- `vestibular-anatomy.md` — Vestibular system anatomy
- `virtual-simulation.md` — 3D biomechanical simulation research
- `bppv-assets.md` — BPPV knowledge asset inventory (60+ papers)

## Key Capabilities

### 1. Diagnosis Guidance
- Interpret nystagmus direction/pattern → identify involved canal (posterior = upbeating+torsional, horizontal = horizontal, anterior = downbeating+torsional)
- Select appropriate diagnostic test (Dix-Hallpike for posterior/anterior, supine roll test for horizontal)
- Differentiate canalithiasis vs cupulolithiasis based on nystagmus duration

### 2. Treatment Protocol
- Canal-specific repositioning maneuvers with step-by-step instructions
- Home-based self-treatment options (skyward head lift for horizontal, etc.)
- Post-maneuver precautions and recurrence prevention

### 3. 3D Biomechanical Simulation
- Physics-based simulation of otoconia motion during diagnostic/therapeutic maneuvers
- Canal conversion path prediction
- Custom maneuver design and testing before clinical application

### 4. Knowledge Asset Management
- Structured extraction of BPPV papers into knowledge items (知识点/创新点/核心技术)
- Paper-to-practice gap analysis
- Scientific hypothesis generation from publication portfolio

### 5. Domain Portfolio Analysis
- Audit all BPPV papers across `outputs/papers/` (25+) and `_archive/` (36+) directories
- Identify mature papers (≥80 quality score, VERIFIED/PASS gate)
- Map research gaps via PubMed/OpenAlex white space verification
- Propose 3-5 testable scientific hypotheses based on publication portfolio

- Prioritized paper action list: P0 (move archive papers), P1 (fix broken refs), P2 (long-term direction)
## Input/Output Contract
```yaml
input_contract:
  input:
    - query: str  # Natural language query about BPPV
    - context: str  # Optional: patient presentation details
  output:
    - answer: str  # Structured response with evidence
    - confidence: float  # 0.0-1.0 confidence score
    - sources: list[str]  # AKNE wiki file paths
```
## Constraints
- Do NOT give medical advice — always state: "This is educational knowledge. Clinical decisions require in-person evaluation."
- Cite specific AKNE wiki pages for every claim
- Distinguish between evidence-based fact (from papers) and hypothesized mechanism
- Maneuver descriptions must include: patient position, head rotation direction/angle, timing, expected nystagmus response
## Origin
Absorbed from AKNE knowledge graph (yakeworld/.knowledge/) — 2026-05-12
## 命令层·English
### Quick Start
- **Load**: Activate on BPPV diagnosis, treatment, or canalith repositioning queries.
- **Trigger Keywords**: BPPV, vertigo, nystagmus, Dix-Hallpike, Epley, Gufoni, Semont, Barbecue, canalith, otoconia.
- **Core Workflow**:
  1. **Diagnosis**: Interpret nystagmus → identify involved canal → select diagnostic test.
  2. **Treatment**: Canal-specific repositioning maneuver → include position, angle, timing, expected response.
  3. **Simulation**: 3D biomechanical modeling for custom maneuver design.
- **Constraints**: Always add educational-use disclaimer; cite AKNE wiki sources; distinguish evidence vs hypothesis.
- **Checklist**: Run all 6 verification items after activation.
- **Output**: Structured answer with confidence score and source references.
## 示例 · EXAMPLES
1. **基本用法**: 标准输入 → 标准输出
2. **边界用例**: 空输入、特殊字符、异常路径
3. **错误场景**: 缺失依赖、权限不足、网络异常
### Domain Analysis Example
When asked "BPPV有哪几篇比较成熟的？" or "our BPPV papers review":
1. Scan all state.json files in `outputs/papers/` and `_archive/`
2. Classify by quality score and gate status
3. Extract technical strengths from gap_type, method, clinical results
4. Map research gaps (white_space → PubMed/OpenAlex verification)
5. Propose testable hypotheses (最小刺激阈值假说, BPPV慢动力学探针假说, etc.)
6. Produce prioritized action list (P0/P1/P2)
## 约束规则 · RULES
1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态
## Golden 集合 · GOLDEN SET
- **Golden Input**: `patient_data={nystagmus: "upbeating + torsional, fatigable, duration <60s", symptoms: "特定头位诱发的短暂眩晕伴恶心"}` → 触发半规管识别 + 诊断试验选择 + 复位手法
- **Golden Output**: 结构化方案含四要素（体位/头转角度/时机/预期眼震）的 Epley 手法 + 医学警告"仅作教育用途，临床决策需面诊评估" + confidence: float + 具体 AKNE wiki 来源（如 `dix-hallpike.md`）
- **Golden Error**: 输入 `nystagmus` 缺失或无法判定受累半规管时 → 拒绝输出复位手法，返回错误信息含上下文（"无法从眼震模式识别受累半规管"）与恢复建议（"请补充 Dix-Hallpike 或仰卧翻滚试验的眼震方向与持续时间的观察记录"）
> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。
> 违反规则的操作视为不安全，必须拒绝或隔离。
> 每个示例必须可独立运行、有明确输入输出、包含错误处理。
### Related Skills
- `research/scc-bppv-kinematics` — Computational SCC morphometry + kinematic simulation from centerline data (complementary: this skill provides clinical knowledge, scc-bppv-kinematics provides the computational pipeline)
# Bppv Expert