# Notebook Splitting Workflow

> How to split a messy Notebook LM notebook with 30-50+ mixed-topic sources into multiple focused notebooks.

## Problem

A notebook accumulates dozens of pasted-text sources across unrelated topics (BPPV, eye tracking, AI, clinical methodology, knowledge management). The user wants them organized by topic.

## Constraint

**NotebookLM does NOT support cross-notebook source movement.** A "Pasted Text" source lives only in the notebook where it was created. You cannot `source add` a source ID from another notebook.

## Solution: Recreate, Don't Move

```
Messy Notebook (46 sources) → Rename to Archive
                              Create Notebook A (Topic A)
                              Create Notebook B (Topic B)
                              Create Notebook C (Topic C)
                                  ↓
                         Search fresh literature via ACQ / S2 / OpenAlex
                                  ↓
                         Add as new Markdown sources to each notebook
```

### Step-by-Step

1. **Assess**: Use `notebooklm source list` to catalog all sources by topic.

2. **Rename old notebook** (preserves all data):
   ```bash
   notebooklm rename -n <old_id> "研究笔记归档（待整理）"
   ```

3. **Create new focused notebooks**:
   ```bash
   notebooklm create "Topic A: Subtopic"
   ```

4. **Populate with fresh literature** (better than moving old notes):
   - Search Semantic Scholar / OpenAlex for 5-7 latest papers per topic
   - Write summary Markdown file with full citations (DOI, year, summary)
   - Add to each notebook:
     ```bash
     notebooklm use <new_notebook_id>
     notebooklm source add /path/to/literature_summary.md
     ```

5. **Optional: Keep archive notebook** for historical reference.

## Why This Approach

| Approach | Result |
|----------|--------|
| Try to "move" sources between notebooks | ❌ Not supported |
| Delete old + re-add to new | ❌ Content lost (source get returns metadata only) |
| Keep old + create new with fresh lit | ✅ Clean structure, latest research, no data loss |

## Pitfalls

- **`source get` returns only metadata**, not full pasted-text content.
- **Fresh literature is often more valuable** than old research notes for active projects.
- **If old notes are irreplaceable**, write a new Markdown file from memory/sources.
