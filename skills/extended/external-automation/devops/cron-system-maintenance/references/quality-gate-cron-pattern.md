# Quality Gate Cron — Operational Patterns

## Key Discovery (2026-06-25)

When running the quality-gate cron job as an automated scheduled task:

### Pipeline State Layout
- **Active papers**: 104 directories under /media/yakeworld/sda2/Synthos/outputs/papers/*/
- **Archive papers** (_archive/): Already retired, FAIL/HARD_FAIL here don't matter
- **Knowledge-only** (_knowledge_only/): No quality scores, all PASS
- **state.json**: Every paper has one, even if quality_score is stale or wrong

### Batch State Check Pattern
Python loop over all directories reading state.json quality_score and gate_status.
One python3 -c call per directory is OK; batch results in < 10s.

### Critical State.json Pitfalls
1. **Internal inconsistency**: top-level quality_score vs gates_result.quality_score may disagree by 11+ points
2. **Stale timestamps**: gate_timestamp may be weeks old while paper.tex was recently modified
3. **Non-numeric scores**: Some papers have 0.935 (normalized) vs 96 (percentage) — don't mix comparison ranges
4. **quality_score=null**: Papers that never had a quality check (not a failure, just unexamined)

### Silent Exit Criteria
Report [SILENT] when ALL of the following are true:
- Zero papers in active pipeline with gate_status = FAIL/HARD_FAIL
- No Codex tmux sessions still running
- Latest comprehensive reports for active papers show PASS
- Archive FAIL papers are in _archive directories (already retired)

### Quality Score Interpretation
- >=85: Strong paper, ready for submission (PIMA at 88)
- 75-84: Moderate, may have minor issues
- <75: Lower quality but still PASS — ODE/PINN template papers often fall here
- 68 or below: Below threshold but if gate=PASS, not blocking

### Common Paper Types
1. PIMA-CRISP-DM: Clinical ML, highest value paper
2. 3D-Eyeball-Iris-Segmentation: Medical imaging, G7 review at 0.935
3. ODE/PINN template papers: ~80 papers, auto-generated with varying quality
4. BPPV papers: Clinical vestibular research
5. VOR-related papers: Vestibular-ocular reflex computational models
