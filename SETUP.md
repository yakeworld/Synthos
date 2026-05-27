# Synthos — Setup Guide

## Requirements

- **Any AI agent** that supports SKILL.md loading (Hermes Agent, Claude Code, Codex, OpenCode, etc.)
- **Python 3.10+** (only for extended skills like Figure Generation)
- **curl** (for API-based knowledge acquisition)
- **Internet access** (PubMed, Semantic Scholar, OpenAlex, arXiv, etc.)

## Quick Start

### 1. Clone

```bash
git clone https://github.com/yakeworld/Synthos.git
cd Synthos
```

### 2. Load the Cognitive OS

In your AI agent session, load the task router:

```
open /path/to/Synthos/skills/task-router/SKILL.md
```

Or use your agent's native skill-loading mechanism to load from:

```
./skills/task-router/SKILL.md
```

### 3. Run a Query

The task router automatically selects the shortest atom chain for your request:

| Query Type | Example | Atoms Used |
|:-----------|:--------|:-----------|
| **Search** | "Find papers on FB risk factors" | ACQ (1 atom) |
| **Extract** | "Extract methods from these papers" | ACQ → EXT (2 atoms) |
| **Analyze** | "Analyze the research landscape of FB" | ACQ → EXT → ASC (3 atoms) |
| **Hypothesize** | "Generate hypotheses about FB risk" | ACQ → EXT → ASC → HYP (4 atoms) |
| **Write** | "Write a review on FB risk prediction" | Full chain (5-6 atoms) |
| **Verify** | "Verify these claims" | HYP → VER (2 atoms) |
| **Assess quality** | "Quality gate this proposal" | GAP + VER (2 atoms) |

### 4. Output

Results are saved to `outputs/runs/<timestamp>/` as structured JSON, markdown reports, and optional LaTeX/PDF.

## Project Structure

```
Synthos/
├── CONSTITUTION.md              # Philosophical constitution
├── PROJECT_QUALITY.md           # Quality thresholds & closed-loop status
├── evolution-state.json         # Evolution state tracker
├── README.md                    # English docs
├── README_CN.md                 # Chinese docs
├── SKILL.md                     # Cognitive OS overview
├── skills/
│   ├── task-router/             # Entry point — routes queries to atom chain
│   ├── knowledge-acquisition/   # Atom 1: literature search
│   ├── knowledge-extraction/    # Atom 2: structured extraction
│   ├── association-discovery/   # Atom 3: relationship discovery
│   ├── hypothesis-generation/   # Atom 4: hypothesis formulation
│   ├── argument-expression/     # Atom 5: academic writing
│   ├── viewpoint-verification/  # Atom 6: falsification & verification
│   ├── gap-discovery/           # Research gap analysis
│   ├── evolution/               # Self-evolution engine
│   └── ...                      # Extended skills
├── archive/                     # Historical reference material
├── docs/                        # Documentation
└── outputs/                     # Run outputs & generated reports
```

## Supported Data Sources

| Source | Coverage | Access |
|:-------|:---------|:-------|
| **PubMed** | 35M+ biomedical abstracts | Free API |
| **Semantic Scholar** | 200M+ papers | Free API (rate limited) |
| **OpenAlex** | 250M+ works | Free, no key needed |
| **arXiv** | 2.4M+ preprints | Free OAI-PMH |
| **Crossref** | 150M+ DOIs | Free API |
| **bioRxiv/medRxiv** | 200K+ preprints | Free API |

## Quality Gate

Every output is automatically checked against:

1. **Structural integrity** — skill files, frontmatter, references
2. **Functional correctness** — golden test cases
3. **Citation verification** — cross-reference against Semantic Scholar
4. **Constitutional alignment** — CONSTITUTION.md compliance
5. **Drift detection** — session consistency check

## Self-Evolution

Synthos runs a daily evolution cycle:

```
LOAD_CONSTITUTION → DRIFT_CHECK → PROBE → BENCHMARK → DIAGNOSE → RECORD
```

Automatically detects degraded atoms, scans external projects for absorption, and self-repairs.

## Contribute

See [AGENTS_CONTRIBUTING.md](AGENTS_CONTRIBUTING.md) for AI agent contribution protocol.

## License

MIT — free to use, modify, and distribute.
