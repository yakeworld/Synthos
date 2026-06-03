# Pre-Commit Security Scan

> 在 `git commit` 前扫描待提交文件中的敏感信息，防止泄露。
> 实战验证：2026-06-02 Synthos 发现 skills/patent-disclosure/ 含未公开专利信息，
> research/ 含 443MB 实验数据不应上传 GitHub。

## 适用范围

- 论文项目首次 push 到 GitHub
- 从本地提交大量新文件的场景
- .gitignore 配置后确认文件未被跟踪

## 扫描步骤

### Step 1: 查看将要提交的文件

```bash
# 查看已暂存的文件
git status --short

# 或查看工作目录中所有未跟踪的文件
git status --porcelain --untracked-files=all
```

### Step 2: 检查敏感模式

```bash
# 记录/API密钥/凭据
grep -rn -iE "(api.key|api_secret|password|token|bearer|secret)" \
  --include="*.py" --include="*.md" --include="*.sh" --include="*.json" \
  --include="*.yaml" --include="*.yml" --include="*.toml" . 2>/dev/null | \
  grep -v ".git/" | grep -v "node_modules/" | grep -v "__pycache__" | \
  grep -vi "example" | grep -vi "placeholder" | grep -vi "redacted" | \
  grep -vi "os.getenv" | grep -vi "os.environ" | grep -vi "env.var" | \
  grep -vi "YOUR_" | grep -vi "<YOUR_"

# 个人邮箱/电话
grep -rn -E "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}" \
  --include="*" . 2>/dev/null | grep -v ".git/" | grep -v "node_modules/" | \
  grep -vi "example.com" | grep -vi "@users.noreply.github.com"

# 本地文件路径/用户名
grep -rn "/home/" --include="*.md" --include="*.py" --include="*.json" \
  . 2>/dev/null | grep -v ".git/" | grep -v "node_modules/"

# 内网IP地址
grep -rn -E "(10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.)" \
  --include="*" . 2>/dev/null | grep -v ".git/" | grep -v "__pycache__"
```

### Step 3: 检查大文件/不应提交的文件类型

```bash
# 大于 10MB 的文件
find . -type f -size +10M -not -path "./.git/*" 2>/dev/null

# 不应提交的文件类型（但可能不在 .gitignore 中）
find . -type f \( -name "*.mp4" -o -name "*.mov" -o -name "*.ts" -o \
  -name "*.aac" -o -name "*.wav" -o -name "*.docx" -o -name "*.pdf" \
  -o -name "*.npz" -o -name "*.h5" -o -name "*.pth" \) \
  -not -path "./.git/*" 2>/dev/null
```

### Step 4: 验证 .gitignore 覆盖范围

```bash
# 检查 .gitignore 是否包含常见目录
for dir in "research" "data" "outputs" ".evolution" "node_modules" "__pycache__" "venv"; do
  grep -q "^/$dir" .gitignore || grep -q "^$dir/$" .gitignore || \
  grep -q "^$dir$" .gitignore || \
  echo "MISSING: $dir not in .gitignore"
done
```

### Step 5: Dry-run 确认

```bash
git add --dry-run .
```

### Step 6: 排除不应提交的目录

如果发现有不应上传的目录：

```bash
# 1. 追加到 .gitignore
echo "# Large data files — not for GitHub upload" >> .gitignore
echo "research/" >> .gitignore

# 2. 如果文件已经 staging/committed，取消跟踪
git rm --cached -r research/  # 保留本地文件

# 3. 提交 .gitignore 变更
git add .gitignore
git commit -m "[chore] .gitignore: exclude research/, data/ from git tracking"

# 重要：git add -A 会在 .gitignore 变更提交前重新 staging 被 rm --cached 的文件！
# 安全步骤：先提交 .gitignore 变更，再 git add -A
```

## 陷阱

- **grep 误报**：代码中的示例/文档中的占位符会被 grep 匹配。必须用 `--include` 和 `--exclude` 过滤。
- **git add -A 重新 staging**：`git rm --cached` 后如果先执行 `git add -A`（而非先 commit），被移除的文件会重新 staging。**安全顺序**：编辑 .gitignore → git rm --cached → git commit → 然后才能 git add -A
- **npz/pth 文件不可**：二进制文件体积小但可能包含模型权重。确认是否需要上传。
- **嵌套 .gitignore**：子目录中的 .gitignore 会覆盖根目录的规则。检查子目录 .gitignore 是否在 git tracking 中。
