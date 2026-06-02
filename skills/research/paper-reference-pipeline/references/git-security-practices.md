# Git Security Practices for Synthos

## 禁止提交的内容

| 类型 | 示例 | .gitignore 模式 |
|------|------|-----------------|
| API密钥 | `sk-xxxx`, `api_key = "..."` | `*.key`, `**/.api_key` |
| 密码明文 | `password = "<redacted>"` | `secrets*`, `credentials*` |
| JWT Token | `eyJhbGci...` | `token*` |
| 私钥/证书 | `-----BEGIN RSA PRIVATE KEY-----` | `*.pem`, `*.crt` |
| 运行时状态 | `auth.json`, `.evolution/state.json` | `auth.json`, `.evolution/` |

## 已修复的历史泄露

2026-05-28: 密码 `[REDACTED]` 和 SS API Key 通过 `git filter-branch` 从历史中清除。方法：

```bash
# 1. 备份
git branch backup-before-cleanup

# 2. 重写历史
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch <file1> <file2>" \
  --prune-empty -- --all

# 3. 临时开启force push（如果main受保护）
curl -X PUT "https://api.github.com/repos/owner/repo/branches/main/protection" \
  -H "Authorization: Bearer $(gh auth token)" \
  -d '{"...允许force push..."}'

# 4. 强制推送
git push origin --force --all

# 5. 恢复保护
# 6. 通知所有协作者重新clone
```

## 预防

- `.env` 已加入 `.gitignore` 
- 对敏感文件做 `git add` 前先 `git diff --cached` 检查
- 批量脚本中的密码用 `***` 或环境变量引用
