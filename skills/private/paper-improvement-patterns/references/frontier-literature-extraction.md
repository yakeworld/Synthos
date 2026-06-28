# Frontier Literature Extraction Guide

## Purpose

Systematically extract 2024-2026 frontier literature from training pipeline analysis documents and integrate them into paper references and Discussion sections.

## Source Files

The primary source is `research_analysis_label_creation.md` or similar analysis documents in training pipeline directories:

- `/mnt/nfs/training_pipeline/research_analysis_label_creation.md`
- `/home/yakeworld/Synthos/outputs/papers/*/09-background/research-analysis.md`
- Any `*.md` file containing "research gap", "future work", or "related work" sections

## Extraction Protocol

### Step 1: Locate Source Files

```bash
# Find research analysis documents
find /mnt/nfs/ /home/yakeworld/Synthos/ -name "*research*analysis*.md" -o -name "*gap*analysis*.md" -o -name "*related*work*.md" 2>/dev/null | head -20
```

### Step 2: Identify 2024-2026 References

Look for references with these patterns:
- **arXiv**: `arXiv:24xx.xxxxx`, `arXiv:25xx.xxxxx`, `arXiv:26xx.xxxxx`
- **Conference**: "NeurIPS 2024", "ICML 2025", "ICME 2025", "CVPR 2026"
- **Journal**: "2024", "2025", "2026" in publication year
- **Preprint**: "preprint 2024", "forthcoming 2025"

**Command**:
```bash
grep -n "202[4-6]" source_file.md | grep -iE "(arxiv|neurips|icml|icme|cvpr|eccv|aaai|ijcai|nature|science|ieee|acm)" | head -30
```

### Step 3: Extract Reference Details

For each reference, extract:
1. **Authors**: Full author list or "et al." if many
2. **Title**: Paper title
3. **Year**: Publication year (2024-2026)
4. **Source**: arXiv ID, conference, journal
5. **DOI**: If available
6. **Relevance**: How it relates to your paper's method/domain

**Example extraction**:
```
- Guo et al. "Probably Approximately Correct Labels", arXiv:2506.10908, 2025
  Relevance: Statistical guarantees for AI-assisted labeling

- Zhang et al. "GAMED-Snake: Gradient-Aware Dynamic Snake with Adaptive Momentum", ICME 2025
  Relevance: Adaptive energy snake optimization for boundary detection

- Huang et al. "The ALCHEmist: Automated Labeling 500x CHEaper", NeurIPS 2024
  Relevance: Automated data annotation pipeline
```

### Step 4: Categorize by Topic

Group extracted references into logical categories:

1. **Core Method**: References directly related to your main technique
2. **Related Techniques**: References to similar but different approaches
3. **Applications**: References showing practical applications
4. **Future Directions**: References suggesting next steps

### Step 5: Create BibTeX Entries

Convert extracted references to BibTeX format:

```bibtex
@misc{guo2025pac,
  title     = {Probably Approximately Correct Labels},
  author    = {Guo, et al.},
  year      = {2025},
  eprint    = {2506.10908},
  archivePrefix = {arXiv},
  primaryClass = {cs.LG},
  url       = {https://arxiv.org/abs/2506.10908},
}

@misc{zhang2025gamed,
  title     = {GAMED-Snake: Gradient-Aware Dynamic Snake with Adaptive Momentum},
  author    = {Zhang, et al.},
  year      = {2025},
  note      = {ICME 2025},
}
```

### Step 6: Integrate into Paper

**In References.bib**: Add all BibTeX entries

**In Discussion/Related Work**: Integrate with narrative structure:

```latex
Recent advances in [topic] have shown promising results~\citep{ref1, ref2}. 
Our method addresses these limitations by...

The emergence of [new trend] highlights...~\citep{ref3, ref4}. 
Future work could incorporate [technique]...~\citep{ref5}.
```

## Quality Checks

1. **Relevance**: Each reference must be directly related to your paper's domain/method
2. **Recency**: Prioritize 2024-2026 references; older references are not "frontier"
3. **Diversity**: Include arXiv preprints, conference papers, and journal articles
4. **Balance**: Don't over-cite one source; spread across multiple references
5. **Integration**: Each reference must be cited in context, not just listed

## Common Pitfalls

1. **Irrelevant references**: Citing papers from unrelated domains
2. **Outdated "frontier"**: Citing 2022-2023 papers as "recent advances"
3. **Duplicate citations**: Same paper cited multiple times with different keys
4. **Missing details**: arXiv references without eprint numbers
5. **Poor integration**: Listing references without narrative connection

## Example: 3D Eyeball Iris Segmentation

Extracted 16 frontier references from `research_analysis_label_creation.md`:

1. **Foundation Models**: SAM 2, DSegU-Net (2024-2026)
2. **Active Learning**: Active Sparse Labeling, CPEAL (2025)
3. **Adaptive Optimization**: GAMED-Snake (2025)
4. **Uncertainty Quantification**: PAC Labeling, Expona (2025-2026)
5. **Bayesian Methods**: Bayesian Next-Best-View (2026)
6. **Gaze Estimation**: PicoEyes (2026)

Integration in Discussion:
```latex
Recent advances in foundation models for medical image segmentation, 
such as the Segment Anything Model (SAM) and its video extensions SAM 2~\citep{sam2pupil2024}, 
have shown promising results for pupil segmentation while revealing limitations for iris and 
sclera boundaries~\citep{islusam2023}. Our method addresses these limitations by providing 
deterministic, geometrically consistent outputs that do not suffer from SAM's variability.

The emergence of automated annotation pipelines~\citep{huang2024alchemist, labelingcopilot2025, 
transformingannotation2025} and weak supervision methodologies~\citep{guo2025pac, guan2025weshap, 
expona2026, boxwrench2024, stronger2025} highlights a growing trend toward reducing human 
annotation burden. Our 3D model-constrained approach contributes to this trend by generating 
high-quality, anatomically consistent annotations without manual intervention.
```

## When to Use

- **Paper quality improvement**: When reviewer requests "more recent references"
- **Literature review update**: When preparing for journal submission with 2024-2026 citation requirements
- **Gap analysis**: When identifying research gaps requires citing recent work
- **Method justification**: When explaining why your approach is novel relative to 2024-2026 state-of-the-art

## When NOT to Use

- **Historical surveys**: Papers focusing on historical development don't need frontier references
- **Theoretical papers**: Purely theoretical work may not have recent empirical references
- **Stable domains**: Fields with slow innovation (e.g., some classical statistics) may not have 2024-2026 breakthroughs

## Advanced: Cross-Reference Validation

After extracting references, validate against:

1. **Crossref API**: Check DOI existence
2. **Google Scholar**: Verify citation count and relevance
3. **PubMed**: For medical/biomedical papers
4. **Semantic Scholar**: For AI/ML papers

**Command**:
```bash
# Check arXiv existence
curl -s "http://export.arxiv.org/api/list/search_list?id=2506.10908" | grep -o "<title>[^<]*</title>"
```
