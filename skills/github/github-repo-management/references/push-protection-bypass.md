# GitHub Push Protection Bypass

> 当 GitHub secret scanning 拦截 push 时，通过 `gh api` 创建 bypass 并继续推送。
> 实战验证：2026-06-02 Synthos 仓库 credential-cleanup.md 被 scanner 误报。

## 原理

GitHub secret scanning 会在 push 时扫描所有 commit 历史中的敏感字符串（token、API key、密码等）。如果发现匹配，拒绝 push。

绕过方式：**创建 push-protection bypass（临时放行）**，不是修改文件。

## 流程

### Step 1: 解析错误信息

```
$ git push origin main
remote: error: GH013: Repository rule violations found
remote:       —— GitHub Personal Access Token ——————————————————————
remote:        locations:
remote:          - commit: abc123def456...
remote:            path: docs/credential-example.md:45
remote:        (?) To push, remove secret from commit(s) or follow this URL to allow the secret.
remote:        https://github.com/OWNER/REPO/security/secret-scanning/unblock-secret/<PLACEHOLDER_ID>
```

关键信息：
- **commit**: 触发 scanner 的 commit hash
- **path**: 文件路径 + 行号
- **placeholder_id**: 用于创建 bypass 的 ID

### Step 2: 确认是误报

```bash
git show <COMMIT_HASH>:<FILE_PATH> | sed -n '<LINE_NUMBER>p'
```

### Step 3: 创建 bypass

```bash
gh api repos/OWNER/REPO/secret-scanning/push-protection-bypasses -X POST \
  --raw-field 'reason=false_positive' \
  --raw-field 'placeholder_id=<PLACEHOLDER_ID>'
```

### Step 4: 重新 push

```bash
git push origin main
# bypass 默认 30 分钟有效
```

## 可选 Reason 值

| reason | 适用场景 |
|:-------|:---------|
| `false_positive` | 扫描器误报，含敏感关键词但实际是文档/示例 |
| `used_in_tests` | 在测试代码中使用的测试/伪凭据 |
| `will_fix_later` | 确实包含真实凭证，但承诺稍后修复 |

## 陷阱

- **Bypass 有时效性**：默认 30 分钟过期
- **`gh api` 404**：如果 `placeholder_id` 不对，返回 404。重新执行 git push 获取新的 ID
- **git filter-branch sed 转义问题**：sed 中 `.` → `[.]`，`&` 有特殊含义。建议用 Python 替代
