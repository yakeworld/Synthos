# Git 仓库隐私扫描方法论

> 检查 git 已追踪文件，检测 token、密钥、密码、手机号、邮箱等敏感信息是否泄露到公开仓库。

## 步骤

### 1. 文件级快速筛查（.gitignore + 文件名模式）
```bash
# 检查 .gitignore
cat .gitignore

# 检查已追踪的敏感文件名
git ls-files | grep -iE 'credential|secret|password|token|env|key\.pem|id_rsa|private'

# 检查未追踪的敏感文件
git ls-files --others --exclude-standard | grep -iE 'credential|secret|password|token|\.env|key\.pem'
```

### 2. 内容级深度扫描
```python
# 对每个 .md/.sh/.py/.yaml/.json/.txt 文件进行正则匹配：
patterns = [
    r'ghp_[A-Za-z0-9]{36,}',         # GitHub PAT
    r'gho_[A-Za-z0-9]{36,}',         # GitHub OAuth
    r'github_pat_[A-Za-z0-9_]{20,}', # GitHub Fine-Grained PAT
    r'hf_[A-Za-z0-9]{20,}',          # HuggingFace
    r'sk-[A-Za-z0-9]{20,}',          # OpenAI/DashScope
    r'-----BEGIN.*KEY-----',         # SSH/SSL 私钥
    r'(?:password|passwd|pwd)\s*[:=]\s*[^\s\n]{8,}',  # 明文密码
    r'(?:ghp_|gho_|github_pat_|hf_|sk-)[A-Za-z0-9]', # 任何令牌前缀
    r'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}',  # JWT
    r'https://[a-z]+:[a-z0-9]+@',   # URL 内嵌凭证
]
```

### 3. 分类与判断
扫描结果需按类别判断：
- **真实凭证**（token、密码、密钥）→ 立即 `git rm --cached` + 修改密码
- **占位符/示例**（@example.com、`password=password`、`TOKEN`）→ 安全，可保留
- **公开学术信息**（论文作者手机号、邮箱）→ 需判断是否应公开
- **变量引用**（`os.environ.get('MEDDATA_PASSWORD')`）→ 安全，非硬编码

### 4. 输出报告
```
✅ 无真实凭证泄露
⚠️  公开学术信息（非隐私，仅为论文元数据）
⚠️  占位符/示例（安全，但建议未来替换为占位符）
```

## 注意

- 跳过大文件（>100KB）和二进制文件
- 跳过 `.gitignore` 已排除的目录
- 仅扫描 `.git ls-files` 中的已追踪文件（未追踪的不影响推送）
- `.git-credentials` 不在 git 仓库内，无需扫描