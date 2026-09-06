# Synthos 🧠⚡

> **A Self-Evolving Cognitive Operating System for AI-Augmented Scientific Research**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Evolution Cycles](https://img.shields.io/badge/evolution-272%20cycles-brightgreen)](evolution-log.md)
[![Quality Score](https://img.shields.io/badge/quality-0.96%20overall%20%C2%B7%200.59%20behavior-success)](evolution-state.json)

**Synthos reifies epistemological principles as executable cognitive atoms.** Unlike conventional research agents that wrap Python libraries as tools, Synthos operates as a purely skill-driven architecture: the Agent itself is the runtime, with **zero Python infrastructure code** (core orchestration is 100% SKILL.md; helper automation scripts in `scripts/` use Python/shell but are not part of the cognitive architecture).

> 📖 Full philosophy → [docs/synthos-philosophy.md](docs/synthos-philosophy.md) — Classical Chinese principles · 8-dimension cognitive framework · Three inviolable laws

---

## Core Innovations

| Innovation | Description |
|:-----------|:------------|
| **🧬 Epistemological Code** | 8 philosophical frameworks (First Principles, Falsificationism, Bayesian Reasoning, etc.) reified as executable SKILL.md atoms with formal I/O contracts |
| **🏛️ Constitutional Hierarchy** | CON ≫ MEM ≫ CMD ≫ SKL ≫ DEF — immutable principles enforced by a philosophical immune system |
| **🔄 Self-Evolution Engine v2.27** | 11-step state machine with SEPL rollback, Git-as-Memory, structural probes, functional benchmarks, external absorption, drift detection, and active inference gates |
| **🌱 Entelechy-Driven Absorption** | Aristotelian self-realization as the absorption axiom — from "gap-filling" to "nutrition assessment" |
| **📝 Zero-Python Architecture** | All cognitive atoms + meta-components are pure SKILL.md markdown. No Python orchestration code |

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              CONSTITUTION.md v5.0                    │
│        (CON ≫ MEM ≫ CMD ≫ SKL ≫ DEF)                │
├─────────────────────────────────────────────────────┤
│   ACQ → EXT → ASC → HYP → ARG/VER                  │
│         ↕        ↕        ↕        ↕                 │
│   [Task Router] [Entelechy Gate] [Quality Gate]      │
├─────────────────────────────────────────────────────┤
│              Evolution Engine (11 steps)              │
│   PROBE → BENCHMARK → OPTIMIZE → EXTERNAL →          │
│   DIAGNOSE → IMPROVE → VERIFY → RECORD               │
└─────────────────────────────────────────────────────┘
```

**6 Cognitive Atoms:** Knowledge Acquisition → Knowledge Extraction → Association Discovery → Hypothesis Generation → Argument Expression → Viewpoint Verification

**3 Meta-Components:** Task Router (shortest-path routing), Entelechy Gate (direction compatibility), Quality Gate (L0–L4 multi-layer verification)

### 3-Layer Skill Architecture

Synthos organizes **157 SKILL.md files** (measured 2026-09-06) into three directories:

| Directory | Skills | Purpose |
|-----------|--------|---------|
| `skills/core/` | 8 | cognitive atoms + task-router + quality-gate |
| `skills/extended/` | 79 | research tools, devops, external automation |
| `skills/private/` | 70 | domain-specific (clinical research, mentoring, writing) |

## Paper Outputs

**261 paper.tex drafts** on disk across multiple biomedical domains (measured 2026-09-06; drafts are machine-generated — publication readiness varies, see Quality Audits below).

> ⚠️ **Status honesty:** these are drafts at various stages (machine draft / human-revised / peer-reviewed / submitted). Only a small subset is near-submittable; the per-category breakdown in the original 44-paper table is not maintained and has been removed rather than kept stale.

## Evolution History

| Metric | Cycle 1 | Cycle 96 | Cycle 272 (current) |
|:-------|:-------:|:--------:|:-------------------:|
| Structural Avg | 0.861 | 0.92 | **1.00** |
| Benchmark Score | 0.66 | 0.82 | **1.00** |
| Composite Score | 0.86 | 0.95 | **0.9638** |
| Behavior dimension | — | — | **0.5934** (current bottleneck) |
| SKILL.md Files | ~50 | ~200 | **157** (2026-09 measured) |

> Cycle 272 numbers come from `evolution-state.json` diagnostics. The behavior dimension (skill gene activation traceability) is the known next bottleneck; it is reported alongside overall on purpose — see `falsification-summary.md` for what the overall score does and does not cover.

## Comparison with Existing Systems

| System | Epistemic Encoding | Constitutional | Self-Evolution | Zero-Python |
|:-------|:-----------------:|:--------------:|:--------------:|:-----------:|
| GPT-Researcher | ✗ | ✗ | ✗ | ✗ |
| AI Scientist | ✗ | ✗ | △ | ✗ |
| PaperQA2 | ✗ | ✗ | ✗ | ✗ |
| Constitutional AI | ✗ | ✓ | ✗ | ✗ |
| DSPy | ✗ | ✗ | ✓ | ✗ |
| DeepResearchAgent | ✗ | ✗ | ✓ | ✗ |
| AI-Research-SKILLs | △ | ✗ | ✗ | ✓ |
| **Synthos (ours)** | **✓** | **✓** | **✓** | **✓** |

## Quality Audits

| Cycle | Paper | Score | Recommendation |
|-------|-------|-------|----------------|
| 97 | synthos-paper.tex | 62.5/100 (C) | MAJOR_REVISION — 7 orphan refs, 80% GitHub refs |

> **Known limitation (2026-09 audit):** per-skill scan results (cycle 181: avg 62.2, healthy 0) and the evolution-state overall score use different measurement systems and were reported inconsistently. The overall score reflects structural/benchmark/absorption dimensions; it does **not** validate scientific quality of outputs. Independent reproduction of a full workflow is not yet available — `examples/` with a complete end-to-end desensitized case is planned.

See `evolution-report-cycle-*.json` for raw scan data.

## License

MIT License — see [LICENSE](LICENSE).

## Citation

If you use Synthos in your research, please cite:

```bibtex
@software{yang2026synthos,
  author = {Yang, Xiaokai},
  title = {Synthos: A Self-Evolving Cognitive Operating System for AI-Augmented Scientific Research},
  year = {2026},
  url = {https://github.com/yakeworld/Synthos}
}
```

---

*Synthos v2.27 — 272 evolution cycles — Overall 0.9638 / Behavior 0.5934 (measured 2026-08-17, cycle 272)*

## Numbers Provenance

All counts in this file (157 skills, 261 paper drafts, 272 cycles, scores) were measured from the repository on 2026-09-06. `evolution-state.json` is the single source of truth for version/cycle/score; if this README disagrees with it, the README is stale — fix the README, not the state file.
