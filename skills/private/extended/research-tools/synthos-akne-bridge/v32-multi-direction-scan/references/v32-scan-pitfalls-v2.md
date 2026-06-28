# v32 Scan Pitfalls v2 - updated

## Pitfall: completed_papers_count drift

**Problem:** The completed_papers_count in agent-tracker.json can drift from the actual completed_papers list length.

**Fix:** After any tracker mutation, verify len(completed_papers) == completed_papers_count. If mismatch, set count = len(list).

**Reconciliation (count > list):** The notes field is authoritative. Set completed_papers_count to the number stated in the most recent note. The list may only contain papers surviving disk cleanup. Never add papers without disk evidence.

**Reconciliation (list > count):** Set completed_papers_count = len(completed_papers).

**Prevention:** Always read the FULL file before overwriting. Use read_file without offset/limit. Partial reads cause truncation.