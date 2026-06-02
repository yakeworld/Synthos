# Competition Supporting Material Preparation

Use this when creating 证明材料 (supporting evidence documents) for AI/medical competitions.

## Required Sections

Per the competition guidelines, supporting materials must include:
1. **Publicly accessible test account** — GitHub repo URL + deployment instructions
2. **Original creator attribution** — R&D team, institution name (for original version only)
3. **IP proof or R&D documentation** — open-source license, code repository, technical roadmap, design docs
4. **School academic affairs office stamp** (original version only) — 教务处/教师教学发展中心

## Two-Version Workflow

Always prepare TWO versions:

| Version | Purpose | Contains | Stamp needed |
|:--------|:--------|:---------|:-------------|
| **Original** | For material review (审核) | Team names, institution, personnel | Yes |
| **Anonymous** | For expert evaluation (评审) | Role-based descriptions only | No |

## LaTeX Compilation (Preferred over Markdown→PDF)

The user strongly prefers LaTeX-compiled PDFs with TikZ diagrams over Markdown→pandoc output.

```bash
# Compile with xelatex for CJK support
xelatex -interaction=nonstopmode materials.tex
# Run twice for cross-references
xelatex -interaction=nonstopmode materials.tex
```

### LaTeX Setup for CJK Documents
```latex
\documentclass[11pt,a4paper]{article}
\usepackage[UTF8]{ctex}
\usepackage[margin=2.5cm]{geometry}
\usepackage{tikz}
\usepackage{booktabs}  % For professional tables
\usepackage{hyperref}  % For clickable URLs
```

## TikZ Technical Roadmap Pattern

Use a 6-layer colored architecture diagram:

```
Layer 1: Philosophy (purple)  — 7+1 framework
Layer 2: Constitution (blue)  — P0, gates
Layer 3: Architecture (teal)  — 4-layer model
Layer 4: Atom (orange)       — 6 cognitive atoms
Layer 5: Evolution (green)   — evolution engine metrics
Layer 6: Output (red)        — papers, patents
```

Each layer: `\node[layer={color}] (lN) {...}\node[content={color}] (cN) {...}`
Connected with `\draw[arrow] (cN.south) -- ++(0,-0.4);`

## Number Verification Rule

Before placing any number in competition materials:
- Must trace to run log, state file, or code output
- "自进化引擎" is acceptable as concept name
- Use qualitative language when uncertain: "多轮"/"多次"/"优异" instead of specific figures
- Never use unverified efficiency claims (6X, 85%+, -40%)

## Anonymous Version Conversion

When anonymizing:
- Remove institution name → replace with role descriptions
- Remove team member names → use functional roles
- Remove academic affairs approval section
- Keep GitHub repos (public info, not personal)
- Keep open-source license info
- Change title to indicate "匿名版本"
