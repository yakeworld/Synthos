# STRING Protein-Protein Interaction Database

## Base URL
https://string-db.org/api/

## Interaction Partners
```
POST /json/interaction_partners
```
**Parameters (form-data):** identifiers=<protein_list>, species=<tax_id>, limit=10

**Example (python snippet as bash alternative):**
```bash
curl -s -X POST "https://string-db.org/api/json/interaction_partners" \
  -d "identifiers=BRCA1" \
  -d "species=9606" \
  -d "limit=10"
```

## Network Image
```
POST /image/network
```
**Parameters:** identifiers=<protein_list>, species=<tax_id>

## Functional Enrichment
```
POST /json/enrichment
```
**Parameters:** identifiers=<protein_list>, species=<tax_id>

## Key Response Fields (interaction_partners)
- `stringId_A` — STRING ID of protein A
- `stringId_B` — STRING ID of protein B
- `preferredName_A` — Common name of A
- `preferredName_B` — Common name of B
- `score` — Combined interaction score (0-1)
- `nscore` — Neighborhood score
- `fscore` — Fusion score
- `pscore` — Phylogenetic profile score
- `ascore` — Co-expression score

## Common Species IDs
- 9606 — Homo sapiens
- 10090 — Mus musculus
- 7227 — Drosophila melanogaster
- 6239 — Caenorhabditis elegans

## Rate Limit
No documented rate limit. Use responsibly.
