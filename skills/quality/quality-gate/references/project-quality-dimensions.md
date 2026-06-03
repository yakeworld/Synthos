# Project-Level Quality Dimensions

> Extends quality-gate from individual-deliverable level (L1-L4) to **project-system level**. Use when assessing a project holistically rather than a single document/output.

## The 6-Dimension Framework

| Dimension | Weight | Description | What It Measures |
|:----------|:-------|:------------|:-----------------|
| D1 基础设施完整性 | 15% | git, CI, LICENSE, README(中) | Project is findable and maintainable |
| D2 认知原子/核心健康 | 25% | Skill files complete, tests passing | Core functionality works |
| D3 工具链就绪 | 20% | Engines, pipelines, scripts accessible | Someone else can use it |
| D4 文档一致性 | 15% | Versions match across files, no stale data | Documents tell the same story |
| D5 文件整洁性 | 10% | No cruft, archive/ clean, no temp files | Easy to navigate |
| D6 外部可接入性 | 15% | Setup guide, onboarding, agent can use | New contributors can start |

## Scoring Scale

| Score | Meaning | Color |
|:------|:--------|:------|
| ≥0.95 | Excellent, no gap | ✅ |
| 0.80–0.94 | Good, minor gap | 🟡 |
| 0.60–0.79 | Fair, needs work | 🔶 |
| <0.60 | Critical, must fix first | 🔴 |

## Exit Threshold

A project is **closed-loop complete** when ALL 6 dimensions ≥ their threshold:

| Dimension | Pass Threshold |
|:----------|:---------------|
| D1 | ≥0.95 |
| D2 | ≥1.0 |
| D3 | ≥0.95 |
| D4 | ≥0.95 |
| D5 | ≥0.90 |
| D6 | ≥0.90 |

Weighted composite ≥ 0.95 to consider project "done."

## How to Use in a Session

1. Create `PROJECT_QUALITY.md` at project root with the 6D table
2. Score each dimension via direct assessment (file checks, version grep, diff)
3. Identify the dimension with the **largest gap × weight** product
4. Fix ONE dimension at a time (smallest-first wins: D4 usually fastest)
5. Re-score after each fix
6. When all pass → project closed-loop complete, move to next project

## Pitfall

- **Don't mix deliverable quality (L1–L4) with project quality (D1–D6)**. They are different levels: L1–L4 is for a single deliverable's production readiness; D1–D6 is for a project's system health. A project can be D4 0.60 (docs stale) while its individual deliverables are L3 (professionally written).
- **Self-assessment drift**: `PROJECT_QUALITY.md` is only as good as its `last_updated` field. A stale score table (e.g. 7 days old) can show all ✅ while the actual state has degraded. **Always re-evaluate D1-D6 from scratch** — trust git status output, `wc -l` counts, and file existence checks. Don't inherit old scores. Real-world example (Synthos, 2026-05-23): self-reported scores were all ~0.95+ (last_updated 2026-05-16), actual assessment found D4 at 0.78, D5 at 0.75. The delta was 0.15–0.20 per dimension.
