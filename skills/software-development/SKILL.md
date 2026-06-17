---

name: software-development
description: 软件开发 — Agent编排、调试、嵌入式Python、眼动追踪平台、开源贡献。
version: 1.0.0
triggers:
  - 需要执行software-development下的子技能
metadata:
  synthos:
    priority: P2
    atom_type: parent-skill
    description: "父级技能 — 软件开发 — Agent编排、调试、嵌入式Python、眼动追踪平台、开源贡献。"
    signature: 'software-development -> sub-skills: [agent-orchestration-harness, debugging-hermes-tui-commands, embedded-python-modularization]'
    related_skills: ["agent-orchestration-harness", "debugging-hermes-tui-commands", "embedded-python-modularization", "eye-tracking-platform", "github-agent-contributions"]

---


# software-development

> 父级技能目录，包含 16 个子技能。
> 子技能通过Hermes技能加载机制自动发现，无需显式调用。

## 子技能

- `agent-orchestration-harness`
- `debugging-hermes-tui-commands`
- `embedded-python-modularization`
- `eye-tracking-platform`
- `github-agent-contributions`
- `k230-canmv-debugging`
- `node-inspect-debugger`
- `open-source-community-building`
- `plan`
- `python-debugpy`
- `requesting-code-review`
- `spike`
- `subagent-driven-development`
- `systematic-debugging`
- `test-driven-development`
- `writing-plans`

## 调试参考

- `references/codex-vllm-debugging.md` — Codex CLI 调用本地 vLLM 的完整调试记录与结论（硬编码限制、shim 测试、清理决策）
- `references/opencode-model-routing.md` — opencode 多模型路由配置、API key 注入陷阱、Hermes vs opencode 路由差异
- `references/opencode-chinese-input.md` — OpenCode 中文输入问题诊断（GTK_IM_MODULE fcitx vs fcitx5、PTY 模式限制）

## 使用方式

直接调用子技能名称即可：

```
skill_view(name='agent-orchestration-harness')  # 加载第一个子技能
```

父级SKILL.md仅作为目录索引，实际执行由子技能完成。
