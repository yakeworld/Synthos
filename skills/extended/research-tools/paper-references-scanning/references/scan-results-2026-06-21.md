# Scan Results — 2026-06-21

**Two-scan cross-validation**: v3 (markdown report) + v7 (JSON stdout).  
**Source**: `/media/yakeworld/sda2/Synthos/outputs/papers/` (93 papers, 4 non-paper dirs)

## v3 Results (paper-d8-d10a-scan/scripts/scan.py)

| Status | Count |
|--------|-------|
| PASS (D8=100%, D10a=100%) | 11 |
| WARN | 1 |
| FAIL | 14 |
| SKIP | 3 |
| THEBIB | 68 |
| **Total** | **97** |

### Key observations
- 68 of 97 papers use inline thebibliography with no `.bib` file (70.1%)
- 5+ papers have template placeholders (`<label>`, `lamport94`) that were never removed
- 7 papers have D8=0.0 (entire citation set unmatched against bib)
- `pima-crispdm`: 88 cites, 49 bib entries, ~40 missing — highest impact
- `hcs3wt-breast-cancer`: 73 cites, 32 bib entries, 15+ missing — high impact
- `submissions` directory: non-formal paper with 115 cites / 30 bib — exclude from pipeline
- `pd-dysphagia-2026`: PASS for D8 but WARN on D10a (81.2%, 9 unused bib entries)

## v7 Results (paper-references-scanning/scripts/d8d10a-scan.py)

- Papers scanned: 93
- Total cites: 1,542
- Total orphans: 17
- Total zombies: 198
- D10a=100%: 92/93 (v7 auto-100% for no-cites papers)
- bib_source=inline: 70 papers
- bib_source=references.bib: 19 papers (all at D10a=100%)
- bib_source=none: 4 papers (1 with cites > 0 = structural gap: orthokeratology)

### v7 orphan papers (2)
- `orthokeratology-corneal-remodeling-ODE-paper-117`: alves2020corneal, cho2022epithelial, ferrante2020okeffect
- `submissions`: 115 orphans (non-formal)

### v7 zombie papers (18)
Includes: 147-lens-capsule, 148-corneal-epithelial, 151-ocular-torsion, 152-iorhythm, 153-choroidal, Paper_101, binaural-vestibular, bppv-canalith-relocation, bppv-nystagmus, corneal-biomechanics, hcs3wt-breast-cancer, pd-dysphagia, pima-crispdm, pupillary-light, tinnitus-pinn, vergence-accommodation, vog-vestibular-review

## Cross-Score Mapping (2026-06-21)

V7's `d10a` field maps to V3's D8 (citation existence = 1 - orphan rate), NOT V3's D10a. V7 does not provide a zombie-consistency metric. See `references/scan-script-discrepancy-v3-vs-v7.md` for full cross-mapping table.
