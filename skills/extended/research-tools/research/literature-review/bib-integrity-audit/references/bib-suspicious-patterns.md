# Suspicious Entry Patterns Catalog

## Pattern 1: URL-as-Year in @misc

**Signal:** `year = {https://...}` or `year = {http://...}`

**Examples found in Synthos:**
- `CASIA2019` in `3D Eyeball Model-Constrained Iris Segmentation/reference4.bib`:
  ```bibtex
  @misc{CASIA2019,
    title={CASIA Iris Image Database. 2019},
    year={http://biometrics.idealtest.org/},
    author={CASIA},
  }
  ```
- `Sarker2021` in same file:
  ```bibtex
  @misc{Sarker2021,
    author={Sarker, Soumick},
    title={OpenEDS Dataset. 2021},
    year={https://www.kaggle.com/datasets/soumicksarker/openeds-dataset},
    publisher={Kaggle}
  }
  ```

**Fix:** Move URL to `url = {...}` field, add `year = {YYYY}` with actual year, add `urldate = {accessed YYYY-MM-DD}`

## Pattern 2: Kaggle Publisher in @misc

**Signal:** `publisher = {...kaggle...}` in a `@misc` entry

**Example:**
```bibtex
@misc{Sarker2021,
  author={Sarker, Soumick},
  title={OpenEDS Dataset. 2021},
  publisher={Kaggle}
}
```

**Fix:** Use `@dataset` type or proper `@misc` with organization, URL, and accessed date

## Pattern 3: Incomplete @misc (missing author/title)

**Signal:** `@misc{...}` entry with no `author` and no `title` fields

**Examples found in Synthos:**
- `CASIA` in `Correcting the Off-Axis Iris Normalization Formulas in Daugman's Method/references.bib`:
  ```bibtex
  @misc{CASIA,
    title={Chinese Academy of Sciences Institute of Automation (CASIA), "CASIA-Iris-V4,"},
    url={http://www.cbsr.ia.ac.cn/english/IrisDatabase.asp}
  }
  ```
- `MMU` in same file:
  ```bibtex
  @misc{MMU,
    title={Multimedia University, "MMU Iris Image Database,"},
    url={http://pesona.mmu.edu.my/~ccteo/}
  }
  ```

**Fix:** Add `author = {...}` and proper `title = {...}` fields

## Pattern 4: arXiv Preprint Without arXiv ID

**Signal:** `journal = {arXiv preprint}` but no `arXiv:XXXX` pattern anywhere in entry

**Note:** Most arXiv entries in the Synthos library are correctly formatted:
```bibtex
@article{garbin2019openeds,
  journal={arXiv preprint arXiv:1905.03702},
  ...
}
```
These are valid and do NOT need fixing — the arXiv ID is in the journal field.

Entries with `doi = {10.48550/arXiv.XXXXX}` also have valid DOI coverage.

## Pattern 5: Duplicate Keys Across Files

**Signal:** Same entry key appears in multiple `.bib` files, possibly with different metadata

**Examples from Synthos scan:**
| Key | Files Found | Issue |
|-----|-------------|-------|
| `swirski2013fully` | 3D-eyeball (×2), pupil-localization | Same entry duplicated |
| `CASIA2019` | 3D-eyeball (×2), pupil-localization | Same malformed entry |
| `Sarker2021` | 3D-eyeball (×2), pupil-localization | Same malformed entry |
| `proencca2009ubiris` | 3 files | Missing DOI in all copies |
| `lu2022neural` | 3 files | Missing DOI in all copies |
| `jia2024condseg` | 4 files | Inconsistent (some have DOI, some don't) |
| `garbin2019openeds` | 4 files | All missing DOI |

## Pattern 6: @misc with publisher={Kaggle} + year-as-URL + no DOI

**Signal:** Multiple suspicious signals combined

**Example:** `Sarker2021` has all three: Kaggle publisher, URL-as-year, no DOI

## Pattern 7: Missing DOI for well-known papers

**Signal:** Complete metadata present but DOI absent for papers that are known to have DOIs

**Known DOIs for common papers:**
| Key | Title | Journal | Known DOI |
|-----|-------|---------|-----------|
| `proencca2009ubiris` | The UBIRIS v2 | IEEE TPAMI | `10.1109/TPAMI.2009.66` |
| `lu2022neural` | Neural 3D gaze | ISMAR 2022 | `10.1109/ISMAR55827.2022.00053` |
| `dierkes2018novel` | A novel approach to single camera glint-free 3D eye model | ETRA 2018 | `10.1145/3281417.3281423` |
| `tsukada2011illumination` | Illumination-free gaze estimation | ICCVW 2011 | `10.1109/ICCVW.2011.6139507` |
| `daugman2009iris` | How iris recognition works | Springer | `10.1016/b978-0-12-374457-9.00025-1` |