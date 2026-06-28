# evolution-state.json JSON Corruption — Diagnosis & Repair

## Symptoms

`python3 -c "import json; json.load(open('evolution-state.json'))"` raises:
```
json.JSONDecodeError: Invalid control character at (line N, column M)
```

The file opens fine in a text editor but the JSON parser rejects it. Common patterns:

| Symptom | Typical Cause |
|:--------|:--------------|
| "Invalid control character" | Unescaped backslash `\` before another special char like `"` — produces `\\"` in the JSON string literal but the parser sees a dangling control character |
| "Unterminated string" | A newline or tab character embedded directly in a JSON string value (not escaped as `\n` or `\t`) |
| "Invalid escape character" | A literal `\` followed by a non-special character (e.g., `\τ` instead of `\\τ` or just `τ`) |

## Root Cause

When the `next_actions[]` or `highlights[]` arrays in evolution-state.json contain text with special characters (backslashes, Unicode symbols like τ/η/ζ/→/≥/≤, or embedded quotes), and the update was performed via template string concatenation rather than through a JSON serializer, the escaping gets corrupted. This is especially common when:

- A cron run's output description contains literal `\` (e.g., from LaTeX commands, file paths, or escaped characters in model names like `\tau_NI`)
- Multiple cron runs append to the array, each potentially introducing new escape artifacts
- The `patch` tool is used with `old_string`/`new_string` that contain backslashes — the escaping layers (JSON → Python → shell) multiply backslashes on each pass

## Detection Script

```bash
cd /media/yakeworld/sda2/Synthos
python3 -c "
import json
with open('evolution-state.json') as f:
    content = f.read()
try:
    json.loads(content)
    print('OK — evolution-state.json is valid')
except json.JSONDecodeError as e:
    print(f'CORRUPT — line {e.lineno}, col {e.colno}: {e.msg}')
    lines = content.split('\n')
    if e.lineno <= len(lines):
        line = lines[e.lineno-1]
        start = max(0, e.colno - 40)
        for i in range(start, min(len(line), e.colno + 20)):
            c = line[i]
            print(f'  pos {i}: {c!r} (0x{ord(c):04x})')
"
```

## Fix Procedure

### Preferred Method: Python re-serialization

This is the most reliable fix because it uses the JSON parser to understand the file structure:

```python
import json

# 1. Read raw content
with open('evolution-state.json') as f:
    content = f.read()

# 2. Attempt to fix common escaping issues
#    (stray backslashes before quotes in string values)
import re
# Pattern: find `\\"` inside a string that appears to be a JSON array element
# (this is heuristic — may need adjustment per case)
fixed = content\
    .replace('\\\\\"', '\\\"')  # double-escaped quote -> single-escaped

# 3. Try parsing the fixed content
try:
    data = json.loads(fixed)
except json.JSONDecodeError:
    # Fallback: try strict=False (allows trailing commas, etc.)
    data = json.loads(fixed, strict=False)

# 4. Re-serialize with proper formatting
with open('evolution-state.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# 5. Verify
with open('evolution-state.json') as f:
    json.load(f)  # should not raise
print('Fixed and verified.')
```

### Alternative: Targeted textual fix (for simple cases)

If the corruption is limited to one known pattern (e.g., `\\\"` at specific lines):

```bash
python3 -c "
with open('evolution-state.json') as f:
    content = f.read()

# Fix specific known pattern: stray backslash before closing quote
# e.g., cancelled.\\\\\", -> cancelled.\",
content = content.replace('cancelled.\\\\\\\",\n', 'cancelled.\",\n')
content = content.replace('translation.\\\\\\\",\n', 'translation.\",\n')

import json
try:
    data = json.loads(content)
    with open('evolution-state.json', 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print('Fixed via targeted replacement')
except json.JSONDecodeError as e:
    print(f'Still broken: {e}')
    print('Fall back to the Python re-serialization method')
"
```

## Prevention

1. **Always use `json.dumps()`** when constructing state updates — never build JSON strings via template concatenation or f-strings with raw content
2. **Batch all updates** to evolution-state.json in a single `json.load()` → modify dict → `json.dump()` cycle
3. **Verify** after every write: `python3 -c "import json; json.load(open('evolution-state.json'))"` — make this part of the post-write checklist
4. **Avoid raw backslashes** in `next_actions` and `highlights` text — replace `\tau` with `τ` (Unicode) or just write `tau`
5. **Long entries** (>500 chars) are more likely to contain special characters — consider splitting into shorter, cleaner entries

## Prevention in Agent State Updates

The most robust approach — used in cycle-135 to fix pre-existing corruption:

```python
# Full read-modify-write cycle through the JSON serializer:
import json
from datetime import datetime

with open('evolution-state.json') as f:
    data = json.loads(f.read().replace('\\\\\"', '\"'))  # heuristic fix on read

# Modify the data structure in-memory
data['cycle'] = 135
data['knowledge_pipeline']['knowledge_score'] = 0.83
data['knowledge_pipeline']['current_step'] = 'knowledge_entry'
data['next_actions'].append('cycle-135: new entry text')
data['highlights'].append('cycle-135: new highlight text')

# Write back through the serializer
with open('evolution-state.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# Verify
with open('evolution-state.json') as f:
    json.load(f)  # raises if still broken
```

This guarantees valid JSON output regardless of the input content's escaping state.
