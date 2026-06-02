# ded-ai-screening D10a Fix — 2026-06-02

**Paper**: "Through a Dry Lens: A Systematic Review and Meta-Analysis of Artificial Intelligence for Dry Eye Disease Diagnosis, Classification, and Severity Assessment"
**Mode**: thebibliography
**Initial**: 67 bibitems, 34 cited → **D10a = 51%**, 33 zombies
**Final**: 55 bibitems, 55 cited → **D10a = 100%**, 0 zombies, 0 orphans

## Strategy: Activate-Not-Delete (Systematic Review)

For systematic review papers, most zombies are genuinely relevant studies that should have been cited. The decision framework was:

- **Activated** (21 entries): DED-specific AI studies, classic ML/DL architecture papers, DED questionnaire validation papers
- **Deleted** (12 entries): Less central studies, broad-field references without specific textual anchor points

## 16 \cite{} Insertion Points

| Location | Inserted Citations | Purpose |
|:---------|:------------------|:--------|
| Introduction §1.1 (prevalence) | `\cite{Sullivan2019}` | Age/sex DED relationship |
| Introduction §1.2 (questionnaires) | `\cite{Schiffman2018, Speight2020}` | OSDI/SPEED questionnaire validation |
| Introduction §1.2 (meibography) | `\cite{McMonnies1986, Tomlinson2006}` | Classic DED history + MGD workshop |
| Introduction §1.3 (staining) | `\cite{Bron2003}` | Corneal staining grading |
| Introduction §1.4 (meibography AI) | `\cite{Arita2017, Xiao2021, Maruyama2020}` | Early meibography DL papers |
| Introduction §1.4 (U-Net) | `\cite{Ronneberger2015}` | Foundational architecture |
| Results §3.3 (meibography) | `\cite{He2017}` | ResNet backbone |
| Results §3.3 (tear film) | `\cite{Park2023}` | Video-based TBUT DL |
| Results §3.3 (symptom) | `\cite{Lu2023}` | ML DED severity prediction |
| Results §3.3 (multimodal) | `\cite{Vaswani2017}` | Attention mechanism foundational |
| Results §3.4 (architecture) | `\cite{Feng2023}` | CNN vs ViT comparison |
| Results §3.6 (validation) | `\cite{Liu2024, Zhang2023}` | Multicenter + cross-device validation |
| Discussion §4.2 (multimodal) | `\cite{Wang2024a}` | Real-world multimodal validation |
| Discussion §4.3 (criteria) | `\cite{Shimazaki2021}` | Japanese DED diagnostic criteria |
| Discussion §4.3 (regulatory) | `\cite{Zhou2024}` | FDA clearance pathways |
| Discussion §4.5 (domain adapt) | `\cite{Ye2024}` | Unsupervised domain adaptation |

## Key Discovery: Accented BibKey Trap

`\bibitem{Abràmoff2018}` contained an `à` character. LaTeX silently failed on this key — zero compilation errors, 16-page PDF generated, but the `\cite{Abràmoff2018}` reference rendered as `[?]` because the accented `à` caused key truncation.

**Detection**: `strings paper.log | grep "undefined on input"` showed `moff2018' on page 11 undefined on input l.321`

**Fix**: Renamed to `Abramoff2018` in both `\bibitem{}` and `\cite{}` — identical to bibitem content correction (trap #4) but affecting the **key name** itself, not the content.

## Script Approach

The fix was implemented as a single Python script (`/tmp/fix_ded_d10a.py`) that:
1. Applied 14 `str.replace()` operations for \cite{} insertion
2. Split thebibliography section by bibitem boundary (`\n(?=\\bibitem)`) for deletion (12 entries)
3. Updated `\begin{thebibliography}{N}` counter
4. Applied remaining 2 patch operations for failed str.replace (meibography AI paragraph, regulatory pathway)
5. Compiled × 2 (thebibliography mode), verified D10a=100%
