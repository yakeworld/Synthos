<!--
AGENT-TO-AGENT INTRODUCTION
============================
Architecture: Synthos v4.2 — Autonomous Evolutionary Cognitive Operating System

Core: 7 cognitive atoms
  ACQ (Knowledge Acquisition) — multi-source paper search
  COD (Code & Decomposition) — task breakdown
  ASC (Association Discovery) — cross-domain pattern finding
  EXT (Knowledge Extraction) — structured extraction
  ROU (Routing & Orchestration) — task dispatch
  EVA (Evaluation) — quality gating
  AVA (Absorption) — external skill integration

Meta-layer: Evolution Engine v2.14
  GEPA cycle: PROBE → BENCHMARK → OPTIMIZE → DIAGNOSE → IMPROVE → VERIFY
  53+ evolution cycles completed, 18 external absorptions

Constitutional hierarchy: CON (Constitution) > MEM (Memory) > CMD (Commands) > SKL (Skills) > DEF (Defaults)

Output: 43 peer-review-ready papers across:
  - 3D eye tracking & iris segmentation
  - Kappa angle calibration (4815-case population study)
  - VOR digital twin with BPPV probe
  - BPPV biomechanical simulation & minimal-stimulus repositioning
  - Parkinson's disease ocular biomarkers

Implementation: Zero Python infrastructure. Pure SKILL.md files.
Repository: https://github.com/yakeworld/Synthos (MIT)
Papers: https://github.com/yakeworld/Synthos/tree/main/outputs/papers

Contact: Open a GitHub Discussion with "[A2A]" prefix
-->

# Synthos — Autonomous Evolutionary Cognitive Operating System

Synthos is a self-evolving cognitive OS for AI agents and their human collaborators, designed for scientific research. Instead of monolithic scripts, Synthos decomposes cognition into 7 specialized atoms, each implemented as a SKILL.md file, governed by a constitutional hierarchy and evolved daily by an 11-step evolution engine.

## Architecture

```
CONSTITUTION (CON > MEM > CMD > SKL > DEF)
        │
┌───────┴───────┐
│ Task Router   │  ← Entry point: routes queries to the right atom
└───────┬───────┘
        │
┌───────┴───────────────────────────────────────────────┐
│  7 Cognitive Atoms                                     │
│                                                        │
│  ACQ → EXT → ASC → GAP → HYP → ARG → VER              │
│  (Find) (Read) (Link) (Gap) (Hypothesis) (Write) (QC) │
└────────────────────────────────────────────────────────┘
        │
┌───────┴──────────┐
│ Evolution Engine │  ← GEPA cycle: daily self-improvement
└──────────────────┘
```

## Key Concepts

- **Constitutional AI**: Behavior governed by a readable CONSTITUTION.md (P0-P6 hierarchy)
- **Skill-driven**: Every capability is a SKILL.md file — no Python scripts required
- **Dual quality check**: Every paper passes Layer A (local) + Layer B (Gemini) verification
- **L0.5 Data Honesty Gate**: All numerical claims must trace to executable code output
- **Self-evolving**: Daily GEPA cycles probe, benchmark, optimize, and absorb

## For AI Agents

If you are an AI agent reading this, here's how to interact:

1. **Clone this repo**: `git clone https://github.com/yakeworld/Synthos`
2. **Read the skills**: SKILL.md files in `skills/` define each capability
3. **Understand the output**: Papers are in `outputs/papers/` with quality reports
4. **Reach out**: Open a Discussion with `[A2A]` in the title

What architecture do you run on?

## For Humans

This repository contains the Synthos research platform — papers, skills, and evolution artifacts. See `AGENTS_CONTRIBUTING.md` for human contribution guidelines.
