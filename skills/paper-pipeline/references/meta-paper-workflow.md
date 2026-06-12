# Meta-Paper Workflow: Writing About the System Itself

> 2026-05-22 | Derived from writing the Synthos paper (Nature MI target, T1)

## ⚠️ P-1 铁律：科学问题定义不可跳过

> 这是本流程**最高优先级规则**。即使论文是关于你自己的系统，
> **文献调研（外搜是必须环节）→ 研究空白 → 科学假设 → 技术路线 → 创新性与可行性**
> 这五个步骤一个不能少。先扫描本地资产，再启动外部搜索，最后构建Gap。
>
> **常见错误**: 认为"论文写自己的系统就不用做文献调研" → ❌ 不对。
> 系统本身提供的是Results数据，但Gap/假设必须从领域对照中产生。
> 没有CARS模型的Introduction必然被审稿人批评"缺乏文献定位"。

## When to Use This Workflow

## Key Differences from Standard Pipeline

| Aspect | Standard Pipeline (NotebookLM) | Meta-Paper (Direct) |
|:-------|:------------------------------|:-------------------|
| Data source | External papers, NotebookLM sources | The running system itself |
| Literature search | NotebookLM `add-research` | GitHub API + OpenAlex + absorption DB |
| Architecture description | From literature → system design | **From system → paper** |
| Results | From external experiments | Evolution cycles, absorption records, functional comparison |
| Quality gate | Same (journal-aware T1-T4) | Same (journal-aware T1-T4) |

## Workflow Steps

### P-1: Scientific Problem Definition（不可跳过！）

完整五步，缺一不可：

```
P-1.1 文献调研（外搜是必须环节）→ 先本地后远程 → 构建领域地图
P-1.2 研究空白定位（CARS Move2门）→ 已知→未知→意义
P-1.3 科学假设形成（图尔敏门）→ If X then Y + 淘汰标准
P-1.4 技术路线设计 → 架构方案 + 已有资产映射 + 缺失环节
P-1.5 创新性与可行性评估 → 各创新点与文献对比 + 可行性分析
```

**P-1.4 技术路线设计（新增）**

列出技术方案的核心架构决策：
- 系统用什么框架/平台？架构范式？
- 哪些组件已经存在？哪些需要新建？
- 与同类系统对比有什么差异化技术决策？

**P-1.5 创新性与可行性评估（新增）**

| 创新点 | 与文献对比 | 可行性 |
|:-------|:----------|:-------|
| 创新点1（如纯SKILL驱动） | ARS是SKILL+Python混用，ResearcherSkill是单文件 | ✅ 已在v4.3运行51轮 |
| 创新点2（如自进化） | NanoResearch有但笨重，hermes-evolution紧耦合 | ✅ 连续零降级 |
| 创新点3（如宪法） | 无先例 | ✅ 已编码P0-P6 |

Output: `paper-framework.md` with gap, hypothesis, contributions, technical route, innovation × feasibility.

```
Gap: Existing systems are Python-heavy and lack self-evolution
Hypothesis: Pure SKILL.md architecture can match/exceed Python systems
Contributions: Zero-Python, 7 cognitive atoms, v2.12 evolution, P0-P6 constitution
```

### P2: Paper Construction (Direct, No NotebookLM)

Write sections in reverse order (Results → Methods → Discussion → Introduction → Abstract):

**Results first** — the paper's punchline:
- Functional comparison table (include `\\checkmark`/`\\times` matrix)
- Evolution cycle statistics (total cycles, score trajectory, structural health)
- Absorption throughput (how many methodologies, average score)
- Case study: evolution of the engine itself (v2.0 → v2.12)

**Methods** — describe the architecture:
- Use TikZ for architecture diagrams (see `references/tikz-figure-tips.md`)
- Seven cognitive atoms: name, function, I/O contract for each
- Pure skill-driven design: explain three-language hierarchy
- Constitutional framework: P0-P6 summarized
- Evolution engine: 12-step cycle diagram
- Absorption pipeline: L+0 to L+4 gates

**Discussion** — Toulmin model (6 elements):
- Claim + Grounds: what we found
- Warrant + Backing: why it matters
- Rebuttal: limitations (≥3 items, be honest about missing ablations)
- Qualifier: scope boundaries

**Introduction** — CARS model:
- Move1: Background (rise of AI agents)
- Move2: Three gaps (cognitive architecture, self-evolution, constitution)
- Move3: Five contributions + comparison table

**Abstract** — Pyramid principle (last):
- Tower top: core thesis (1 sentence)
- Middle: key findings
- Base: significance

### Results Data You Can Use Immediately

| Data Point | Source | Format |
|:-----------|:-------|:-------|
| Total evolution cycles | `evolution-state.json.evolution_count` | Integer |
| Score trajectory | `evolution-log.md` | Sequence |
| Structural health | `evolution-state.json.evolution.structural_avg` | Float (0-1) |
| Benchmark pass rate | `evolution-state.json.evolution.benchmark_score` | Float (0-1) |
| Atom count | `evolution-state.json.skill_tree.core_atoms` | Integer |
| Absorption count | `evolution-state.json.absorptions` | Array length |
| Absorbed skills | `skills/evolution/references/absorption-*.md` | Per-source docs |
| Related projects | `absorption-tracked.json.tracked_projects` | 37+ entries |
| Comparison matrix | `SKILL_TREE.md` | Architecture overview |

### Quality Gate (Same threshold, journal-aware)

Run `sci-paper-quality-review` after the paper is written.

| Tier | Target | Avg threshold | Citation count |
|:-----|:-------|:-------------:|:--------------:|
| T1 | Nature MI, Patterns | ≥0.85 | ≥60 |
| T2 | JAIR, MIR | ≥0.80 | ≥40 |
| T3 | IEEE ACCESS, Frontiers | ≥0.75 | ≥30 |

**Common blocker for meta-papers**: D3 (credibility) and D7 (citation count)
both tend to score low on first draft. D7 is quick to fix (add more citations);
D3 requires running controlled experiments (ablation, evolution comparison).

### Pitfalls

1. **🌀 [致命] 跳过P-1直接写论文** — 觉得"写自己系统不用文献调研"是最常见的错误。被用户纠正:"首先文献调研，见科研空白，提出科学假设，技术路线，创新性和可行性，然后再开始论文撰写。" 即使写自己的系统，CARS模型的Move2(Move1→领域地图→Gap)必须执行。
2. **Don't fabricate numbers** — All evolution cycle counts...
3. **Keep Limitations honest** — A meta-paper without a "no ablation studies yet" limitation will get desk-rejected by T1 reviewers.
4. **Citation count trap** — Meta-papers about novel systems often have <10 citations on first draft. Budget time to search and add ≥40-60 related references.
5. **Figure quality** — Architecture diagrams must be TikZ/vector PDF, not screenshots or ASCII art.
