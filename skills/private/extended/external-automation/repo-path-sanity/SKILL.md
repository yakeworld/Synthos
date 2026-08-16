---
name: repo-path-sanity
description: git config --list --show-origin | grep credential
signature: 'repo-path-sanity -> external-automation: synthetic skill for repo path
  sanity'
allowed-tools:
- terminal
- read_file
- write_file
- session_search
version: 1.0.0
license: MIT
metadata:
  synthos:
    atom_type: mechanical
    description: git config --list --show-origin | grep credential
    signature: 'repo-path-sanity -> external-automation: synthetic skill for repo
      path sanity'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
category: private
---


|
| `url.https://github.com/.insteadOf = ssh://git@github.com/` 在 `~/.gitconfig` | HTTPS remote 被转 SSH | `git config --global --unset url.https://github.com/.insteadOf` |
| `credential.helper = store` 在 `~/.gitconfig` | 覆盖 repo 级别的 `gh auth git-credential` | `git config --global --unset credential.helper` |
| `gh auth status` 显示已登录但 `gh pr create` 报错 | PAT 只有只读 scope，无 repo 权限 | 创建新的 Classic PAT，勾选 repo + write:repository |
| `ssh -vT git@github.com` → "Permission denied (publickey)" | SSH key 未注册到 GitHub | 在 GitHub Settings → SSH keys 中添加 |

## IO_CONTRACT

- **input**: `repo_path: str` — 待检查的 Git 仓库路径（含全局/仓库级 `git config` 与 `gh auth` 状态）
- **input**: `failure_symptom: str` — 症状（`gh pr create` 报错、`Permission denied (publickey)`、HTTPS remote 异常等）
- **output**: `sanity_report: table` — 问题 → 根因 → 修复命令对照（insteadOf / credential.helper / PAT scope / SSH key 注册）
- **output**: `fix_commands: list[str]` — `git config --unset`、新建 Classic PAT（repo + write:repository）、SSH key 添加等

## 原则 (Principles)

1. **「先查配置，后断故障。」** — 先以 `git config --list --show-origin` 溯源 insteadOf / credential.helper，再下结论。
2. **「全局覆仓，慎去其弊。」** — 全局 `~/.gitconfig` 会覆盖 repo 级 `gh auth git-credential`，查源须含全局层。
3. **「登录非凭据，权限乃凭据。」** — `gh auth status` 已登录不代表可写：PAT scope 须含 repo + write:repository。
4. **「深巡慢道，浅探为先。」** — NFS 极慢，`os.walk`/`du` 全遍历超时 300s；用 `timeout` + 浅层命令，勿全盘扫描。

### 调试命令

```bash
git config --list --show-origin | grep credential
git config --global --get url.https://github.com/.insteadOf || echo "no insteadOf"
gh auth status
gh pr create --title test --body test --head test 2>&1 | grep -i "accessible\|denied"
```


## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[REPO-001]** 遇到 Git 认证或远程连接故障 → 优先执行 `git config --list --show-origin` 溯源配置来源，再下结论
- **[REPO-002]** 全局 `~/.gitconfig` 存在 `credential.helper` 或 `insteadOf` 配置 → 检查其是否覆盖 Repo 级 `gh auth` 设置，必要时执行 `git config --global --unset` 移除冲突项
- **[REPO-003]** `gh auth status` 显示已登录但 `gh pr create` 报错 → 检查 PAT Scope，确保包含 `repo` 和 `write:repository` 权限，否则重建 Classic PAT
- **[REPO-004]** `ssh -vT git@github.com` 返回 "Permission denied (publickey)" → 确认 SSH Key 已正确注册到 GitHub Settings → SSH keys
- **[REPO-005]** 在 NFS 挂载点（如 `/mnt/nfs`）执行文件遍历或统计 → 使用 `timeout` 限制执行时间并采用浅层命令，避免 `os.walk` 或 `du` 导致 300s 超时
- **[REPO-006]** 调试 Git 凭据问题 → 组合使用 `grep credential`、`gh auth status` 及 `gh pr create` 测试命令以定位具体故障点

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

## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
