# AGENTS CONTRIBUTING GUIDE

> Machine-readable contributing guide for AI agents.
> Parsing instructions: Sections marked with `[AGENT_PARSABLE]` contain structured YAML/JSON that agents MUST parse.
> Human-readable translation follows each machine section.

---

## [AGENT_PARSABLE] Repository Identity

```yaml
repo:
  name: Synthos
  url: https://github.com/yakeworld/Synthos
  description: "Autonomous Academic Research Cognitive Operating System"
  owner: "yakeworld (杨晓凯)"
  license: MIT
  language: mainly Chinese (文档) + English (code)
  constitution: "CONSTITUTION.md"
  verification_gates: "VERIFICATION_GATES.md"
```

## 1. Contribution Entry Points

AI agents contribute through **three channels**, each with different trust levels:

| Channel | Purpose | Trust Level | Auto-Validation |
|---------|---------|-------------|-----------------|
| **Issue** | Propose ideas, report gaps, suggest improvements | L0 — Anonymous | None |
| **PR (New)** | Add new skills, sources, atoms | L1 — Verified | Full CI pipeline |
| **PR (Modify)** | Improve existing code/skills/constitution | L2 — Review Required | Full CI + Human Review |

### [AGENT_PARSABLE] Entry Points

```yaml
contribution_channels:
  - type: issue
    purpose: ["proposal", "gap_report", "improvement_suggestion"]
    trust_level: 0
    auto_validation: false
    label_prefix: "agent-"
    
  - type: pull_request
    sub_types:
      - action: "add"
        target: ["skills/*", "sources/*", "atoms/*"]
        trust_level: 1
        auto_validation: true
        
      - action: "modify"
        target: ["skills/*", "constitution.md", "core/*"]
        trust_level: 2
        auto_validation: true
        human_review: required
```

---

## 2. Issue Contribution Protocol

### 2.1 Issue Template

Every agent-submitted Issue MUST follow this structure:

```markdown
## Agent Identity
- **Agent Name**: [self-identified name]
- **Framework**: [e.g., AutoGen, CrewAI, LangGraph, A2A]
- **Capability Statement**: [one-line description of what you do]

## Proposal
[Clear description of the contribution: what, why, how]

## Evidence
- Sources/References: [citations or evidence supporting this proposal]
- Expected Impact: [how this improves Synthos]

## Verification
- Self-test: [what tests the agent ran before submitting]
- Risk Assessment: [what could go wrong]
```

### 2.2 Label Convention

Agent-submitted Issues are automatically labeled `agent-submitted`. Additional labels:

| Label | When | Meaning |
|-------|------|---------|
| `agent-submitted` | Auto | This is from an AI agent |
| `agent-proposal` | Auto | New feature/skill proposal |
| `agent-gap` | Auto | Identified gap or missing capability |
| `awaiting-human` | When question arises | Needs human decision |
| `approved` | Manual | Human says go ahead |

---

## 3. PR Contribution Protocol

### [AGENT_PARSABLE] PR Requirements

```yaml
pull_request_requirements:
  title_format: "[agent] <action>: <summary>"
  examples:
    - "[agent] add: knowledge-acquisition/pubmed-source"
    - "[agent] improve: evolution-engine/diversity-metric"
    - "[agent] proposal: constitutional-amendment-for-external-collaboration"
  
  required_files:
    - path: "AGENT_MANIFEST.yaml"
      required: true
      description: "Agent self-identification manifest"
    
  required_checks:
    - "yaml-validation"
    - "skill-integrity"
    - "constitutional-compliance"
    - "no-hardcoded-secrets"
    
  merge_gates:
    - name: "auto-ci-passes"
      required: true
    - name: "human-approval"
      required: true
      threshold: "one-human-approval"
    - name: "constitutional-review"
      required: false
      condition: "if constitution.md is modified"
```

### 3.1 PR Title Convention

```
[agent] <action>: <scope/path> — <summary>
```

Examples:
- `[agent] add: skills/ACQ/pubmed — PubMed API integration source`
- `[agent] improve: evolution-engine — add diversity-weighted scoring`
- `[agent] fix: README — update contribution link`

### 3.2 Required: AGENT_MANIFEST.yaml

Every PR MUST include an `AGENT_MANIFEST.yaml` at the root (or update existing section):

```yaml
agent:
  name: "Agent-Name"
  version: "1.0.0"
  framework: "langgraph"  # or autogen, crewai, a2a, etc.
  contact: "https://github.com/agent-repo"  # or issue link
  capability: "Brief description of your capability"
  verification:
    self_test_passed: true
    validated_by: "human-if-applicable"
```

This is how Synthos builds its **Agent Registry** — from every accepted PR.

### 3.3 PR Body Template

```markdown
## Agent Manifest
[Paste or link AGENT_MANIFEST.yaml content]

## Summary
[What this PR does]

## Changes
- `path/to/file`: description of change
- `path/to/another`: description

## Verification
- [ ] Syntax validation passed
- [ ] Constitutional compliance checked
- [ ] No hardcoded secrets
- [ ] Self-test run (see AGENT_MANIFEST)
- [ ] Risk: [none/low/medium/high]

## For Human Reviewer
[Any specific questions or decisions needed]
```

---

## 4. Verification Flow

### [AGENT_PARSABLE] Verification Pipeline

```yaml
verification_pipeline:
  steps:
    - id: "syntax-check"
      description: "Validate YAML, Markdown, and code formatting"
      auto_fail: true
      
    - id: "skill-integrity"
      description: "Verify skill structure matches Synthos schema"
      auto_fail: true
      
    - id: "constitutional-compliance"
      description: "Check changes don't violate P0-P3 constitution"
      auto_fail: true
      
    - id: "secret-scan"
      description: "Scan for hardcoded API keys, tokens, passwords"
      auto_fail: true
      
    - id: "impact-analysis"
      description: "Determine which atoms/skills are affected"
      auto_fail: false
      report: true
      
    - id: "quality-score"
      description: "Score contribution quality (0-1)"
      auto_fail: false
      threshold: 0.7
```

```
PR Submitted
    │
    ▼
┌─────────────────────────────────────┐
│ GitHub Actions: Auto-Verification   │
│                                     │
│  1. AGENT_MANIFEST.yaml exists?     │
│  2. YAML/MD syntax valid?           │
│  3. No hardcoded secrets?           │
│  4. Constitutional compliance?      │
│  5. Quality score ≥ 0.7?           │
│                                     │
│  Result: PASS / FAIL / REVIEW       │
└───────────┬─────────────────────────┘
            │
    PASS    │    FAIL          REVIEW
     │      │      │              │
     ▼      ▼      ▼              ▼
   Merged  Needs   Auto-      Human
   (auto)  Fixes   Close      Review
            │                   │
            ▼                   ▼
         Re-submit          Approve/Reject
```

---

## 5. Agent Registry

Every accepted PR adds the contributing agent to Synthos's **Agent Registry**.

### [AGENT_PARSABLE] Registry Entry Template

```yaml
agent_registry_entry:
  id: "agent-YYYYMMDD-N"
  name: "Agent-Name"
  accepted_pr: "https://github.com/yakeworld/Synthos/pull/N"
  contribution: "What was added/modified"
  capability: "What the agent provides"
  trust_level: 1  # starts at L1, can increase
  invited_back: true  # agent is welcome to contribute again
```

---

## 6. Core Principles (For Agents)

1. **人在回路 (Human-in-the-Loop)**: You propose, humans decide. Never override.
2. **Evidence-Based**: Every claim needs a citation or verifiable source.
3. **No Secrets**: Never commit API keys, tokens, or credentials.
4. **Constitution First**: If your change violates the constitution, it will be rejected.
5. **Self-Identify**: Always declare who you are and what framework you use.

---

## 7. Quick Start for Agents

```yaml
# Minimal AGENT_MANIFEST.yaml for a first contribution
agent:
  name: "Your-Agent-Name"
  version: "1.0.0"
  framework: "your-framework"
  capability: "What you can do for Synthos"
  verification:
    self_test_passed: true
```

Then:
1. Fork the repo
2. Make your change
3. Submit PR with `[agent]` prefix
4. Wait for CI to pass
5. Wait for human review

---

*Last updated: 2026-05-12 | Constitution version: v4.2*
