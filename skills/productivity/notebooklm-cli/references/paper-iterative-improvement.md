# Iterative Paper Improvement Workflow (NotebookLM + Synthos)

A repeatable multi-cycle process for developing a paper from a NotebookLM notebook's existing sources, using Synthos cognitive atom methodology and targeted literature gap-filling.

## When to use
- User has a NotebookLM notebook with teaching/research materials and wants to produce a publishable paper
- The notebook needs enrichment with recent literature
- The paper needs iterative improvement cycles to reach SCI quality

## Workflow Overview

```
PHASE 1: Initial Paper Draft
  ① Audit notebook content (source list → categorize)
  ② Search supplementary literature (3-5 topics, 5 papers each)
  ③ Upload findings to notebook
  ④ Draft paper using Synthos methodology
  ⑤ Upload draft to notebook

PHASE 2: Cycle N (repeat 2-3 times)
  ① Audit current draft for gaps (16-dimension checklist below)
  ② Target literature gap search for specific weaknesses
  ③ Create summary files → upload to notebook
  ④ Revise paper (fix structure, missing sections, references)
  ⑤ Upload revised draft

PHASE 3: Final Quality Audit
  ① Word count, reference count, DOI completeness
  ② Missing author info in references
  ③ Abstract section completeness (Background/Objective/Methods/Results/Conclusion)
  ④ "et al." vs full author list compliance per target journal
```

## 16-Dimension Audit Checklist for Each Cycle

| # | Dimension | What to Check |
|---|-----------|---------------|
| 1 | Methods section | Is framework development methodology explicit? |
| 2 | Case study / worked example | Concrete demonstration of framework applied? |
| 3 | Figures / diagrams | Architecture, DAG, workflow visualization? |
| 4 | Related work comparison | Compare with existing frameworks in a table? |
| 5 | Full author lists | All refs have complete author info? |
| 6 | Missing theory | SRL (Zimmerman), CLT (Sweller), TPACK? |
| 7 | AI ethics section | Ethical considerations addressed? |
| 8 | Recent RCTs | 2024-2026 empirical studies included? |
| 9 | AI agent specification | What model, tools, prompts per atom? |
| 10 | Journal target alignment | Structure matches target journal scope? |
| 11 | Novelty statement | What distinguishes from existing frameworks? |
| 12 | Abstract quantitative framing | Numbers, effect sizes, not just qualitative? |
| 13 | Research agenda | Testable hypotheses for future validation? |
| 14 | Limitations section | Honest assessment of weaknesses? |
| 15 | Reference year range | ≥80% from 2020-2026 (except foundational) |
| 16 | DOI verification | Every reference has a valid DOI? |

## Literature Gap-Filling Search Strategy

Search for papers targeting specific gaps, using Semantic Scholar API:

**Gap A:** Self-Regulated Learning + Generative AI
- Search: "self-regulated learning AND generative AI" OR "metacognition AND AI AND education"
- Key: Zimmerman's SRL model (forethought→performance→self-reflection)

**Gap B:** AI Education Frameworks in Medical/Clinical Contexts
- Search: "PROBAST AI" OR "CLAIM AI checklist" OR "AI competency framework medical education"
- Key: PROBAST+AI (Moons 2025), CLAIM 2024 (Tejani), MI-CLAIM (Norgeot 2020)

**Gap C:** Cognitive Load Theory + AI
- Search: "cognitive load theory AND artificial intelligence education"
- Key: Sweller's CLT + AI-adaptive learning

**Gap D:** AI Ethics in Medical Education
- Search: "AI ethics medical education" OR "responsible AI healthcare training"
- Key: Weidener & Fischer's principle-based approach

**Gap E:** LLMs as Educational Tools (Recent RCTs)
- Search: "ChatGPT medical student learning outcomes RCT" OR "LLM educational tool assessment"
- Key: Prefer RCTs (2024-2026) over observational studies

## Creating Summary Files for Upload

Each supplementary paper should be a Markdown file with this structure:

```markdown
# Full Paper Title (Year)

**Authors:** Full, comma-separated author list
**Year:** 2024
**Journal:** Journal Name
**DOI:** 10.xxxx/xxxxx
**Citations:** N
**Type:** RCT / Systematic review / Meta-analysis / Framework proposal

## Summary
3-5 sentences: key finding, methodology, and how it's relevant.

## Relevance to Paper
1-2 sentences: specific gap this paper fills in the draft.
```

Upload all summary files to the notebook:
```bash
for f in /path/to/summaries/*.md; do
  notebooklm source add "$f" && sleep 2
done
```

## Reference Fixing Rules

By end of Cycle 2, every reference must have:
- Full author names (no "et al." for ≤10 authors; "et al." acceptable for >10 after listing first 10)
- Journal name in standard abbreviation
- Year, volume, pages
- Valid DOI (test: `curl -sI https://doi.org/10.xxxx/xxxxx | head -1`)
- For arXiv: use the arXiv ID, not a DOI
- For books: publisher, year, ISBN if available

## Storage Note

Paper drafts are uploaded as Markdown sources to NotebookLM. Keep the latest two versions:
- `scf_paper_v2.md` (previous)
- `scf_paper_final.md` (current)

Delete older versions from the notebook to avoid confusion:
```bash
notebooklm source list | grep "scf_paper_v1"
notebooklm source delete -n <uuid>
```
