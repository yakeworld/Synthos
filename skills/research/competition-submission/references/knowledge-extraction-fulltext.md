# Knowledge Extraction — Full-Text PDF Methodology

## Rule: Always Use Full Text, Never Abstracts

When extracting structured knowledge from academic papers, **you must read the full text**, not just the abstract. Abstracts are unreliable for:

- **Methodology details**: A paper may claim "portable eye tracking" but the full text reveals it's a 2D tablet system with chin rest, not a wearable 3D head-mounted device.
- **Negative results**: The abstract highlights positive findings; the full results section may reveal that certain modalities (e.g., EEG) "did not contribute to the final model."
- **Exclusion criteria**: Abstracts never list exclusion criteria — critical for understanding generalizability (e.g., "excluded ASD, bipolar, psychotic disorders").
- **Sample descriptions**: Actual sample demographics and sizes are in Methods, not the abstract.
- **Limitations**: The Discussion section's honest assessment is never in the abstract.

## Workflow

1. **Download PDF**: Use S2's `openAccessPdf.url`, arXiv PDF endpoint, or DOI redirect.
2. **Convert to Markdown**: `pymupdf` (available on most systems): `python3 -c "import pymupdf; doc = pymupdf.open('paper.pdf'); text = ''; [text := text + p.get_text() for p in doc]; open('paper.md','w').write(text)"`
3. **Read key sections**: Introduction (background + gap), Methods (study design + sample), Results (quantitative findings), Discussion (limitations + future work).
4. **Extract**: Key findings, methodology classification, limitations, key themes, evidence level, sample size, and — crucially — what the abstract DIDN'T say.

## When Abstract-Only Is Acceptable

- **Initial screening**: To decide if a paper is worth downloading
- **Supplementary papers**: When the full text is behind a paywall and no open-access version exists (mark as `pdf_status: "unavailable"`)
- **Rapid broad search**: When collecting 20+ papers and only 3-5 warrant full-text reading
