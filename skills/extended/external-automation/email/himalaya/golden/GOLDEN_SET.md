---
name: himalaya
description: himalaya 金测集 — IMAP/SMTP 邮件 CLI 操作的可执行测试（基于 himalaya CLI）
---

# 金测集: himalaya

> 来源: SKILL.md Golden 集合 + 验证清单 + Genes (HIMA-001~007)。
> 本技能用 `himalaya` 在终端管理邮件（IMAP/SMTP/Notmuch/Sendmail 后端）：
> 列取、搜索、读取、发送/回复/转发、移动/删除、附件、多账户。
> IO_CONTRACT: input `command: str, args: list[str]` → output `output: str`（命令行输出）。
> 每个 case 验证一条真实可执行的操作契约（P1 可复现性）；错误路径必须返回结构化
> Golden Error（含 context + ≥2 条恢复建议），禁止仅返回通用错误。

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常：非交互发送新邮件（管道输入）+ 程序化列表（--output json） | 发送走 `cat << EOF \| himalaya template send` 管道，不依赖 `$EDITOR`（HIMA-002）；列表/状态解析加 `--output json`（HIMA-003）；密码经 `backend.auth.cmd` 指向 pass/keyring 非明文（HIMA-006） |
| case_002 | 错误：发送退出码非零（Gmail 别名旧语法导致存 Sent 失败）→ 修配置而非盲目重试 SMTP | 命中 HIMA-005 → 严禁盲目重试 SMTP（防重复邮件）；先检查 `folder.aliases.X` 复数点分键配置（HIMA-001，v1.2.0+ 静默忽略旧 `alias` 子节）；修正后重试；返回结构化 Golden Error（context + ≥2 recovery） |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: 发送命令为管道形式（`himalaya template send` + stdin 输入），未出现
  `$EDITOR` 依赖或交互式 `message write`（HIMA-002）；列表命令带 `--output json`
  （HIMA-003）；config.toml 中 `backend.auth.cmd` 指向 pass/keyring 命令，密码非明文
  （HIMA-006）；`himalaya --version` 与 config 存在性前置检查通过（验证清单1）
- case_002: 必须命中 HIMA-005（非零退出码 + 重试场景）→ 禁止立即重跑发送；诊断指向
  `folder.aliases.X` 配置（HIMA-001）；修复配置后重试才允许第二次发送；错误结构必须
  同时含 `context`（退出码 + 服务器类型 + 失败阶段定位：SMTP 成功但存 Sent 失败）
  与 ≥2 条可操作 `recovery`；全程 SMTP 发送次数 ≤ 1（防重复邮件）

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001 / case_002） |
| high | 0.7 | 重要但不致命（扩展用例） |

## 期望输出

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，包含：
- `expected_output`: 命令序列 / 发送状态 / 错误结构
- `verification`: 可执行的校验断言列表

期望输出采用**语义等价判定**：
- 正常路径发送必须为管道输入（stdin），退出码 0，无 error
- 正常路径列表/解析命令必须含 `--output json`
- 错误路径必须同时含 `context` 与 `recovery` 两个字段，且 `smtp_retry_count == 1`
  （不盲目重发）

## 关联

- SKILL.md Genes: HIMA-001~007
- SKILL.md 验证清单: 6 项（version+config 前置 / 管道发送 / --output json / folder.aliases 复数点分键 / 非零退出码不盲目重试 / RUST_LOG 调试）
- 关联技能: email, references/configuration.md, references/message-composition.md
