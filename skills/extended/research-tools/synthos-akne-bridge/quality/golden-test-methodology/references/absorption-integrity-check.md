# Absorption File Integrity Check

> Signal from Cycle 43: evolution/SKILL.md listed `references/absorption-patent-disclosure.md`
> but the file didn't exist on disk. The reference table was stale.

## The Problem

Evolution's absorption record table references markdown files (`references/absorption-*.md`).
If a file is listed but doesn't exist, the absorption record is a **dead link** — the skill claims
knowledge it can't actually retrieve. This is a silent data integrity failure.

## The Fix

Evolution's VERIFY step must now check absorption file existence:

```
For each row in the absorbed-skills table:
  Extract the referenced file path
  Check file_exists(reference_path)
  If missing → flag as P0 data integrity error
  
Additionally:
  Check that each absorption-*.md file is referenced in the table
  Unreferenced files are orphaned — either add to table or remove file
```

## Implementation

The check is simple: parse the table, extract markdown link paths, verify each resolves.

```python
# Simplified check logic
import re
with open('evolution/SKILL.md') as f:
    content = f.read()
refs = re.findall(r'`(references/absorption-[\w-]+\.md)`', content)
for ref in refs:
    full_path = f'/home/yakeworld/.hermes/skills/evolution/{ref}'
    if not os.path.exists(full_path):
        print(f'BROKEN: {ref} referenced but not found')
```

## Key Lesson

A skill's reference table and its reference files directory must be **bidirectionally consistent**:
- Every row in the table must have a corresponding file
- Every file in the directory under the naming convention should have a row in the table

This is analogous to a database foreign key constraint in a skill system.
