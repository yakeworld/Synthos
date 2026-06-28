# opencode 作为 Codex CLI 回退 — 使用指南

## 何时使用
- `@openai/codexec` 从 npm registry 移除，`codexec` 命令不可用
- `@codexapi/codexclaude` bundler 安装的嵌套 `@openai/codexec` 损坏
- 需要临时替代方案进行编码任务

## 基本配置
```bash
opencode --version        # 确认 >= 1.17.0
opencode models           # 查看模型列表
opencode providers list   # 查看已配置 provider
```

## 模型对接 vLLM
opencode 支持 `hermes/qwen3.6-35b-nvfp4` 模型（指向本机 vLLM 服务）。
配置方式与 codexec 不同：opencode 使用 `~/.local/share/opencode/auth.json` 管理凭证。

如需自定义 vLLM provider，参考 opencode 文档添加自定义 OpenAI-compatible provider：
- provider name: 任意名称
- base_url: `http://100.82.27.51:8000/v1`
- api_key: 任意值（vLLM 不校验）
- 模型列表: `qwen3.6-35b-nvfp4`

## 常用操作对比

| codexec | opencode |
|---------|----------|
| `codexec exec "task"` | `opencode run "task"` |
| `codexec review "..."` | `opencode run "review this code"` |
| `codexec --skip-git-repo-check` | opencode 默认不强制 git 检查 |
| `~/.codex/config.toml` | `~/.local/share/opencode/auth.json` |
| 项目信任: `[projects."path"]` | 通过 cwd 或 `--cwd` 指定 |

## 注意事项
- opencode 使用 Anthropic Messages API 协议（默认），非 OpenAI Responses
- 通过自定义 provider 可桥接到 OpenAI-compatible 端点
- 不继承 `~/.codex/config.toml`，需独立配置
- `opencode` 的 `run` 模式是非交互的，适合自动化