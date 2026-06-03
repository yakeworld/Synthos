# UniProt REST API

## Basic URL
https://rest.uniprot.org/uniprotkb/search?query=

## Query Examples
- BY gene name: `https://rest.uniprot.org/uniprotkb/search?query=gene:BRCA1`
- BY protein name: `https://rest.uniprot.org/uniprotkb/search?query=BRCA1`
- BY organism: `https://rest.uniprot.org/uniprotkb/search?query=BRCA1%20AND%20organism_id:9606`
- BY accession: `https://rest.uniprot.org/uniprotkb/P38398`

## Filtering
- Add `&format=json` for JSON output
- Add `&size=25` for limit results (default 25, max 500)
- Add `&fields=accession,id,gene_names,protein_name,organism_name,length,sequence,function,subcellular_location` for specific fields

## Response Fields
- `results[].primaryAccession` — UniProt ID
- `results[].uniProtkbId` — Entry name
- `results[].proteinDescription.recommendedName.fullName.value` — Full name
- `results[].genes[].geneName.value` — Gene name
- `results[].organism.scientificName` — Species
- `results[].sequence.length` — Length
- `results[].sequence.value` — Sequence (when requested)
- `results[].comments[].texts[].value` — Function/comment text

## Rate Limit
None documented. Use responsibly.
