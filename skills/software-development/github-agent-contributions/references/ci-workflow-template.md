# CI Workflow Template for Agent PR Verification

## File: `.github/workflows/agent-pr-verify.yml`

```yaml
name: Agent PR Verification

on:
  pull_request:
    types: [opened, synchronize, reopened]
    branches: [main]

permissions:
  contents: read
  pull-requests: write

jobs:

  gate-1-identity:
    name: "Gate 1: Agent Identity"
    if: startsWith(github.event.pull_request.title, '[agent]')
    runs-on: ubuntu-latest
    outputs:
      agent_name: ${{ steps.run.outputs.agent_name }}
    steps:
      - uses: actions/checkout@v4
      - name: Validate AGENT_MANIFEST.yaml
        id: run
        run: |
          python3 .github/scripts/gate1_identity.py 2>&1 | tee output.txt
          grep -q '^OK' output.txt && echo "✅ Identity OK" || (echo "❌ Identity FAILED"; exit 1)
          AGENT=$(grep '^OK' output.txt | sed 's/OK name=//' | cut -d' ' -f1)
          echo "agent_name=$AGENT" >> $GITHUB_OUTPUT

  gate-2-syntax:
    name: "Gate 2: Syntax Validation"
    needs: gate-1-identity
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate syntax
        run: python3 .github/scripts/gate2_syntax.py

  gate-3-secrets:
    name: "Gate 3: Secret Scan"
    needs: gate-1-identity
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Scan secrets
        run: python3 .github/scripts/gate3_secrets.py

  gate-456-advanced:
    name: "Gates 4-6: Constitution, Quality, Impact"
    needs: [gate-1-identity, gate-2-syntax, gate-3-secrets]
    runs-on: ubuntu-latest
    outputs:
      quality_score: ${{ steps.run.outputs.quality_score }}
      impact_level: ${{ steps.run.outputs.impact_level }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 2
      - name: Run advanced gates
        id: run
        run: |
          python3 .github/scripts/gates456_advanced.py 2>&1 | tee output.txt
          SCORE=$(grep 'Quality Score:' output.txt | awk '{print $NF}')
          IMPACT=$(grep 'Impact:' output.txt | tail -1 | awk '{print $NF}')
          echo "quality_score=$SCORE" >> $GITHUB_OUTPUT
          echo "impact_level=$IMPACT" >> $GITHUB_OUTPUT
          grep -q 'ALL PASS' output.txt || exit 1

  summary:
    name: "Verification Summary"
    needs: [gate-1-identity, gate-2-syntax, gate-3-secrets, gate-456-advanced]
    if: always()
    runs-on: ubuntu-latest
    steps:
      - name: Post summary
        uses: actions/github-script@v7
        with:
          script: |
            const gates = [
              ['1: Identity', '${{ needs.gate-1-identity.result }}'],
              ['2: Syntax', '${{ needs.gate-2-syntax.result }}'],
              ['3: Secrets', '${{ needs.gate-3-secrets.result }}'],
              ['4-6: Advanced', '${{ needs.gate-456-advanced.result }}'],
            ];
            const qs = '${{ needs.gate-456-advanced.outputs.quality_score }}';
            const im = '${{ needs.gate-456-advanced.outputs.impact_level }}';
            let allOk = true;
            let body = '## 🤖 PR Verification Report\n\n| Gate | Status |\n|------|--------|\n';
            gates.forEach(([name, status]) => {
              const ok = status === 'success';
              if (!ok) allOk = false;
              body += `| ${name} | ${ok ? '✅ PASS' : '❌ FAIL'} |\n`;
            });
            if (qs) body += `\n**Quality Score:** ${qs}\n`;
            if (im) body += `**Impact Level:** ${im}\n`;
            body += allOk
              ? '\n🎉 **All gates passed!** Ready for human review.'
              : '\n⚠️ **Some gates failed.**';
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            });
```

## Design Rule

> **Do NOT embed Python code inline in the YAML workflow file.** Put scripts in `.github/scripts/` and call them from `run:` steps. YAML's `|` block scalar combined with Python heredocs (`<< 'PYEOF'`) causes indentation errors because the parser sees Python code as bare YAML keys.

## Script Files

All 4 gate scripts go in `.github/scripts/`:

- `gate1_identity.py` — Validates AGENT_MANIFEST.yaml structure and required fields
- `gate2_syntax.py` — Checks YAML/Python/JSON syntax of PR-changed files
- `gate3_secrets.py` — Regex scan for hardcoded API keys/tokens in changed files
- `gates456_advanced.py` — Constitutional compliance + quality scoring + impact analysis
