---


name: github-repo-management
related_skills: []
description: GitHub仓库管理 — clone/create/fork, remotes, releases, branches.
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    version: 1.0.0
    author: Synthos



---



## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）



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
