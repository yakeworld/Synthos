# MedData API Details (2026-06-04/05)

## Authentication
```bash
# SSO login → bucToken → meddata token
export MEDDATA_USERNAME="MEDDATA_USERNAME_PLACEHOLDER"
export MEDDATA_PASSWORD="..."

# _get_token() in meddata.py does auto-login
```

## Download

```
fileName = doi.replace('/', '')    # NOT doi + PMID. Just remove slashes.
```

URL: `http://www.meddata.com.cn/api/abstract/viewtext?fileName={fileName}&token={token}`

## full_look API (fallback, less reliable)
URL: `http://www.meddata.com.cn/api/abstract/full_look?token={token}&abstractId={fileName}&pmid=1&doi={真实DOI}`

Parameters:
- `abstractId` / `fileName`: DOI without slashes (can be arbitrary string)
- `pmid`: any number (doesn't need to be real PMID)
- `doi`: the real DOI of the target paper

## Key finding
The `fileName` does NOT need a PMID suffix. `doi.replace('/', '')` is sufficient.
Earlier attempts with `doi_no_slash + PMID` also work because meddata accepts multiple ID formats.

## Source code
`tools/paper-manager/src/sources/meddata.py` — `_make_abstract_id(doi)` returns `doi.replace('/', '')`
