# PubChem REST API

## Base URL
https://pubchem.ncbi.nlm.nih.gov/rest/pug/

## Compound by Name
```
GET /compound/name/<name>/cids/JSON
GET /compound/name/<name>/property/MolecularWeight,MolecularFormula,XLogP,HBondDonorCount,HBondAcceptorCount,TPSA/JSON
GET /compound/name/<name>/synonyms/JSON
```

**Examples:**
```bash
curl -s "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/aspirin/cids/JSON"
curl -s "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/ibuprofen/property/MolecularWeight,MolecularFormula,HBondDonorCount,HBondAcceptorCount/JSON"
```

## Compound by CID
```
GET /compound/cid/<cid>/JSON
```

**Example:**
```bash
curl -s "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/JSON" | jq '.PC_Compounds[0].props' | head -50
```

## Substance Search
```
GET /substance/name/<name>/cids/JSON
```

## Assay Data
```
GET /assay/aid/<assay_id>/JSON
```

## Key Response Fields (compound/property)
- `MolecularWeight` — Molecular weight
- `MolecularFormula` — Chemical formula
- `XLogP` — Log P (octanol-water partition coefficient)
- `HBondDonorCount` — H-bond donors
- `HBondAcceptorCount` — H-bond acceptors
- `TPSA` — Topological polar surface area
- `IUPACName` — IUPAC name

## Rate Limit
5 requests per second (burst), 400 requests per minute (sustained).
