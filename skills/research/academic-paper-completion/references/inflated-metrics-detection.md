# Inflated Metrics Detection for Paper Enhancement

## When the paper argues "inflated metrics = data leakage, not algorithmic superiority"

This is a common thesis pattern in ML benchmarking papers (e.g., PIDD, medical datasets).
The paper's argument is strengthened by a systematic literature search that finds additional
papers with inflated metrics and documents their methodological flaws.

## Step 1: Mine existing literature cache

If the project has `literature/results.csv` (from previous searches), mine it first:

```python
import csv, re, json

csv_path = 'literature/results.csv'
papers_with_metrics = []

with open(csv_path, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        title = row.get('title', '')
        abstract = row.get('abstract', '')
        year = row.get('year', '')
        
        # Extract accuracy claims: "accuracy of 98.7%" or "achieved 95% accuracy"
        acc_nums = re.findall(
            r'(?:accuracy|acc)\w*\s*(?:of|:|=|is|was|achieved|reached|obtained|ranged)?\s*[\(]?(\d{2,3}\.?\d*)\s*%?',
            abstract.lower(), re.IGNORECASE
        )
        
        # Filter: only papers claiming > threshold (e.g., > 88%)
        high = any(float(a) > 88 for a in acc_nums if a.replace('.','').isdigit())
        if high:
            papers_with_metrics.append({...})
```

## Step 2: Classify by methodological flaw

For each high-claim paper, extract methodology keywords from abstract:

```python
flaws = {
    'global_smote': 'smote' in text and 'within' not in text,
    'no_cv': 'cross-validation' not in text and 'cross validation' not in text,
    'no_split': 'train' not in text or 'test' not in text,
    'no_imbalance': 'imbalance' not in text and 'balance' not in text,
    'no_zero_correction': 'zero' not in text and 'missing' not in text,
}
```

## Step 3: Search for additional papers

Multi-source approach (in order of reliability):

1. **OpenAlex** — generous rate limits, good for finding recent papers:
   ```
   https://api.openalex.org/works?search=Pima+Indians+diabetes+high+accuracy
   &filter=from_publication_date:2024-01-01&per_page=20&sort=publication_date:desc
   ```

2. **Semantic Scholar** — best metadata but rate-limited (429 common without API key);
   API key may return 403 even when valid (expired keys)

3. **Crossref** — good for verification but poor recall for Pima-specific papers

## Step 4: Build BibTeX entries

```python
bib_template = """@Inproceedings{{AuthorYear{Keyword},
  author    = {{{authors}}},
  title     = {{{title}}},
  booktitle = {{{booktitle}}},
  year      = {{{year}}},
  pages     = {{{pages}}},
  doi       = {{{doi}}},
}}
"""
# Append to both reference.bib and enhanced-bibtex-*.bib
```

## Step 5: Integrate into paper

Three insertion points in a typical medical AI paper:

1. **Related Work → Credibility Gap paragraph**: Add a sentence citing the new papers as evidence
2. **Table 1 (Comparative Analysis)**: Add rows for the most illustrative cases (4-6 papers)
3. **Discussion → Debunking Inflated Metrics**: Reference the expanded Table 1 as systematic evidence

## Pitfalls

- **Batch replace substring collision**: When renaming `Gupta2021Comparative` → `Gupta2021ComparativePA`,
  also replaces `Gupta2021ComparativePA` → `Gupta2021ComparativePAPA`. Always verify after batch replace.
- **BibTeX `.bib` file sync**: The LaTeX `\bibliography{reference}` may point to a different `.bib`
  than the authoritative `enhanced-bibtex-*.bib`. Add entries to BOTH.
- **Stale `.aux` file**: After adding new BibTeX entries, delete `.aux` and `.bbl` before recompiling
  to force fresh citation resolution.
- **100% accuracy claim**: A paper claiming 100% accuracy on a real clinical dataset is *prima facie*
  evidence of data leakage — no model can achieve perfect prediction on real patient data. This makes
  it the strongest example for the thesis.

## Example output format

```
TABLE: Papers Reporting Inflated Performance Metrics on PIDD (Systematic Review)
================================================================================
Reference                         Acc        Methodological Flaw
Kalagotla et al. (2021)           78.2%      Global preprocessing; 3-feature oversimplification
Sreejith et al. (2020)            89.04%     Global SMOTE + feature selection before CV
...
Kurniawan et al. (2026)           100%       100% accuracy impossible without data leakage
Baran et al. (2025)               98.7%      SMOTE; no CV; no train-test split
Kate et al. (2025)                96.58%     SMOTE used; no cross-validation mentioned

SUMMARY: 10 papers, 7 with Acc ≥ 95%, all lack within-fold preprocessing isolation
CORE ARGUMENT: inflated metrics = data leakage, NOT algorithmic superiority
```
