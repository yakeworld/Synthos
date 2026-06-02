---
name: open-source-community-building
description: Promote an open-source project and build a contributor community — README optimization, GitHub config, content strategy (Zhihu/Reddit/Twitter), auto-promotion cron, and metrics tracking.
tags: [github, community, promotion, open-source, marketing, zhihu, reddit]
---

# Open-Source Community Building

## Trigger

User asks to promote an OSS project, grow its community, attract contributors (human or AI), write a README, or create a promotion strategy.

## Workflow

### Phase 0: Branch Protection Setup

After the initial push, protect the main branch BEFORE any other work:

```bash
# Personal repo variant (restrictions=null)
cat > /tmp/bp.json << 'EOF'
{
  "required_status_checks": {
    "strict": true,
    "checks": [
      {"context": "Gate 1: Identity", "app_id": 0},
      {"context": "Gate 2: Syntax", "app_id": 0}
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
EOF
gh api repos/OWNER/REPO/branches/main/protection --input /tmp/bp.json --method PUT
```

**Key differences by repo type:**
- **Personal repo**: `restrictions: null` (NOT omitted — API rejects without it)
- **Org repo**: `restrictions: { "users": ["admin"], "teams": [] }` (actual restrictions object)
- **Admin bypass**: `enforce_admins: false` lets you use `gh pr merge --admin` to bypass review

### Phase 1: GitHub Infrastructure (Day 1)

#### 1.1 README Optimization

Add a badge row at the top:

```markdown
<p align="center">
  <a href="https://github.com/OWNER/REPO/stargazers"><img src="https://img.shields.io/github/stars/OWNER/REPO?style=flat&logo=github" alt="Stars"/></a>
  <a href="https://github.com/OWNER/REPO/actions/workflows/WORKFLOW.yml"><img src="https://github.com/OWNER/REPO/actions/workflows/WORKFLOW.yml/badge.svg" alt="CI"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License"/></a>
  <a href="https://github.com/OWNER/REPO/discussions"><img src="https://img.shields.io/badge/Community-Discussions-blueviolet" alt="Discussions"/></a>
  <img src="https://img.shields.io/badge/Version-v1.0.0-blue" alt="Version"/>
</p>
```

Key sections every README needs:
- **One-liner**: What the project does in 1 sentence
- **Architecture diagram**: ASCII or SVG showing system design
- **Quick start**: Minimal steps to get running
- **Contribution section**: Link to CONTRIBUTING.md or AGENTS_CONTRIBUTING.md
- **Badges**: stars, CI status, license, version
- **Reference table**: Links to key docs at bottom

For bilingual projects: create `README.md` (English) and `README_CN.md` (Chinese) with cross-links at the top.

#### 1.2 GitHub Config via API

```bash
# Topics (increases search discoverability)
# ⚠️ MUST use curl, NOT gh api --field (--field sends JSON as string, breaks the API)
curl -X PUT https://api.github.com/repos/OWNER/REPO/topics \
  -H "Authorization: token $(gh auth token)" \
  -H "Accept: application/vnd.github.mercy-preview+json" \
  -d '{"names":["ai-agent","multi-agent","cognitive-architecture","open-source","research-tool"]}'

# Discussions
gh api repos/OWNER/REPO -X PATCH -f has_discussions=true
```

Recommended topics for an AI/OSS project: `ai-agent`, `multi-agent`, `cognitive-architecture`, `open-source`, plus project-specific tags.

#### 1.3 CITATION.cff

Create `CITATION.cff` for academic referencing:

```yaml
cff-version: 1.2.0
title: "Project Name"
message: "If you use this in your research, please cite it."
type: software
authors:
  - family-names: "Author"
    given-names: "Name"
repository-code: "https://github.com/OWNER/REPO"
license: MIT
version: "1.0.0"
date-released: 2026-05-12
```

#### 1.4 GitHub Release

Create an initial release after the first major push:
```bash
gh release create v1.0.0 -R OWNER/REPO \
  --title "v1.0.0 — Release Title" \
  --notes "## Changelog\n\n- Feature A\n- Feature B" \
  --target main --latest
```

### Phase 2: Content Strategy (Week 1)

**⚠️ CRITICAL: Verify user identity before writing promotional content**. Before writing any Zhihu/Reddit/Twitter content about the user:
1. Check if the user has a NotebookLM with personal profile documents (resume, CV, personal intro)
2. Ask the notebook: "根据个人介绍来源，用户的准确信息是什么？专业、职称、单位、研究方向"
3. Cross-check the answer against what you think you know

Common mistakes from real sessions:
- Said 儿童保健科 instead of 神经内科 (wrong department entirely)
- Said 6万门诊儿童 instead of 眩晕中心+实验室 (wrong clinical narrative)
- These errors damage credibility in promotional content and are embarrassing

**⚠️ Bilingual README pitfall**: English READMEs on predominantly-Chinese projects are extremely prone to containing Chinese text. After writing/editing the English README, verify:
```bash
grep -Pn '[\\x{4e00}-\\x{9fff}]' README.md && echo "❌ Has Chinese!" || echo "✅ Pure English"
```
Check EVERY section: title, table content, architecture descriptions, section headers. A single Chinese character in the English README breaks the bilingual contract.

#### 2.1 Zhihu (知乎) Long-Form Article

Best platform for Chinese technical audience. Write a narrative-driven article:

**Title formula**: 《我开源了一个[project-one-liner]——[hook]》

**Structure**:
1. 缘起：个人故事和问题
2. 思考：核心哲学/理念
3. 设计：系统架构
4. 效果：数据/成果
5. 开放：如何参与
6. 未来：下一步

Save to `docs/zhihu-article-PROJECT.md` for the user to review and publish.

#### 2.2 Reddit

Target subreddits for AI/OSS projects:

| Subreddit | Audience | Best time | Note |
|-----------|----------|-----------|------|
| r/AIAgents | Agent developers | Mon-Wed AM | Best fit for agent projects |
| r/MachineLearning | ML researchers | Showcase Saturday | Must have technical depth |
| r/Python | Python developers | Mon-Wed | Emphasize implementation |
| r/opensource | OSS community | Anytime | Share the story |

Post template:
```
Title: Project Name — one-line value prop

I built [project summary in 2 sentences].

Key features:
- Feature 1
- Feature 2  
- Feature 3

MIT licensed. Contributions welcome.

https://github.com/OWNER/REPO
```

#### 2.3 Twitter/X

Create an announcement thread:
```
🧬 Project Name just hit v1.0!

Built because [problem].
Solves it with [approach].

Key stats:
- [stat 1]
- [stat 2]

Open source, MIT.
Contributors & agents welcome!

https://github.com/OWNER/REPO
```

### Phase 3: Automation (Day 2-3)

Set up a daily cron job for promotion monitoring:

```
cronjob action=create name=PROJECT-daily-promotion \
  schedule="0 9 * * *" \
  prompt="Tasks: 1) Check GitHub stars/forks via API \
  2) Read evolution state if exists \
  3) Generate daily status report \
  4) Suggest social media posts"
```

The cron job should track:
- Star count changes
- Fork count
- Open issues/PRs
- Any new releases
- Recommend actions for the day

### Phase 4: Metrics & Milestones

Set expectations:

| Metric | 1-month | 3-month | 6-month |
|--------|---------|---------|---------|
| GitHub Stars | 50 | 200 | 500+ |
| Forks | 10 | 30 | 100+ |
| Contributions | 2 | 10 | 30+ |

Celebrate milestones with a Discussion post when hit.

## References

- `references/agent-contribution-protocol.md` — setup guide for AI agent PR verification (AGENTS_CONTRIBUTING.md, VERIFICATION_GATES.md, CI workflow, scripts)
- `references/zhihu-article-template.md` — reusable Zhihu article outline
- `references/reddit-posting-guide.md` — subreddit rules and timing

## Related Skills

- `github-agent-contributions` — for setting up AI agent contribution infrastructure  
- `github-repo-management` — for basic repo config  
- `subagent-driven-development` — for delegating social media content generation

## Admin Merge Workflow

When the user says "go ahead and merge" but branch protection requires review:

1. First ensure `enforce_admins: false` in branch protection settings
2. Use `--admin` flag to bypass review:

```bash
gh pr merge PR_NUM -R OWNER/REPO --squash --admin --subject "commit message"
```

This only works when:
- Branch protection has `enforce_admins: false`
- The agent is operating as the repo owner (via terminal/gh auth)
- CI checks have passed (required_status_checks still enforced even with admin bypass)

## AI Agent Contribution Protocol

For projects that want AI agents to contribute (not just humans):

Create these files in the repo:
- `AGENTS_CONTRIBUTING.md` — Machine-readable contribution guide with AGENT_MANIFEST.yaml spec
- `VERIFICATION_GATES.md` — 6-gate verification pipeline  
- `.github/workflows/agent-pr-verify.yml` — CI workflow triggered by `[agent]` PR title prefix

Key design points:
- **Trigger condition**: `if: startsWith(github.event.pull_request.title, '[agent]')` 
- **Identity check**: PR must include `AGENT_MANIFEST.yaml` with agent name, framework, and capability
- **Secret scan**: Scan for hardcoded API keys/tokens in the PR
- **Constitutional check**: Verify changes don't violate project principles
- **Quality score**: Automated scoring (completeness, clarity, relevance, safety, testability) with ≥ 0.7 threshold
- **Merge gate**: All 4 CI checks must pass + human approval
