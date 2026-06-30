# Cron Provider Drift — 2026-06-29

## Problem

`vLLM 更新追踪` cronjob (job_id: 775aad716956) failed with:
```
Unknown provider 'custom:amax-1'. Check 'hermes model' for available providers, or run 'hermes doctor' to diagnose config issues.
```

## Root Cause

When server node 100.125.10.93 was removed from the infrastructure, the custom provider name changed from `custom:amax-1` to `custom:amax`. However, existing cronjobs pinned at creation time retain their original provider name, and `cronjob(action='update')` does NOT update the provider field.

## Fix

```
1. cronjob(action='remove', job_id='775aad716956')
2. cronjob(action='create', ..., model={'provider': 'custom:amax', ...})
```

## Prevention

After any server node change:
1. `cronjob(action='list')` — list all jobs
2. Check `provider` field for each job
3. Compare against current provider list (`hermes model` or config.yaml `custom_providers`)
4. Remove + recreate any jobs with stale provider names

## Note

Provider names in config.yaml:
- `custom:amax` → 100.100.252.99 (current primary)
- `custom:amax-fallback` → 100.82.27.51 (fallback)

Old names (`custom:amax-1`) no longer exist.