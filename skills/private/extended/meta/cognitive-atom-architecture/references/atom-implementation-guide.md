# Atom Implementation Guide

> Concrete Python implementation patterns for the 6 cognitive atoms.
> These are the patterns validated in the Synthos 3.1 pipeline.

## File Structure

```
core/
├── __init__.py               # Package marker, version="1.0.0"
├── atom_pipeline.py          # Pipeline orchestrator
├── llm_client.py             # Shared LLM client (OpenAI/Anthropic/OpenRouter)
└── atoms/
    ├── __init__.py            # Exports AtomBase, TaskRouter
    ├── base.py                # AtomBase ABC
    ├── atom0_task_router.py   # Router (keyword-based complexity classifier)
    ├── atom1_knowledge_acquisition.py  # Multi-source search with fallback chain
    ├── atom2_knowledge_extraction.py   # Rule-based NLP extraction
    ├── atom3_association_discovery.py  # Pairwise comparison + scoring
    ├── atom4_hypothesis_generation.py  # Gap-to-hypothesis templates
    ├── atom5_argument_expression.py    # IMRaD section builder
    └── atom6_viewpoint_verification.py # Counterargument + falsification
```

## AtomBase Contract (base.py)

```python
class AtomBase(ABC):
    atom_id: int = 0
    atom_name: str = "base"

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir or os.getcwd()

    @abstractmethod
    def run(self, input_dict: Dict) -> Dict:
        """MUST return envelope via self._ok(output) or self._err(msg)."""

    def _ok(self, output: Any) -> Dict:
        return {"status": "ok", "atom_id": self.atom_id,
                "atom_name": self.atom_name, "output": output}

    def _err(self, message: str) -> Dict:
        return {"status": "error", "atom_id": self.atom_id,
                "atom_name": self.atom_name, "error": message}

    @staticmethod
    def save_json(data: Dict, path: str): ...
    @staticmethod
    def load_json(path: str) -> Dict: ...
    def safe_filename(self, prefix: str) -> str: ...
```

## CRITICAL RULES (violated → pipeline crashes)

### Rule 1: `__init__` MUST accept `output_dir`
```python
# ✅ CORRECT
def __init__(self, output_dir: str = None) -> None:
    super().__init__(output_dir=output_dir)

# ❌ WRONG — pipeline calls cls(output_dir=...) and crashes
def __init__(self) -> None:
    super().__init__()
```

### Rule 2: `run()` MUST return envelope, not raw dict
```python
# ✅ CORRECT
return self._ok({"raw_papers": papers, "metadata": meta})

# ❌ WRONG — pipeline expects envelope["output"] and envelope["status"]
return {"raw_papers": papers, "metadata": meta}
```

### Rule 3: Accept flexible input keys
The Pipeline merges all prior outputs into a flat accumulated dict.
Atom 1 receives `{"query": "..."}`, not `{"search_query": "..."}`.

```python
# ✅ CORRECT
query = input_dict.get("search_query") or input_dict.get("query", "")
if not query:
    return self._err("Missing search_query or query")

# ❌ WRONG — rigid key name
self._validate_input(input_dict, ["search_query"], ...)
```

### Rule 4: No `asyncio.run()` without cleanup
If atom1 uses academic_writer's async APIs via `asyncio.run()`, aiohttp sessions
will be left unclosed, logging warnings. Acceptable for now; fix by using
sync wrappers or proper async context management.

### Rule 5: Save outputs to outputs/atomN_output.json
```python
_OUTPUT_PATH = "/path/to/Synthos/outputs/atom1_output.json"
os.makedirs(os.path.dirname(_OUTPUT_PATH), exist_ok=True)
self.save_json(output, _OUTPUT_PATH)
```

## Pipeline Integration (atom_pipeline.py)

```python
ATOM_REGISTRY = {
    "knowledge-acquisition": ("core.atoms.atom1_knowledge_acquisition", "Atom1KnowledgeAcquisition"),
    "knowledge-extraction": ("core.atoms.atom2_knowledge_extraction", "Atom2KnowledgeExtraction"),
    # ...
}

class Pipeline:
    def run(self, query: str) -> Dict:
        routing = self.router.run({"query": query})
        atom_chain = routing["output"]["atom_chain"]

        accumulated = {"query": query}
        for atom_name in atom_chain:
            atom = self._load_atom(atom_name)  # importlib + cls(output_dir=...)
            envelope = atom.run(accumulated)    # envelope = {status, output, ...}
            if envelope["status"] == "ok":
                accumulated.update(envelope["output"])  # merge for downstream

    def _load_atom(self, atom_name):
        module_path, class_name = ATOM_REGISTRY[atom_name]
        mod = importlib.import_module(module_path)
        cls = getattr(mod, class_name)
        return cls(output_dir=self.output_dir)
```

## Atom Implementation Patterns

### Atom 1: Knowledge Acquisition (multi-source search)
- **Fallback chain**: S2 → PubMed → Crossref → arXiv (standalone fallback per source)
- **Try academic_writer first**: import from `/media/yakeworld/sda2/academic_writer/work/src/`
- **Standalone fallback**: direct `requests` calls for each API
- **Deduplication**: DOI exact match + title SequenceMatcher similarity (threshold 0.90)
- **API keys**: `SEMANTIC_SCHOLAR_API_KEY` from env var, never hardcoded
- **S2 403**: Key expired → gracefully skipped, PubMed+arXiv take over

### Atom 2: Knowledge Extraction (rule-based NLP)
- **Methodology classification**: 13 regex patterns (RCT, meta-analysis, cohort, ML, eye-tracking, etc.)
- **Finding extraction**: sentence-level pattern matching (found/show/demonstrate + significant/effect/impact)
- **Domain classification**: 9 domain patterns (neurology, psychiatry, cardiology, etc.)
- **Keyword extraction**: 4+ char words minus stopwords, top 20
- **Output format**: `{id, title, findings, year, methodology, domain, keywords}`
- **IMPORTANT**: Output keys must match what atom3 expects (`title` not `paper_title`, `findings` not `key_findings`)

### Atom 3: Association Discovery (pairwise comparison)
- **Similarity threshold**: 0.30 Jaccard keyword overlap minimum
- **Association types**: contradiction (>0.40), supplement (>0.25), evolution (year gap ≥3)
- **Scoring**: weighted by overlap, methodology difference, domain, year gap, effect direction
- **Gap detection**: rare keywords (freq=1), missing methodologies, recency checks
- **LIMITATION**: <5 papers → 0 associations. Need ≥10 papers or LLM-based semantic matching.

### Atom 4: Hypothesis Generation (template-based)
- **Sources**: gaps (highest priority) → contradictions → evolution → supplement pairs
- **Templates**: longitudinal, unexplored, reproducibility, comparative, population
- **Scoring**: novelty (0-1) based on source type + vagueness penalty; feasibility (0-1) based on study design
- **LIMITATION**: Templates produce vague hypotheses. LLM needed for specific, testable outputs.

### Atom 5: Argument Expression (IMRaD builder)
- **Structures**: introduction, methods, results, discussion, full_paper
- **Evidence matching**: keyword overlap between hypothesis text and paper abstracts (≥3 keyword matches)
- **Sections**: markdown-formatted with # headings and structured subsections

### Atom 6: Viewpoint Verification (rule-based)
- **Counterarguments**: 6 patterns (confounding, reverse causality, selection bias, measurement, publication bias, clinical significance)
- **Falsification conditions**: matched to hypothesis type (longitudinal→no change, comparison→MCID, etc.)
- **Robustness**: domain specificity, temporal stability, method dependency, cultural factors
- **Confidence**: Bayesian-inspired (prior 0.7, -0.05 per counterargument, -0.08 per weakness)
- **Verdict**: strongly_supported (≥0.7), moderately_supported (≥0.5), weakly_supported (≥0.3), insufficient_evidence

## Falsification Testing Pattern

```python
# Load atom1 output, pass to atom2, validate
atom2 = Atom2KnowledgeExtraction()
result = atom2.run({"raw_papers": atom1_output["raw_papers"]})
extracted = result["output"]["extracted_knowledge"]

# Measurable criteria
required_fields = ["id", "title", "findings", "methodology", "domain"]
completeness = sum(all(f in item for f in required_fields) for item in extracted) / len(extracted)
items_with_findings = sum(1 for item in extracted if item.get("findings") not in [["Abstract not available"], ["No extractable findings"]])

# Success: completeness >= 0.8, findings >= 2
success = completeness >= 0.8 and items_with_findings >= 2
```

## Trust Score Heuristics

| Score | Meaning | Typical atoms |
|-------|---------|--------------|
| 0.90+ | Production-ready, all tests pass | Router, atom1 |
| 0.75-0.85 | Production-ready, minor limitations | atom2, atom5, atom6 |
| 0.50-0.65 | Needs LLM enhancement, partial tests | atom3, atom4 |
| <0.50 | Not implemented or failing tests | — |

## Common Script Integration Targets

| Existing Script (in scripts/) | Size | → Atom | Integration |
|------|------|--------|-------------|
| cross_model_review.py | 65KB | atom6 | LLM multi-model review backend |
| rag_enhance.py | 55KB | atom3 | Semantic RAG for association discovery |
| lit_monitor.py | 30KB | atom1 | Continuous monitoring mode |
| adversarial_tests.py | 80KB | atom6 | Systematic adversarial test cases |
| canon_analyzer.py | 39KB | atom2 | Canonical analysis enhancement |
| trust_manager.py | 33KB | all | Trust score persistence and Bayesian updates |

## Synthos 3.1 Test Results (2026-05-09)

```
test_001 (atom1): ✅ 3 papers, multi-source
test_002 (atom2): ✅ completeness=1.00, 5/5 findings
test_003 (atom3): ⚠️ 0 associations, 7 gaps (small corpus)
test_004 (atom4): ⚠️ 5 hypotheses, 0 testable (template limit)
test_005 (atom5): ✅ 4 sections, 5 arguments
test_006 (atom6): ✅ counterarguments + falsification
test_007 (e2e):   ✅ correct routing, minimal chain

Pass rate: 71% (5/7 passing or partial)
```
