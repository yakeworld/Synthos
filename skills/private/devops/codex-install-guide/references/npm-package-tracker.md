# npm 包名更迭时间线

## 2026-06-19

- `@openai/codexec@0.141.0` 从 npm registry 完全移除（E404）
- `@openai/codex`（新包名）恢复，仍为 v0.141.0

## 当前状态

**已恢复**。`npm install -g @openai/codex` 获取 v0.141.0。

## 关键教训

1. **npm 包名可能随时变更** — 安装命令需验证包名有效性（`npm view <package>`）
2. **第三方打包器可能覆盖配置** — `@codexapi/codexclaude` 会修改 `~/.codex/config.toml` 指向其付费服务端点，与 vLLM 场景冲突
3. **安装后必须验证二进制** — `which codex` + `codex --version` 是必需步骤，不是可选