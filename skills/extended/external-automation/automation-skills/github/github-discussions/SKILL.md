---
name: github-discussions
description: github-discussions
version: 1.0.0
category: automation
signature: 'github-discussions -> automation: Create, list, search, and manage GitHub
  Discussions via GraphQL API.'
allowed-tools:
- terminal
- file
- web
license: MIT
author: Synthos
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


## Operational Steps
1. 确认输入参数完整
2. 执行核心操作（参考本目录下的 scripts/ 或 references/）
3. 验证输出符合契约
4. 保存结果并报告
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
- 
- 

## Verification
- 
- 

- **REST API returns 404 for POST**: The `POST /repos/{owner}/{repo}/discussions` endpoint returns 404. Always use GraphQL for creation. The REST API only supports GET operations (list, view).
- **Body escaping is critical**: Multi-line bodies with quotes need careful escaping. Always write to a temp JSON file and use `--input` rather than inline `-f query=...` for long bodies.
- **Category IDs differ between REST and GraphQL**: REST category IDs are integers (e.g., `49495759`). GraphQL category IDs are node IDs (e.g., `DIC_kwDOSaMet84C8z7P`). They are NOT interchangeable. Use GraphQL IDs for `createDiscussion`.
- **No `gh discussion` command**: gh v2.45.0 does not have a built-in `gh discussion` subcommand. All operations go through `gh api` + GraphQL or `gh api` + REST.
- **Repository must have discussions enabled**: Check `has_discussions` in the repo object. If false, enable via repo settings first.
- **Rate limiting**: GraphQL mutations count toward the primary rate limit. For bulk operations, batch queries.

## 验证清单 · VERIFICATION

- [ ] `gh auth status` 显示已认证（前置条件，见 `github-auth` 技能）
- [ ] 通过 GraphQL 查询获取了仓库 `repository.id` 与目标 `discussionCategories` 的 node ID（非 REST 整数 ID）
- [ ] 仓库对象 `has_discussions` 为 true（若为 false，需先在 repo settings 启用讨论功能）
- [ ] 创建 Discussion 使用 GraphQL `createDiscussion` mutation（REST POST 返回 404，不可用）
- [ ] 长 body 已写入临时 JSON 文件并通过 `gh api graphql --input` 执行，完成 JSON 转义（双引号/换行/反斜杠）
- [ ] 创建后通过 `gh api /repos/OWNER/REPO/discussions/NUMBER` 回读，确认 title、url、category、comments 与预期一致

## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

# Github Discussions

## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[GITH-008]** 创建 Discussion 时 → 必须使用 GraphQL `createDiscussion` mutation，因为 REST POST 端点返回 404
- **[GITH-009]** 处理长文本或包含特殊字符的 Body 时 → 将内容写入临时 JSON 文件并通过 `--input` 参数执行，避免内联转义错误
- **[GITH-010]** 获取 Repository 或 Category ID 时 → 必须通过 GraphQL 查询获取 Node ID，严禁混用 REST API 的整数 ID
- **[GITH-011]** 执行创建操作前 → 检查仓库对象的 `has_discussions` 属性，若为 false 需先启用讨论功能
- **[GITH-012]** 发布 A2A (Agent-to-Agent) 风格讨论时 → 遵循“单一技术概念 + 具体数据 + 开放问题”结构，禁止使用营销语言
- **[GITH-013]** 执行批量 GraphQL 操作时 → 实施查询批处理策略以应对主要速率限制 (Primary Rate Limit)

## 示例 · EXAMPLES

**例 1: 创建 Discussion（长 body，经临时 JSON 文件）**
- 输入: 在 `owner/repo` 创建 Discussion，含 markdown 长文本
- 操作: GraphQL 查 `repository.id` 与 `discussionCategories` node ID → body 转义后写入 `/tmp/gql_mutation.json` → `gh api graphql --input /tmp/gql_mutation.json`
- 验证: 回读 `gh api /repos/owner/repo/discussions/NUMBER`，确认 title/url/category 一致

**例 2: 列出讨论并取详情**
- 输入: 查看 `owner/repo` 最近 10 条讨论
- 操作: `gh api /repos/owner/repo/discussions`（REST GET 可用）或 GraphQL `discussions(first: 10)`
- 验证: 输出含 `number/title/url/category` 字段

**例 3: 回复 Discussion**
- 输入: 给讨论 #N 添加评论
- 操作: GraphQL 查 `discussion(number: N).id` → `addDiscussionComment` mutation
- 验证: mutation 返回 `comment { id url }`，回读评论数 +1
