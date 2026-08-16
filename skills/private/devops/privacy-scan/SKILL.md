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

1. 输入验证: 输入参数/文件/路径是否完整且有效
2. 过程验证: 中间步骤/转换/计算是否正确
3. 输出验证: 输出格式/内容是否符合预期
4. 边界验证: 空输入、极大值、异常场景是否处理
5. 错误处理: 失败时是否有明确的错误信息和恢复指引

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

- Golden Input: 标准输入样本（覆盖正常路径）
- Golden Output: 预期输出（精确匹配或格式校验）
- Golden Error: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。---





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

1. 输入验证: 输入参数/文件/路径是否完整且有效
2. 过程验证: 中间步骤/转换/计算是否正确
3. 输出验证: 输出格式/内容是否符合预期
4. 边界验证: 空输入、极大值、异常场景是否处理
5. 错误处理: 失败时是否有明确的错误信息和恢复指引

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

- Golden Input: 标准输入样本（覆盖正常路径）
- Golden Output: 预期输出（精确匹配或格式校验）
- Golden Error: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
