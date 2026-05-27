# NCBI Entrez E-Utilities (Gene + GDS)

## Base URL
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/

## Rate Limit
MAX 3 requests per second without API key.
10 requests per second WITH API key.
Use `sleep 0.5` between calls to stay safe.

## Gene Search
```
esearch.fcgi?db=gene&term=<query>&retmax=10&retmode=json
```

**Example:**
```bash
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gene&term=BRCA1+human&retmax=10&retmode=json"
```

**Response:**
- `esearchresult.idlist` — List of gene IDs
- `esearchresult.count` — Total matches

## Gene Summary
```
esummary.fcgi?db=gene&id=<gene_id>&retmode=json
```

**Example:**
```bash
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gene&id=672&retmode=json"
```

## GEO DataSets Search
```
esearch.fcgi?db=gds&term=<query>&retmax=10&retmode=json
```

**Example:**
```bash
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&term=ADHD+eye+tracking&retmax=5&retmode=json"
```

## PubChem Compound Search
```
esearch.fcgi?db=pcsubstance&term=<query>&retmax=10&retmode=json
```

## Common Parameters
- `db`: gene, gds, pubmed, pcsubstance, snp, clinvar
- `term`: URL-encoded search query, use `+AND+` for boolean
- `retmax`: Max records (1-10000, default 20)
- `retmode`: json (for programmatic) or xml (for full details)
