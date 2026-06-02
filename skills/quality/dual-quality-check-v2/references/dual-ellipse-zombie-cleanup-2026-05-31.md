# Dual-Ellipse Pupil Localization — Zombie Cleanup Worked Example

## Context

Paper migrated from `_todo/` to standard pipeline. Dual-ellipse modeling for pupil localization using OpenEDS dataset. 616-line LaTeX, elsarticle template, 20 pages.

## Pre-Cleanup State

- D8: 64 bib entries
- D10a (strict): 19/64 = 30%
- D10a (narrow): 19/19 = 100% (all cited exist in bib)
- Orphans: 0
- Zombies: 45 (70% zombie ratio)

## Decision Framework Applied

| Keep Category | Count | Examples |
|:--------------|:-----:|:---------|
| Dataset papers | 5 | garbin2019openeds, CASIA2019, proencca2005ubiris, proencca2009ubiris, garbin2020openeds |
| Foundational | 2 | daugman2001statistical, jain201650 |
| Method papers (pupil/iris) | 16 | swirski2013fully, kasprowski2016comparison, chaudhary2019ritnet, feng2022iris, tan2010efficient, chen2020deep, zhao2019deep, li2019efficient, jalilian2017iris, jan2024iris, bature2024iris, ejiogu2023real, wang2022light, he2024enhancedeepiris, nguyen2020constrained, liu20203d |
| **Deleted** | **22** | Sarker2021 (survey), dierkes2019fast (hw), huo2021heterogeneous, kansal2019eyenet, kim1999vision (old), kuang2022towards, lee2008fake, lee20123d, lu2016estimating (3D gaze), lu2022neural (3D gaze), mathot2018pupillometry, matsumoto2000algorithm (old), morimoto2002detecting (old), newman2000real (old), nguyen2017long (survey), palmero2020openeds2020 (redundant), proencca2010iris (error rates), sun2019evaluation (VR), tsukada2012automatic, venkateswarlu2003eye (old), wang2019cross (cross-spectral), wang2019realtime (3D gaze) |

## Cite Insertion Strategy

Used 3-tier approach via `sed`/`python .replace()`:

1. **Introduction-level** (5 keys): Added foundational + survey refs to first `\cite{fuhl2020pupilnet}` group
2. **Related Work 2.1** (7 keys): Added method refs to `\cite{wildes1997iris}`, `\cite{he2008toward}`, `\cite{daugman2009iris}`
3. **Related Work 2.2** (9 keys): Added learning-based refs to `\cite{chen2017deeplab}`
4. **Results/Dataset** (3 keys): Added OpenEDS + CASIA2019 to dataset description
5. **Discussion/Methods** (2 keys): Added liu20203d to daugman2007new cite

Key sed technique:
```bash
# In single quotes: \\ = literal backslash in sed
# So \\cite matches \cite in the file
sed -i '0,/\\cite{target}\\./s//\\cite{target, newkey1, newkey2}\\./' paper.tex
```

## Post-Cleanup State

- D8: 42 bib entries (22 deleted, 23 kept+cited)
- D10a (strict): 42/42 = 100%
- Orphans: 0
- Zombies: 0
- Pages: 22 (was 18 when bibtex was running from a clean aux)
- Compilation: Clean, 2 minor bib warnings (bature2024iris volume+number conflict, empty pages)

## Bib Processing Technique Used

Bib entries parsed by splitting on `\n(?=@\w+\{)` rather than `re.sub` for deletion:

```python
entries = re.split(r'\n(?=@\w+\{)', bib_content)
for entry in entries:
    m = re.match(r'@\w+\{([^,]+),', entry)
    key = m.group(1).strip() if m else None
    if key in delete_list:
        continue  # skip deletion candidates
    kept.append(entry)
new_bib = '\n\n'.join(kept)
```

This approach is cleaner than `re.sub` because it avoids issues with nested braces in bib entries (author fields with `and`, institution names, etc.).
