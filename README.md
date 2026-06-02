# Synthos 🧠⚡

> **A Self-Evolving Cognitive Operating System for AI-Augmented Scientific Research**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Evolution Cycles](https://img.shields.io/badge/evolution-53%20cycles-brightgreen)](evolution-log.md)
[![Quality Score](https://img.shields.io/badge/quality-0.98%20EXCELLENT-success)](evolution-state.json)

**Synthos reifies epistemological principles as executable cognitive atoms.** Unlike conventional research agents that wrap Python libraries as tools, Synthos operates as a purely skill-driven architecture: the Agent itself is the runtime, with **zero Python infrastructure code** (core orchestration is 100% SKILL.md; helper automation scripts in `scripts/` use Python/shell but are not part of the cognitive architecture).

> 📖 Full philosophy → [docs/synthos-philosophy.md](docs/synthos-philosophy.md) — Classical Chinese principles · 8-dimension cognitive framework · Three inviolable laws

---

## Core Innovations

| Innovation | Description |
|:-----------|:------------|
| **🧬 Epistemological Code** | 8 philosophical frameworks (First Principles, Falsificationism, Bayesian Reasoning, etc.) reified as executable SKILL.md atoms with formal I/O contracts |
| **🏛️ Constitutional Hierarchy** | CON ≫ MEM ≫ CMD ≫ SKL ≫ DEF — immutable principles enforced by a philosophical immune system |
| **🔄 Self-Evolution Engine v2.14** | 11-step state machine with SEPL rollback, Git-as-Memory, hypothesis-first improvement, Pareto optimization, and Nudge soft-feedback |
| **🌱 Entelechy-Driven Absorption** | Aristotelian self-realization as the absorption axiom — from "gap-filling" to "nutrition assessment" |
| **📝 Zero-Python Architecture** | All 7 cognitive atoms + 3 meta-components are pure SKILL.md markdown. No Python orchestration code |

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              CONSTITUTION.md v5.0                    │
│        (CON ≫ MEM ≫ CMD ≫ SKL ≫ DEF)                │
├─────────────────────────────────────────────────────┤
│   ACQ → EXT → ASC → RIF → HYP → ARG/VER             │
│         ↕        ↕        ↕        ↕                 │
│   [Task Router] [Entelechy Gate] [Quality Gate]      │
├─────────────────────────────────────────────────────┤
│              Evolution Engine (11 steps)              │
│   PROBE → BENCHMARK → OPTIMIZE → EXTERNAL →          │
│   DIAGNOSE → IMPROVE → VERIFY → RECORD               │
└─────────────────────────────────────────────────────┘
```

**7 Cognitive Atoms:** Knowledge Acquisition → Knowledge Extraction → Association Discovery → Research Ideation → Hypothesis Generation → Argument Expression → Viewpoint Verification

**3 Meta-Components:** Task Router (shortest-path routing), Entelechy Gate (direction compatibility), Quality Gate (L0–L4 multi-layer verification)

## Paper Outputs

Synthos has produced **44 paper drafts** across multiple biomedical domains and methodology:

| Category | Papers | Size |
|:---------|:-------|:----:|
| 🧠 **Neurology** | PD Torsion Review ✅, BPPV Minimal Stimulus ✅, PD Dysphagia Risk, HCS-3WT Breast Cancer | 4 full papers |
| 👁️ **Ophthalmology** | Iris 3D Anatomical Segmentation, Iris YOLO, CutEye Model, Portable Eye Tracking | 4 full papers |
| 🔄 **VOR/Vestibular** | VOR Sparse Modular NN, VOR Digital Twin | 2 full papers |
| 📊 **Methodology** | PIMA CRISP-DM Helix ✅ | 1 full paper |
| 📚 **Literature Reviews** | 33 reviews across eye-tracking, VOR, BPPV, iris, eyeball, methods | 33 reviews |
| **Total** | **44 paper.tex files** | **10 full papers + 33 reviews** |

✅ = Dual quality check passed (local Layer A + NotebookLM Gemini Layer B)

## Results (53 Evolution Cycles)

| Metric | Cycle 1 | Cycle 10 | Cycle 23 | Cycle 41 | Cycle 53 |
|:-------|:-------:|:--------:|:--------:|:--------:|:--------:|
| Structural Avg | 0.861 | 1.00 | 1.00 | 1.00 | **1.00** |
| Benchmark Score | 0.66 | 1.00 | 1.00 | 1.00 | **1.00** |
| Composite Score | 0.86 | 0.94 | 0.97 | 0.975 | **0.98** |
| External Absorptions | 0 | 1 | 3 | 10 | **18** |

## Getting Started

```bash
# Clone the repository
git clone https://github.com/yakeworld/Synthos.git
cd Synthos

# Load any cognitive atom
open skills/knowledge-acquisition/SKILL.md
```

See [SETUP.md](SETUP.md) for detailed installation instructions.

## Project Structure

```
Synthos/
├── CONSTITUTION.md          # Immutable principles (v5.0)
├── CITATION.cff             # Citation metadata
├── CONTRIBUTING.md          # How to contribute
├── SETUP.md                 # Installation guide
├── LICENSE                  # MIT License
├── README_CN.md             # Chinese README
├── README.md                # This file
│
├── skills/                  # 🧠 Cognitive atoms (SKILL.md)
│   ├── knowledge-acquisition/
│   ├── knowledge-extraction/
│   ├── association-discovery/
│   ├── research-ideation/
│   ├── hypothesis-generation/
│   ├── argument-expression/
│   ├── viewpoint-verification/
│   ├── task-router/
│   ├── evolution/
│   ├── latex-output/
│   ├── scientific-database-lookup/
│   └── shared/
│
├── docs/                    # 📖 Documentation
│   ├── getting-started.md
│   ├── architecture_v4.3.svg
│   ├── synthos-philosophy.md
│   └── ...
│
├── scripts/                 # 🔧 Helper scripts
├── outputs/                 # 📊 Evolution data (gitignored)
└── knowledge-graph/         # 🧩 Personal knowledge (gitignored)
```

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

## External Absorption Record

Synthos has absorbed patterns from **18 external projects** across four categories:

| Category | Sources | Key Patterns Absorbed |
|:---------|:--------|:----------------------|
| Infrastructure | Constitutional AI, LangGraph, MCP, Reflexion | Hook events, state machines, dynamic discovery |
| Evolution Mechanisms | 724-office, DeepResearchAgent, ARIS, GEPA, OpenAI Agents SDK, DSPy | Nudge feedback, SEPL rollback, Git-as-Memory, Pareto optimization |
| Skill Enhancement | GPT-Researcher, AutoResearchClaw, ARS, PaperOrchestra, AI-Research-SKILLs | Deep crawling, citation verification, anti-sycophancy, ARA provenance |
| Methodology | KILO-KIT, Agent4S, PaperSpine V2 | CRISP-DM templates, structured absorption, paper writing workflow |

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

*Synthos v4.3.0 — 53 evolution cycles — Quality Score 0.98 (EXCELLENT)*
