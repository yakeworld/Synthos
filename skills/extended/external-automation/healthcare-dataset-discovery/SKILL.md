---
name: healthcare-dataset-discovery
description: 'Public healthcare dataset discovery — known accessible sources, dead sources, and API patterns for medical AI research.'
version: 1.0.0
allowed-tools:
- terminal
- read_file
- write_file
metadata:
  synthos:
    priority: P2
    atom_type: tool
    description: Public healthcare dataset discovery — known accessible sources, dead sources, and API patterns for medical AI research.
    signature: "medical_domain: str -> dataset_results: list[Dataset] -> dataset_results: list[Dataset] (name, source, url, description, access_type, relevance)"
    related_skills: [dataset-discovery, knowledge-acquisition, knowledge-extraction, healthcare-dataset-discovery, dataset-discovery]

---



# Healthcare Dataset Discovery

## Discovery Protocol

When searching for public healthcare datasets:

1. **OpenML** → Primary source. Use `/api/v1/json/data/list` (not `/limit/50` pattern). Response structure: `{"data": {"dataset": [...]}}` with `did`, `NumberOfInstances`, `NumberOfFeatures` fields.
2. **HuggingFace** → `/datasets-server.huggingface.co/search?query={keyword}&limit=50` (returns 422 on this server — may need alternate access)
3. **Kaggle** → Requires authentication. Check `/datasets?search={keyword}` but expect paywalls.
4. **UCI Archive** → Many datasets removed. Check `archive.ics.uci.edu` — expect 404 for popular datasets.

## Known Dataset Status

### ✅ ACCESSIBLE
- **OpenML Cardiovascular-Disease-dataset** (DID=45547): 70,000 records, 13 features, 50/50 CVD class balance. Features: age, gender, height, weight, ap_hi, ap_lo, cholesterol, gluc, smoke, alco, active, cardio. Download via `https://www.openml.org/data/v1/download/{file_id}`.

### ❌ UNAVAILABLE
- **UCI Healthcare Dataset** (healthcare-dataset-stroke-data.csv): Removed from UCI. All GitHub mirrors dead (dsrscientist, codeheroku, krishnaik06, etc.). HuggingFace: 404. Kaggle: requires auth.
- **UCI Breast Cancer** (WDBC): Also moved/removed from UCI.

## API Quirks

- OpenML `list` endpoint returns 6,400+ datasets. Search locally by name/description.
- OpenML detail API returns `{"data_set_description": {...}}` (NOT `{"data": {"dataset": {...}}}`).
- OpenML `limit/5` works but `limit/500` returns empty — use `/api/v1/json/data/list` without limit.
- Crossref `query=` param works (not `search=`). Use `+` for spaces or `quote_plus()`.
- PubMed eSearch requires `+` for spaces, not URL encoding.

## Reference

- See `references/uci-stroke-404-session.md` for detailed investigation transcript