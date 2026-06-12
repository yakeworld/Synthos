# Full-Text → Structured Knowledge Extraction Pipeline

## Problem

Abstracts omit critical details that change research conclusions. Proven in this session: 5 ADHD+eye-tracking papers analyzed with abstract-only vs full-text extraction.

## What abstracts miss (empirical findings)

| Detail Type | Abstract | Full Text | Impact |
|-------------|----------|-----------|--------|
| EEG contribution | Not mentioned | "EEG contributed zero features to final model" | Contradicts multi-modal assumption |
| Hardware type | "Portable eye tracking" | "Samsung Galaxy Tab 7+ with SeeSo SDK, 2D gaze, chin rest at 50cm" | It's NOT head-mounted 3D |
| Sample characteristics | "n=56 ADHD, 79 controls" | "45 males out of 56 ADHD, all Korean, excluded ASD" | Gender bias + ethnicity limitation |
| Exclusion criteria | Not mentioned | "Excluded ASD, bipolar, psychotic disorders" | Comorbidity gap invisible |
| Statistical nuance | "76.3% accuracy" | "AUC not significantly different from ATA (p=0.419) or Stroop (p=0.235)" | ET not better than simpler tools |

## Pipeline Steps

### Step 0: Load prior knowledge first
Before extracting, you need the context of WHAT to look for. Reference the user's research focus, known gaps, and existing hypotheses from the project context (e.g., NSFC grant goals, prior literature reviews).

### Step 1: Download PDFs
Use the 6-strategy download chain documented in `research-paper-search`:
- OA URL → arXiv → PMC → Unpaywall → DOI → Sci-Hub
- Record `pdf_status` for transparency
- For medical research: Frontiers, Nature/Springer, and JMIR are reliably open-access

### Step 2: Convert to Markdown
```python
import pymupdf
doc = pymupdf.open("paper.pdf")
text = ""
for page in doc:
    text += page.get_text() + "\n\n---\n\n"
with open("paper.md", "w") as f:
    f.write(f"# {title}\n\n{text}")
```

### Step 3: Read in structured order
Do NOT read linearly. Read in this priority order:

| Order | Section | What to extract |
|:-----:|---------|-----------------|
| ① | **Methods** | Sample size, hardware, paradigm, analysis method, exclusion criteria |
| ② | **Results** | Exact accuracy/AUC/p-values, which variables were significant, which were NOT |
| ③ | **Discussion** | Author's own limitations, "future work" suggestions, unexpected findings |
| ④ | **Abstract + Intro** | Check that abstract claims match full-text data |

### Step 4: Extract structured KnowledgeItem

For each paper, extract:

```json
{
  "id": "DOI",
  "title": "Full title",
  "full_text_extracted": true,
  "key_findings": [
    "Concrete quantitative findings from Results section",
    "Include null/negative findings — often more important than positive ones"
  ],
  "methodology": "methodology_type",
  "methods_detail": "Full text of methods: hardware, n, paradigm, analysis",
  "domain": "research_domain",
  "limitations": [
    "Exclusion criteria that limit generalizability",
    "Methodological limitations only visible in full text"
  ],
  "key_themes": ["theme1", "theme2"],
  "sample_size": 135,
  "year": 2024,
  "evidence_level": "cross_sectional | rct | meta_analysis | etc."
}
```

### Step 5: Cross-check contradictions

After all papers are extracted, scan for contradictions that are ONLY visible in full text:

- Does Paper A claim X while Paper B's full text shows NOT-X?
- Does a paper's abstract promise more than the Results deliver?
- Are hardware/paradigm differences that would explain discrepant results?

**Real example from ADHD-ET session:**
- Abstract: "Portable eye tracking achieves 76.3% accuracy"
- Full text: "Chin-rested 2D tablet at 50cm, AUC NOT significantly different from simpler ATA test (p=0.419)"
- Contradiction: "Portable" is misleading — it's not wearable/3D

### Pitfalls

1. **Abstract overpromise**: Papers often emphasize best result in abstract but bury limitations in Discussion
2. **Sample size inflation**: Abstract says "n=135" but full text may reveal n after exclusions is smaller
3. **"Portable" ≠ "wearable"**: Always verify hardware details from Methods section, not abstract terminology
4. **Comorbidity exclusion**: If a study excludes all comorbidities, its "95% accuracy" is clinically meaningless — only visible in full text exclusion criteria
5. **Forced classification framing**: Some papers frame modest AUC (e.g. 0.70) as "promising" when it's actually barely above chance — you need full text to assess this

### When to skip full-text

Only skip when:
- PDF download fails (all 6 strategies exhausted)
- PDF is scanned/image-based AND marker-pdf not installed (≥5GB needed)
- The only available data is a structured abstract (conference proceedings without full paper)
