---
name: codex-install-guide
description: '`codex` 和 `opencode` 互不干扰：'
signature: 'codex-install-guide -> devops: synthetic skill for codex install guide'
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
    description: '`codex` 和 `opencode` 互不干扰：'
    signature: 'codex-install-guide -> devops: synthetic skill for codex install guide'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---

|
| `@openai/codex` | 官方 | ✅ 当前安装 |
| `@openai/codexec` | 旧包名 | ❌ 已从 npm registry 移除 |
| `@codexapi/codexclaude` | 第三方付费打包器 | ❌ 会覆盖 vLLM 配置，拒绝安装 |
| `opencode-ai` | 独立替代 | ✅ 保留作为共存方案 |

### 共存策略

`codex` 和 `opencode` 互不干扰：
- `codex` 使用 `~/.codex/config.toml`
- `opencode` 使用 `~/.local/share/opencode/auth.json`
- 二进制名不同：`codex` vs `opencode`

## 防错清单

- [ ] 安装后验证 `which codex` 返回有效路径
- [ ] 确认 `codex --version` 不报错
- [ ] 不要安装 `@codexapi/codexclaude`（它会修改 `~/.codex/config.toml` 指向付费端点）
- [ ] 使用 `@openai/codex`，不用旧包名 `@openai/codexec`
- [ ] 安装后检查 `ls ~/.codex/profiles/` — 如果 cron 脚本引用了 profile 但不存在，会批量超时。确保所有 cron 脚本调用的 profile（如 `amax`、`hermes`）对应文件存在

## 多 Profile 管理

Codex CLI 通过 `~/.codex/profiles/<name>.config.toml` 管理多节点 profile：

```toml
# amax.config.toml
model = "qwen3.6-35b-nvfp4"
model_provider = "amax"

[model_providers.amax]
name = "Amax vLLM"
env_key = "AMAX_API_KEY"
base_url = "http://[T1_NODE_IP_2]:8000/v1"
wire_api = "chat_completions"
```

```bash
# 使用特定 profile
codex -p amax exec "command"

# 验证 profile 是否存在
codex -p amax exec "echo test"
```

**关键**：所有 cron 脚本引用的 profile 必须存在，否则 `codex exec` 会超时且无具体错误信息。

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 验证清单 · VERIFICATION

- [ ] 已使用官方包 `@openai/codex` 安装，未使用已移除的旧包名 `@openai/codexec`（CODE-001）
- [ ] 未安装第三方付费打包器 `@codexapi/codexclaude`，确认 `~/.codex/config.toml` 未被改指向付费端点（CODE-002）
- [ ] `which codex` 返回有效二进制路径，且 `codex --version` 无报错（CODE-004，防错清单）
- [ ] 与 `opencode` 共存时隔离完好：`codex` 用 `~/.codex/`，`opencode` 用 `~/.local/share/opencode/`，二进制名不冲突（CODE-003，共存策略）
- [ ] `ls ~/.codex/profiles/` 下存在所有 cron 脚本引用的 profile 文件（如 `amax`、`hermes`），缺失会导致 `codex exec` 无错误静默批量超时（CODE-005）
- [ ] `codex -p <name> exec "echo test"` 对每个待用 profile 验证可通（多 Profile 管理节）
- [ ] 调试 `codex exec` 超时时已优先检查对应 profile 文件是否存在（CODE-006）

## 核心原则 · PRINCIPLES

1. **准确为先**: 所有输出必须经过事实核查，不编造数据
2. **证据驱动**: 每个结论必须可追溯到具体证据或数据源
3. **可复现性**: 每一步操作必须可重复，结果可验证

## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

## Golden 集合 · GOLDEN SET

- **Golden Input**: 在已有 `opencode` 的 Linux 工作站安装 Codex CLI，且 cron 脚本引用 profile `amax`（CODE-003/005）
- **Golden Output**: `npm i -g @openai/codex` 后 `which codex` 返回有效路径、`codex --version` 无报错；`~/.codex/config.toml` 未被指向付费端点；`codex -p amax exec "echo test"` 返回 `test`，与 opencode（`~/.local/share/opencode/`）共存无冲突（CODE-001/002/004）
- **Golden Error**: cron 脚本引用的 profile 缺失（`ls ~/.codex/profiles/` 无 `amax.config.toml`）→ `codex exec` 无具体错误信息静默批量超时（CODE-006）；或误装 `@codexapi/codexclaude` 覆盖 vLLM 配置指向付费端点（CODE-002，须拒绝）
> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。
> 违反规则的操作视为不安全，必须拒绝或隔离。
> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。
> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
# Codex Install Guide---
> (P032 去重: 以下为合并前第二份中的 1 行独有内容, 保留以防丢失)
# Codex Install Guide
## Genes (策略基因)
> 紧凑策略表示。条件→策略。需要深度时参考完整文档。
- **[CODE-001]** 安装 Codex CLI 时 → 必须使用官方包 `@openai/codex`，严禁使用已移除的旧包名 `@openai/codexec`
- **[CODE-002]** 遇到第三方打包器（如 `@codexapi/codexclaude`）时 → 拒绝安装，防止其覆盖 vLLM 配置或修改指向付费端点
- **[CODE-003]** 需要与 `opencode` 共存时 → 利用二进制名及配置路径（`~/.codex` vs `~/.local/share/opencode`）的天然隔离实现互不干扰
- **[CODE-004]** 安装完成后 → 执行 `which codex` 和 `codex --version` 以验证二进制路径有效且版本无报错
- **[CODE-005]** 配置多节点 Profile 时 → 确保 `~/.codex/profiles/` 下存在所有 cron 脚本引用的 profile 文件，避免批量超时
- **[CODE-006]** 调试 `codex exec` 超时问题时 → 优先检查对应 profile 文件是否存在，因为缺失 profile 会导致无具体错误信息的静默超时

## 示例 · EXAMPLES

- **示例 1**：输入「在 Linux 工作站安装 Codex CLI」→ 执行 `npm i -g @openai/codex`（CODE-001，拒绝旧包名 `@openai/codexec` 与付费打包器 `@codexapi/codexclaude`）→ 验证：`which codex` 返回有效路径且 `codex --version` 无报错（CODE-004/防错清单），`~/.codex/config.toml` 未被改指向付费端点（CODE-002）。
- **示例 2**：输入「已有 opencode，需 codex 共存」→ 按共存策略利用天然隔离：`codex` 用 `~/.codex/config.toml`、`opencode` 用 `~/.local/share/opencode/auth.json`，二进制名不同（CODE-003）→ 验证：两工具互不覆盖配置，`which codex` / `which opencode` 各自返回独立二进制。
- **示例 3**：输入「cron 脚本引用 profile `amax`，`codex exec` 批量超时」→ 按 CODE-006 先 `ls ~/.codex/profiles/` 确认 `amax.config.toml` 是否存在（多 Profile 管理节），缺失则按模板创建（model=qwen3.6-35b-nvfp4 / amax 供应商）→ 验证：`codex -p amax exec "echo test"` 返回 `test`，超时消除（CODE-005，验证清单）。