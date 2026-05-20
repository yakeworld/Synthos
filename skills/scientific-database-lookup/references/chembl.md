# ChEMBL API

## Base URL
https://www.ebi.ac.uk/chembl/api/data/

## Search Compounds by Name
```
GET /molecule?molecule_synonyms__molecule_synonym__iexact=<name>&limit=10&format=json
```

**Example:**
```bash
curl -s "https://www.ebi.ac.uk/chembl/api/data/molecule?molecule_synonyms__molecule_synonym__iexact=aspirin&limit=5&format=json"
```

## By ChEMBL ID
```
GET /molecule/<chembl_id>.json
```

**Example:**
```bash
curl -s "https://www.ebi.ac.uk/chembl/api/data/molecule/CHEMBL1080949.json"
```

## Bioactivity Data
```
GET /activity?molecule_chembl_id=<chembl_id>&limit=20&format=json
```

## Target Search
```
GET /target?pref_name__iexact=<name>&format=json
```

## Key Response Fields (molecule)
- `molecule_chembl_id` — ChEMBL ID
- `pref_name` — Preferred name
- `molecule_type` — Type of molecule
- `molecule_properties.full_mwt` — Molecular weight
- `molecule_properties.alogp` — AlogP
- `molecule_properties.hba` — H-bond acceptors
- `molecule_properties.hbd` — H-bond donors

## Rate Limit
No documented rate limit. Use responsibly.
