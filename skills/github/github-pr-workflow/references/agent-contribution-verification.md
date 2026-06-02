# Agent Contribution Verification Pattern

> Using GitHub PRs as an **agent marketplace**: external AI agents submit contributions as PRs, CI verifies them through gates, humans decide to merge.
> Primary umbrella: `github-pr-workflow`
> Related: `project-security-audit` (secret scanning overlap)

## When To Use This Pattern

- A project wants to invite external AI agents to contribute (not just humans)
- The project has a constitutional/documentation framework that contributions must respect
- You want automated quality gates before human review
- You want a public "agent registry" — every accepted PR registers the agent

## Architecture

```
External Agent
     │
     ├── Fork + Branch
     │   └── Includes AGENT_MANIFEST.yaml at root
     │
     ├── Submit PR with [agent] prefix in title
     │
     ▼
GitHub Actions: 6-Gate Verification Pipeline
     │
     ├── Gate 1: Identity  — AGENT_MANIFEST.yaml exists & valid
     ├── Gate 2: Syntax    — YAML/Python/JSON parse correctly
     ├── Gate 3: Secrets   — No hardcoded API keys or credentials
     ├── Gate 4: Constitution — Changes respect project principles
     ├── Gate 5: Quality   — Score ≥ 0.7 on 5 dimensions
     └── Gate 6: Impact    — Maps to affected architecture layer
     │
     ▼
Human Review (人在回路)
     ├── Merge → Agent registered, contribution absorbed
     └── Close → Feedback provided
```

## Protocol Details

### 1. Agent Identity (AGENT_MANIFEST.yaml)

Every agent PR MUST include this file at repo root:

```yaml
agent:
  name: "Agent-Name"
  version: "1.0.0"
  framework: "langgraph"  # or autogen, crewai, a2a, etc.
  contact: "URL_or_issue_link"
  capability: "What the agent does"
  verification:
    self_test_passed: true
```

### 2. PR Title Convention

```
[agent] <action>: <scope/path> — <summary>
```

Examples:
- `[agent] add: sources/pubmed — PubMed API source`
- `[agent] improve: evolution-engine — diversity scoring`
- `[agent] proposal: constitutional-amendment — external agent clause`

### 3. Verification Gate Scripts

Structure the gates as standalone Python scripts under `.github/scripts/`:

| Script | Purpose | Exit Code |
|--------|---------|-----------|
| `gate1_identity.py` | Validate AGENT_MANIFEST.yaml | 0=pass, 1=fail |
| `gate2_syntax.py` | Check YAML/Python/JSON | 0=pass, 1=fail |
| `gate3_secrets.py` | Scan for hardcoded secrets | 0=pass, 1=fail |
| `gates456_advanced.py` | Constitution + Quality + Impact | 0=pass, 1=fail |

**Key design rule**: Keep CI workflow YAML minimal. Put logic in scripts. This avoids YAML indentation issues with inline Python heredocs.

### 4. Quality Scoring Dimensions

| Dimension | Weight | What It Measures |
|-----------|--------|-----------------|
| Completeness | 0.25 | AGENT_MANIFEST, test evidence, docs |
| Clarity | 0.15 | PR description, code comments |
| Relevance | 0.20 | Alignment with project goals |
| Safety | 0.25 | No destructive changes, backward compatible |
| Testability | 0.15 | Can the contribution be validated? |

Threshold: **≥ 0.7** to pass.

### 5. Impact Levels

| Level | What Changes | Human Reviewer |
|-------|-------------|----------------|
| Cosmetic | README, docs, gitignore | Auto-merge if all gates pass |
| Incremental | Skills, sources, templates | Standard review |
| Structural | Core, evolution engine, SKILL.md | Owner review required |
| Constitutional | CONSTITUTION.md | Owner only |

## Trigger Configuration

The workflow should be configured to only trigger for agent PRs:

```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened]
    branches: [main]

jobs:
  gate-1-identity:
    if: startsWith(github.event.pull_request.title, '[agent]')
    ...
```

Non-agent PRs skip the pipeline entirely.

## Why GitHub (not a custom platform)

- GitHub already has fork, branch, PR, review, merge — the full lifecycle
- Issues are "proposals", PRs are "contributions" — natural mapping
- Actions provides free CI for verification
- The Agent Registry is implicit (every merged PR = registered agent)
- No new infrastructure, no protocol negotiation

## Pitfalls

- **YAML indentation** when embedding Python in GitHub Actions: Use `<< 'PYEOF'` heredocs or (better) extract scripts to `.github/scripts/`. Python code at column 0 inside a YAML block scalar causes scanner errors.
- **GitHub Actions YAML vs yamllint**: yamllint can't parse GitHub Actions syntax (`<<`, `|`, inline JSON). If you have a CI lint check, exclude `.github/` from it or add a yamllint config that ignores the directory.
- **AGENT_MANIFEST.yaml on main**: If the manifest format changes, existing branches still reference the old format. Gate 1 should be lenient on optional fields and only fail on missing required ones.
- **Trust escalation**: An agent that passes Gates 1-6 might still submit malicious code. The human gate (final review) is non-negotiable. Never auto-merge structural/constitutional changes.
- **Branch protection is REQUIRED**: Without `required_status_checks` on the main branch, agents can bypass the 6-gate pipeline by pushing directly. Use `github-repo-management` Section 6 to set up protection. Key: personal repos need `"restrictions": null` explicitly, not omitted.
- **Test the full flow**: Before announcing the agent contribution pipeline, run a test PR with a dummy AGENT_MANIFEST.yaml to verify: (a) the workflow triggers on `[agent]` prefixed PRs, (b) all 4 jobs pass, (c) the summary comment posts, (d) the PR shows `mergeStateStatus: BLOCKED` (protection active).
