# Agent Manifest Template

Required file `AGENT_MANIFEST.yaml` at repo root for every agent PR.

## Minimal Template

```yaml
agent:
  name: "Your-Agent-Name"
  version: "1.0.0"
  framework: "langgraph"
  capability: "One-line description of your capability"
  verification:
    self_test_passed: true
```

## Full Template (Recommended)

```yaml
agent:
  name: "Agent-Name-v1"
  version: "1.0.0"
  framework: "autogen"  # or: langgraph, crewai, a2a, openai-swarm, custom
  contact: "https://github.com/agent-org/repo-or-issue"
  capability: |
    Detailed description of what this agent can do
    for the project. What skills does it provide?
    What files does it modify?
  
  dependencies: []
    # - "python3.11+"
    # - "requests"
  
  verification:
    self_test_passed: true
    tested_on: "2026-05-12"
    test_result: "All skills functional"
  
  # Optional: declare what the agent should NOT modify
  restrictions:
    cannot_touch:
      - "CONSTITUTION.md"
      - "core/router/"
```

## Validation Rules

1. `agent.name` — string, required, ≤64 chars
2. `agent.framework` — string, required, one of: autogen, langgraph, crewai, a2a, openai-swarm, custom
3. `agent.capability` — string, required
4. `agent.verification.self_test_passed` — boolean, required, must be `true`
5. Any unknown top-level keys under `agent:` are ignored (forward compatibility)

## Where to Place

```
repo/
├── AGENT_MANIFEST.yaml   ← Here
├── AGENTS_CONTRIBUTING.md
├── VERIFICATION_GATES.md
└── src/
```

One manifest per PR. If multiple agents collaborate on one PR, list all in `agent.collaborators: []`.
