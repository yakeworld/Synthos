---




name: paper-queue-audit
description: "Directory index for paper-queue-audit: paper-queue-audit"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "queue: list[Paper], priorities: dict -> audit_report: dict (queue_health, missing_items, priority_adjustments)"
    atom_type: skill
    priority: P1
    related_skills: []
---




## IO_CONTRACT

- **input**: `queue_file: str` — 用户请求描述、上下文信息
- **output**: `audit_report: dict — 队列审计报告`

> 对应原则：P2（机械原子暴露输入输出规范）

io_contract:
  input:
    - 'papers_dir: str -> queue_report: dict'
  output:
    - 'queue_report: dict (stage_distribution, bottleneck_papers, stuck_papers)'
---




# Paper Queue Audit — 论文管线健康诊断

> Scan all papers, classify by pipeline stage, identify bottlenecks and anomalies.

## When to Use

- Before any G1-G7 batch processing (need to know what's stuck where)
- After a cron run that processes papers (verify queue state changed as expected)
- When investigating why papers aren't advancing through the pipeline
- Cron job startup — quick health check before executing any paper work

## Execution Steps

1. **Scan all paper directories** for `state.json`
   - Path: `/media/yakeworld/sda2/Synthos/outputs/papers/<paper-dir>/state.json`
   - Note: Some systems use `/home/yakeworld/Synthos/papers/` — check both paths

2. **Extract key fields** from each state.json:
   - `current_step` — pipeline stage
   - `quality_score` — numeric or dict (Layer B calibration)
   - `gate_status` — PASS/CONDITIONAL/FAIL/MISSING
   - `stage` — optional user-defined stage

3. **Classify papers by current_step** — typical distribution:
   - `g1g7_gate_check` — most common bottleneck (40-65 papers)
   - `quality_check` — missing quality_score extraction
   - `method` / `introduction` / `gap_analysis` — earlier pipeline stages
   - `complete` — fully done
   - `MISSING` / `G1-ACQ` — anomalous states

4. **Cross-reference gate_status** with current_step to determine action:
   - At `g1g7_gate_check` + CONDITIONAL → advance past
   - At `g1g7_gate_check` + FAIL → repair needed
   - At `g1g7_gate_check` + MISSING → full G1-G7 check
   - At `quality_check` + score MISSING → extract score from step file

5. **Identify papers with NO state.json**:
   - Check for `01-manuscript/paper.tex` to confirm real papers
   - Flag as `FILES_NO_STATE` category

6. **Produce classification report** with step distribution, gate summary, critical items

## Common Anomalies

| Anomaly | Detection | Fix |
|---------|-----------|-----|
| Score in state.json but current_step still at quality_check | State has score, hasn't advanced | Advance to g1g7_gate_check |
| gate_status but no gates_result JSON | Partial gate processing | Complete gates_result with full G1-G7 JSON |
| steps_completed lists g1g7_gate_check but no step file | state.json ↔ filesystem mismatch | Write step file to 01-manuscript/ |
| quality_score as dict instead of number | Layer B calibration score | Normalize to 0-100 scale |
| quality_score from write_quality_score (0-5) vs G1-G7 (0-100) | Scale mismatch | Score > 5 means already on 0-100 scale |

## Pitfalls

- Step files are stored in `<paper-dir>/01-manuscript/`, not directly in the paper dir. Always use the subdirectory path.
- 100+ papers can be in the directory without state tracking. These represent completed work that lost state file.
- Papers with prior G1-G7 have score 0-100. Papers from write_quality_score only have score 0-5. This affects gate threshold decisions.
- At g1g7_gate_check: 45 CONDITIONAL, 19 FAIL, and missing-gate papers need entirely different actions. Classify before acting.

## Support Files

- `scripts/paper-queue-health.py` — Automated audit script
- `references/state-filesystem-mismatch-2026-06-11.md` — state.json ↔ filesystem mismatch pattern and fix
- `references/quality-score-scale-detection-2026-06-11.md` — Three-scale quality_score detection (0-100, 0-5, dict)

## Related

- `paper-pipeline` — Full pipeline for advancing papers through stages
- `quality-gate` — G1-G7 gate check methodology