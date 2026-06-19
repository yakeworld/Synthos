---
name: opencode
description: "1. **非常驻服务** — OpenCode 不是 daemon，按需启动、用完即关。`ps aux | grep opencode` 无进程是正常状态，不是故障。"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "task_desc: str, params: dict -> result: dict"
    atom_type: skill
    priority: P2
    related_skills: []

---






## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）

## 核心原则

1. **非常驻服务** — OpenCode 不是 daemon，按需启动、用完即关。`ps aux | grep opencode` 无进程是正常状态，不是故障。
2. **轻量替代** — Codex CLI 是主力编码代理。OpenCode 仅用于极轻量一次性脚本。
3. **API 不可互换** — OpenCode 用 `chat/completions`（OpenAI 兼容），Codex 用 `responses`（OpenAI Responses API）。

## 安装与位置

- **包名**: `opencode-ai`（不在 npm 公开索引，需全局安装 `npm install -g opencode-ai`）
- **可执行文件**: `~/.nvm/versions/node/v22.22.2/bin/opencode`（Node.js v22）
- **全局备选**: `~/.npm-global/bin/opencode`
- **版本**: v1.17.8（截至 2026-06-19 为最新）

## 版本检查与升级

```bash
opencode --version      # 检查当前版本
npm update -g opencode-ai  # 尝试升级（如有新版本）
# 如 npm update 无变化 = 已是最新
```

> **注意**: `opencode-ai` 不在 npm 公开索引中（`npm search opencode` 不返回它）。版本检查用 `npm update -g opencode-ai`，无变化即最新。
> **子命令陷阱**: `opencode` 没有 `doctor`/`health`/`version` 子命令。输入未知子命令会被当作路径切换，报错 "Failed to change directory to /.../XXX"。可用子命令：`models`、`providers`、`run`、`resume` 等。

## 配置结构

配置文件: `~/.config/opencode/opencode.json`

```json
{
  "provider": {
    "hermes":         // 默认主节点: 100.125.10.93:8000 → Qwen3.6-35B-NVFP4
    "amax-fallback":  // AMAX 备用: 100.82.27.51:8000 → Qwen3.6-35B-A3B-GPTQ-Int4
    "hermes-fallback": // Hermes 备用: 100.100.252.99:8000 → Qwen3.6-35B-NVFP4
    "deepseek":       // DeepSeek 云端: api.deepseek.com/v1 → v4-flash / v4-pro
  },
  "model": "hermes/qwen3.6-35b-nvfp4",  // 默认模型
  "mcp": { "lark-mcp": { ... } },        // 飞书 MCP
  "plugin": ["oh-my-openagent@latest"]
}
```

## 诊断流程

当需要检查 OpenCode 是否正常运行时，按此顺序执行：

### Step 1: 进程检查
```bash
ps aux | grep -i opencode
# 无进程 = 正常（非常驻服务），不是故障
```

### Step 2: 安装验证
```bash
opencode --version      # 应返回版本号
# 或: which opencode    # 定位二进制
```

### Step 3: 配置完整性
```bash
cat ~/.config/opencode/opencode.json   # 配置存在且格式正确
ls ~/.config/opencode/skills/          # 技能目录存在
ls ~/.config/opencode/node_modules/    # 依赖已安装
```

### Step 4: 后端连通性
```bash
nc -zv -w 3 100.125.10.93 8000  # 主节点
nc -zv -w 3 100.82.27.51 8000   # AMAX 备用
nc -zv -w 3 100.100.252.99 8000 # Hermes 备用
# 全部成功 = 后端正常
```

### Step 5: 使用历史
```bash
tail -3 ~/.local/state/opencode/prompt-history.jsonl  # 最近使用记录
ls -lt ~/.local/state/opencode/locks/                 # 锁文件（空=无正在运行的会话）
```

## 故障排查

| 症状 | 原因 | 修复 |
|------|------|------|
| `command not found` | 未安装或 PATH 缺失 | 检查 `~/.nvm/versions/node/v22.22.2/bin/opencode` |
| 端口不可达 | 后端服务宕机或 Tailscale 断开 | 检查 Tailscale 状态，确认 vLLM 容器运行 |
| 模型返回错误 | API key 过期或模型未就绪 | 检查 config.json 中 `apiKey`，确认 vLLM 加载模型 |
| 技能目录为空 | 未初始化或清理过 | 重新运行 `opencode` 会自初始化 |

## 与 Codex CLI 的关系

| 维度 | OpenCode | Codex CLI |
|------|----------|-----------|
| 角色 | 轻量替代 | 主力编码代理 |
| API | chat/completions | responses |
| 提供商 | DeepSeek/本地 vLLM | 仅本地 vLLM |
| 使用场景 | 一次性简单脚本 | 复杂编码任务 |
| 部署 | 本地 Node.js | 多节点 profile + .env |

详细 Codex 部署见 `codex-cli` 技能。

## 参考文件

- `references/diagnostic-log-2026-06-19.md` — 2026-06-19 完整诊断实录：后端连通性、进程状态、配置结构
委托OpenCode CLI编码 — 仅限一次性简单脚本。
