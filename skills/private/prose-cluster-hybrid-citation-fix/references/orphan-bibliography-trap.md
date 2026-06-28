# Pure Prose Variant: Citation Orphan Trap

> **Trigger**: D10a=0% or near-0%, 0 `\cite{}` keys in text, `\begin{thebibliography}` has N bibitems, **no prose author-year clusters** (unlike the hybrid variant).
>
> **Not hybrid**: No "(Author Year)" prose patterns exist anywhere in the paper.
> **Not inline**: This is the simplest variant — bibitems exist but were never cited.

## Detection

```bash
grep -c '\\\\cite{' paper.tex                # should be 0
grep -c '\\\\bibitem' paper.tex               # count bibitems (N)
python3 -c "
import re
with open('paper.tex') as f: tex = f.read()
bibitems = re.findall(r'\\\\bibitem\{([^}]+)\}', tex)
cite_keys = re.findall(r'\\\\cite\{([^}]+)\}', tex)
prose = re.findall(r'\([A-Z][a-z]+.*?\d{4}\)', tex)
print(f'Bibitems: {len(bibitems)}')
print(f'Cite keys: {len(cite_keys)}')
print(f'Prose author-year refs: {len(prose)}')
if len(prose) == 0 and len(cite_keys) == 0 and len(bibitems) > 0:
    print('→ PURE PROSE VARIANT confirmed')
"
```

## Fix Strategy: Contextual Mapping

Unlike the hybrid variant where prose clusters give you direct replacement targets, the pure prose variant requires **reading and understanding each bibitem's domain**, then finding the right insertion point.

### Step 1: Extract bibitem list

Read the `\begin{thebibliography}` block and list all bibitem keys + their titles/authors:

```python
python3 -c "
import re
with open('paper.tex') as f: tex = f.read()
bib = re.search(r'\\\\begin\{thebibliography\}.*?\\\\end\{thebibliography\}', tex, re.DOTALL)
if bib:
    items = re.findall(r'\\\\bibitem\{([^}]+)\}\s*(.*?)(?=\\\\bibitem|\\\\end\{thebibliography\})', bib.group(), re.DOTALL)
    for key, body in items:
        # Extract first sentence (title-ish)
        title = body.strip().split('.')[0][:80]
        print(f'{key} | {title}')
"
```

### Step 2: Map bibitems to paper context

For each bibitem, determine:
1. What domain does it belong to? (AMD, diabetic retinopathy, choriocapillaris, thermometry, etc.)
2. Which section of the paper discusses that topic?
3. Which specific sentence or phrase is the most natural anchor?

**Common mapping patterns for ophthalmic/ODE papers**:

| Bibitem Domain | Typical Section | Anchor Phrase Pattern |
|:---------------|:----------------|:----------------------|
| Clinical disease (AMD, glaucoma, DR) | Introduction, 1st paragraph | "pathogenesis of [disease]" or "affects X million people" |
| Anatomy (choriocapillaris, choroid) | Introduction, 2nd paragraph | "[structure] provides the dominant [function]" |
| Measurement technique | Introduction or Discussion | "measured non-invasively using [technique]" |
| Thermal/mechanical properties | Methods or Results | "thermal damage threshold at" |
| Blood flow / vascular | Introduction or Discussion | "blood flow compensation maintains" |
| Choroidal thickness | Discussion | "choroidal thickness decreasing by" |
| Disease mechanism (diabetic) | Discussion | "diabetic microangiopathy impairs" |
| Related computational model | Introduction (gap) | "no computational dynamical model of [X] exists" |

### Step 3: Insert `\cite{}` at anchor points

Do NOT batch-insert at the end of paragraphs. Each bibitem deserves a contextually accurate insertion point. Example mappings from a real fix:

```
pflugare2004 → "is implicated in thermal damage mechanisms \cite{pflugare2004,ablan2019}"
spaide2018   → "pathogenesis of age-related macular degeneration (AMD) \cite{spaide2018,ishibashi2010,pople2000}"
martins2017  → "measured non-invasively using MRI thermometry and infrared techniques \cite{martins2017,fujimoto2015}"
chen2020     → "thermal dysregulation occurs in diabetic retinopathy \cite{chen2020,wolfson2017}"
morpugco2011 → "choriocapillary blood flow provides the dominant heat sink \cite{morpugco2011,dunn1999}"
read2006     → "choroidal thickness decreasing by approximately 0.01 mm/year after age 40 \cite{read2006,hamann2013}"
sun2021      → "Diabetic microangiopathy similarly impairs microvascular thermoregulation \cite{wolfson2017,chen2020,sun2021}"
```

**CRITICAL**: Group related bibitems at the same anchor point instead of scattering them. This preserves readability. E.g., all AMD refs go together at the AMD mention.

### Step 4: Compile twice and verify

```bash
pdflatex -interaction=nonstopmode paper.tex
pdflatex -interaction=nonstopmode paper.tex  # second pass for cross-refs
grep -c "undefined" paper.log
# Should be 0
```

## Verification

```bash
python3 -c "
import re
with open('paper.tex') as f: tex = f.read()
bibitems = set(re.findall(r'\\\\bibitem\{([^}]+)\}', tex))
cite_keys = re.findall(r'\\\\cite\{([^}]+)\}', tex)
cites = set()
for ck in cite_keys:
    for k in ck.split(','): cites.add(k.strip())
orphans = bibitems - cites
matched = len(cites & bibitems)
total = len(bibitems)
print(f'D10a: {matched}/{total} = {matched/total*100:.0f}%')
if orphans:
    print(f'Orphans ({len(orphans)}): {', '.join(sorted(orphans))}')
else:
    print('0 orphans — ALL bibitems cited')
"
```

## When This Pattern Occurs

Most common in papers where:
1. The LLM generated a complete thebibliography block but never added `\cite{}` commands in the prose
2. The paper reads naturally without citations because it's written as pure expository/prose description
3. The paper has a standard IMRaD structure with clinical/domain background but all references are at the back only

## Pitfalls

1. **Don't insert citations at the end of every paragraph**. This creates orphan-looking citations in unrelated contexts. Each bibitem maps to one specific sentence.
2. **Group related bibitems together**. Multiple AMD refs at one AMD mention > one AMD ref at ten scattered locations.
3. **Check for citation duplicates** — the same bibitem cited in multiple places is fine (it just appears multiple times).
4. **Watch for LaTeX special characters** in bibitem keys (underscores `_` need escaping in text, but `\cite{}` handles them fine as-is).
5. **Always compile twice** — one pass won't resolve the `\cite{}` → `\bibitem{}` cross-references.
