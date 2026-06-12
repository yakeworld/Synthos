# OpenML API Behavior — 2026-06-06

## Response Structure
OpenML `/api/v1/json/data/list` returns:
```json
{"data": {"dataset": [
  {"did": 2, "name": "anneal", "NumberOfInstances": 898, ...}
]}}
```
- ID is `did` (NOT `id`)
- Data is in `data.dataset` (NOT `data.data`)
- Use `/api/v1/json/data/list` without limit parameter for full list
- `/limit/5` returns 0 datasets — don't use this pattern
- Detail API returns `{"data_set_description": {...}}` (NOT `{"data": {"dataset": {...}}}`)

## Known Accessible Datasets
- Cardiovascular-Disease-dataset (DID=45547): 70,000 records, 13 features, ARFF format
- Download: `https://www.openml.org/data/v1/download/{file_id}`

## API Quirks  
- Accept-Encoding must be `identity` (not gzip)
- 412 Precondition Failed on some endpoints (requires specific headers)
- Name search endpoint returns 412
- Must use GET, not POST, for data listing
- Full list endpoint: `/api/v1/json/data/list` returns 6,400+ datasets
- Search locally by name/description after fetching full list