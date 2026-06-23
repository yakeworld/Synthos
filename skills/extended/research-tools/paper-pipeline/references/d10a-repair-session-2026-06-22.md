# D10a Repair Session Patterns

## Session: 2026-06-22 Cycle 186

### Pattern 1: Stale .bbl Shadowing Inline Thebibliography

**Paper**: `hcs3wt-breast-cancer`
**Symptom**: D10a=0% (30 orphans, 12 zombies). Script reports `bib_source=bbl`.
**Root cause**: Two stale `.bbl` files (`paper.bbl`, `hcs3wt-breast-cancer.bbl`) existed from a prior compilation that used a completely different bib file with short-key naming convention. The tex file had since been updated with an inline `\begin{thebibliography}...\end{thebibliography}` block using long-key citations, but the D10a script uses `.bbl` as priority 1, so it found 0 matches between the old bbl's short keys and the tex's long keys.
**Fix**: `rm paper.bbl hcs3wt-breast-cancer.bbl` → script falls back to inline thebibliography → D10a=100%.
**Key insight**: When D10a=0% and `bib_source=bbl`, always suspect stale bbl from a different compilation era. Delete bbls and re-scan before doing anything else.

### Pattern 2: `.txt` Bib File Masquerading as Missing `.bib`

**Paper**: `3d-eyeball-iris-segmentation`
**Symptom**: D10a=67.8% (19 orphans). BibTeX run reveals 6 additional "I didn't find a database entry" warnings for keys that were in the old bbl but not in reference4.bib.
**Root cause**: The tex uses `\bibliography{reference4}` but `reference4.bib` didn't exist. However, `06-references/reference4.txt` was a 656-line, fully-populated bib file with 50 complete entries — just with the wrong file extension. Additionally, `06-references/references.bib` had ~15 skeleton entries (empty `@Article{key,`) that were never populated.
**Fix**:
1. Copied `06-references/reference4.txt` → `01-manuscript/reference4.bib`
2. Found and populated 11 missing entries (5 orphan + 6 bibtex-warned) across multiple API searches (OpenAlex, arXiv, Crossref, DBLP)
3. Unified `rathnayake2023pupilreview` → `rathnayake2023current` (duplicate cite key for same paper)
4. Recompiled pdflatex→bibtex→pdflatex×2 → 0 warnings, 35pp PDF
**Key insight**: When `\bibliography{name}` fails, search for `name.txt`, `name.bib` in `06-references/`, or any `.txt` file with matching content. The bib content may exist under a different extension.

### Pattern 3: Duplicate Citation Keys for Same Paper

**Paper**: `3d-eyeball-iris-segmentation`
**Symptom**: BibTeX compilation succeeded but the bib file has both `farmanifard2024iriscnn` and `yao2024irissam` — both referencing the same paper (Iris-SAM: Iris Segmentation Using a Foundation Model, arxiv:2402.06497).
**Context**: The tex cites `farmanifard2024iriscnn` in one sentence and `yao2024irissam` in another, treating them as different papers. This was only discovered because bibtex warned about the missing `farmanifard2024iriscnn` entry — without that warning, the duplication would have gone unnoticed.
**Fix needed**: Human review required — unify to a single citation key in the tex.
**Key insight**: After populating missing bib entries, always check for duplicate keys referencing the same paper. The `note` field was used to flag this: `note = {DUPLICATE of yao2024irissam — same paper, different cite key. Unify citations in tex.}`

### Pattern 4: BibTeX Reveals Entries Missing from Current Bib That Were in Old Bbl

**Paper**: `3d-eyeball-iris-segmentation`
**Symptom**: After adding the initial 5 orphan entries and recompiling, BibTeX warned about 6 MORE missing entries (`yin2023deeplearning`, `farmanifard2024iriscnn`, `chen2022novel`, `vazquez2020pistol`, `qin2022gazed`, `wang2017pupernet`). These weren't in the original D10a orphan list because they existed in the old `.bbl` (which had bibitems for them) — the D10a scan matched them against the old bbl. But when we switched to a new bib source, they became missing.
**Fix**: All 6 added as minimal entries with `NEEDS_VERIFICATION` notes. API searches (OpenAlex, arXiv, Crossref, DBLP) failed to find definitive matches for all — these are likely niche/preprint citations.
**Key insight**: After any bib source change, run bibtex separately to catch the "silently matched before" entries that the D10a scan missed because it was using the old bbl.

### Pattern 5: NEEDS_VERIFICATION Flag Protocol

When a citation cannot be verified through academic APIs (OpenAlex, arXiv, Crossref, DBLP), add a minimal BibTeX entry with:
```bibtex
@Article{key,
  author  = {BestGuess, Author},
  title   = {Best Guess Title},
  journal = {arXiv preprint},
  year    = {YYYY},
  note    = {NEEDS_VERIFICATION: Requires manual bibliographic verification}
}
```
This allows compilation to succeed while flagging the entry for human review. The `note` field survives BibTeX processing and appears in the `.bbl` output.
