# Multi-API Probe Sequence: Finding PINNIES (July 2026)

## Scenario
H01 paper needed 3 key references: PINNIES (arXiv:2024.PINNIES), SVD-NO (arXiv:2025.SVD-NO), iFOL (arXiv:2025.iFOL). None had real arXiv IDs — they were hypothesis-phase placeholders.

## Probe Sequence (exact queries and results)

| API | Query | Result | Diagnosis |
|:----|:------|:-------|:----------|
| **Semantic Scholar** | `PINNIES integral operator tensor vector product` | `data=0` (HTTP 200) | Query too specific |
| **Semantic Scholar** | `neural integral operator tensor vector PINN` | `data=0` (HTTP 200) | Still too niche |
| **Semantic Scholar** | `SVD parameterized kernel operator neural` | `data=0` (HTTP 200) | Placeholder ID → no match |
| **Semantic Scholar** | `implicit operator learning PDE` | 5 results, none correct | Not finding target |
| **arXiv API** | `all:"integral operator" AND all:"tensor vector" AND all:"PINN"` | `totalResults=0` | Combinatorial query too specific |
| **OpenAlex** | `search=integral+operator+efficient+tensor+vector+product+PINN` | 5 noisy results | Found Cuomo2022, hp-VPINNs etc — noise |
| **OpenAlex** | `search=PINNIES+integral+operator+efficient+tensor` | **1 result found** | ✅ **arXiv 2409.01899** |

## Key Takeaway

**Only OpenAlex found it.** SS returned 0 (not 429 — just no match). arXiv returned 0 (too specific). OpenAlex's broader text matching engine found PINNIES with a query that failed everywhere else.

## Pattern for Future Sessions

When searching for a paper and every API returns 0:
1. Check if the arXiv ID is a hypothesis-phase placeholder (looks like `arXiv:2025.SOMETHING`)
2. If yes → extract the descriptive words (e.g. "PINNIES integral operator efficient tensor") and search OpenAlex
3. If OpenAlex also fails → the paper may not exist → mark as "placeholder, not blocking" in README
4. The 3 other hypothesis references (SVD-NO, iFOL) never resolved — they are concept names, not real papers

## Diagnosis Table for API Responses

| Response | Meaning | Next Action |
|:---------|:--------|:------------|
| `data=0`, HTTP 200 | Search term too specific or paper doesn't exist | Simplify query, try OpenAlex |
| `error: rate limit exceeded`, HTTP 429 | Rate limited | Switch API, wait 60s+ |
| `totalResults=0`, valid XML/JSON | No match in index | Try different search schema |
| 500 Internal Server Error | Backend error (common in OpenAlex with booleans) | Simplify to phrase query |
| Empty body, hang >30s | Service down | Skip this API entirely |
