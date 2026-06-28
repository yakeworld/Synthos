---
name: privacy-scan
description: Git 推送前隐私安全扫描 — 拦截 API Key、GitHub Token、密码、手机号等敏感信息泄露
version: 1.0.0
author: Synthos
license: MIT
signature: "privacy-scan -> processed_result"
---

# 隐私安全扫描（Pre-Push Privacy Scanner）

## 原理

每次 `git push` 时，pre-push hook 自动扫描即将推送的 commit，拦截敏感信息。

## 安装

### 已安装的仓库
- `Synthos`
- `academic_agent_prompt`（本地）
- `Synthos-competition`
- `crispdm-pima`

### 手动安装到新仓库
```bash
ln -sf ~/.hermes/scripts/privacy-scan.sh /path/to/repo/.git/hooks/pre-push
```

### 全局模板（新仓库自动安装）
已在 `~/.git-templates/hooks/pre-push` 配置了全局 git 模板：
```bash
git config --global init.templateDir ~/.git-templates
```

## 扫描内容

| 类别 | 模式 | 示例 |
|:-----|:-----|:-----|
| GitHub PAT（经典） | `ghp_` + 36位 | `ghp_xxxx...` |
| GitHub PAT（细粒度） | `github_pat_` + 82位 | `github_pat_xxx...` |
| GitHub OAuth | `gho_` + 36位 | `gho_xxxx...` |
| OpenAI / API Key | `sk-` + 20位以上 | `sk-xxxx...` |
| HuggingFace Token | `hf_` + 20位 | `hf_xxxx...` |
| JWT Token | `eyJ` + base64.base64 | `eyJxxx.xxx.` |
| SSH 私钥 | `-----BEGIN...PRIVATE KEY-----` | 私钥内容 |
| URL 内嵌凭证 | `https://user:pass@host` | 明文密码 |
| 中国大陆手机号 | `1[3-9]` + 9位数字 | `139xxxxxxx` |
| 已知真实凭证 | 精确字符串匹配 | 已泄露的 Key |

## 维护

### 添加已知凭证到黑名单
编辑 `~/.hermes/scripts/privacy-scan.sh`：
```bash
KNOWN_SECRETS=***    "新泄露的key"
    # ...
)
```

### 跳过扫描（紧急情况）
```bash
git push --no-verify
```
仅在确认没有敏感信息时使用。

## 文件位置
- 脚本: `~/.hermes/scripts/privacy-scan.sh`
- 全局模板: `~/.git-templates/hooks/pre-push`

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
