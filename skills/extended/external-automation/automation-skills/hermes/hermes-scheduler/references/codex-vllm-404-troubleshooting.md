# Codex Cron Job vLLM 404 Troubleshooting

## Problem

Cron jobs using `codex -p <provider> exec` fail with:
```
ERROR: unexpected status 404 Not Found: The model `X` does not exist., url: http://<host>:8000/v1/responses
ERROR: Reconnecting... 1/5 through 5/5
```

## Diagnostic Path

### Step 1: Identify the broken provider

The cron script calls `codex -p <profile> exec`. The profile maps to:
```
~/.codex/<profile>.config.toml
```

For the `amax` profile, check:
```bash
cat ~/.codex/amax.config.toml
# Look for: model = "...", base_url = "http://..."
```

### Step 2: Verify the model exists on the endpoint

The vLLM endpoint may have been redeployed with a different model name. Check the current working configs:
```bash
cat ~/.codex/config.toml | grep -A3 "base_url"
cat ~/.codex/hermes.config.toml | grep -A3 "base_url"
```

The working model is typically `qwen3.6-35b-nvfp4` on the primary AMAX node (`http://100.125.10.93:8000/v1`).

### Step 3: Fix the config

Update the broken config file to match a working endpoint:
```toml
# Before (broken):
model = "Qwen3.6-35B-A3B-GPTQ-Int4"
base_url = "http://100.82.27.51:8000/v1"

# After (fixed):
model = "qwen3.6-35b-nvfp4"
base_url = "http://100.125.10.93:8000/v1"
```

### Step 4: Verify the fix

```bash
bash ~/.hermes/scripts/synthos-evolution-probe.sh 2>&1 | head -20
# Should show: model: qwen3.6-35b-nvfp4 (no 404 errors)
```

## Common Broken Patterns

1. **Old model name after vLLM redeploy** — The most common cause. The vLLM server is restarted with a different model, and old configs still reference the old model name.

2. **Stale IP address** — The vLLM server was migrated to a new host, but config files weren't updated.

3. **Case sensitivity** — `Qwen3.6-35B-A3B-GPTQ-Int4` vs `qwen3.6-35b-nvfp4` — vLLM model names are case-sensitive.

## Related Cron Scripts Using Codex

| Script | Provider | File |
|--------|----------|------|
| synthos-evolution-probe | amax | `.hermes/scripts/synthos-evolution-probe.sh` |
| synthos-github-discussion | amax | `.hermes/scripts/synthos-github-discussion.sh` |
| papers-daily-scan | hermes | `.hermes/scripts/papers-daily-scan.sh` |
| daily-papers-report | hermes | `.hermes/scripts/daily-papers-report.sh` |
| bib-standardization | hermes | `.hermes/scripts/bib-standardization.sh` |
