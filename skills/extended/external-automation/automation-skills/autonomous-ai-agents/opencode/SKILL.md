---
name: opencode
description: "OpenCode CLI — 已降级为轻量替代。Codex CLI 是主力编码代理。保留用于极轻量一次性脚本。"
version: 1.0.0
metadata:
  synthos:
    version: 1.0.0
    author: Synthos

---

## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）

> 对应原则：P2（机械原子暴露输入输出规范）



# Opencode

> ⚠️ **已降级为轻量替代。** Codex CLI 是主力编码代理。OpenCode 仅用于极轻量的临时脚本任务，复杂编码一律走 Codex。

## 补充说明

- OpenCode 支持 OpenAI 兼容 API（`chat/completions` 格式），可调用 DeepSeek 等供应商
- Codex CLI 仅支持 OpenAI Responses API（`responses` 格式），只能调本地 vLLM 模型
- 两者 API 协议不同，不可互换
- 远程部署 Codex CLI 见 `codex-cli` 技能（含 .env 环境变量配置、base64 传输、doctor 诊断流程）

委托OpenCode CLI编码 — 仅限一次性简单脚本。
