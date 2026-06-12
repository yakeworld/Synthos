---
name
## 原理层·文言

> 文以验法，技乃所产。GitHub仓库管理 — clone/create/fork, remotes, releases, branches.。
: github-repo-management
description: GitHub仓库管理 — clone/create/fork, remotes, releases, branches.
metadata:
  synthos:
    version: 1.0.0
    author: Synthos
---

# GitHub Repo Management

## 快速命令

```bash
# 克隆
git clone git@github.com:owner/repo.git
gh repo clone owner/repo

# 创建
gh repo create repo-name --public --clone

# Fork
gh repo fork owner/repo --clone

# Remotes
git remote add upstream git@github.com:owner/repo.git
git remote -v

# Releases
gh release create v1.0.0 --title "v1.0.0" --notes "Release notes"

# 分支管理
git branch feature-x
git checkout -b feature-x
git merge feature-x
git branch -d feature-x
```

详细命令参考见 `references/github-cheatsheet.md`。
