# Iterative Literature-First Paper Writing Protocol

## Principle

**"问题引导，文献检索"** — Question-driven, literature-search-first. Do NOT write paper sections directly from the agent's training data or by asking NotebookLM to "write a section." Instead, use iterative Q&A rounds to:

1. Extract knowledge from uploaded PDFs and web sources
2. Identify research gaps by cross-referencing sources
3. Then compile extracted knowledge into paper sections

This prevents hallucinated citations, fabricated data, and language mixing.

## Protocol: Multi-Round Workflow

### Round 1: Literature Extraction (What do the sources say?)

Ask focused questions about each key paper's methods and findings. One question per paper or per theme.

```
Q1: "Extract from [PaperName]: what equation/model did they use? 
     What geometric assumptions? How many parameters? RMSE?"
Q2: "From [PaperName]: what is the classical model equation? 
     Reynolds number? Cross-section assumption?"
```

Output: Structured notes for each paper (save to file).

### Round 2: Literature Extraction (Gap identification)

Cross-reference Round 1 findings to locate research gaps.

```
Q: "Based on all source files, answer these gap questions:
    (1) Has any paper proposed a closed-form parametric equation for [structure]?
    (2) Has any paper systematically compared [type A vs type B]?
    (3) Has [specific finding] been reported before?
    Answer each with confidence: High/Medium/Low."
```

Output: Gap analysis document with innovation claims.

### Round 3: Section Construction (Write from extracted knowledge)

Now that knowledge is extracted and gaps are identified, construct each paper section. For each section, provide the Q&A results from Rounds 1-2 as context.

```
Q: "Based on our Q&A results (attach Round 1-2 findings), 
    write the Introduction section. Structure:
    1. Start with classical model
    2. Point out three oversimplified assumptions
    3. Cite [PaperA] for [finding], [PaperB] for [finding]
    4. List research gaps (from Round 2)
    5. Preview your proposed model
    Use \cite{} format. Write in LaTeX."
```

Output: LaTeX section. Save to file.

### Round 4: Compile and Verify

Assemble all sections into a complete LaTeX document, compile, and verify:

```bash
pdflatex paper.tex
grep -c 'Error' paper.log    # should be 0
grep -c 'undefined' paper.log # should be 0
```

## Common Mistakes

| Mistake | Consequence | Fix |
|:--------|:------------|:-----|
| Writing sections directly (skipping Rounds 1-2) | Citations made up, findings not grounded in sources | Always do knowledge extraction first |
| Asking "write the full paper" in one NotebookLM ask | Output too long, loses focus, introduces errors | One section per ask, one question per round |
| Using delegate_task to write paper sections | Bypasses NotebookLM source grounding | Never delegate paper writing—use NotebookLM ask directly |
| Not saving intermediate Q&A output | Context lost when session resets | Save each round's output to `tmp/qa_round{N}.txt` |
| Uploading PDFs via OpenCode while doing Q&A | PDFs not ready when Gemini queries them | Wait for PDF uploads to finish before starting Q&A |
