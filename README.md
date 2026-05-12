
<p align="center">
  <img src="docs/architecture_v4.3.svg" alt="Synthos Architecture" width="700"/>
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
  <img src="https://img.shields.io/badge/Evolution-13%20cycles-success" alt="Evolution"/>
  <img src="https://img.shields.io/badge/Version-v4.3.0-blue" alt="Version"/>
</p>

<p align="center">
  <a href="#-philosophy">Philosophy</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-cognitive-atoms">Atoms</a> •
  <a href="#-extended-skills">Extended Skills</a> •
  <a href="#-self-evolution">Evolution</a> •
  <a href="#-getting-started">Setup</a> •
  <a href="#-for-ai-agents">🤖 Contribute</a>
</p>

---

**Synthos** is a **pure SKILL.md-driven** cognitive operating system for scientific research. It decomposes the entire research workflow into **cognitive atoms**, each defined as an SKILL.md executed natively by an AI agent — no Python scripts, pure reasoning through agent capabilities.

From literature retrieval to paper output, Synthos covers the complete cognitive loop of scientific research. Its **self-evolution engine** automatically checks health, runs functional benchmarks, and absorbs patterns from external projects every day.

> **v4.3.0** · Evolution Engine v2.3 · Quality Score: 0.933 (EXCELLENT) · 13 Evolution Cycles · 6 Cognitive Atoms + 3 Extended Skills + 2 Infrastructure · Agent PR Verification: ✅

[🇨🇳 中文版](README_CN.md)

---

## 🧠 Philosophy

Synthos is built on an **8-dimensional cognitive framework**:

| # | Dimension | Core Idea | Covered Atoms | Progress |
|:-:|-----------|-----------|:-------------:|:--------:|
| 1 | **First Principles** | Build from fundamental facts | ACQ, EXT, HYP, ARG | 95% |
| 2 | **Systems Thinking** | Holistic view of knowledge | ACQ, ASC, EXT | 95% |
| 3 | **Bayesian Thinking** | Update beliefs with evidence | HYP, VER | 90% |
| 4 | **Analogical Thinking** | Cross-domain knowledge transfer | HYP, EXT (absorption) | 80% |
| 5 | **Occam's Razor** | Shortest path first | ROU, EXT, ARG | 80% |
| 6 | **Falsificationism** | Actively seek counter-evidence | VER, ACQ | 80% |
| 7 | **Model-Dependent Realism** | Multi-perspective validation | ASC | 60% |
| 8 | **Free Energy Principle** | Minimize prediction error via evolution | VER, evolution engine | 55% |

**Overall Progress**: 85% (based on built-in audit framework)

Core principle: **Constitution → Architecture → Schema → Implementation**, each layer formalized with non-overlap proofs, I/O contracts, and traceability matrices.

---

## 🏗 Architecture

> **Design philosophy**: Constitutional design, human-in-the-loop, from philosophy to code.

```text
                     ┌──────────────────────┐
                     │  Task Router (ROU)   │  ← Human-in-the-Loop
                     │ [Route→Atom→Eval]   │
                     └──────┬───────────────┘
                            │
    ┌───────────────────────┼───────────────────────┐
    ▼                       ▼                       ▼
┌──────────┐         ┌──────────┐            ┌──────────┐
│  ACQ     │   ═══>  │  EXT     │    ═══>    │  ASC     │
│Acquisition│        │Extraction│           │Association│
└──────────┘         └──────────┘            └────┬─────┘
                                                   │
                                              ┌────▼─────┐
                                              │  HYP     │
                                              │Hypothesis│
                                              └────┬─────┘
                                                   │
                                    ┌───────────────┼───────────────┐
                                    ▼                               ▼
                              ┌──────────┐                   ┌──────────┐
                              │  ARG     │                   │  VER     │
                              │Argument  │                   │Verification│
                              └──────────┘                   └──────────┘

Extended: BPPV Expert  •  Research Thinking  •  Figure Generation ⭐
Infra:    Evolution Engine  •  LaTeX Output

         ┌─────────────────────────────────────────────┐
         │         Evolution Loop (daily cycle)         │
         │  PROBE → BENCHMARK → EXTERNAL → DIAGNOSE   │
         └─────────────────────────────────────────────┘
```

---

## 🧬 Cognitive Atoms

| Atom | Name | Function | Status |
|:-----|:-----|:---------|:-------|
| **ROU** | Task Routing | Route user queries to shortest atom chain. Occam's razor | ✅ v4.2 |
| **ACQ** | Knowledge Acquisition | Multi-source search: Semantic Scholar, PubMed, OpenAlex, arXiv, Crossref | ✅ v4.2 |
| **EXT** | Knowledge Extraction | Extract structured knowledge: method, findings, conclusion, limitations | ✅ v4.2 |
| **ASC** | Association Discovery | Identify 7 typed edges between knowledge items. Integrated GAP research gap detection | ✅ v4.2 |
| **HYP** | Hypothesis Generation | Formal falsifiable hypotheses with prediction, counter-evidence, competitive hypotheses | ✅ v4.3 |
| **ARG** | Argument Expression | Transform hypotheses into structured academic arguments with citations | ✅ v4.2 |
| **VER** | Viewpoint Verification | Multi-angle falsification: counterarguments, robustness checks, Bayesian confidence | ✅ v4.2 |

---

## 🧩 Extended Skills

| Skill | Source | Function | Status |
|:------|:-------|:---------|:-------|
| **BPPV Expert** | AKNE Knowledge Graph | Structured BPPV medical diagnosis & treatment knowledge (126 nodes) | ✅ v1.0 |
| **Research Thinking** | AKNE Philosophy | First Principles, Systems Thinking, Bayesian Thinking, Falsificationism | ✅ v1.0 |
| **Figure Generation** ⭐ | [nature-figure](https://github.com/Yuan1z0825/nature-skills) (交大袁一哲) | Publication-grade scientific figures: Figure Contract methodology, 16 layout patterns, Nature color palettes, SVG/PDF export | ✅ v1.0 🆕 |

### Figure Generation — What's New

Absorbed from [nature-figure](https://github.com/Yuan1z0825/nature-skills) by YiZhe Yuan (Shanghai Jiao Tong University), rated **4.5/5** as the most mature skill in the repository:

- **Figure Contract Methodology**: Claim → Evidence Hierarchy → Panel Mapping → Export Contract → QA Review — before any plotting code
- **16 layout patterns**: ultra-wide bars, clinical triptych, dark image plates, asymmetric hero panels, ablation alphagradient, hatch grayscale safety, etc.
- **Nature semantic color system**: blue-main/green-positive/red-baseline + NMI pastel family + 5 domain-specific palettes (imaging, clinical, genomics, materials, clinical)
- **Export**: SVG (editable text), PDF, TIFF at publication DPI

Unlike the cognitive atoms, Figure Generation requires Python/matplotlib execution as a **visual output mechanism** — the figure contract design remains Agent-native reasoning.

---

## 🔄 Self-Evolution

Synthos runs a **self-evolution engine** that cycles daily:

| Step | Action |
|:-----|:-------|
| **PROBE** | Structural score all atoms (frontmatter, I/O contracts, boundary declarations) |
| **BENCHMARK** | Run functional golden tests against each atom's search/analysis capabilities |
| **EXTERNAL** | Scan for quality patterns in external open-source AI-research projects |
| **DIAGNOSE** | Calculate composite score, identify degraded atoms, repair automatically |
| **RECORD** | Log lessons, update evolution-state.json, repeat |

| Metric | Value |
|:-------|:------|
| Evolution Cycles | 13 (as of May 2026) |
| Consecutive EXCELLENT | 7 |
| Benchmark Pass Rate | 100% (8/8 in Cycle 13) |
| Atom Structural Score | 1.0 (perfect — all 7 atoms) |
| Overall Quality Score | 0.933 (EXCELLENT) |
| External Sources Absorbed | 3 (AKNE, nature-figure, ADHD review) |

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
