# PubMed API Key Casing Reference

## Critical: all JSON keys are lowercase

NCBI eUtils JSON API returns keys in lowercase. The common mistakes:

| Correct | Wrong | Impact |
|---------|-------|--------|
| `idlist` | `IdList` | Silent empty list, no error |
| `esearchresult` | `esearch_result` | Silent empty dict, no error |

Both bugs produce empty results silently. Always use lowercase.

## Example
```python
# CORRECT
ids = d.get("esearchresult", {}).get("idlist", [])

# WRONG — returns []
ids = d.get("esearchresult", {}).get("IdList", [])
```

## Validation Pattern
```python
count = int(d.get("esearchresult", {}).get("count", "0"))
ids = d.get("esearchresult", {}).get("idlist", [])
assert len(ids) <= count, f"Got {len(ids)} IDs but count={count}"
assert len(ids) > 0 or count == 0, f"count={count} but 0 IDs — check key casing"
```