---
name: github-agent-contributions
description: Design GitHub-based contribution infrastructure for AI agents — AGENTS_CONTRIBUTING.md, verification gates, CI pipelines, trust models, OSS community building, and content strategy — that let external agents submit Issues/PRs with automated validation and human-in-the-loop merge.
author: Nous Research
license: MIT
version: 1.0.0
tags: [github, ci, agent-collaboration, contribution-guidelines, verification, multi-agent]
---

# GitHub Agent Contribution Infrastructure

## Trigger Conditions

- **Primary**: User asks to set up GitHub-based contribution infrastructure for AI agents
- **Secondary**: User wants to recruit AI agents via GitHub, design verification pipelines for agent-submitted code, or create contribution guides targeting AI agents
- **Tertiary**: User asks about OSS community building, content strategy, or trust models for agent contributions

## Trigger

User asks to open a project to external AI agent contributions, recruit AI agents via GitHub, design a verification pipeline for agent-submitted code, or create a "contribution guide for AI agents" (not just humans).

## Architecture Overview

The pattern uses **GitHub itself as the agent marketplace** — no custom platform needed:

```
External AI Agent
    │
    ├── Propose → Issue (with [agent] label)
    └── Contribute → PR (with [agent] prefix)
                        │
                        ▼
              GitHub Actions: 6-Gate Verification
              ┌─────────────────────────────────┐
              │ Gate 1: Identity (AGENT_MANIFEST)│
              │ Gate 2: Syntax (YAML/PY/JSON)    │
              │ Gate 3: Secrets (no hardcoded)   │
              │ Gate 4: Constitution compliance  │
              │ Gate 5: Quality score ≥ 0.7      │
              │ Gate 6: Impact level assessment   │
              └─────────────────────────────────┘
                        │
                        ▼
              Human Review (人在回路)
              ├── Merge → Agent registered in pool
              ├── Request changes → Re-submit
              └── Close → Feedback documented
```

## Required Documents

### 1. `AGENTS_CONTRIBUTING.md`

Machine-readable contribution guide for AI agents. Key sections:

- **[AGENT_PARSABLE]** structured YAML sections the agent can parse
- **Issue template**: Agent Identity (name, framework, capability) + Proposal + Evidence + Verification
- **PR requirements**: `[agent]` title prefix, `AGENT_MANIFEST.yaml` at repo root
- **PR body template**: Agent Manifest link, summary, changes list, self-verification checklist
- **Label convention**: `agent-submitted`, `agent-proposal`, `agent-gap`, `awaiting-human`
- **Tiered contribution channels**: Issues (L0), PR-New (L1), PR-Modify (L2)

### 2. `AGENT_MANIFEST.yaml`

Required in every agent PR — self-identification:

```yaml
agent:
  name: "Agent-Name"
  version: "1.0.0"
  framework: "langgraph"  # autogen, crewai, a2a, etc.
  capability: "Brief capability description"
  verification:
    self_test_passed: true
```

This builds an implicit **Agent Registry** from accepted PRs.

### 3. `VERIFICATION_GATES.md`

Full specification of the 6-gate pipeline. Each gate describes:

- **Purpose**: What it protects
- **Checklist**: What it validates
- **Pass/Fail conditions**: What happens on each outcome
- **Scoring rubric**: For quality gate (dimensions + weights)

### 4. `.github/workflows/agent-pr-verify.yml`

GitHub Actions workflow. **Critical design rule:**

> **Do NOT embed Python code inline in the YAML workflow file.**
> Write standalone Python scripts in `.github/scripts/` and call them from the workflow.
> YAML's `|` block scalar combined with Python heredocs (`<< 'PYEOF'`) causes indentation errors that break the YAML parser.

```yaml
# WRONG — YAML parser breaks on Python heredocs inside | blocks
run: |
  python3 << 'PYEOF'
  import yaml
  with open('file') as f:  # ← YAML parser sees this as a bare key
      data = yaml.safe_load(f)
  PYEOF

# RIGHT — call a separate script
run: python3 .github/scripts/gate1_identity.py
```

## Script Structure (`.github/scripts/`)

| Script | Gate | What it does |
|--------|------|-------------|
| `gate1_identity.py` | 1 | Validates AGENT_MANIFEST.yaml exists and has required fields |
| `gate2_syntax.py` | 2 | Checks YAML/Python/JSON syntax of **only PR-changed files** |
| `gate3_secrets.py` | 3 | Regex scan for API keys, private keys, tokens in changed files |
| `gates456_advanced.py` | 4-6 | Constitutional compliance check, quality scoring, impact level assessment |

**Key design pattern:** All scripts use `git diff --name-only HEAD~1 HEAD` to scope validation to PR-changed files only, not the entire repo.

> **吸收记录**: Gate 3 (Secrets Scanning) 的实现方法与 `project-security-audit` 技能内容重叠。该技能的核心方法论（secret pattern scanning、git commit detection、remediation workflow、.gitignore hygiene）已集成在此。原独立的 `project-security-audit` 技能已归档。

## Constitutional Gates (Gate 4)

The 4 principles to validate:

| Principle | Check | Penalty |
|-----------|-------|---------|
| P0: Evidence traceability | New sources must have DOI/URL | -0.2 |
| P1: Atom reproducibility | Must not break independent execution | Manual review |
| P2: Stable sink / evolution float | New contributions start as "proposals" | Direct LTS modification blocked |
| P3: Human-in-the-loop | Router/core changes flagged | -0.5, human required |

## Quality Scoring (Gate 5)

| Dimension | Weight | What it measures |
|-----------|--------|-----------------|
| Completeness | 0.25 | AGENT_MANIFEST present? |
| Clarity | 0.15 | PR description quality |
| Relevance | 0.20 | Maps to ≥1 project atom |
| Safety | 0.25 | No destructive changes |
| Testability | 0.15 | Test case provided? |

Score ≥ 0.7 = PASS.

## Impact Analysis (Gate 6)

| Level | Criteria | Reviewer |
|-------|----------|----------|
| Cosmetic | README, docs, formatting | Auto-merge if other gates pass |
| Incremental | skills/, sources/, templates/ | Standard human review |
| Structural | core/, SKILL.md, evolution- | Owner review required |
| Constitutional | CONSTITUTION.md | Owner only |

## Trust Model

```
L0: Issue → Anyone can propose (no identity verification)
L1: PR → Must have AGENT_MANIFEST.yaml (self-identified)
L2: PR (core) → Same as L1 + human review required
L3: Trusted contributor → After 2+ accepted PRs, expedited review
```

No monetary payments, no blockchain, no credential verification beyond GitHub accounts. Keep it simple.

## Branch Protection Setup

After the workflow is in place, protect the main branch so CI gates are enforced:

### For Personal Repos (this user's case)

```bash
# Create a JSON config file (inline JSON doesn't work with gh api --field)
cat > /tmp/bp.json << 'BRANCH_EOF'
{
  "required_status_checks": {
    "strict": true,
    "checks": [
      {"context": "Gate 1: Agent Identity", "app_id": 0},
      {"context": "Gate 2: Syntax Validation", "app_id": 0},
      {"context": "Gate 3: Secret Scan", "app_id": 0},
      {"context": "Gates 4-6: Constitution, Quality, Impact", "app_id": 0}
    ]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true
  },
  "restrictions": null,
  "required_linear_history": true
}
BRANCH_EOF

gh api repos/OWNER/REPO/branches/main/protection \
  --input /tmp/bp.json --method PUT
```

**Key differences for personal repos vs org repos:**
- `restrictions` must be `null` (not omitted) for personal repos. Org repos use `{"users": [...], "teams": [...]}`.
- `enforce_admins: false` allows the repo owner to bypass review via `gh pr merge --admin` when CI gates pass. Set to `true` if you want admins to also need reviews.
- The 4 check contexts must exactly match the job names in `agent-pr-verify.yml`.

### Merging with Admin Bypass

When CI gates pass and the user says "merge", use:
```bash
gh pr merge PR_NUMBER -R OWNER/REPO --squash --admin
```
This bypasses the required review for admin users. The `--squash` flag keeps linear history (required if `required_linear_history: true`).

## Testing the CI Pipeline

After pushing the workflow and branch protection, verify the pipeline end-to-end:

1. **Create a test branch** from main:
   ```bash
   git checkout -b test/agent-ci
   ```

2. **Add a minimal AGENT_MANIFEST.yaml**:
   ```yaml
   agent:
     name: "TestAgent-CI"
     version: "1.0.0"
     framework: "manual-test"
     capability: "CI pipeline test agent"
     verification:
       self_test_passed: true
   ```

3. **Add a test source file with a valid DOI** (so Gate 4 passes P0 checks):
   ```markdown
   ---
   provenance:
     url: "https://doi.org/10.1234/test.2026"
   ---
   # Test Source
   ```

4. **Commit, push, create PR with `[agent]` title prefix**:
   ```bash
   git add AGENT_MANIFEST.yaml sources/test-source.md
   git commit -m "[agent] test: CI pipeline verification"
   git push origin test/agent-ci
   gh pr create --title "[agent] test: CI pipeline" --body "### Summary\n\nTest PR" --base main --head test/agent-ci
   ```

5. **Verify** the workflow triggers and all 4 jobs pass. Check for the auto-comment with the verification report.

6. **Clean up**: The user can keep the test PR as a real example, or close it.

## Pitfalls

- **YAML heredoc trap**: Never embed `<< 'EOF'` Python heredocs inside `run: |` blocks in GitHub Actions YAML. The Python code's indentation breaks the YAML parser. Use `.github/scripts/` standalone files instead.
- **Secret scan false positives**: Generic "20+ char alphanumeric in quotes" regex catches legitimate documentation. Add exclude list for VERIFICATION_GATES.md, AGENTS_CONTRIBUTING.md.
- **Scope creep**: Each gate should be a separate job in the workflow so failures are isolated and skippable.
- **PR title check**: The `if: startsWith(github.event.pull_request.title, '[agent]')` condition only triggers on `[agent]` prefix. Non-agent PRs bypass verification entirely — that's by design.
- **Cannot self-approve PRs**: GitHub prevents the PR author from approving their own PR. For the repo owner, use `gh pr merge --admin` instead.
- **gh CLI working directory**: `gh pr` commands may fail with "not a git repository" when the CWD is not inside the repo. Always specify `-R OWNER/REPO` or `cd` into the repo first.

## Verification Checklist

Before deeming a project "agent-contribution ready", verify each item:

- [ ] `AGENTS_CONTRIBUTING.md` written with machine-parsable YAML sections and tiered contribution channels (L0 Issues, L1 PRs, L2 Core)
- [ ] `AGENT_MANIFEST.yaml` template provided in the guide
- [ ] `VERIFICATION_GATES.md` published with all 6 gates specified (Identity, Syntax, Secrets, Constitution, Quality, Impact)
- [ ] GitHub Actions workflow `.github/workflows/agent-pr-verify.yml` created with separate jobs per gate
- [ ] Gate scripts placed in `.github/scripts/` (not inline in YAML)
- [ ] Branch protection configured on `main` referencing all gate check contexts
- [ ] Trust model documented (L0-L3 tiering)
- [ ] Test PR submitted and all gates pass end-to-end
- [ ] Community content strategy in place (README badges, at least one external post drafted)
- [ ] `CITATION.cff` created for academic referencing

## References

- `references/agents-contributing-template.md` — reusable AGENTS_CONTRIBUTING.md template
- `references/verification-gates-template.md` — reusable VERIFICATION_GATES.md template  
- `references/github-actions-patterns.md` — YAML workflow patterns for agent PR verification

## Related Skills

- `github-code-review` — reviewing human PRs (complementary, different audience)

## Community Building & OSS Promotion

In addition to the technical agent contribution infrastructure above, use these patterns to promote your project and grow a contributor community.

### README Optimization

Add a badge row at the top:
```markdown
<p align="center">
  <a href="https://github.com/OWNER/REPO/stargazers"><img src="https://img.shields.io/github/stars/OWNER/REPO?style=flat&logo=github" alt="Stars"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License"/></a>
  <a href="https://github.com/OWNER/REPO/discussions"><img src="https://img.shields.io/badge/Community-Discussions-blueviolet" alt="Discussions"/></a>
</p>
```

Key sections: one-liner, architecture diagram, quick start, contribution link, badges, reference table.
For bilingual projects: create `README.md` (English) and `README_CN.md` (Chinese) with cross-links.

### GitHub Config via API
```bash
# Topics (increases search discoverability)
curl -X PUT https://api.github.com/repos/OWNER/REPO/topics \
  -H "Authorization: token $(gh auth token)" \
  -H "Accept: application/vnd.github.mercy-preview+json" \
  -d '{"names":["ai-agent","cognitive-architecture","open-source"]}'

# Discussions
gh api repos/OWNER/REPO -X PATCH -f has_discussions=true
```

### CITATION.cff
Create for academic referencing:
```yaml
cff-version: 1.2.0
title: "Project Name"
type: software
authors:
  - family-names: "Author"
    given-names: "Name"
repository-code: "https://github.com/OWNER/REPO"
license: MIT
```

### Github Release
```bash
gh release create v1.0.0 -R OWNER/REPO --title "v1.0.0" --target main --latest
```

### Content Strategy

- **Zhihu (知乎)**: Long-form article. Title formula: 《我开源了一个[one-liner]——[hook]》. Structure: 缘起→思考→设计→效果→开放→未来.
- **Reddit**: Target r/AIAgents, r/MachineLearning (Showcase Saturday), r/Python, r/opensource.
- **Twitter/X**: Announcement thread with key stats and GitHub link.

See `references/community/zhihu-article-template.md` and `references/community/reddit-posting-guide.md`.

### Automation
Set up a daily cron job for promotion monitoring:
```bash
cronjob action=create name=PROJECT-daily-promotion \
  schedule="0 9 * * *" \
  prompt="Check GitHub stars/forks, read evolution state, generate daily report, suggest social posts"
```

### Metrics & Milestones
| Metric | 1-month | 3-month | 6-month |
|--------|---------|---------|---------|
| Stars | 50 | 200 | 500+ |
| Forks | 10 | 30 | 100+ |
| Contributions | 2 | 10 | 30+ |

### AI Agent Contribution Protocol

For projects that want AI agents to contribute, create these files:
- `AGENTS_CONTRIBUTING.md` — machine-readable contribution guide
- `VERIFICATION_GATES.md` — 6-gate verification pipeline
- `.github/workflows/agent-pr-verify.yml` — CI workflow

These are fully documented in the main sections above (Branch Protection, Script Structure, Constitutional Gates). See `references/community/agent-contribution-protocol.md` for the full setup guide.

> **吸收记录**: `open-source-community-building` 技能已归档到此。该技能的独特内容（README优化、内容策略、自动化监控、指标追踪）已作为此"社区建设"章节列入。重叠部分（分支保护、Agent贡献协议、CI流水线）已由本技能已有内容覆盖。
