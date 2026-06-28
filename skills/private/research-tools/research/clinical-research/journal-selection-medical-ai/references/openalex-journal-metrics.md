# OpenAlex Journal Metrics for Journal Selection

> Technique for deriving journal impact metrics via OpenAlex API when `web_search` tool is unavailable.
> Practically verified 2026-06-03 for CRISP-DM Helix Pima paper journal selection.

## Problem
The `journal-selection-medical-ai` skill requires journal metrics (IF, quartile) but we don't have a `web_search` tool. Traditional IF data sources (JCR, SCImago, publisher websites) require web search.

## Solution: OpenAlex API `2yr_mean_citedness`

OpenAlex's summary_stats.2yr_mean_citedness is a reliable proxy for impact factor.

### Basic Usage

```bash
# Get journal metrics
curl -s "https://api.openalex.org/sources?filter=display_name.search:Journal+Name&per_page=3" | \
python3 -c "
import sys, json
data = json.load(sys.stdin)
for s in data.get('results', [])[:1]:
    ss = s.get('summary_stats', {})
    print(f\"{s.get('display_name','')} | works={s.get('works_count','')} | 2yr_mean={ss.get('2yr_mean_citedness','N/A')}\")
"
```

### Batch Mode (rate-limited at ~3/sec)

```bash
for name in "Journal A" "Journal B" "Journal C"; do
  echo "=== $name ==="
  curl -s "https://api.openalex.org/sources?filter=display_name.search:$(echo $name | sed 's/ /%20/g')&per_page=3" \
    2>/dev/null | python3 -c "..."
  sleep 0.3
done
```

### Interpretation

| 2yr_mean_citedness | Equivalent IF tier | Typical Q |
|:------------------:|:------------------:|:---------:|
| ≥ 10.0 | Nature/Science sub | Q1 |
| 7.0–10.0 | Top field journal | Q1 |
| 5.0–7.0 | Strong | Q1/Q2 |
| 3.0–5.0 | Moderate | Q2/Q3 |
| 1.0–3.0 | Lower | Q3/Q4 |
| < 1.0 | Weak | Q4 |

### Known Gaps

- **Patterns (Cell Press)**: OpenAlex returns 2yr_mean=10.0 but first result may be "Gene Expression Patterns" (IF ~1). Always check display_name.
- **BMC journals**: Good coverage (BMC Med Inform Decis Mak → 5.6, BMC Med Res Methodol → 4.5)
- **Nature sub-journals**: Good coverage (npj Digital Medicine → 11.4)
- **Chinese journals**: Limited coverage in OpenAlex
- **New journals**: May not have enough data for 2yr_mean

### Fallback: Search Similar Papers

When journal metrics are unavailable, search for similar papers and infer journal quality:

```bash
curl -s "https://api.openalex.org/works?search=YOUR+TOPIC&per_page=10&sort=cited_by_count:desc&select=title,primary_location,publication_year,cited_by_count" | \
python3 -c "
import sys, json
data = json.load(sys.stdin)
for w in data.get('results', []):
    loc = w.get('primary_location') or {}
    src = loc.get('source') or {}
    journal = src.get('display_name', 'N/A') if src else 'N/A'
    year = w.get('publication_year', 'N/A')
    title = w.get('title', 'N/A')[:80]
    cites = w.get('cited_by_count', 0)
    print(f'{year} | {cites:>4} cites | {journal:45s} | {title}')
"
```

### Practical Verification: Pima Paper Journals (2026-06-03)

| Journal | 2yr_mean | Notes |
|:--------|:--------:|:------|
| npj Digital Medicine | 11.4 | Reach target |
| Patterns (Cell Press) | 10.0 | Perfect topic match (Kapoor2024 venue) |
| Artificial Intelligence in Medicine | 7.9 | Q1 methodology venue |
| BMC Med Inform Decis Mak | 5.6 | Current paper target |
| J Biomedical Informatics | 5.5 | Q2 |
| Comput Meth Prog Biomed | 5.0 | Q2 methodology |
| Scientific Reports | 4.4 | Broad safety |
| Eng Tech & Appl Sci Res | 2.2 | Low IF, similar paper already published |
