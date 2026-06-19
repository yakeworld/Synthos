# Cross-Project Contamination Patterns in Bibliographies

> **来源**: 2026-06-20 Paper Repair Agent run — `086-endolymph-perilymph-coupling-ode` and `3d-eyeball-iris-segmentation`
> **相关陷阱**: Trap #38 (Zero-citation thebibliography), Trap #32 (D10a values not trustworthy)

## Quick Detection Heuristics

When scanning a paper's bibliography for zombies, check each uncited key against these patterns. A match strongly suggests cross-project contamination — the entry was added by an earlier D10a fix run that constructed bibitems without understanding they belonged to other papers.

### Pattern 1: Synthos Paper ID Suffix

Keys ending in `-NN` where NN is a 2-digit number matching another paper in the pipeline.

| Pattern | Example | Source |
|:--------|:--------|:-------|
| `*-76` | `saccade-kinematic-76` | Synthos Paper 76 (saccade kinematics) |
| `*-83` | `endolymph-hydropressure-83` | Synthos Paper 83 (endolymph hydropressure) |

**Detection**: `grep -E '[a-z]+-[0-9]{2}$'` on zombie keys.

### Pattern 2: Generic Placeholder Keys

Keys that describe a concept rather than cite an author. These were generated when the LLM knew a topic should be cited but couldn't resolve it to a real paper.

| Example | What it probably meant |
|:--------|:----------------------|
| `computational-baseline` | "a computational baseline paper exists" |

**Detection**: Keys that don't match `AuthorYear` or `authorYEARword` format.

### Pattern 3: Corrupted/Empty Bib Entries

Bib entries with only a key and no body — `@Article{key,` followed immediately by the next entry or end-of-file. These inflate bib_count but can't be cited.

```
@Article{nguyen2017long,
@Article{omelina2021survey,
```

**Detection**: Check if the bib entry has required fields (author, title, year). An entry with no fields between `@Article{` and the next `@` is corrupted.

### Pattern 4: Prose Mention Without \cite{} (Author-Year in Text)

The paper's prose uses author-year format like "(Raissi et al., 2019)" but has no corresponding `\cite{raissi2019}`. This is common in AI-generated papers — the LLM writes author-year citations in natural language but forgets to add the LaTeX citation command.

**Detection**: `grep -E '\([A-Z][a-z]+ et al\., [0-9]{4}\)' paper.tex` — find prose mentions that should be `\cite{}` commands.

**Fix**: Replace the prose mention with `~\cite{key}` or add `\cite{key}` after it. Example:
- Before: `The PINN methodology (Raissi et al., 2019)`
- After: `The PINN methodology~\cite{raissi2019}`

## Repair Priority

| Pattern | Severity | Action |
|:--------|:---------|:-------|
| Synthos Paper ID suffix | High | Delete immediately — not a real external reference |
| Generic placeholder key | High | Delete — was never a real paper |
| Corrupted empty entry | Medium | Delete — can't be cited, inflates bib_count |
| Prose mention without `\cite{}` | Medium | Convert to proper `\cite{}` if the bibitem exists |

## 2026-06-20 Case Study: 086-endolymph-perilymph-coupling-ode

**State before repair**: queue claimed D10a=100% (15/15), but independent scan found D10a=50% (9/16).

**7 cross-project zombies deleted**:
| Key | Pattern | Why it was wrong |
|:----|:--------|:-----------------|
| `saccade-kinematic-76` | Paper ID suffix | Synthos Paper 76 — unrelated saccade paper |
| `endolymph-hydropressure-83` | Paper ID suffix | Synthos Paper 83 — companion paper, not cited in prose |
| `computational-baseline` | Generic placeholder | Never a real paper |
| `parnes1999` | Valid author-year but uncited | Legitimate paper, but never cited in text |
| `cohen2021` | Valid author-year but uncited | Legitimate paper, but never cited in text |
| `chen2018` | Valid author-year but uncited | Neural ODE — not relevant to endolymph coupling |
| `jagtap2022` | Valid author-year but uncited | Conservative PINN — not specifically referenced |

**1 orphan fixed**: `sculer1987` → added as Schuknecht HF (1987) — typo in key generation dropped "h" and "k".

**1 prose mention converted**: `(Raissi et al., 2019)` → `~\cite{raissi2019}`.

**Result**: D10a 50% → 100% (10/10). Clean compile: 12pp, 200KB, 0 errors, 0 undefined.
