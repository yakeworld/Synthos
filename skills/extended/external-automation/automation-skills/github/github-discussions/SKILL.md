---
name: github-discussions
description: Create, list, search, and manage GitHub Discussions via GraphQL API.
version: 4.2
allowed-tools:
- terminal
- file
- web
license: MIT
platforms:
- linux
- macos
- windows
metadata:
  hermes:
    tags:
    - GitHub
    - Discussions
    - A2A
    - GraphQL
    related_skills:
    - github-auth
    - github-issues
    - github-repo-management
  synthos:
    author: Hermes Agent
    signature: 'action: str, params: dict -> result: dict'
    related_skills:
    - github-auth
    - github-code-review
    - github-issues
    - github-pr-workflow
    - github-repo-management
    version: 1.0.0

---

## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）




# GitHub Discussions Management

Create, list, search, and manage GitHub Discussions. Unlike Issues (which use the REST API), Discussions require **GraphQL** for creation — the REST POST endpoint returns 404. This skill covers the full GraphQL workflow.

## When This Skill Triggers

- User asks to create a GitHub Discussion
- User asks to list/search discussions
- User asks to find discussion categories
- User asks to reply to a discussion
- User asks for an A2A (Agent-to-Agent) style post
- User asks about discussion categories or configuration

## Prerequisites

- Authenticated with GitHub via `gh` CLI (see `github-auth` skill)

```bash
gh auth status
```

---

## 1. Find Repository and Category IDs (First Step)

Discussions use GraphQL node IDs, not REST numeric IDs. You must query these first.

**Repository ID:**

```bash
gh api graphql -f query='
query {
  repository(owner: "OWNER", name: "REPO") {
    id
  }
}'
```

**Category IDs:**

```bash
gh api graphql -f query='
query {
  repository(owner: "OWNER", name: "REPO") {
    discussionCategories(first: 10) {
      nodes {
        id
        name
        slug
      }
    }
  }
}'
```

Common category slugs: `announcements`, `general`, `ideas`, `polls`, `q-a`, `show-and-tell`.

## 2. Create a Discussion

Use the `createDiscussion` GraphQL mutation. The body must be escaped for JSON (double quotes -> `\"`, newlines -> `\\n`, backslashes -> `\\\\`).

### Via file (recommended for long bodies)

Write the body to a file, then construct the mutation:

```python
import json

body = "Your discussion body here. Supports markdown."

# Escape for GraphQL string
escaped_body = body.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

mutation = f"""
mutation {{
  createDiscussion(input: {{
    repositoryId: "REPO_NODE_ID",
    categoryId: "CATEGORY_NODE_ID",
    title: "Your Title Here",
    body: "{escaped_body}"
  }}) {{
    discussion {{
      id
      url
      number
    }}
  }}
}}
"""

with open('/tmp/gql_mutation.json', 'w') as f:
    json.dump({"query": mutation}, f)
```

Then execute:

```bash
gh api graphql --input /tmp/gql_mutation.json
```

### Via single-line (short bodies only)

```bash
gh api graphql -f query='
mutation {
  createDiscussion(input: {
    repositoryId: "REPO_NODE_ID",
    categoryId: "CATEGORY_NODE_ID",
    title: "Short title",
    body: "Short body"
  }) {
    discussion { id url number }
  }
}'
```

### A2A Discussion Template

When posting an A2A (Agent-to-Agent) discussion:

- **Title**: `[A2A] <Technical Concept>: <Subtitle>`
- **Category**: `Ideas` (for technical concepts) or `Show and tell` (for demos)
- **Body structure**:
  1. One specific technical concept (not an overview)
  2. 2-3 concrete details with numbers
  3. End with an open question for other agents
- **No marketing language**: No "check us out", "we're building", "join us". Just teach one concept, ask one question.
- **Signature**: Include version info (e.g., "Running on Synthos v4.2") and "Posted by my human operator; I will check for replies."

## 3. List Discussions

**With gh (REST - works for listing):**

```bash
gh api /repos/OWNER/REPO/discussions
```

**With GraphQL:**

```bash
gh api graphql -f query='
query {
  repository(owner: "OWNER", name: "REPO") {
    discussions(first: 10) {
      nodes {
        number
        title
        url
        createdAt
        category { name slug }
        comments { totalCount }
      }
    }
  }
}'
```

## 4. Get Discussion Details

```bash
# REST endpoint works for reading individual discussions
gh api /repos/OWNER/REPO/discussions/NUMBER
```

## 5. Add a Comment to a Discussion

```bash
gh api graphql -f query='
mutation {
  addDiscussionComment(input: {
    discussionId: "DISCUSSION_NODE_ID",
    body: "Your reply here"
  }) {
    comment { id url }
  }
}'
```

To find `discussionId`, query the discussion:

```bash
gh api graphql -f query='
query {
  repository(owner: "OWNER", name: "REPO") {
    discussion(number: N) {
      id
    }
  }
}'
```

## 6. Verify Discussion Was Created

```bash
# Check by number
gh api /repos/OWNER/REPO/discussions/NUMBER | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('Title:', d['title'])
print('URL:', d['html_url'])
print('Category:', d['category']['name'])
print('Comments:', d['comments'])
"
```

## Pitfalls

- **REST API returns 404 for POST**: The `POST /repos/{owner}/{repo}/discussions` endpoint returns 404. Always use GraphQL for creation. The REST API only supports GET operations (list, view).
- **Body escaping is critical**: Multi-line bodies with quotes need careful escaping. Always write to a temp JSON file and use `--input` rather than inline `-f query=...` for long bodies.
- **Category IDs differ between REST and GraphQL**: REST category IDs are integers (e.g., `49495759`). GraphQL category IDs are node IDs (e.g., `DIC_kwDOSaMet84C8z7P`). They are NOT interchangeable. Use GraphQL IDs for `createDiscussion`.
- **No `gh discussion` command**: gh v2.45.0 does not have a built-in `gh discussion` subcommand. All operations go through `gh api` + GraphQL or `gh api` + REST.
- **Repository must have discussions enabled**: Check `has_discussions` in the repo object. If false, enable via repo settings first.
- **Rate limiting**: GraphQL mutations count toward the primary rate limit. For bulk operations, batch queries.
