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

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引

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

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

# Codex Install Guide---





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

> (P032 去重: 以下为合并前第二份中的 1 行独有内容, 保留以防丢失)
# Codex Install Guide
