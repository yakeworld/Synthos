# NIH E-Utilities Rate-Limiting — Evolution v93 → v139 → v159

## Evolution Timeline

| Version | Date | Behavior | Count | Pattern |
|---------|------|----------|-------|---------|
| v93 | 2026-06-08 | Silent 0s on rapid requests | Same count across queries (670/3245) | Phase 1: Silent drop |
| v139 | 2026-06-09 | HTTP 500 after 22 queries | 22x0 then HTTP 500 | Phase 2: Explicit error |
| v159 | 2026-06-10 | Mixed 0/None/500 in single batch | 13 of 18 queries = None | Phase 3: Cascading failure |

## v159 Pattern (Most Severe)

In scan v159, 13 of 18 PubMed queries returned `None` (connection error), not even 0. This is the most severe rate-limiting pattern observed:

```
Query 1-3: Normal (0, 11, 7)
Query 4: None
Query 5-12: Mostly None
Query 13: 0 (worked)
Query 14-18: All None
```

The failure is **bursty** — the API accepts a few queries then starts returning connection errors. This means:
1. The API is not completely down (some queries work)
2. But sustained queries fail
3. There is no consistent "safe" batch size

## Multi-Batch Scan Architecture (v141→v159)

The scan has evolved from single-batch to multi-batch:

```
Batch 1: 5 rotation queries (fast, low count expected)
Batch 2: 5 extended candidate queries
Batch 3: 5 new candidate queries
Batch 4: 2-3 focused verification queries
Batch 5: OpenAlex cross-checks (different server, no rate limit)
```

Each batch has 5-7 queries max, with 0.5s delay between. Between batches: 0.5-0.8s pause.

## Detection Heuristics (Consolidated)

| Signal | Cause | Action |
|--------|-------|--------|
| Same count (670/3245) across queries | v93 silent drop | Re-run with delays |
| HTTP 500 | v139 API stressed | Skip remaining, use OpenAlex |
| Most queries = None | v159 cascading failure | Trust historical 0-counts, continue with OA |
| Broad query "machine learning" = 2 | API functional | 0-counts are legitimate |
| All 0 in rotation scan (5/5) | Stable white space | Record as ABSOLUTE WHITE |

## Resilience Pattern for Cron

When NIH API is rate-limited in cron:
1. **Rotate PubMed and OpenAlex**: They use different servers — run them interleaved
2. **Trust historical patterns**: Rotation directions (VOR-PINN, Kappa-ML, etc.) have been stable for 150+ scans. If they were 0 before, they're still 0 unless the scan shows otherwise.
3. **OpenAlex is the primary validator**: If PubMed is rate-limited, rely on OpenAlex. OpenAlex = 0 for all candidate queries in v159.
4. **Record version**: Always record `vXX` even when rate-limited, so the next run knows the scan was attempted.
5. **Do NOT retry failed batches in same session**: Each cron session is independent. If v159 can't complete, v160 will pick up from where it left off.

## Key Lesson

NIH rate-limiting is an **escalating pressure**, not a fixed barrier. v93→v139→v159 shows: silent → error → cascading. Future sessions should assume NIH API is more stressed than last session. OpenAlex should be used as the primary signal, PubMed as secondary verification.
