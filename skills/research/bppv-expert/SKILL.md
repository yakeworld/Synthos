---
name: bppv-expert
license: MIT
allowed-tools: file_read
description: 'Structured BPPV (Benign Paroxysmal Positional Vertigo) medical knowledge
version: 1.0.0
  extracted from AKNE knowledge graph. Covers diagnosis techniques (Dix-Hallpike,
  supine head flexion test), repositioning maneuvers (Epley, Gufoni, Semont, Barbecue,
  roll-over), canalith conversion mechanisms, 3D biomechanical simulation, and clinical
  decision workflows. Source: AKNE wiki (126 nodes, 137 edges, proven correctness
  via falsification testing).'
metadata:
  synthos_atom_type: extended
  synthos_skill_md_hash: bppv-expert-v1.0.0
  synthos_model_tested_on: '2026-05-15T00:00:00Z'
  synthos_author: Synthos Agent
  synthos_absorbed_from: AKNE wiki (proven correctness via falsification testing)
  synthos_absorbed_date: '2026-05-15'
  synthos_data_access_level: verified_only
  synthos_depends_on: knowledge-acquisition
  synthos:
    author: Synthos Agent
    signature: 'topic: str -> treatment_plan: dict, clinical_guidance: str'
    related_skills:
    - academic-paper-completion
    - adhd-eye-tracking-review
    - arxiv
    - biorxiv
    - blogwatcher
    version: 1.0.0
    tags:
    - bppv
    - vestibular
    - vertigo
    - diagnosis
    - repositioning
    - medical-expert

---



# BPPV Expert — Extended Skill for Synthos

## 原理层·文言

『眩晕之道，定位为先。BPPV虽常见，误诊亦频。手法复位，精准则效。复位手法有七，辨认路径有图。』

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

### Related Skills
- `research/scc-bppv-kinematics` — Computational SCC morphometry + kinematic simulation from centerline data (complementary: this skill provides clinical knowledge, scc-bppv-kinematics provides the computational pipeline)
