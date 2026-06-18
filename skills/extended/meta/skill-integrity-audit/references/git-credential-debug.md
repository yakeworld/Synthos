# GitHub Push 调试路径 (2026-06-12)

## 症状

```
fatal: 无法访问 'https://github.com/...'：The requested URL returned error: 403
fatal: git@github.com: Permission denied (publickey).
```

## 调试步骤

### Step 1: 检查 SSH key 是否添加到 GitHub

```bash
ssh -vT git@github.com 2>&1 | tail -5
# → "Permission denied (publickey)" = key未注册到GitHub
```

### Step 2: 检查 gh CLI 认证状态

```bash
gh auth status
# 显示已登录，但需要检查 token scope

# 验证是否有写权限
gh pr create --title 'test' --body 'test' --head 'test' 2>&1
# → "Resource not accessible by personal access token" = 只读PAT，无repo scope
```

### Step 3: 检查 git credential.helper 配置

```bash
git config --list --show-origin | grep credential
# 常见冲突: 'store' (旧，读取~/.git-credentials) vs '!f() { gh auth git-credential "$@"; }; f' (新)
# 移除 'store'：
git config --global --unset credential.helper
```

### Step 4: 检查 ~/.gitconfig 中的 url insteadOf

```bash
cat ~/.gitconfig | grep -A1 insteadOf
# → url.https://github.com/.insteadOf = ssh://git@github.com/
# 这会将所有 HTTPS URL 强制转换为 SSH，即使 remote 配置为 HTTPS
# 移除：
git config --global --unset url.https://github.com/.insteadOf
```

### Step 5: 确认 PAT 有 repo scope

```bash
# 只读PAT的表现：
# - gh api repos/yakeworld/Synthos → 200 (公开仓库可读)
# - gh api user/repos → 200 (可读用户仓库列表)
# - gh api repos/yakeworld/Synthos/permissions → 404 或无push权限
# - gh pr create → "Resource not accessible by personal access token"

# 修复：需要新的Classic或Fine-grained PAT，勾选 repo 权限
# gh auth refresh -s repo -s write:repository (需交互式确认)
# 或手动在 GitHub 创建新PAT后运行 gh auth login
```

## 根因

本次会话中两个问题同时存在：

1. **`~/.gitconfig`** 有 `url.https://github.com/.insteadOf = ssh://git@github.com/`
   - 导致即使 remote 配置为 HTTPS，git 仍尝试通过 SSH 连接
2. **`~/.gitconfig`** 中有 `credential.helper = store`
   - 覆盖了 repo 级别的 `gh auth git-credential` helper
3. **唯一的 PAT 是只读的**，没有 `repo` scope，无法执行 git push

## 修复步骤

```bash
# 1. 移除 url insteadOf
git config --global --unset url.https://github.com/.insteadOf

# 2. 移除 store credential helper
git config --global --unset credential.helper

# 3. 确认 gh 已正确认证
gh auth status

# 4. 在 GitHub 创建新的 write-enabled PAT
#    Settings → Developer settings → Personal access tokens → Classic PAT
#    勾选: repo, write:repository

# 5. 重新登录 gh
gh auth login --with-token <<< 'your-new-token'

# 6. 推送
git push
```

## 防止复发

- 定期检查 `git config --list --show-origin | grep credential`
- 不要手动编辑 `~/.gitconfig` 添加 `url.https://github.com/.insteadOf` 规则
- 使用 `gh auth status` 定期检查 token scope
- 如需 SSH，需先在 GitHub 账户中添加 SSH key