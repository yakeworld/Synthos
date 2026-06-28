---
name: repo-path-sanity
description: "**Purpose:** Diagnose and fix broken directory relationships when `~/Synthos` and `/media/yakeworld/sda2/Synthos` diverge into independent copies instead of symlink."
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "task_desc: str, params: dict -> result: dict"
    atom_type: skill
    priority: P2
    related_skills: []

---





## IO_CONTRACT

- **input**: `project_root: str` — 用户请求描述、上下文信息
- **output**: `sanity_report: dict — 路径健康报告`

> 对应原则：P2（机械原子暴露输入输出规范）



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

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引


## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
