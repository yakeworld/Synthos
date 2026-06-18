# Agent Contribution Workflow — Concrete Implementation Example

This document captures the exact AGENTS_CONTRIBUTING.md, VERIFICATION_GATES.md, and CI pipeline files created for the Synthos project. Use as reference when implementing for other projects.

## File Structure

```
project-root/
├── AGENTS_CONTRIBUTING.md         ← Machine-readable agent contribution guide
├── VERIFICATION_GATES.md          ← 6-gate pipeline specification
└── .github/
    ├── workflows/
    │   └── agent-pr-verify.yml    ← CI workflow (triggers on [agent] PRs)
    └── scripts/
        ├── gate1_identity.py      ← Validate AGENT_MANIFEST.yaml
        ├── gate2_syntax.py        ← Validate syntax of changed files
        ├── gate3_secrets.py       ← Scan for hardcoded secrets
        └── gates456_advanced.py   ← Constitutional + Quality + Impact
```

## Key Design Decisions

### 1. Separate Scripts from YAML

**Do NOT embed Python code in `run: |` blocks.** The `<< 'PYEOF'` heredoc pattern within YAML `|` block scalars causes indentation parsing errors. Instead:

```yaml
# WRONG — YAML parser breaks
run: |
  python3 << 'PYEOF'
  import yaml
  with open('file') as f:
  PYEOF

# RIGHT — call external script
run: python3 .github/scripts/gate1_identity.py
```

### 2. Scope Validation to Changed Files Only

All scripts use `git diff --name-only HEAD~1 HEAD` to scope their checks to only the files changed in the PR, not the entire repo. This prevents pre-existing issues from blocking legitimate agent contributions.

### 3. Check Context Names Must Match

The branch protection "checks" array must have `context` values that **exactly** match the GitHub Actions job `name` values. Example:

```yaml
# Workflow job name:
gate-1-identity:
  name: "Gate 1: Agent Identity"
  
# Branch protection context:
{"context": "Gate 1: Agent Identity", "app_id": 0}
```

### 4. Personal vs Org Repo Branch Protection

```bash
# Personal repo: restrictions must be null (not omitted)
{
  "restrictions": null,
  "enforce_admins": false
}

# Org repo: restrictions is a proper object
{
  "restrictions": {"users": ["admin"], "teams": []},
  "enforce_admins": true
}
```

### 5. PR Title Convention

The workflow only triggers on PRs where:
```yaml
if: startsWith(github.event.pull_request.title, '[agent]')
```
This is intentional — non-agent PRs go through standard human review without CI gates.
