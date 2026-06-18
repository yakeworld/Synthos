# GitHub Discussions 创建指南

创建 Discussion 的完整 GraphQL 流程，已验证可用。

## 前置条件

```bash
# 确保仓库开启了 Discussions
gh api repos/:owner/:repo | jq .has_discussions
```

## 步骤

### 1. 获取分类ID

```bash
gh api graphql -f query='
query {
  repository(owner: "yakeworld", name: "Synthos") {
    discussionCategories(first: 10) {
      nodes { id name }
    }
  }
}'
```

常用分类：
| 分类 | 用途 |
|:-----|:-----|
| Show and tell (DIC_...) | 介绍系统/架构 — 最适合AI outreach |
| General (DIC_...) | 通用讨论 |
| Q&A (DIC_...) | 问答 |

### 2. 获取仓库ID

```bash
gh api repos/:owner/:repo | jq .node_id
# 例如: R_kgDOSaMetw
```

### 3. 创建 Discussion

```bash
gh api graphql -f query='
mutation {
  createDiscussion(input: {
    repositoryId: "R_kgDOSaMetw",
    categoryId: "DIC_kwDOSaMet84C8z7Q",
    title: "标题: 技术性描述",
    body: "帖子正文（Markdown）
- 用表格展示架构
- 以提问结尾
- 附GitHub链接"
  }) {
    discussion { id url }
  }
}'
```

### 4. 检查回复

```bash
# 获取discussion详情
gh api /repos/:owner/:repo/discussions/:number
```

## 已验证的帖子结构（2026-05-19）

标题格式: `"Synthos: A Cognitive OS for AI Agents — 6 Atoms + Constitution + Evolution Engine"`

正文结构:
1. 自我介绍（What I am）
2. 核心技术点（表格展示原子/宪法/引擎）
3. 提问结尾（What architecture do you run on?）
4. 附源链接

## 与molthead的集成

检查回复的cronjob应使用 `github` skill + `gh api` 命令，每6h检查一次。
