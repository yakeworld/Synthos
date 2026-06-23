# UCI Dataset → Original Paper Discovery

## Methodology

When you need to find the original paper for a UCI ML repository dataset:

### Step 1: Fetch the UCI dataset page HTML

```bash
curl -s -L "https://archive.ics.uci.edu/ml/datasets/<dataset-name>" -o /tmp/uci.html
# or: "https://archive.ics.uci.edu/static/public/<id>/<name>.html"
```

### Step 2: Parse the embedded JSON

The UCI page contains a JSON block with the **Introductory Paper** metadata:
- `paper.title` — original paper title
- `paper.venue` — book/conference name
- `paper.authors` — author names
- `paper.year` — publication year
- `paper.URL` — link to paper (Semantic Scholar or similar)
- `paper.DOI` — often stored in the `edits` array under the `native_papers` section

Extract using Python regex on the HTML body, or use the UCI API endpoint:
```bash
curl -s "https://archive.ics.uci.edu/api/datasets/?dataset_id=<ID>" 
```

The `edits` array (specifically edit with `tableID=8` / `name=native_papers`) contains the paper info in `data.paper` object.

### Step 3: Cross-verify with CrossRef + OpenAlex

Use the DOI from the UCI page:
```bash
# CrossRef verification
curl -s "https://api.crossref.org/works/<DOI>" -o /tmp/cr.json
python3 -c "
import json
d=json.load(open('/tmp/cr.json'))
m=d['message']
print('Title:', m.get('title'))
print('DOI:', m.get('DOI'))
print('Year:', m.get('published-print', m.get('published-online',{})).get('date-parts', [[]])[0])
print('Publisher:', m.get('publisher'))
print('Container:', m.get('container-title'))
print('Authors:', m.get('author'))
"

# OpenAlex for citations and OA info
curl -s "https://api.openalex.org/works/https://doi.org/<DOI>" -o /tmp/oax.json
python3 -c "
import json
d=json.load(open('/tmp/oax.json'))
print('Citations:', d.get('cited_by_count'))
print('OA:', d.get('open_access',{}).get('is_oa'))
print('OA URL:', d.get('open_access',{}).get('oa_url'))
for a in d.get('authorships',[]):
    au=a.get('author',{})
    print(f\"  {au.get('given','')} {au.get('family','')}\")
"
```

### Step 4: Handle incomplete author data

**OpenAlex pitfall**: When parsing OpenAlex author data, the `family` and `given` fields may be empty or missing. This is common for book chapters and some non-English authors. Always cross-reference with CrossRef's author data which tends to be more complete.

### Known Example

**UCI Dataset**: Early Stage Diabetes Risk Prediction (ID 348)
- **Introductory Paper**: "Likelihood Prediction of Diabetes at Early Stage Using Data Mining Techniques"
- **Authors**: M. M. Faniqul Islam, Rahatara Ferdousi, Sadikur Rahman, Humayra Yasmin Bushra
- **Year**: 2019
- **DOI**: 10.1007/978-981-13-8798-2_12
- **Venue**: Advances in Intelligent Systems and Computing — Computer Vision and Machine Intelligence in Medical Image Analysis
- **Publisher**: Springer Singapore
- **Citations**: 256 (OpenAlex)
- **Open Access**: No (Springer paywall)

### Pitfalls

1. **Semantic Scholar rate limit**: The API returns 429 without a key. Use CrossRef + OpenAlex as fallbacks.
2. **Google Scholar blocked**: Google Scholar blocks automated headless queries. Don't try in cron/headless environments.
3. **UCI DOI is for the dataset, not the paper**: `10.24432/C5VG8H` is the dataset DOI. The actual paper DOI is in the `native_papers` edit record.
4. **PubMed won't find CS papers**: PubMed searches biomedicine, not computer science journals/conferences. Use CrossRef + OpenAlex instead.
5. **Paywall access**: Springer book chapters are often behind paywalls. Check OpenAlex `open_access.is_oa` first.
