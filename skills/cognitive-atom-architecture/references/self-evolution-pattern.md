# Self-Evolution Pattern: Meta-Atom Design v2.0

## Overview

This document records the Synthos Evolution Engine v2.0.0 as a worked example of the meta-atom pattern. v2.0 builds on v1.0 (structural probes only) by adding functional benchmarks, external skill absorption, skill tree tracking, and comprehensive scoring.

## File Structure

```
skills/evolution/
├── SKILL.md                       # Evolution cycle v2.0 (8 steps)
├── references/
│   ├── IO_CONTRACT.md             # I/O contract
│   ├── QUALITY_CRITERIA.md        # Structural/funcional quality weights
│   ├── EVIDENCE_SCHEMA.md         # Evidence chain node types
│   ├── BOUNDARY.md                # What evolution can/cannot fix
│   ├── CHANGE_LOG.md              # Version history
│   ├── BENCHMARKS.md              # 12 benchmark test scenarios across 7 atoms
│   ├── ABSORPTION.md              # External GitHub/Hermes/paper search + absorption workflow
│   └── SKILL_TREE.md              # Skill tree growth and tracking strategy
```

```
outputs/evolution/
└── report_{cycle}.json            # Per-cycle full report (probe + benchmark + diagnosis + actions)
```

## Evolution Cycle v2.0 (Detailed)

### Step 1: LOAD_STATE

Read these files at the start of each cycle:
- `evolution-state.json` — current quality_metrics, synthos_metrics, evolution_count, skill_tree
- `evolution-log.md` — last 30 lines for recent history
- `evolution-config.yaml` — evolution parameters (cycle interval, thresholds)

### Step 2: PROBE (structural — every cycle)

For each atom, use `terminal(cat <atom>/SKILL.md)` (NOT skill_view — project-local skills not in Hermes registry) to:
1. Load SKILL.md → check loadability (weight 0.30)
2. Validate frontmatter name (weight 0.15): must match directory name
3. Validate description (weight 0.15): ≥80 chars, concrete keywords
4. Check allowed-tools (weight 0.10): field present in text
5. Check reference files (weight 0.30): terminal(cat) each of IO_CONTRACT, EVIDENCE_SCHEMA, BOUNDARY, CHANGE_LOG

**`terminal(cat)` vs `read_file()`**: `read_file()` returns `{'status': 'unchanged'}` with no content for files already read in the same conversation (dedup cache). In cron sessions there's no prior conversation, so `read_file` works fine. But for consistent results in any context, `terminal(cat path)` is more reliable — it always returns the current file content.

For knowledge-acquisition, additionally — API health check with curl:
- `curl -s -o /dev/null -w "%{http_code}" "https://api.semanticscholar.org/graph/v1/paper/search?query=test&limit=1"` (mit x-api-key header)
- `curl -s -o /dev/null -w "%{http_code}" "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=test&retmax=1"`
- `curl -s -o /dev/null -w "%{http_code}" "https://api.openalex.org/works?search=test&per_page=1"`
- API health = (S2_200?1:0 + PubMed_200?1:0 + OpenAlex_200?1:0) / 3
- knowledge-acquisition overall = structural × 0.80 + api_health × 0.20

### Step 3: BENCHMARK (functional — rotating, every cycle)

**Rotation**: Odd cycles → knowledge-acquisition + knowledge-extraction + association-discovery. Even cycles → hypothesis-generation + argument-expression + viewpoint-verification. task-router tested every cycle.

For each atom in the current batch:
1. Load `references/BENCHMARKS.md` to get test scenarios for that atom
2. Pick a test that hasn't been run recently (or the first one)
3. Execute — for knowledge-acquisition: curl S2/Pubmed/OpenAlex and check paper count ≥5
4. For knowledge-extraction: extract from an abstract → check 4 fields
5. For association-discovery: analyze papers → check associations found
6. Score: pass(1.0) / partial(0.5) / fail(0.0)

**benchmark_score = passed_tests / total_tests_this_cycle**

### Step 4: EXTERNAL (absorption search — every 7th cycle)

Only runs when `current_cycle % 7 == 0`. Skip otherwise.

Search GitHub via `web_search`: "AI research assistant", "semantic scholar agent", "academic paper agent". Filter: Star ≥ 50, updated in last year, readable README.

Search Hermes skills via `skills_list`: look for complementary skills (systematic-review, openalex, pubmed, competition-submission, nsfc-grant-audit, etc.).

Search papers: "autonomous literature review system 2025".

Score each candidate (0-5 per dimension): Complementarity(×0.25), Code quality(×0.20), Community(×0.15), Integration cost(×0.25), License(×0.15). ≥4.0 → proposal; 3.0-3.9 → log; <3.0 → skip.

Proposals go into the report but are NEVER auto-executed. User must approve.

### Step 5: DIAGNOSE (comprehensive scoring)

Compare each atom's current structural score vs last recorded trust_score. Track:
- Degradation: score drop > 0.1 → DEGRADED
- Critical: score < 0.5 → CRITICAL (atom load failed)
- Missing: file not found → MISSING

Compute overall:

```
overall = structural_avg × 0.30 + benchmark_score × 0.40 + skill_tree_coverage × 0.20 + absorption_potential × 0.10
```

| Level | Score | Status |
|-------|-------|--------|
| EXCELLENT | ≥ 0.85 | healthy |
| GOOD | 0.70—0.84 | minor_degradation |
| FAIR | 0.50—0.69 | needs_attention |
| POOR | < 0.50 | needs_intervention |

### Step 6: IMPROVE (conservative + proposals)

**Automatic fixes** (structure only):
1. Missing reference file: `write_file()` create from pattern
2. Outdated version/CHANGE_LOG: `patch()` append entry
3. Frontmatter corruption: `patch()` fix field

**Proposals** (user must approve):
1. Absorption candidates from EXTERNAL step
2. Benchmark-identified gaps (e.g., ACQ-01 failed 3 times → suggest adding more search sources)

### Step 7: VERIFY

Re-read patched atom SKILL.md via `terminal(cat)`. Confirm:
- File loads without error
- Structural score now ≥ previous baseline

If verification fails: revert the patch and log the failure.

### Step 8: RECORD

**evolution-state.json update** — patch:
```json
{
  "last_updated": "<ISO>",
  "evolution_count": <n+1>,
  "evolution_engine": { "cycle": <n>, "status": "...", "last_cycle": {...} },
  "skill_tree": { "total_skills": 7, "core_atoms": 7, "extended_skills": 0, "benchmark_pass_rate": <float> },
  "quality_metrics": { "<atom>": { "trust_score": <probe_score> } }
}
```

**evolution-log.md append**:
```
## 进化周期 #{cycle} — {timestamp}
- **综合分**: {overall} (结构{structural}+基准{benchmark}+技能树{tree}+吸收{absorp})
- **状态**: {status}
- **结构平均分**: {structural_avg}
- **基准通过率**: {benchmark_score}
- **API健康**: {api_health}
- **退化原子**: {degraded}
- **执行操作**: {actions}
- **详情**: outputs/evolution/report_{cycle}.json
```

**outputs/evolution/report_{cycle}.json** — full cycle report with probe_results, benchmark_results, external_findings, diagnosis, actions, verification.

## Cron Integration

```yaml
cronjob action=create \
  name=synthos-evolution \
  skills=["evolution"] \
  schedule="0 6 * * *" \
  enabled_toolsets=["terminal", "web", "file", "skills"] \
  workdir=/media/yakeworld/sda2/Synthos \
  prompt="Execute Synthos self-evolution cycle v2.0..."
```

**Required setup**: The evolution SKILL.md is project-local at `/media/yakeworld/sda2/Synthos/skills/evolution/`. Cron needs it accessible via `skill_view`, so create a symlink:
```bash
ln -sf /media/yakeworld/sda2/Synthos/skills/evolution ~/.hermes/skills/evolution
```

All atoms remain project-local (loaded by `terminal(cat)` or `read_file()`), but the meta-atom itself needs Hermes registration for cron loading.

## Pitfalls (v2.0)

1. **Expensive probes**: Full functional execution of each atom takes 10-30 minutes. Structural probes only in the daily PROBE step. Benchmark tests are lightweight (curl + text check, ~60s per atom).

2. **Network flakiness**: API health checks may fail due to transient issues. Record but don't act until 3 consecutive failures.

3. **read_file dedup**: `read_file()` returns `{'status': 'unchanged'}` without content for files already read in the same conversation. Use `terminal(cat path)` for probes when you need fresh content. In cron sessions (no prior conversation) this is not a problem.

4. **Cron authentication**: Cron jobs run without SSH agent or user environment. If evolution needs API keys, ensure they're in `.bashrc` or a file accessible by the cron session. `source ~/.bashrc` may not fire in all shells — prefer env vars set in the shell profile loaded by cron.

5. **Log file growth**: `evolution-log.md` grows unbounded. Consider rotating or truncating after 100 entries (keep only last 50).

6. **First benchmark cycle is baseline**: No previous benchmark scores to compare against. The real trend data starts from cycle 3.

7. **External search is sparse**: Absorption candidates are rare. Expect most cycles to find 0-1 viable candidates. Don't force proposals — reporting "nothing found" is the correct behavior.

8. **skill_view vs terminal cat for project skills**: Synthos atoms are NOT in `~/.hermes/skills/`. They're at `/media/yakeworld/sda2/Synthos/skills/<name>/`. `skill_view()` will return "not found" for them. Always use `terminal(cat path)` or `read_file(path=absolute_path)` for Synthos atom files. Only the `evolution` meta-atom itself gets symlinked into Hermes for cron loading.
