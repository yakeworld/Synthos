# Evolution Engine — I/O Contract

## Input

| Source | Path | Format | Required |
|--------|------|--------|----------|
| Evolution state | `/media/yakeworld/sda2/Synthos/evolution-state.json` | JSON | Yes |
| Evolution log | `/media/yakeworld/sda2/Synthos/evolution-log.md` | Markdown | Yes |
| Evolution config | `/media/yakeworld/sda2/Synthos/evolution-config.yaml` | YAML | Yes |
| Atom skill files | `skills/<atom-name>/SKILL.md` | Markdown+Frontmatter | Yes |
| Atom references | `skills/<atom-name>/references/*.md` | Markdown | Partial |
| Atom golden tests | `skills/<atom-name>/golden/` | JSON/MD | Partial |

## Output

| Destination | Path | Format |
|-------------|------|--------|
| Evolution state (updated) | `/media/yakeworld/sda2/Synthos/evolution-state.json` | JSON |
| Evolution log (appended) | `/media/yakeworld/sda2/Synthos/evolution-log.md` | Markdown |
| Evolution report | `outputs/evolution/report_{cycle}.json` | JSON |
| Patched atom files | `skills/<atom-name>/SKILL.md` | Markdown+Frontmatter |

## Key Data Structures

### ProbeResult (per atom)
```json
{
  "atom_name": "str",
  "structural_score": 0.0-1.0,
  "api_health_score": 0.0-1.0,
  "overall_score": 0.0-1.0,
  "issues_found": ["str", ...],
  "reference_files_ok": int,
  "reference_files_total": int,
  "golden_exists": bool,
  "skill_loadable": bool,
  "load_error": "str|null"
}
```

### DiagnosisResult
```json
{
  "degraded_atoms": ["str", ...],
  "critical_issues": [{"atom": "str", "issue": "str", "severity": "critical|major|minor"}, ...],
  "api_health": "healthy|degraded|failure",
  "overall_quality_delta": -1.0-1.0,
  "eight_dim_deltas": {"dim_name": int, ...},
  "recommendations": ["str", ...]
}
```

## Non-guarantees

- Evolution does NOT guarantee zero false positives in degradation detection
- Evolution does NOT automatically fix API connectivity issues
- Evolution does NOT create new atoms or modify core logic
- Evolution does NOT execute full atom pipelines (structural probe only)
