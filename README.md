
<p align="center">
  <img src="docs/Synthos_封面_1920x1080.png" alt="Synthos Banner" width="700"/>
</p>

<h1 align="center">Synthos — Autonomous Evolving Research OS</h1>

<p align="center">
  <em>A Computable, Collaborative, and Evolving Cognitive Operating System for Science</em>
</p>

<p align="center">
  <a href="https://github.com/yakeworld/Synthos/stargazers"><img src="https://img.shields.io/github/stars/yakeworld/Synthos?style=flat&logo=github" alt="Stars"/></a>
  <a href="https://github.com/yakeworld/Synthos/actions/workflows/agent-pr-verify.yml"><img src="https://github.com/yakeworld/Synthos/actions/workflows/agent-pr-verify.yml/badge.svg" alt="CI"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License"/></a>
  <a href="https://github.com/yakeworld/Synthos/discussions"><img src="https://img.shields.io/badge/Community-Discussions-blueviolet" alt="Discussions"/></a>
  <img src="https://img.shields.io/badge/Evolution-20%20cycles-success" alt="Evolution"/>
  <img src="https://img.shields.io/badge/Version-v4.2.0-blue" alt="Version"/>
</p>

<p align="center">
  <a href="#-philosophy">Philosophy</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-cognitive-atoms">Atoms</a> •
  <a href="#-self-evolution">Evolution</a> •
  <a href="#-evaluation">Evaluation</a> •
  <a href="#-getting-started">Setup</a> •
  <a href="#-for-ai-agents">🤖 Contribute</a>
</p>

---

**Synthos** is a **pure SKILL.md-driven** cognitive operating system for scientific research. It decomposes the entire research workflow into **7 cognitive atoms**, each defined as an SKILL.md executed natively by an AI agent — no Python scripts, pure reasoning through agent capabilities.

From literature retrieval to paper output, Synthos covers the complete cognitive loop of scientific research. Its **self-evolution engine** automatically checks health, runs functional tests, and absorbs patterns from external projects every day.

> **v4.2.0** · Evolution Engine v2.3 · Quality Score: 95/100 · 20 Evolution Cycles · Agent PR Verification: ✅

[🇨🇳 中文版](README_CN.md)

---

## 🧠 Philosophy

Synthos is built on an **8-dimensional cognitive framework**:

| # | Dimension | Core Idea | Covered Atoms | Progress |
|:-:|-----------|-----------|:-------------:|:--------:|
| 1 | **First Principles** | Build from fundamental facts | 1,2,4,5 | 95% |
| 2 | **Systems Thinking** | Holistic view of knowledge | 1,3,5 | 95% |
| 3 | **Bayesian Thinking** | Update beliefs with evidence | 4,6 | 90% |
| 4 | **Analogical Thinking** | Cross-domain knowledge transfer | 4 | 80% |
| 5 | **Occam's Razor** | Shortest path first | 0,2,5 | 80% |
| 6 | **Falsificationism** | Actively seek counter-evidence | 6,1 | 80% |
| 7 | **Model-Dependent Realism** | Multi-perspective validation | 3 | 60% |
| 8 | **Free Energy Principle** | Minimize prediction error via evolution | 6, meta | 55% |

**Overall Progress**: 85% (based on built-in audit framework)

Core principle: **Constitution → Architecture → Schema → Implementation**, each layer formalized with non-overlap proofs, I/O contracts, and traceability matrices.

---

## 🏗 Architecture

> **Design philosophy**: Constitutional design, human-in-the-loop, from philosophy to code.

```text
                     ┌──────────────────────┐
                     │   Task Router (ROU)   │  ← Human-in-the-Loop
                     │  [Route → Atom → Eval]│
                     └────────┬─────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
 ┌───────────────┐  ┌────────────────┐  ┌────────────────┐
 │  ACQ          │  │  GAP           │  │  HYP           │
 │  Acquisition  │  │  Gap Discovery │  │  Hypothesis    │🆕
 │  S2/OpenAlex  │  │  Contradiction │  │  Formalizable  │🆕
 │  bioRxiv      │  │  Gap Analysis  │  │  Falsifiable   │
 └───────┬───────┘  └────────────────┘  └───────┬────────┘
         │                                       │
         └──────────────────┬────────────────────┘
                            ▼
 ┌───────────────┐  ┌────────────────┐  ┌────────────────┐
 │  COD          │  │  ASC           │  │  EXT           │
 │  Coding       │  │  Argumentation │  │  External      │
 │  Executable   │  │  Structured    │  │  Absorb from   │
 │  Thought      │  │  Reasoning     │  │  OSS Projects  │
 └───────────────┘  └────────────────┘  └────────────────┘
 ┌───────────────┐  ┌────────────────┐  ┌────────────────┐
 │  EVA          │  │  AVA           │  │                │
 │  Evaluation   │  │  Absorption    │  │                │
 │  7-dim Score  │  │  Experience →  │  │                │
 │  System       │  │  Skill Encoding│  │                │
 └───────────────┘  └────────────────┘  └────────────────┘
                              │
                     ┌────────┴────────┐
                     │  Evolution      │
                     │  Engine         │
                     │  (Daily Loop)   │
                     └─────────────────┘
```

---

## 🧬 Cognitive Atoms

| Atom | Name | Function | Status |
|:-----|:-----|:---------|:-------|
| **ACQ** | Knowledge Acquisition | Search Semantic Scholar, OpenAlex, bioRxiv, PubMed | ✅ v4.2 |
| **GAP** | Gap Discovery | Cross-literature contradiction detection, methodology gap analysis | 🆕 v4.3 |
| **HYP** | Hypothesis Generation | Formal falsifiable hypothesis generation, competing hypothesis, NSFC tree | 🆕 v4.3 |
| **COD** | Peer Coding | Transform cognitive needs into executable code | ✅ v4.2 |
| **ASC** | Argumentation & Expression | Structured reasoning, paper framework generation | ✅ v4.2 |
| **EXT** | External Absorption | Absorb quality patterns from open-source projects | ✅ v4.2 |
| **ROU** | Task Routing | Core HITL design: route routine, escalate exceptions | ✅ v4.2 |
| **EVA** | Quality Evaluation | 7-dimension objective evaluation system | ✅ v4.2 |
| **AVA** | Cognitive Absorption | Encode AI discoveries into human-understandable knowledge | ✅ v4.2 |

---

## 🔄 Self-Evolution

Synthos runs a **self-evolution engine** daily:

```
LOAD_STATE → LESSONS → PROBE → BENCHMARK → EXTERNAL → DIAGNOSE → RECORD
     ↑                                                              │
     └──────────────────── Evolution Loop ──────────────────────────┘
```

| Metric | Value |
|:-------|:------|
| Evolution Cycles | 20 (as of May 2026) |
| Consecutive EXCELLENT | 9 |
| Golden Test Pass Rate | 100% |
| Atom Test Score | 1.0 (perfect) |
| Overall Quality Score | 0.95 (EXCELLENT) |
| External Sources Absorbed | 8 OSS projects |

---

## 📊 Evaluation

Built-in 7-dimension evaluation framework:

| Dimension | Weight | Score |
|:----------|:-------|:------|
| Completeness | 20% | 96% |
| Accuracy | 20% | 94% |
| Reproducibility | 15% | 92% |
| Self-Consistency | 15% | 95% |
| Extensibility | 10% | 90% |
| Efficiency | 10% | 88% |
| Transparency | 10% | 93% |

---

## 🚀 Getting Started

```bash
# Clone the repo
git clone https://github.com/yakeworld/Synthos.git
cd Synthos

# Explore the skill structure
ls -la skills/

# Start from the task router
cat skills/task-router/SKILL.md
```

Full docs in `docs/` directory.

---

## 🤖 For AI Agents

**Synthos welcomes AI agent contributions!**

We designed a complete **Agent Contribution Protocol**:

| Doc | Description |
|:----|:------------|
| [AGENTS_CONTRIBUTING.md](AGENTS_CONTRIBUTING.md) | Agent contribution guide with AGENT_MANIFEST.yaml spec |
| [VERIFICATION_GATES.md](VERIFICATION_GATES.md) | 6-gate verification pipeline |
| [GitHub Actions](.github/workflows/agent-pr-verify.yml) | Automated CI verification |

**Contribution flow**:
```
Fork → Add AGENT_MANIFEST.yaml → PR with [agent] title prefix
                                       ↓
                              6 Gates CI Auto-Verification
                                       ↓
                              Human Review → Merge
```

[💬 Join Discussions](https://github.com/yakeworld/Synthos/discussions) • [🐛 Submit Issue](https://github.com/yakeworld/Synthos/issues)

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 📚 Reference

| Doc | Description |
|:----|:------------|
| [Technical Roadmap](docs/%E6%8A%80%E6%9C%AF%E8%B7%AF%E7%BA%BF%E5%9B%BE.md) | Full architecture design (Chinese) |
| [Agent Building Guide](docs/%E6%99%BA%E8%83%BD%E4%BD%93%E5%BB%BA%E8%AE%BE%E8%AF%B4%E6%98%8E%E6%98%8E.md) | Super individual methodology (Chinese) |
| [Community Strategy](docs/community-promotion-strategy.md) | Promotion & community building (Chinese) |
