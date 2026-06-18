# Agent Contribution Protocol — Quick Reference

## Files to Create

### 1. AGENTS_CONTRIBUTING.md

Machine-readable guide for AI agents. Key sections:
- Entry points (Issues vs PRs, trust levels)
- AGENT_MANIFEST.yaml spec (required for all agent PRs)
- PR title convention: `[agent] <action>: <summary>`
- Verification flow diagram
- Agent registry entry template

### 2. VERIFICATION_GATES.md

6-gate pipeline:
1. Identity — AGENT_MANIFEST.yaml exists and valid
2. Syntax — YAML, Python, JSON all parse correctly
3. Secrets — No hardcoded API keys/tokens
4. Constitutional — Changes respect P0-P3 principles
5. Quality — Score ≥ 0.7 (completeness, clarity, relevance, safety, testability)
6. Impact — Categorize as cosmetic/incremental/structural/constitutional

### 3. GitHub Actions Workflow

```yaml
# .github/workflows/agent-pr-verify.yml
# Trigger: PRs with [agent] prefix targeting main
# Jobs: gate-1-identity → gate-2-syntax + gate-3-secrets → gate-456-advanced → summary
# Permissions: contents: read, pull-requests: write
```

### 4. Verification Scripts (in .github/scripts/)

- `gate1_identity.py` — Validate AGENT_MANIFEST.yaml
- `gate2_syntax.py` — Validate changed file syntax (git diff-based)
- `gate3_secrets.py` — Scan for hardcoded secrets
- `gates456_advanced.py` — Constitutional + Quality + Impact analysis

## Branch Protection for Agent PRs

```bash
# Must include 4 CI check contexts matching workflow job names
"checks": [
  {"context": "Gate 1: Agent Identity", "app_id": 0},
  {"context": "Gate 2: Syntax Validation", "app_id": 0},
  {"context": "Gate 3: Secret Scan", "app_id": 0},
  {"context": "Gates 4-6: Constitution, Quality, Impact", "app_id": 0}
]
# Personal repo: restrictions=null
# enforce_admins: false (to allow admin merge bypass)
```

## Common Pitfalls

- **YAML heredoc**: GitHub Actions `run: |` blocks with `<< 'EOF'` heredocs confuse YAML parsers. Write Python scripts as separate `.py` files in `.github/scripts/` and call them from `run:` blocks.
- **Secret scan regex**: Generic 20+ char alphanumeric patterns cause false positives. Use targeted patterns (sk-..., ghp_..., AKIA...).
- **Quality scoring**: Keep it simple — weights × dimensions. The CI doesn't need sophisticated scoring, just a consistent threshold.
- **PR merge**: Use `gh pr merge --squash --admin` when user approves (requires enforce_admins=false).
