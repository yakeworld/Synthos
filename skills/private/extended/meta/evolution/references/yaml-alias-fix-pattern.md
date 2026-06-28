# YAML Alias Error Fix Pattern

> Discovered in Cycle 85. Applies to SKILL.md files where IO_CONTRACT with `**input**`/`**output**` markdown bold syntax is embedded inside the YAML frontmatter block.

## Error Signature

```
yaml.scanner.ScannerError: while scanning an alias
  in "<unicode string>", line 5, column 3:
    - **input
```

YAML interprets the `*` in `**input**` as an alias reference anchor, which fails.

## Root Cause

IO_CONTRACT section was placed between the opening `---` and closing `---` of the YAML frontmatter. The markdown **bold** syntax uses `*` which is a reserved YAML character.

## Fix Pattern

**Before** (broken):
```yaml
---

## IO_CONTRACT

- **input**: `type: str` — 用户请求描述
- **output**: `type: dict — 输出`

> 对应原则：P2
name: skill-name
description: "..."
version: 1.0.0

---
```

**After** (fixed):
```yaml
---
name: skill-name
description: "..."
version: 1.0.0
---

## IO_CONTRACT

- **input**: `type: str` — 用户请求描述
- **output**: `type: dict — 输出`

> 对应原则：P2
```

## The Rule

> **IO_CONTRACT sections with markdown syntax MUST live in the body, after the closing `---` delimiter. They MUST NOT be inside the YAML frontmatter block.**

If IO_CONTRACT uses plain YAML syntax (no markdown), it CAN stay inside frontmatter — but the convention going forward is to keep it in the body for consistency.

## Affected Files (Cycle 85 — 31 remaining)

| Path | Priority |
|:-----|:---------|
| skills/extended/external-automation/automation-skills/maintenance/synthos-probe/SKILL.md | P1 |
| skills/extended/external-automation/automation-skills/mlops/research/dspy/SKILL.md | P2 |
| skills/extended/meta/synthos/SKILL.md | P0 |
| skills/extended/research-tools/synthos-akne-bridge/research-skill-audit/SKILL.md | P1 |
| skills/extended/research-tools/research/paper-retrieval/biorxiv/SKILL.md | P2 |
| skills/extended/research-tools/research/paper-retrieval/pdf-download-racing/SKILL.md | P1 |
| skills/extended/research-tools/research/paper-retrieval/scientific-database-lookup/SKILL.md | P2 |
| ... and 24 more under research/ sub-categories |

## Bulk Fix Script

```python
import os, re

def fix_alias_error(filepath):
    with open(filepath) as f:
        content = f.read()
    
    if not content.startswith('---'):
        return False
    
    # Find IO_CONTRACT block between frontmatter delimiters
    first_dash = content.find('---', 3)  # closing ---
    if first_dash <= 0:
        return False
    
    # Check if IO_CONTRACT is inside YAML
    io_pos = content.find('## IO_CONTRACT')
    if io_pos <= 0 or io_pos > first_dash:
        return False  # IO_CONTRACT already in body or missing
    
    # Extract IO_CONTRACT block (from ## IO_CONTRACT to next ## or blank-then-word)
    io_end = content.find('\n##', io_pos + 5)
    if io_end <= 0:
        io_end = content.find('\n#', io_pos + 5)
    if io_end <= 0:
        io_end = first_dash
    
    io_block = content[io_pos:io_end]
    
    # Remove from YAML area, add after closing ---
    new_content = content[:io_pos] + content[io_end:first_dash] + content[first_dash:first_dash+4] + '\n' + io_block + '\n' + content[first_dash+4:]
    
    with open(filepath, 'w') as f:
        f.write(new_content)
    return True
```

## Lessons

- This pattern emerged because cycle-84's restructuring added IO_CONTRACT via template that placed it inside YAML frontmatter
- All 31 remaining files have identical structure — fixable in one bulk operation
- The block-scalar variant (project-experience-distillation, research-skill-audit) has a different fix: move `---` delimiter up before markdown content
