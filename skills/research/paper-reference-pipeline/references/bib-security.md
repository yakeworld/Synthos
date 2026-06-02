# BibTeX 工具安全规范

> 2026-05-28 安全事件: MedData密码(MEDDATA_PASSWORD_PLACEHOLDER)和SS API Key被提交到git历史。
> 教训: 任何明文凭证一旦git push即永久泄露，即使后续删除文件。

## 禁止行为

| 行为 | 风险 | 替代方案 |
|------|------|----------|
| .py文件硬编码密码/API key | 提交到git永久泄露 | `os.environ.get("VAR")` |
| .sh文件export密码 | 同上 | `.env` 文件 + `.gitignore` |
| .bib中含token/secret | 同上 | 仅存DOI、标题等元数据 |
| `git add -A` 不加审查 | 误加敏感文件 | 先用 `git status` 审查 |

## 必须配置

1. `.gitignore` 必须包含 `.env`, `*.key`, `credentials*`, `auth.json`, `token*`, `secrets*`
2. 所有凭证从环境变量读取，禁止硬编码
3. 示例代码中密码用 `***` 占位，禁止真实密码

## 已泄露处理

1. 立即修改对应平台密码
2. `git rm --cached <file>` 从追踪中移除
3. 更新 `.gitignore` 防止再次提交
4. 可选: `git filter-branch` 或 `bfg` 重写历史强制抹除

## 检查命令

```bash
# 扫描git中是否有密码/API key
git grep -n -E "password\s*=|api_key\s*=|sk-[a-zA-Z0-9]{20,}|eyJ[a-zA-Z0-9_-]+[.][a-zA-Z0-9_-]+[.][a-zA-Z0-9_-]+"

# 检查是否所有敏感文件被.gitignore覆盖
git status --ignored --short | grep -E "\.key|\.env|credentials|auth\.json|token"
```
