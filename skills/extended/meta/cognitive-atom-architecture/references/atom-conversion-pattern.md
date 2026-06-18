# Atom Conversion Pattern: Python → Agent-native SKILL.md

> Worked example from the Synthos v4.0→v4.1 refactoring. Atom1 (knowledge-acquisition) was 939 lines of Python; it became a 210-line SKILL.md that produces better results.

## The Problem

In v4.0, Synthos claimed "Agent IS the cognitive engine" but atom1 was still 939 lines of Python doing multi-source paper search. The MECHANICAL/COGNITIVE split created a blind spot: mechanical atoms bypassed the Hermes skill system entirely, hiding design decisions in code.

## The Conversion (Step by Step)

### Step 0: Audit the Python code

What did the Python atom1 do?
1. Search S2 via requests/aiohttp (34 lines)
2. Search PubMed via E-utilities (~40 lines)
3. Search Crossref (~30 lines)
4. Search arXiv (~25 lines)
5. Multi-source coordinator + dedup (~50 lines)
6. PDF download with 6-strategy chain (~100 lines)
7. Caching, error handling, rate limiting (~50 lines)
8. CLI entry point (~30 lines)

Total: ~400 lines of actual logic + ~540 lines of boilerplate (imports, error handling, async setup, class wrapping).

### Step 1: Map Python logic → Agent tools

| Python function | Agent equivalent |
|----------------|-----------------|
| `import requests; requests.get(url)` | `terminal: curl -s <url>` |
| `aiohttp.ClientSession().get()` | `terminal: curl -s <url>` |
| `JSON parsing` | `terminal: python3 -c "..."` or Agent reasoning |
| `asyncio.gather()` | `delegate_task` for parallel execution |
| `PDF download` | `terminal: curl -L -o file.pdf <url>` |
| `try/except` | Agent judges response code + content |
| `class Atom1KnowledgeAcquisition` | Not needed — Agent loads SKILL.md directly |

### Step 2: Write the SKILL.md

Key changes in frontmatter:
```yaml
# BEFORE (mechanical)
synthos_atom_type: "mechanical"
allowed-tools: Read Write

# AFTER (cognitive)
synthos_atom_type: "cognitive"
allowed-tools: terminal web delegate_task Read Write
synthos_depends_on: "semantic-scholar, pubmed, arxiv, openalex, research-paper-search"
```

Body structure:
1. Overview — what this atom does
2. Input contract — field names, types, defaults
3. Output contract — exact JSON schema with example
4. Execution steps — numbered, with curl commands for each API
5. Quality requirements — measurable criteria
6. Known pitfalls — from the Python code's error handling patterns
7. Change log

### Step 3: Update the pipeline

In `atom_pipeline.py`'s ATOM_REGISTRY:
```python
# BEFORE
"knowledge-acquisition": {
    "atom_type": "MECHANICAL",
    ...
}

# AFTER
"knowledge-acquisition": {
    "atom_type": "COGNITIVE",
    ...
}
```

Remove:
- `importlib` import and class loading
- Short-circuit checks tied to atom1
- `atom1_output` variable
- Any Python-specific error handling

The pipeline now treats all atoms uniformly: generate prompt → save to disk → Agent executes later.

### Step 4: Deprecate the Python file

Add a deprecation header and keep as reference:
```python
"""
[DEPRECATED v4.0] Replaced by skills/knowledge-acquisition/SKILL.md.
Kept as reference for API endpoints, field formats, fallback chain order.
"""
```

### Step 5: Clean up

- Remove `core/` directory entirely (once ALL atoms are converted)
- Remove `run_pipeline.py` (Agent is the CLI)
- Update evolution-state.json
- Update CHANGE_LOG.md in the atom's references/

## Results

| Metric | Before (Python) | After (SKILL.md) |
|--------|----------------|-----------------|
| Lines of code | 939 | 210 |
| Search sources | S2 + PubMed + arXiv | S2 + PubMed + arXiv + OpenAlex + Crossref |
| Add new source | Edit Python + redeploy | Edit SKILL.md + re-run |
| Error handling | try/except in one place | Per-source in curl response handling |
| Hermes skills used | 0 | 5 (semantic-scholar, pubmed, arxiv, openalex, research-paper-search) |

## Key Lesson

> If the Agent can execute a task with its built-in tools + Hermes skills, it belongs in a SKILL.md, not Python code. Every line of Python is a line that bypasses the skill system.
