# ClinicalTrials.gov API v2

## Base URL (v2 API)
https://clinicaltrials.gov/api/v2/

## Full Studies Search
```
GET /studies?query.term=<query>&pageSize=10&format=json
```

**Examples:**
```bash
curl -s "https://clinicaltrials.gov/api/v2/studies?query.term=ADHD+eye+tracking&pageSize=5&format=json"
curl -s "https://clinicaltrials.gov/api/v2/studies?query.term=Parkinson+balance&pageSize=5&format=json"
```

## Study by NCT ID
```
GET /studies/<nct_id>?format=json
```

**Example:**
```bash
curl -s "https://clinicaltrials.gov/api/v2/studies/NCT01234567?format=json"
```

## Filter Parameters
- `query.term` — Search terms (boolean: `+AND+`, `+OR+`)
- `query.cond` — Condition/disease
- `query.intr` — Intervention/treatment
- `query.titles` — Search only title fields
- `filter.overallStatus` — Status filter: RECRUITING, ACTIVE_NOT_RECRUITING, COMPLETED, etc.
- `filter.phase` — Phase filter: EARLY_PHASE1, PHASE1, PHASE2, PHASE3, PHASE4
- `pageSize` — Results per page (max 100)
- `pageToken` — Pagination token

## Key Response Fields
- `studies[].protocolSection.identificationModule.nctId` — NCT ID
- `studies[].protocolSection.identificationModule.briefTitle` — Title
- `studies[].protocolSection.statusModule.overallStatus` — Status
- `studies[].protocolSection.designModule.phases[]` — Trial phases
- `studies[].protocolSection.eligibilityModule.healthyVolunteers` — Healthy volunteers?
- `studies[].protocolSection.conditionsModule.conditions[]` — Conditions
- `studies[].protocolSection.interventionsModule.interventions[].name` — Interventions

## Rate Limit
No documented rate limit. Use responsibly (~1 req/sec).
