---
name: codex-install-guide
description: Codex CLI 安装与环境验证 — npm包名、二进制验证、与opencode共存、vLLM配置。
version: 1.0.0
author: Synthos
license: MIT
metadata:
  synthos:
    priority: P2
    atom_type: tooling
signature: "codex-install-guide -> processed_result"
---

# Codex CLI 安装与环境验证

## 原理层·文言

> 动在工欲善，先立其基。npm包名更迭，二进制必验。共存不扰，vLLM独尊。

## 核心流程

**Step 1: 安装 Codex CLI**

```bash
npm install -g @openai/codex
codex --version  # 验证二进制在 PATH 中
```

**Step 2: 验证环境**

```bash
codex --version   # 预期 v0.141.0
opencode --version  # 预期 v1.17.8（如已安装）
node --version    # 预期 v22+（via nvm）
```

**Step 3: 检查配置文件**

```bash
cat ~/.codex/config.toml          # Codex CLI 配置
cat ~/.local/share/opencode/auth.json  # OpenCode 配置（独立）
```

## 关键决策

### 包名选择

| 包名 | 类型 | 状态 |
|------|------|------|
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
