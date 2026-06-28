# Partial Citation Orphan Repair Pattern

## When to Use

D10a is between 50-95% — most bibitems are cited, but a minority (typically 2-5) are orphans. Each orphan bibitem already exists in the `thebibliography` or `.bib` file with a valid key, but no `\cite{key}` appears in the paper body.

**Not for**: D10a=0% (use `zero-citation-auto-repair.md` in paper-references-scanning) or hybrid prose variants (use `prose-cluster-hybrid-citation-fix` skill).

## Step-by-Step

### 1. Identify orphans

```bash
# Extract bibitem keys
grep -oP '\\bibitem\{([^}]+)\}' paper.tex | sed 's/.*{//;s/}//' | sort > /tmp/bibitems.txt

# Extract cite keys (handle multi-key cites)
grep -oP '\\cite\{([^}]+)\}' paper.tex | sed 's/\\cite{//;s/}//' | tr ',' '\n' | sed 's/^ *//' | sort -u > /tmp/cites.txt

# Find orphans (in bibitems but not in cites)
comm -23 /tmp/bibitems.txt /tmp/cites.txt
```

### 2. Map each orphan to a semantic insertion point

For each orphan bibitem, read its title/author from the paper bibliography to determine the domain:

| Bibitem content hints | Likely insertion section |
|:----------------------|:-------------------------|
| Force platform, COP, postural measurement | Methods → Data Generation |
| GVS, galvanic, postural sway | Introduction → Non-linearity Problem |
| Vestibular noise, head-vertical prior, spatial orientation | Introduction → Clinical Background |
| Machine learning method, classifier, specific algorithm | Methods or Discussion → Prior Work |
| Clinical condition, disease mechanism | Introduction → Clinical Background or Discussion |
| Validation dataset, benchmark | Results or Methods → Evaluation |

### 3. Insert citations with natural phrasing

**Principle**: Don't just append `~\cite{key}` — integrate it into the sentence's meaning.

**Good**:
```
...add Gaussian noise ($\sigma$ = 0.5 mm) representing force platform 
measurement error typical of clinical COP recording~\cite{karamanidis2003}.
```

**Bad** (gratuitous):
```
...add Gaussian noise ($\sigma$ = 0.5 mm)~\cite{karamanidis2003}.
```

Group related orphans into the same citation anchor when they share domain:
```
...using galvanic vestibular stimulation (GVS)~\cite{day2010,honyuke1999,okamoto2006}...
```

### 4. Recompile and verify

```bash
pdflatex -interaction=nonstopmode -halt-on-error paper.tex
pdflatex -interaction=nonstopmode -halt-on-error paper.tex  # second pass for references
```

Then re-run step 1 to confirm zero orphans.

## Real Example: binaural-vestibular-PINN (2026-06-22)

**Before**: D10a = 11/14 = 78.6%. 14 bibitems, 11 cited, 3 orphans:
- `karamanidis2003`: Force platform feedback properties (Gait & Posture, 2003)
- `okamoto2006`: GVS-induced postural sway modeling (Neuroscience Research, 2006)
- `macneilage1999`: Head-vertical prior in noisy vestibular stimuli (Nature Neuroscience, 1999)

**Mapping**:
- `macneilage1999` → Introduction, Clinical Background: "Prior computational work on vestibular noise processing has revealed a head-vertical prior that biases perception during noisy stimulation~\cite{macneilage1999}."
- `okamoto2006` → Introduction, Non-linearity Problem: added to existing cite group with day2010 and honyuke1999
- `karamanidis2003` → Method, Data Generation: "Gaussian noise representing force platform measurement error typical of clinical COP recording~\cite{karamanidis2003}."

**After**: D10a = 14/14 = 100%, clean compile (12pp, 245KB, 0 errors).

## Pitfalls

1. **Don't create a zombie in reverse**: Adding a cite key that doesn't match any bibitem creates a LaTeX undefined citation error. Always verify the key matches exactly (case-sensitive).

2. **Don't disrupt narrative flow**: A citation inserted mid-sentence without grammatical integration reads as "citation stuffing." The sentence must remain coherent with the citation removed.

3. **Check for `%` commented cites**: Some orphan bibitems may have cite keys buried in LaTeX comments (`% \cite{key}`). These won't be picked up. Move them to active text or remove the bibitem.
