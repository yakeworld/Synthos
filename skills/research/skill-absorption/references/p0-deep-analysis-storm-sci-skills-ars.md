# P0 Deep Absorption Analysis: STORM, scientific-agent-skills, AI-Research-SKILLs

**Concrete example of 3-Layer Deep Analysis Pattern (v3.8.0).**
**Session:** 2026-05-15
**Source:** Awesome-Auto-Research-Tools (⭐427) cross-reference with Synthos absorption DB.

## Executive Summary

Three major open-source AI agent skill ecosystems analyzed for Synthos absorption:

| Project | Stars | Key Value | Absorbable Pattern |
|---------|-------|-----------|-------------------|
| **STORM** (Stanford) | 28K | Multi-perspective questioning, citation-backed curation | KnowledgeCuration → ACQ+VER pipeline, Co-STORM discourse protocol |
| **scientific-agent-skills** (K-Dense) | 21K | 137 skills, 78 database refs, Agent Skills standard | Skill directory structure, reference system, category taxonomy |
| **AI-Research-SKILLs** (Orchestra) | 8.4K | 98 skills, two-loop autoresearch, ARA artifacts | Autoresearch orchestration, ARA compiler, skill lifecycle coverage |

**Critical finding:** These ecosystems share the same "skill-driven agent" paradigm as Synthos but lack Synthos's unique advantages: atomic purity, evolution engine, zero-Python architecture, and non-overlapping atom boundaries. The three projects are **complementary** — STORM excels at asking questions (fills ACQ/EXT/ASC gaps), scientific-agent-skills at accessing data sources (fills EXT gap), and AI-Research-SKILLs at orchestrating the full lifecycle (fills ROUTE/HYP/VER gaps).

## 1. STORM (Stanford) — Layer 1: Philosophy

STORM's core insight: **"The hardest part of automated research is asking good questions."** Rather than prompting an LLM to generate questions directly (which fails), STORM uses two strategies:
1. **Perspective-Guided Question Asking** — surveys existing articles on similar topics to discover diverse perspectives
2. **Simulated Conversation** — enacts a Wikipedia Writer ↔ Topic Expert dialogue grounded in search results

Co-STORM extends this to **human-in-the-loop collaborative knowledge curation** with a dynamic mind map and discourse protocol.

### Architecture (Layer 2)

```
STORMWikiRunner
  ├── Pre-writing Stage
  │   ├── KnowledgeCuration Module
  │   │   ├── PersonaGenerator (DSPy module)
  │   │   ├── ConvSimulator (DSPy module)
  │   │   ├── OutlineGenerator (DSPy module)
  │   │   └── ArticleGen (DSPy module)
  │   └── Search API (Bing/You.com/etc.)
  └── Writing Stage
      ├── Outline → Article pipeline
      └── Polish Module
```

DSPy-based: all modules are DSPy programs (LLM + few-shot examples, not prompts). The system compiles modules at runtime.

### Absorbable Patterns (Layer 3)

| Pattern | Target Atom | Priority | Direct Transfer? |
|---------|-------------|----------|-----------------|
| Multi-perspective persona generation | ACQ → EXT → ASC bridge | P0 | 🔄 DSPy → SKILL.md adaptation needed |
| Simulated Q&A conversation for knowledge curation | ACQ (search strategy) | P0 | ✅ Protocol pattern directly absorbable |
| Co-STORM human-in-loop discourse protocol | ROUTE (orchestration) | P1 | ✅ Protocol, no Python dependency |
| Knowledge Tree mind map | ASC (association) | P1 | 🔄 Visualization pattern |
| Citation-backed outline generation | EXT → ARG bridge | P2 | 🔄 Depends on DSPy Compiler |

## 2. scientific-agent-skills (K-Dense AI) — Layer 1: Philosophy

Core insight: **"Scientific research should be atomized into reusable agent skills, each with a single responsible data source and a standard SKILL.md format."** Raw directory walk reveals 137 skills across 12 categories, each skill = 1 SKILL.md + 1 references/ directory.

### Architecture (Layer 2)

```
skills/
  ├── bioinformatics/ (37 skills: blast, bioconductor, dbsnp, ensemble, ...)
  ├── biomedical/ (21 skills: clinical-trials, fda, icd, pubchem, ...)
  ├── clinical/ (12 skills: epic, fhir, i2b2, mrn-resolve, ...)
  ├── drug-discovery/ (8 skills: admetlab, chebi, drugbank, ...)
  ├── materials-science/ (16 skills: asm, cod, matbench, ...)
  ├── medical-imaging/ (11 skills: dcm4chee, dicom, nifti, ...)
  ├── ml-models/ (7 skills: chemberta, esm, gnina, ...)
  ├── molecular-modeling/ (7 skills: openbabel, rdkit, ...)
  ├── omics/ (38 skills: cellxgene, gtex, proteomicsdb, ...) ← largest category
  ├── python-env/ (7 skills: conda, pip, ...)
  └── references/
```

**SKILL.md format**: Each skill has YAML frontmatter (name, description, tools, input, output, tags), body with purpose, steps, tips, examples.

### Absorbable Patterns (Layer 3)

| Pattern | Target Atom | Priority | Direct Transfer? |
|---------|-------------|----------|-----------------|
| Unified database lookup (78 databases) | EXT (data access) | P0 | ✅ Pure API calls, no Python |
| Skill dir structure + reference/ pattern | Reference for Synthos skill taxonomy | P0 | ✅ Already same paradigm |
| Standard YAML frontmatter | SKILL.md format template | P1 | ✅ Already mostly aligned |
| Individual skills (e.g., blast, dbsnp) | Extended skills | P1 | 🔄 Need adaptation (path, API keys) |
| 70+ Python package skills | — | ❌ | Python dependencies, not absorbable |

**Not absorbable**: ~70 Python-package-dependent skills (biopython, rdkit, scanpy, etc.)

## 3. AI-Research-SKILLs (Orchestra Research) — Layer 1: Philosophy

Core insight: **"AI research is a two-loop process — inner loop (hypothesis→experiment→analyze) and outer loop (literature→research management→publication)."** The 98 skills are organized around these two loops. Most philosophically aligned with Synthos among the three.

### Architecture (Layer 2)

```
SKILLs/
  ├── architecture-autoresearch/
  │   ├── two-loop-architecture.SKILL.md
  │   ├── inner-loop.SKILL.md
  │   └── outer-loop.SKILL.md
  ├── architecture-cognitive/
  ├── architecture-code/
  ├── data-literature/
  ├── data-web/
  ├── deployment/ (vLLM, llama.cpp, docker, etc.)
  ├── domain-biomedical/
  ├── eval-benchmark/ (lm-eval, mmlu, etc.)
  ├── eval-review/ (auto-evaluation, meta-eval, rubric, rigor, self-eval)
  ├── experimentation/ (logging, sweeps, swe-bench, etc.)
  ├── generation/ (latex, paper, poster, response, review, slides)
  ├── ideation/ (gap-analysis, hypothesis-gen, idea-refine)
  ├── llm-api/ (all major providers)
  ├── management/ (project, research, time)
  ├── implementation-code/ (architecture, code-gen, doc-gen, refactor)
  ├── implementation-ml/ (dataloader, training, architecture, modeling)
  └── references/
```

**ARA artifacts**: core infrastructure — ARA Compiler (knowledge extraction from any source), ARA Research Manager (provenance tracking), ARA Rigor Reviewer (self-consistency + multi-model cross-check).

### Absorbable Patterns (Layer 3)

| Pattern | Target Atom | Priority | Direct Transfer? |
|---------|-------------|----------|-----------------|
| Two-loop architecture (inner+outer) | ROUTE (orchestration) | P0 | ✅ Protocol pattern |
| ARA Compiler (knowledge from any source) | ASC → VER | P0 | ✅ Protocol, no Python |
| ARA Research Manager (provenance tracking) | ROUTE | P1 | ✅ Protocol |
| ARA Rigor Reviewer (self-consistency) | VER | P1 | ✅ Protocol |
| Skill category taxonomy (22 categories) | Reference for skill organization | P1 | ✅ Already aligned |
| Code generation/refactoring skills | — | P2 | 🔄 Depends on code execution |
| Experimentation skills (logging, sweeps) | — | ❌ | Python dependency |

## 4. Synthos Gap Mapping

### Current Synthos Atom Coverage vs Ecosystem

| Synthos Atom | Synthos Score | Filled By | Gap |
|:------------:|:-------------:|:----------|:----|
| **ACQ** (Knowledge Acquisition) | Strong | STORM questioning patterns, scientific-agent-skills DB access | Knowledge curation (STORM → structured article gen) |
| **EXT** (Knowledge Extraction) | Strong | scientific-agent-skills DB lookup, ARA Compiler | Multi-source extraction protocol |
| **ASC** (Association Discovery) | Moderate | STORM Knowledge Tree, ARA Compiler | Cross-pattern mind-map generation |
| **HYP** (Hypothesis Generation) | Moderate | AI-Research-SKILLs two-loop inner loop | Structured hypothesis pipelines |
| **ARG** (Argument Expression) | Strong | — | Already covered by existing atoms |
| **VER** (Viewpoint Verification) | Moderate | ARA Rigor Reviewer, Co-STORM debate | Multi-model cross-verification |
| **ROUTE** (Task Router) | Strong | AI-Research-SKILLs two-loop architecture | Dynamic orchestration patterns |

### Architecture Weaknesses in Synthos (Identified from Ecosystem)

1. **Knowledge Curation** — No skill for multi-source structured article generation (STORM's specialty)
2. **Skill Ecosystem** — No absorption of external skill packs (scientific-agent-skills, AI-Research-SKILLs)
3. **Tree Search Exploration** — No agentic tree search (AI-Scientist-v2 BFTS)
4. **Code Editing Infrastructure** — No sandboxed code agent integration (OpenHands, Aider)
5. **Findings Memory** — No persistent structured research memory (DeepScientist)
6. **Biomedical Domain Skills** — No domain-specific skills (Biomni)
7. **Peer Review Automation** — No review skill (ChatReviewer)

## 5. Absorption Queue (Priority Order)

| Priority | Project | Key Capability | Target Atom | Time Estimate |
|:--------:|:--------|:---------------|:-----------:|:-------------:|
| P0-1 | STORM | Multi-perspective persona + knowledge curation | ACQ+EXT+ASC | 1 day |
| P0-2 | scientific-agent-skills | 78 DB lookup patterns (pure API) | EXT | 1 day |
| P0-3 | AI-Research-SKILLs | Two-loop orchestration + ARA Compiler | ROUTE+HYP+VER | 2 days |
| P1-1 | AI-Scientist-v2 | BFTS tree search | HYP (new atom?) | 2 days |
| P1-2 | DeepScientist | Findings Memory + Bayesian opt | Experiment atom | 1 day |
| P1-3 | Aider/OpenHands | Sandboxed code editing | Code atom | 2 days |
| P2 | ChatReviewer | Peer review automation | VER enhancement | 1 day |

## 6. Level of Effort

| Phase | Complexity | Dependencies | Verification |
|:------|:----------:|:-------------|:-------------|
| STORM absorption | Medium | — | ACQ golden test with multi-source article gen |
| DB lookup skills | Low | — | EXT test on 5 databases |
| Two-loop orchestration | Medium-High | STORM + DB skills done first | ROUTE benchmark |
