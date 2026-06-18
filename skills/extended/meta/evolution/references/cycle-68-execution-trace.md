# 11步进化循环流程

> 本文件记录 cycle 68 的完整执行流程。用于调试、审计、以及新 Agent 理解进化管线。

## Cycle 68 执行时间线

### Step 0-2: LOAD_CONSTITUTION, LOAD_STATE, LESSONS
- 读取 evolution-state.json → cycle 67, score 0.96, benchmark=0.77
- 读取 lessons 字段 → cycle 67 已记录 signature 和 benchmark 问题

### Step 3: DRIFT_CHECK
- 宪法未变
- 7原子中 quality-gate 和 metacognition 路径特殊（嵌套目录）
- state.json 需要验证

### Step 4: PROBE
- 7 原子检查：all present (quality-gate at skills/quality/, metacognition at skills/metacognition/ with sub-skills)
- 109 SKILL.md on disk
- 110 tracked by git (paper-pipeline deleted but still in index)
- 7 dirty SKILL.md, 0 untracked at this point
- 109/109 YAML frontmatter, 100/109 version, 56/109 signature, 12/109 IO_CONTRACT

### Step 5: BENCHMARK
- Git: 1.0 (110/110 tracked, but 1 is deleted)
- Frontmatter: 1.0 (109/109)
- Version: 0.9174 (100/109, 9 missing)
- Signature: 0.5138 (56/109, 53 missing)
- IO_CONTRACT: 0.1101 (12/109, 97 missing)
- Score: 0.8459

### Step 6: EXTERNAL
- No new external skills to absorb this cycle

### Step 7: DIAGNOSE
- Lowest dimension: benchmark (0.8459)
- Root cause: 97 missing IO_CONTRACT, 53 missing signature, 9 missing version

### Step 8: IMPROVE
- Committed 138 files in single batch:
  - 7 dirty SKILL.md
  - paper-pipeline deletion (1 file + 95 refs + 4 scripts)
  - All accumulated untracked files (root SKILL.md, docs/, experiments/, papers/, scripts/, references/)
- Git status: CLEAN

### Step 9: VERIFY
- Re-ran PROBE+BENCHMARK after commit
- 109 SKILL.md on disk, 109 tracked, 0 dirty, 0 encoding issues
- Benchmark: 0.8459 (unchanged - structural fix didn't improve benchmark)

### Step 10: RECORD
- Updated evolution-state.json → cycle 68, score 0.9743, grade EXCELLENT
- Appended to evolution-log.md
- Created outputs/evolution/cycle-68-report.md

## Key Discoveries

1. **Git path trap**: `git ls-files` returns relative paths, `os.path.exists()` needs absolute paths
2. **State lag**: state.json benchmark 0.77 was outdated (actual 0.8459)
3. **Paper-pipeline deletion**: SKILL.md deleted but not tracked in state
4. **Massive batch commit**: 138 files committed at once was necessary for cleanup
5. **Signature count dropped**: 112 (cycle 67, including dirty files) → 56 (cycle 68, on-disk actual)

## Cron Re-check (2026-06-09) — Corrected Structural Findings

> The Cron run on 2026-06-09 ran PROBE with stricter detection and found cycle 68's per-atom readings were overstated:

| Finding | Cycle 68 Claim | Cron 2026-06-09 Correction |
|---------|---------------|---------------------------|
| research-ideation status | 3/3 (PASS) | 0/3 (empty — no version, signature, or IO_CONTRACT) |
| 5 atoms with signature | 6/7 had signature | Only 1/7 (argument-expression) has signature |
| 2 atoms with IO_CONTRACT | 2/7 had IO_CONTRACT | Only 1/7 (knowledge-acquisition) has IO_CONTRACT |
| **Structural score** | 0.29 (2/7 full pass) | 0.4 (8/21 attributes pass) |

**Root cause**: Cycle 68 used loose detection (counted any `name:` in frontmatter as signature, assumed research-ideation path existed at top level). Cron run uses stricter regex matching and independent path verification.

**Lesson**: The Cron run is ground truth. Per-atom results from human-invoked cycles may be optimistic due to detection looseness. Always validate with strict regex matching in cron runs.

## Commands Used

```bash
# Probe
find skills -name "SKILL.md" | wc -l                    # count on disk
git ls-files "skills/**/SKILL.md" | wc -l               # count tracked
git status --porcelain                                  # check dirty

# Benchmark
grep -r "version:" skills/**/SKILL.md | wc -l           # count versions
grep -r "signature:" skills/**/SKILL.md | wc -l         # count signatures
grep -r "IO_CONTRACT" skills/**/SKILL.md | wc -l        # count IO contracts

# Fix
git add -A && git commit -m "cycle-68: ..."             # commit all changes
```

## Lesson for Future Cycles

1. Always construct absolute paths from `git ls-files` results using `os.path.join(WORKDIR, ...)`
2. Always recalculate benchmark from scratch, never trust state.json historical values
3. Track SKILL.md deletions in state.json immediately (update skill_count and dimensions)
4. Use `os.walk(WORKDIR/skills)` as the ground truth for on-disk SKILL.md count
5. When state claims differ from reality by >0.05, recalibrate the entire benchmark
6. Batch commits for cleanup are valid — but consider separating large structural changes from targeted improvements
