# corneal-ai-review D10a Fix — 2026-06-02

## Paper
`corneal-ai-review` — Deep Learning in Corneal Disease Diagnosis: A Systematic Review and Meta-Analysis of AI-Based Keratoconus Detection from Corneal Topography and Tomography

## Starting State
- D10a: 56/68 = 82%
- 12 zombies (bibitems in thebibliography but never cited)
- 0 orphans
- Mode: `thebibliography` (68 entries)

## Zombie Activation Strategy

All 12 zombies were highly relevant to the paper (systematic review of corneal AI). The strategy was to read the paper's section structure first, then assign each zombie to its natural section/paragraph:

| Zombie | Topic | Section | Method |
|:-------|:------|:--------|:-------|
| Flaxman2017 | Global blindness causes | §2 Burden | Appended to existing `\cite{Rabinowitz1998, Kymes2004}` |
| Rabinowitz1996b | Videokeratographic indices | §3 Topography | Appended to existing `\cite{Rabinowitz1996, Maeda1994}` |
| Klyce2009 | Klyce/Maeda expert system | §3 Topography | Appended to cite after "Klyce-Maeda expert system" |
| Belin2012b | Corneal elevation/pachymetry | §3 Tomography | Appended to `\cite{Ambrosio2011, Belin2012, Ambrosio2019}` |
| Buhren2009 | Topography/tomography in KC | §3 Tomography | Appended to `\cite{Ambrosio2011, Belin2012, Ambrosio2013}` |
| Vinciguerra2021 | Biomechanical index | §3 Tomography | New sentence: "Biomechanical assessment using the Corvis ST..." |
| Brown2021 | DL for corneal imaging map | §4 DL intro | Appended to `\cite{Ting2019, Gulshan2016, DeFauw2018}` |
| Kim2021 | EfficientNet for KC | §4 Topography DL | Appended to `\cite{Kamiya2019, Kuo2020, Lavric2020, Hizal2020}` |
| Martinez2022 | Transfer learning for KC | §4 Tomography DL | Appended to tomography-based cite group |
| Zhang2023 | ViT for KC severity | §4 Severity | Appended to `\cite{Arbelaez2020, Lopes2021, Cao2022}` |
| Alio2020 | AI in refractive surgery | Discussion | Inserted `\cite{Alio2020, Randleman2022}` after "refractive surgery screening" |
| Randleman2022 | Ectasia risk factors | Discussion | Same insertion as Alio2020 |

## Technique: Section-by-Section Analysis

1. **Read sections first**: Used python3 to extract `\section` and `\subsection` names to understand paper structure
2. **Assign each zombie**: Decided section, then read that section's paragraphs to find the exact sentence containing the most natural insertion point
3. **Python str.replace**: Used precise context strings (not just the cite group) to ensure unique matches:
   ```python
   old = r'ectasia \cite{Rabinowitz1996, Maeda1994}. Topography-based'
   new = r'ectasia \cite{Rabinowitz1996, Rabinowitz1996b, Maeda1994}. Topography-based'
   assert old in tex
   tex = tex.replace(old, new, 1)
   ```
4. **Verify after each batch**: After all 12 replacements, re-extract all cite keys and verify all 12 are present
5. **Check D10a**: Verify that cites ∩ bibkeys = full set

## Accented Bibkey Bug

`Zéboulon2023` with Unicode `é` in the bibitem key caused pdflatex to silently fail at resolving the citation. Even after replacing all occurrences with `Zeboulon2023`, the first recompile still showed undefined because the `.aux` file cached the old accented key.

**Fix sequence**:
1. `tex.replace('Zéboulon2023', 'Zeboulon2023')` — replace both bibitem key AND all \cite references
2. `rm -f paper.aux paper.bbl paper.blg` — clear stale cache
3. `pdflatex` × 2 — clean two-pass compilation

## Results
- D10a: 82% → **100%** (68/68)
- Compilation: 21 pages, **0 undefined references**
- Time: ~10 minutes (analysis + implementation + compile + verify)

## Lesson for Future
When activating 10+ zombies in a systematic review with well-organized sections:
- **Don't randomly insert** — read the section structure first, then assign each zombie to its most natural section
- **Prefer appending to existing \cite{} groups** over creating new sentences (less text to add, same effect)
- **Save new sentences for zombies that don't naturally fit** any existing cite group (like Vinciguerra2021 biomechanical index)
- **Thebibliography mode** needs `rm -f .aux` after bibitem key changes, then 2-pass pdflatex
