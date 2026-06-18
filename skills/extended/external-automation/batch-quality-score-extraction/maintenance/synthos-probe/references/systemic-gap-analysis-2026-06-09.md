# Systemic Structural Gap Analysis — 2026-06-09

## Context

Cycle 68 probe and this Cron run (cycle 68→69 boundary) both confirmed a systemic structural defect across the Synthos skill library.

## Gap Summary (Cycle 68 / Cron Run)

| Metric | Value |
|---|---|
| Total SKILL.md files | 110 |
| Valid YAML frontmatter | 110/110 (100%) |
| Git tracked | 110/110 (100%) |
| 7-atom structural pass | 2/7 (28.6%) |
| Skills missing version | 9/110 |
| Skills missing signature | 53/110 |
| Skills missing IO_CONTRACT | 97/110 |

## 7 Atoms Per-Atom Status

| Atom | Version | Signature | IO_CONTRACT | Pass? |
|---|---|---|---|---|
| knowledge-acquisition | ✓ v1.7.0 | ✓ | ✓ | YES |
| knowledge-extraction | ✓ 1.0.0 | ✗ | ✗ | NO |
| association-discovery | ✓ 1.0.0 | ✗ | ✗ | NO |
| hypothesis-generation | ✓ 1.0.0 | ✗ | ✗ | NO |
| argument-expression | ✓ (implicit) | ✗ | ✗ | NO |
| viewpoint-verification | ✓ 1.0.0 | ✗ | ✗ | NO |
| research-ideation | ✓ v2.1.0 | ✓ | ✓ | YES |

**Pattern**: The 5 failing atoms share an identical gap pattern — version present (in `metadata.synthos.version`), but neither `signature` nor `IO_CONTRACT` present in body or frontmatter. This is NOT random corruption; it's a systematic omission from the skill creation process.

## Root Cause Analysis

The version field was the first structural requirement introduced (in cycle ~40-50 range). Signature and IO_CONTRACT were added later as requirements, but existing skills were never retrofitted. New skills still vary in adoption:
- `knowledge-acquisition` and `research-ideation` have all three fields
- The other 5 core atoms were created before signature/IO_CONTRACT became standard

## Implications for Future Probes

1. **Structural score is the bottleneck** — benchmark scores are high (0.84-1.0) because YAML validity and git tracking are clean. The structural dimension (0.3) drags the overall score to ~0.64.

2. **Bulk edit required** — fixing 5 atoms × 2 fields = 10 file edits minimum. This exceeds the per-cycle edit budget (typically 3). Resolution requires either:
   - An `IMPROVE` action in a future cycle that allocates budget for this
   - A multi-cycle plan that addresses one atom per cycle
   - A bot/automation to add standard signature/IO_CONTRACT blocks

3. **Detection is working correctly** — the probe IS catching this. Previous cycles underreported (cycle 68 claimed 6/7 pass). The Cron-run-independent verification is reliable.

## Verification Commands for Future Runs

```python
# Path resolution for all 7 atoms (research-ideation is at depth 2)
atoms = {
    "knowledge-acquisition": "skills/knowledge-acquisition/SKILL.md",
    "knowledge-extraction": "skills/knowledge-extraction/SKILL.md",
    "association-discovery": "skills/association-discovery/SKILL.md",
    "hypothesis-generation": "skills/hypothesis-generation/SKILL.md",
    "argument-expression": "skills/argument-expression/SKILL.md",
    "viewpoint-verification": "skills/viewpoint-verification/SKILL.md",
    "research-ideation": "skills/research/research-ideation/SKILL.md",  # depth 2
}

# Count all SKILL.md files including ARCHIVED variant
for root, dirs, fnames in os.walk(base_path):
    for fn in fnames:
        if "SKILL.md" in fn:  # catches both SKILL.md and ARCHIVED-SKILL.md
            count += 1
```
