# Git 凭证清理：git-filter-repo 移除历史中的硬编码凭证

> **信息安全、个人隐私是首要任务。** 必须严格配置、仔细审计，做好规划后再执行。
> 工作流：PLAN（全面审计） → 确认方案 → EXECUTE（清理历史） → VERIFY（验证推送）

## 适用场景
- API key、密码、token 被硬编码提交到 git 历史（即使是当前文件已修复，历史提交仍含敏感信息）
- GitHub 仓库已推送，需重写历史移除凭证
- GitHub Push Protection 拦截了推送（检测到 secret scanning 命中）

## 第一步：全面审计（PLAN）

### 1.1 列出所有含 GitHub 远程的仓库
```bash
find /path/to/workspace -name ".git" -maxdepth 4 -type d | while read d; do
  r=$(cd "$(dirname "$d")" && git remote -v 2>/dev/null | grep "github.com" | head -1)
  [ -n "$r" ] && echo "$(dirname $d) → $(echo $r | grep -oP 'github\.com[^ ]+' | head -1)"
done
```

### 1.2 扫描各仓库的敏感信息
```bash
for repo in /repo1 /repo2; do
  cd "$repo"
  
  # 当前工作树的凭证文件
  for f in .git-credentials .env .api_key credentials.json *.pem *.key id_rsa id_ed25519; do
    [ -f "$f" ] && echo "⚠️ 存在: $f"
  done
  
  # git 历史中的凭证
  for pattern in "ghp_" "github_pat" "sk-" "SEMANTIC_SCHOLAR.*[A-Za-z0-9]\{20,\}"; do
    git log --all -p -S "$pattern" -- "*.py" "*.json" "*.yaml" "*.sh" ".git-credentials" 2>/dev/null | \
      grep "^diff\|^+.*$pattern" | head -10
  done
done
```

### 1.3 常见凭证模式

| 凭证类型 | 格式示例 | 长度 | 扫描关键词 |
|:---------|:---------|:----:|:-----------|
| GitHub PAT（旧格式） | `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` | 40+ | `ghp_` |
| GitHub PAT（新格式） | `github_pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` | 80+ | `github_pat` |
| Semantic Scholar Key | `iYTNXXDH278PVXl2FJ2YU1TyZ5joLAZr3WA9IVzt` | 40 | `SEMANTIC_SCHOLAR`；注意旧格式纯字母数字无前缀，`s2k-xxx` 前缀的通常已过期 |
| OpenAI / DeepSeek | `sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` | 30+ | `sk-` |
| MedData 账号密码 | `wzsrmyy` / `77306268` | 6-8 | `MEDDATA_USERNAME` / `MEDDATA_PASSWORD` |
| HuggingFace Token | `hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` | 30+ | `hf_` |
| Git 凭证文件 | `.git-credentials` 含 `https://user:pat@github.com` | — | `.git-credentials` |
| Roo Code MCP 配置 | `.roo/mcp.json` + `.roo/rules-researcher/mcp.json` | — | `.roo/`（含 API Key 环境变量定义） |

## 第二步：清理历史（EXECUTE）

### 2.1 安装 git-filter-repo
```bash
pip install git-filter-repo
```

### 2.2 创建替换规则文件
```bash
cat > /tmp/replace_sensitive.txt << 'EOF'
literal:ACTUAL_API_KEY_OR_PASSWORD==>PLACEHOLDER_TEXT
literal:another_sensitive_string==>ANOTHER_PLACEHOLDER
EOF
```
- 每行一个 `literal:OLD==>NEW` 规则
- `literal:` 前缀表示精确匹配（非正则），推荐用于凭证
- OLD 是实际敏感字符串，NEW 是替换后的安全文本

### 2.3 替换敏感字符串（所有提交）
```bash
# 注意：git-filter-repo 会自动移除 origin remote（安全机制）
git filter-repo --force --replace-text /tmp/replace_sensitive.txt
```

### 2.4 移除整个文件（可选）
如果某文件包含太多敏感信息，直接整体从历史中移除：
```bash
git filter-repo --force --path github_maintenance.py --invert-paths
git filter-repo --force --path .git-credentials --invert-paths
```

### 2.5 修复工作树
历史重写后工作树中的文件也会被替换。必要时修复 fallback 值：
```bash
# 例如：config.py 中的 os.environ.get('KEY', 'PLACEHOLDER')
# 需要把 PLACEHOLDER 改为 ''（空字符串）
sed -i 's/PLACEHOLDER_TEXT//g' src/core/config.py
```

### 2.6 提交当前修复
```bash
git add -A
git commit -m "Remove hardcoded credentials; use env vars only"
```

### 2.7 恢复远程并 force push
```bash
git remote add origin https://github.com/username/repo.git
git push --force origin local_branch:remote_branch
```

### 2.8 处理 GitHub Push Protection 拦截
如果 GitHub 的 secret scanning 拦截了推送：
- **方案A**（推荐）：用 filter-repo 彻底移除被标记的文件/字符串，重新推送
  ```bash
  # 识别被标记的 blob
  git rev-list --objects --all | grep <blob_id_from_github_error>
  
  # 移除该文件/替换该字符串
  git filter-repo --force --path <filename> --invert-paths
  ```
- **方案B**：通过 GitHub 提供的 bypass URL 一次性跳过保护（https://github.com/.../security/secret-scanning/unblock-secret/...）
  > 注意：bypass 只是绕开当前检查，历史中的凭证仍然存在。推荐方案A。

## 第三步：验证与防护（VERIFY）

### 3.1 验证历史中无凭证残留
```bash
# 对每种凭证类型
git log --all -p -S "iYTNXXDH278" -- . 2>/dev/null | head -3 || echo "✅ 已清除"
git log --all -p -S "github_pat" -- . 2>/dev/null | head -3 || echo "✅ 已清除"
git log --all --oneline -- ".git-credentials" || echo "✅ 已清除"
```

### 3.2 查看清理后的提交列表（hash 应已改变）
```bash
git log --oneline --all
```

### 3.3 更新 .gitignore 防止再次泄露
在清理后的仓库中添加以下规则：
```gitignore
# 凭证文件
.api_key
.env
credentials.json
.git-credentials

# 私人配置（Roo Code MCP、API Keys）
.roo/

# 研究输出数据（非代码）
research/
```

### 3.4 检查各仓库的远程是否正确
```bash
for repo in /path/*; do
  (cd "$repo" 2>/dev/null && git remote -v)
done
```

### 3.5 删除严重泄露的仓库（可选）
如果仓库包含大量无法逐个清理的敏感信息，可直接从 GitHub 删除：
```bash
# 需要 gh CLI 已认证
gh repo delete owner/repo-name --yes

# 同步移除本地 remote
git remote remove origin
```
> 仅当：仓库可放弃（非核心项目）、历史无法彻底清理、或用户明确要求。

## 已知陷阱

1. **git-filter-repo 删除 origin remote** — 这是安全机制，不是 bug。完成后需重新 `git remote add origin`
2. **所有 commit hash 改变** — 其他人 clone 过该仓库的需重新 clone
3. **filter-repo 会修改工作树** — 当前文件中的敏感字符串也会被替换。替换后需手动修复 fallback 值
4. **filter-repo 需要干净的 git 仓库** — 运行前 commit 或 stash 所有未提交变更
5. **多次 filter-repo 运行** — 每次都会从当前 HEAD 重写，可以叠加多个清理操作
6. **凭证替换后检查残留** — `git log --all -p -S "OLD_STRING" -- .` 应为空
7. **不要用 git filter-branch** — 它被官方弃用，且对大型仓库极其缓慢
8. **GitHub 推送保护** — 即使历史已清理，GitHub 的 secret scanning 仍可能因为 blob 缓存而拦截。用 filter-repo 彻底移除被标记的 blob 即可解决
9. **大文件警告** — GitHub 对 >50MB 的文件有警告，不影响推送

## 一次性审计命令

快速扫描所有仓库的凭证泄露：
```bash
for repo in /path/to/*/; do
  [ ! -d "$repo/.git" ] && continue
  echo "=== $repo ==="
  cd "$repo"
  for pat in "ghp_" "github_pat" "SEMANTIC_SCHOLAR.*[A-Za-z0-9]\{20,\}" "sk-[A-Za-z0-9]\{20,\}" "wzsrmyy\|77306268" "MEDDATA_USERNAME\|MEDDATA_PASSWORD"; do
    git log --all -p -S "$pat" -- "*.py" "*.json" "*.yaml" "*.sh" 2>/dev/null | \
      grep "^+.*$pat" | head -3 && echo "⚠️ $pat"
  done
done
```
