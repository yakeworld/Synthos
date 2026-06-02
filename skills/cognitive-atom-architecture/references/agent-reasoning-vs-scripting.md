# Agent Reasoning vs Scripting — Executing Cognitive Atoms

## The Core Lesson

> **When a SKILL.md says to extract, analyze, associate, hypothesize, write, or verify — the Agent should THINK, not SCRIPT.**

Scripts (Python, bash, or otherwise) are for **data transformation** — merging JSON, reformatting output, counting, filtering, arithmetic. They are NOT for **cognitive work** — reading a paper and understanding its methodology, comparing two papers and finding their relationship, generating a novel hypothesis from a research gap.

## Wrong Way (what NOT to do)

```python
# BAD: Agent writes a Python script with keyword matching to classify methodology
def classify_methodology(title, abstract):
    text = (title + ' ' + abstract).lower()
    if any(k in text for k in ['machine learning', 'deep learning', 'cnn']):
        return 'machine_learning'
    if any(k in text for k in ['review', 'systematic']):
        return 'systematic_review'
    ...
```

This is **rule-based NLP** — it's brittle, misses context, and defeats the purpose of having an AI Agent. The Agent has general intelligence to *understand* what a paper is about. Using keyword matching means the Agent is dumbing itself down to the level of a 1970s search algorithm.

## Right Way (what TO do)

```python
# GOOD: Agent reads the paper and reasons about it
# (no Python script — just thinking)
extracted.append({
    "id": "10.3389/fpsyt.2024.1337595",
    "key_findings": [
        "33 eye-tracking features across 5 tasks discriminate ADHD from TDC",
        "Soft voting model achieves 76.3% accuracy using eye-tracking alone",
        "Eye-tracking AUC not significantly different from ATA or Stroop test"
    ],
    "methodology": "machine_learning_cross_sectional",
    # ^^ I determined this by reading the abstract and seeing:
    #   - They collected cross-sectional data (ML and control groups)
    #   - They used ML to select features and build a classifier
    #   → It's a cross-sectional ML study
    "domain": "pediatric_psychiatry",
    # ^^ Mean age 8.38, recruiting children, ADHD diagnosis
    "limitations": [
        "Binary ADHD vs TDC only, no subtype classification",
        "Moderate sample (n=135), single-site Korean population"
    ],
    # ^^ I reasoned about what's missing from the study design
    "key_themes": ["portable_diagnosis", "ml_screening", "saccade_biomarkers"],
    # ^^ I identified the key concepts from the content
})
```

## When Scripts ARE Acceptable

Scripts are for **mechanical** operations, not **cognitive** operations:

| Acceptable (data transformation) | Unacceptable (cognitive work) |
|----------------------------------|-------------------------------|
| `python3 -c "import json; ..."` to merge two JSON files | Python script that classifies paper methodology by keyword matching |
| Count papers per source | Python script that computes Jaccard similarity for association discovery |
| Filter papers by year | Python script that generates hypothesis text from templates |
| Sort by confidence score | Python script that writes argument paragraphs |
| Validate JSON schema | Python script that looks up counterarguments from a hardcoded list |
| Reformat output | Python script that extracts "key findings" using regex |

**Test**: Does the script replace something you (the Agent) could do by thinking? If yes, don't write it. If the script does something you can't do mentally (process 1000 rows of CSV, make 50 API calls rapidly), write it.

## Session History (2026-05-10): How This Lesson Was Learned

The user ran a full Synthos pipeline test. For each atom, I defaulted to writing Python scripts:

1. **knowledge-extraction**: Wrote a Python script with keyword matching to classify methodology, domain, limitations, and themes of 25 papers
2. **association-discovery**: Wrote a Python script computing Jaccard similarity between paper themes
3. **hypothesis-generation**: Wrote a Python script with hardcoded hypothesis texts
4. **argument-expression**: Wrote a Python script with hardcoded paragraphs
5. **viewpoint-verification**: Wrote a Python script with hardcoded counterarguments

User's reaction: 

> "研究空白和科学假设为什么是编程提取的？不应该是AI提取的吗？为什么每一个步骤都是需要编程实现？"

This is the core criticism: **an AI Agent should THINK, not SCRIPT**. The whole point of Synthos is that Agent reasoning IS the cognitive engine. Offloading the thinking to Python scripts means you've rebuilt the old Python pipeline in /tmp/.

### Corrected Approach (Same Session)

After the correction, I re-did knowledge-extraction by:
1. Reading the full text of 4 PDFs (57K, 56K, 61K, 66K chars each)
2. Thinking about each paper's methodology, findings, limitations
3. Writing my reasoned analysis directly as JSON output

And association-discovery by:
1. Looking at all 25 papers' themes, methods, domains, years
2. Reasoning about their relationships: supplements (same topic, different aspect), evolutions (temporal progression), contradictions (conflicting findings)
3. Writing my reasoned associations directly

**No Python scripts were used for cognitive work.** Only one `python3 -c "import json"` call to read the input file and save the output.

### The /tmp/ Trap (Second Correction)

Even after the fix, I immediately fell back to writing a script for argument-expression:

> "为什么又开始编程了？"

The `/tmp/` directory is not a shielding mechanism. Writing `python3 /tmp/arg_expr.py` is quantitatively different from `core/atoms/atom5_argument_expression.py` only in location — qualitatively, both are Python code doing the Agent's thinking.

### 5. PDF→Markdown before extraction

When full-text PDFs are available, **convert them to Markdown first** before reading. Raw PDF text extraction (pdfminer) produces scrambled output due to multi-column layouts. Use `pymupdf4llm` which handles layout detection, produces clean `##` headings, and preserves paragraph order:

```bash
pip install pymupdf4llm
python3 -c "
import pymupdf4llm
md = pymupdf4llm.to_markdown('paper.pdf')
with open('paper.md', 'w') as f:
    f.write(md)
"
```

The Markdown version is readable by both Agent and human and makes knowledge extraction significantly more accurate. This is a **mechanical preprocessing step** — acceptable to script.

### 6. Full text > Abstract > Title

Knowledge extraction must respect the **information hierarchy**:

| Source | Priority | What you can extract |
|--------|----------|---------------------|
| Full text (Markdown) | ✅ Always read if available | Specific statistical values, task descriptions, sample demographics, explicit limitations |
| Abstract | ✅ Only if full text unavailable | Main findings, methodology type, domain |
| Title only | ⚠️ Last resort | Core topic, sometimes methodology hint |

If a PDF is downloaded (step in knowledge-acquisition), **convert it to Markdown immediately** and read it for extraction. Abstract-only extraction misses critical details: Wiebe et al. (2024) abstract says "EEG did not contribute" — full text reveals *how* (MRMR selected 0 EEG features from 76), *quantitatively* (all-feature 0.69 → 11-feature 0.81 test accuracy), and *which* features succeeded (CPT + actigraphy + eye-tracking + experience sampling). Abstract-only wouldn't catch the distinction between "EEG doesn't help" and "EEG in VR specifically doesn't help."

### 1. The /tmp/ Trap
Writing scripts in /tmp/ instead of core/ doesn't make them any less Python-dependent. The Agent should not write scripts at all for cognitive tasks.

### 2. "But I'm good at Python" Fallacy
The Agent is better at reasoning than at writing Python. Don't fall back to scripting because it feels familiar or efficient. The thinking is the work.

### 3. Volume Pressure
25 papers feels like a lot. The temptation is to write a script to process them all. Resist it. Read the key papers in full text, reason about the rest from abstracts. Quality over mechanical quantity.

### 4. The keyword matching illusion
Keywords like "machine learning" in an abstract → that's a clear match. But what about a paper that uses SVM without mentioning "machine learning"? Or a study described as "data-driven" that should be classified as ML? Only human-level reading catches these nuances.
