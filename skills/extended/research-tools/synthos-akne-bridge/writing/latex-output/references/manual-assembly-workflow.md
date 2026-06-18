# Manual Assembly: step_*.md with Raw LaTeX → paper.tex

## Problem

The `assemble_pdf_from_steps.py` script expects:
1. Specific filenames: `step_intro.md` (short names)
2. Fenced LaTeX blocks: content wrapped in ` ```latex ... ``` `

But manual cron writing produces:
1. Long filenames: `step_introduction.md` (not `step_intro.md`)
2. Raw LaTeX math: `$$...$$` in plain text, no fenced blocks
3. The script produces an empty/invalid .tex

## Manual Assembly Pattern (2026-06-06)

When script format doesn't match:

```python
import os, re

manuscript_dir = "01-manuscript"
sections = {
    "step_abstract.md": "Abstract",
    "step_introduction.md": "Introduction",
    "step_method.md": "Method",
    "step_results.md": "Results",
    "step_discussion.md": "Discussion",
}

tex = r"\documentclass[12pt]{article}\usepackage{amsmath,amssymb}\usepackage{graphicx}\usepackage{booktabs}\usepackage{geometry}\geometry{margin=1in}\usepackage{hyperref}\begin{document}\maketitle"

for sf in sorted(os.listdir(manuscript_dir)):
    if sf not in sections or not sf.endswith('.md'):
        continue
    with open(os.path.join(manuscript_dir, sf)) as fh:
        body = fh.read().split('\n')[1:]
    tex += f"\\section{{{sections[sf]}}}\n"
    for line in body:
        s = line.strip()
        if s.startswith('|'):
            continue
        line = re.sub(r'\*\*(.+?)\*\*', r'\textbf{\1}', line)
        tex += line + '\n'
tex += r"\end{document}"
```

## Key Differences

| Aspect | Script | Manual |
|--------|--------|--------|
| Filename | step_intro.md | step_introduction.md |
| LaTeX | Fenced blocks | Raw `$$` notation |
| Bold | As-is | `**text**` → `\textbf{}` |

## Recommendation

When writing papers via manual cron:
1. Use short filenames: `step_intro.md` not `step_introduction.md`
2. Wrap LaTeX in ` ```latex ` fenced blocks
3. Makes both script and manual assembly work

Or create symlinks if content is already written:
```bash
cd 01-manuscript && ln -s step_introduction.md step_intro.md
```