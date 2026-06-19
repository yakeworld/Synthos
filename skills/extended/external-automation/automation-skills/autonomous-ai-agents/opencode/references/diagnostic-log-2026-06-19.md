# OpenCode 诊断记录 — 2026-06-19 更新

## 生态调查

- `opencode-ai` 包名不在 npm 公开索引，`npm search opencode` 不返回它
- 版本检查方式: `npm update -g opencode-ai`，无变化即最新
- 当前版本 **v1.17.8**（2026-06-19 为最新）
- 与 `@openai/codex`（官方）无冲突，各自独立二进制

## 子命令陷阱

`opencode` 没有 `doctor`/`health`/`version` 子命令。输入未知子命令会被当作路径切换：
```
$ opencode doctor
Error: Failed to change directory to /path/doctor
```

可用子命令: `models`、`providers`、`run`、`resume`、`start`、`changelog` 等。
完整列表: `opencode --help` 或 `opencode --help commands`（如支持）。

## 诊断确认

- 安装: `/home/yakeworld/.nvm/versions/node/v22.22.2/bin/opencode`（符号链接到 `opencode-ai/bin/opencode.exe`）
- 配置: `~/.config/opencode/opencode.json` ✅
- 凭证: `~/.local/share/opencode/auth.json`（1个凭证）
- 后端连通性: 全部三节点 vLLM ✅
- 功能验证: `opencode run "test" --model "hermes/qwen3.6-35b-nvfp4"` 正常 ✅
