---
name: repo-path-sanity
class: infrastructure
description: Diagnose and fix broken directory relationships when ~/Synthos and /media/yakeworld/sda2/Synthos diverge into independent copies instead of symlink.
---

# Repository Path Sanity Check

**Purpose:** Diagnose and fix broken directory relationships when `~/Synthos` and `/media/yakeworld/sda2/Synthos` diverge into independent copies instead of symlink.

## Why This Happens

Hermes Agent clones `https://github.com/yakeworld/Synthos` into `~/Synthos` (a real directory), while the actual source of truth lives at `/media/yakeworld/sda2/Synthos` (sda2 main repo). The expectation is that `~/Synthos` should be a symlink: `~/Synthos → /media/yakeworld/sda2/Synthos`. If the symlink breaks or was never created, both become independent directories that drift apart.

## Diagnosis

```bash
# Check if ~/Synthos is a symlink
ls -la ~/Synthos
# If it shows "drwx..." instead of "lrwx?", it's a real directory

# Check if they're the same inode
stat -c '%i' ~/Synthos
stat -c '%i' /media/yakeworld/sda2/Synthos
# Same inode = same directory (symlink works)
# Different inode = two separate copies

# Check actual paths
readlink -f ~/Synthos
readlink ~/Synthos
```

## Fix Procedure

### Step 1: Merge unique data from clone → main

```bash
# Identify ~/Synthos files NOT in sda2 (excluding .git, node_modules, outputs/papers internals)
# Copy only valuable files:
# - SKILL-*.md (root-level skill entries)
# - VERIFICATION_GATES.md
# - docs/ (article drafts, technical docs)
# - experiments/ (experiment records)
# - papers/ (draft manuscripts)
# - scripts/ (utility scripts)
# - outputs/papers-md/ (paper markdown versions)
```

### Step 2: Remove clone, create symlink

```bash
rm -rf ~/Synthos
ln -s /media/yakeworld/sda2/Synthos ~/Synthos
```

### Step 3: Verify

```bash
readlink ~/Synthos          # Should show /media/yakeworld/sda2/Synthos
ls ~/Synthos/SKILL.md       # Should work via symlink
cd ~/Synthos && git status  # Should operate on sda2 repo
```

## Prevention

- When cloning from GitHub, clone to a different location (e.g., `~/synthos-clone/`) and compare before deciding to replace
- After any repo restructure, verify `readlink ~/Synthos` immediately
- The canonical path is `/media/yakeworld/sda2/Synthos`; `~/Synthos` is only ever a symlink

## Git Credential 陷阱 (2026-06-12 新增)

> **`git push` 返回 403 时，问题往往不在网络，而在 credential 配置冲突。**

### 常见组合

| 症状 | 根因 | 修复 |
|------|------|------|
| `url.https://github.com/.insteadOf = ssh://git@github.com/` 在 `~/.gitconfig` | HTTPS remote 被转 SSH | `git config --global --unset url.https://github.com/.insteadOf` |
| `credential.helper = store` 在 `~/.gitconfig` | 覆盖 repo 级别的 `gh auth git-credential` | `git config --global --unset credential.helper` |
| `gh auth status` 显示已登录但 `gh pr create` 报错 | PAT 只有只读 scope，无 repo 权限 | 创建新的 Classic PAT，勾选 repo + write:repository |
| `ssh -vT git@github.com` → "Permission denied (publickey)" | SSH key 未注册到 GitHub | 在 GitHub Settings → SSH keys 中添加 |

### 调试命令

```bash
git config --list --show-origin | grep credential
git config --global --get url.https://github.com/.insteadOf || echo "no insteadOf"
gh auth status
gh pr create --title test --body test --head test 2>&1 | grep -i "accessible\|denied"
```

## NFS Quirks

`/mnt/nfs` is extremely slow — `os.walk()`, `du -sh`, shell loops over all
entries **timeout at 300s** after single output line. Always use `timeout` +
shallow commands. See `references/nfs-behavior.md` for full details and project
anatomy.