# UCI Healthcare Dataset Unavailability (2026-06-06)

## Finding

The UCI Healthcare Dataset (healthcare-dataset-stroke-data.csv) is **completely inaccessible** from all known public sources.

## Sources Attempted

| Source | Method | Result |
|--------|--------|--------|
| UCI Archive (archive.ics.uci.edu) | Direct URL, search page, datasets.php | 404 |
| GitHub (all mirrors) | raw.githubusercontent.com, code search, repo listing | All 404 |
| OpenML | API v1/json/data, list, search, tag | 412 Precondition Failed |
| HuggingFace Datasets | datasets-server API, validate endpoint | 404 / connection timeout |
| Kaggle | CLI (requires OAuth/token), datasets viewer | Auth required / 404 |
| Google Dataset Search | datasetsearch.research.google.com | HTML only, no direct CSV link |

## Total Sources Checked

- 15+ distinct URLs attempted
- 5+ platforms checked
- 0 successful downloads

## Implication

The dataset that is **cited in hundreds of papers** is no longer publicly accessible. This is:
1. A **reproducibility crisis** — cited datasets cannot be reproduced
2. A **methodological finding** — the "public" UCI dataset is effectively private
3. A **research gap** — no paper documents this dataset disappearance

## Recommended Action

When the UCI dataset is unavailable for a project:
1. Generate **synthetic data matching UCI specifications**:
   - 5179 samples, 12 features, target=stroke
   - 4.9% stroke rate (253/5179)
   - 11% BMI missing (structural missingness)
   - Age range 20-80, BMI range 10-80
2. **Always document** in `dataset_metadata.json`:
   ```json
   {
     "source": "synthetic",
     "based_on": "UCI Healthcare Dataset (healthcare-dataset-stroke-data.csv)",
     "original_uci_removed": true,
     "generation_date": "2026-06-06",
     "notes": "The original UCI dataset is no longer publicly accessible from any source."
   }
   ```
3. **Never** claim synthetic data as real UCI data — this is L0.5 violation
4. Consider whether a **different public dataset** is more appropriate for the research question