# Evolution Engine — Quality Assessment Criteria

## 1. Structural Quality (applies to all atoms)

### 1.1 SKILL.md Loadability (weight: 0.30)

| Score | Condition |
|-------|-----------|
| 1.0 | `skill_loader(name)` returns full content without error |
| 0.5 | `skill_loader(name)` returns content but with warnings |
| 0.0 | `skill_loader(name)` fails (file missing or malformed) |

### 1.2 Frontmatter Validity (weight: 0.15)

| Score | Condition |
|-------|-----------|
| 1.0 | `name` matches directory name, all required fields present |
| 0.5 | `name` present but minor field missing |
| 0.0 | `name` missing or mismatched |

### 1.3 Description Quality (weight: 0.15)

| Score | Condition |
|-------|-----------|
| 1.0 | Description ≥100 characters, contains concrete keywords |
| 0.5 | Description ≥50 characters |
| 0.0 | Description <50 characters or missing |

### 1.4 Allowed-tools (weight: 0.10)

| Score | Condition |
|-------|-----------|
| 1.0 | allowed-tools present with 2+ tools |
| 0.5 | allowed-tools present with 1 tool |
| 0.0 | allowed-tools missing |

### 1.5 Reference Files (weight: 0.30)

Scored as: count of present files / 4 (IO_CONTRACT, EVIDENCE_SCHEMA, BOUNDARY, CHANGE_LOG)

| Files present | Score |
|---------------|-------|
| 4/4 | 1.0 |
| 3/4 | 0.75 |
| 2/4 | 0.50 |
| 1/4 | 0.25 |
| 0/4 | 0.0 |

## 2. API Health (knowledge-acquisition only, weight: 0.20)

| API status | Score contribution |
|------------|-------------------|
| HTTP 200 | 1.0 |
| HTTP 429 (rate limit) | 0.5 |
| HTTP 403 (auth error) | 0.3 |
| Other / timeout | 0.0 |

Overall API health = (S2_score + PubMed_score + OpenAlex_score) / 3

## 3. Overall Score Computation

### knowledge-acquisition:
```
overall = structural × 0.80 + api_health × 0.20
```

### All other atoms:
```
overall = structural_score (no API component)
```

## 4. Degradation Thresholds

| Level | Condition | Action |
|-------|-----------|--------|
| `HEALTHY` | overall ≥ 0.7 AND delta ≥ -0.1 | Log only |
| `DEGRADED` | overall < 0.7 OR delta < -0.1 | Attempt fix |
| `CRITICAL` | overall < 0.5 OR skill unloadable | Alert + log |
| `MISSING` | atom directory/skill not found | Emergency log |

## 5. Evolution Cycle Cap

Maximum cycles before forced human review: 30
After 30 cycles with no changes, auto-pause with message: "No evolution needed. System stable."
