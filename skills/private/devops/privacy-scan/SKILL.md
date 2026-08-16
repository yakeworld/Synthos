---
name: privacy-scan
description: Git 推送前隐私安全扫描 — 拦截 API Key、GitHub Token、密码、手机号等敏感信息泄露
signature: privacy-scan -> processed_result
allowed-tools:
- terminal
- read_file
- write_file
- session_search
version: 1.1.0
license: MIT
metadata:
  synthos:
    atom_type: mechanical
    description: Git 推送前隐私安全扫描 — 拦截 API Key、GitHub Token、密码、手机号等敏感信息泄露
    signature: privacy-scan -> processed_result
    priority: P2
    synthos_version: 1.1.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
category: devops
author: Synthos
---

` 边界 bug 已记录 — SKILL.md 文件需要 `git ls-tree` 二次验证
- 2026-07-06: .gitignore 注释与规则可能矛盾 — 注释写"私有技能纳入git"但实际规则只排除 pycache/pyc/Dotstore 等缓存文件，导致 776 个 private skill 文件被追踪。修复：`git rm --cached` 逐个移除 + `.gitignore` 中用 `skills/private/` 直接排除整个目录。

## 维护

### 添加已知凭证到黑名单
编辑 `~/.hermes/scripts/privacy-scan.sh`：
```bash
KNOWN_SECRETS=(
    "新泄露的key"
    # ...
)
```

### 跳过扫描（紧急情况）
```bash
git push --no-verify
```
仅在确认没有敏感信息时使用。

## 已知泄漏记录（2026-07-03）

**泄露内容**: SS API Key (iYTNXX, 40位) + SS API Key (s2k-HT, 44位) + PubScholar SALT + 2个手机号
**影响范围**: 267 个历史提交（a2af230 → f08ba8a）
**已清理**: 全部 267 个 commits 已通过 git-filter-repo 重写清除
**本地凭证**: ~/.secrets (mode 600) 仍含原密钥，需轮换
**磁盘文件**: outputs/ 日志/脚本含密钥，已清理

## 文件位置
- 脚本: `~/.hermes/scripts/privacy-scan.sh`
- 全局模板: `~/.git-templates/hooks/pre-push`

## 参考文件
- `references/gitignore-audit-protocol.md` — .gitignore 规则审计完整步骤（注释/规则矛盾检测、批量 `git rm --cached`、验证）
- `references/gitrepo-cleanup.md` — 历史泄露清理完整流程（git-filter-repo 操作指南）

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 验证清单 · VERIFICATION

- [ ] Git 推送前 pre-push 钩子已触发，对 API Key / GitHub Token / 密码等敏感信息完成扫描（PRIV-001）
- [ ] 发现的已知泄露凭证或新敏感数据已加入 `~/.hermes/scripts/privacy-scan.sh` 的 `KNOWN_SECRETS` 黑名单数组（PRIV-002）
- [ ] 仅在使用 `git push --no-verify` 跳过扫描时，已人工确认代码库不含任何敏感信息（PRIV-003）
- [ ] .gitignore 注释与实际排除规则一致，无私有技能文件（如 `skills/private/` 下文件）被误追踪（PRIV-004）
- [ ] 历史提交发生泄露时已用 `git-filter-repo` 重写清除，且 `~/.secrets`（mode 600）中的原凭证已轮换（PRIV-005，已知泄漏记录）
- [ ] 已用 `git ls-tree` 等命令二次验证敏感文件确实未被追踪或已从历史中清除（PRIV-006）
- [ ] 扫描异常/失败时错误信息包含具体上下文和恢复建议，操作可复现可追溯（PRIV-007）

## 核心原则 · PRINCIPLES

1. 准确为先: 所有输出必须经过事实核查，不编造数据
2. 证据驱动: 每个结论必须可追溯到具体证据或数据源
3. 可复现性: 每一步操作必须可重复，结果可验证

## 约束规则 · RULES

1. 输入约束: 参数类型、范围、格式必须校验
2. 输出约束: 返回值结构、编码、命名必须一致
3. 异常约束: 错误信息必须包含上下文和恢复建议
4. 安全约束: 不执行未验证的任意代码，不暴露内部状态

## Golden 集合 · GOLDEN SET

- Golden Input: `git push` 触发 `~/.git-templates/hooks/pre-push` 钩子，仓库中含疑似 GitHub Token / API Key 的文件（PRIV-001）
- Golden Output: 钩子扫描通过且无命中；`git ls-tree` 二次验证敏感文件未被追踪，`skills/private/` 下无私有技能文件被误追踪（PRIV-004/006）
- Golden Error: 扫描命中已知泄露凭证 → 推送被拦截，凭证加入 `~/.hermes/scripts/privacy-scan.sh` 的 `KNOWN_SECRETS` 数组（PRIV-002）；历史提交已泄露 → `git-filter-repo` 重写清除（267 commits 先例）+ `~/.secrets` 凭证轮换（PRIV-005）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。
> 违反规则的操作视为不安全，必须拒绝或隔离。
> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。
> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。---
## Genes (策略基因)
> 紧凑策略表示。条件→策略。需要深度时参考完整文档。
- **[PRIV-001]** 执行 Git 推送操作前 → 必须触发 pre-push 钩子进行敏感信息（API Key、Token、密码等）扫描
- **[PRIV-002]** 发现已知泄露凭证或新敏感数据 → 将其加入 `KNOWN_SECRETS` 黑名单数组以增强后续拦截能力
- **[PRIV-003]** 确认代码库中绝对不含敏感信息且需紧急推送 → 使用 `git push --no-verify` 跳过扫描，但需承担泄露风险
- **[PRIV-004]** 检测到 .gitignore 注释与实际排除规则矛盾 → 执行 `git rm --cached` 移除误追踪文件并修正规则以直接排除整个私有目录
- **[PRIV-005]** 发生历史提交敏感信息泄露 → 使用 `git-filter-repo` 重写历史提交清除数据，并立即轮换本地存储的原始凭证
- **[PRIV-006]** 验证扫描结果或清理效果 → 采用 `git ls-tree` 等命令进行二次验证，确保敏感文件确实未被追踪或已清除
- **[PRIV-007]** 处理扫描异常或失败场景 → 错误信息必须包含具体上下文和明确的恢复建议，确保操作可复现且可追溯