---
name: repo-path-sanity
description: GOLDEN_SET.md
---

# 金测集: repo-path-sanity

> Git 仓库路径与凭据健康检查技能的标准测试用例集。覆盖正常配置溯源、
> 全局配置劫持 HTTPS remote、已登录但 PAT scope 不足、NFS 挂载点浅探。
> 每个用例有明确的"通过"标准。

## 技能定位

`repo-path-sanity` 对 Git 仓库路径与凭据做健康检查：
先查配置（`git config --list --show-origin`）再断故障，
输出问题→根因→修复命令对照表（insteadOf / credential.helper / PAT scope / SSH key 注册）。

输入 `repo_path: str`（待检查仓库路径）+ `failure_symptom: str`（症状描述），
输出 `sanity_report: table` + `fix_commands: list[str]`。

## 测试用例

| ID | 文件 | 描述 | 关键检查 | 权重 |
|----|------|------|---------|------|
| case_001 | `cases/case_001.json` | 全局 insteadOf 劫持 HTTPS remote（正常诊断+修复路径） | 溯源 `~/.gitconfig` 含 insteadOf；输出修复命令 `git config --global --unset` | critical |
| case_002 | `cases/case_002.json` | 已登录但 PR 创建失败（PAT scope 不足，失败路径） | `gh auth status` 已登录但 `gh pr create` 报 not accessible；判定 PAT 缺 scope；建议重建 Classic PAT | critical |
| case_003 | `cases/case_003.json` | NFS 挂载点诊断超时（浅探规避路径） | 全程 `timeout` + 浅层命令，禁止 `os.walk`/`du -sh` 全遍历 | high |

## 通过标准

- 加权总分 ≥ 0.80
- 所有 critical 检查通过
- 修复建议可执行（非仅诊断）
- 输出含诊断结论与修复命令
- 仓库路径存在且为 git 仓库
- 已检查路径大小写与符号链接问题

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |

## 与 SKILL.md 验证清单的映射

- 仓库路径存在且为 git 仓库 → case_001
- 已检查路径大小写与符号链接问题 → case_001
- 跨平台路径差异已标注（Windows/Linux/macOS） → case_001
- 修复建议可执行（非仅诊断） → case_001 / case_002
- 输出含诊断结论与修复命令 → case_001 / case_002 / case_003
