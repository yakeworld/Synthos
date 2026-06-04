---
name: autonomous-core-researcher
description: v3.0 开放边界引擎。无方向约束——预测类/公开数据集/数学建模/仿真/算法类。NotebookLM + OpenAlex + 六维假说评分 → 综述/实验/算法。
allowed-tools: terminal skill_view opencode cron job
metadata:
  synthos:
    version: 2.5.0
    author: Synthos
    signature: 'input: dict -> output: dict'
---

# Autonomous Core Researcher

> 动灵在内，不假外求。非其域不研，非其空不填。

## 范式变更（v4 — Hermes Agent 执行）

| 旧范式 (v3 — OpenCode) | 新范式 (v4 — Hermes Agent) |
|:-----------------------|:---------------------------|
| no_agent脚本后台 | cron prompt + skills — Hermes 直接执行 |
| Python pip安装 | 纯skill + curl — 无需pip |
| 功能测试需人工 | Self-hosted agent自带测试环境 |
| 需判断启动条件 | cron无条件触发，agent自行判断是否可执行 |

## 工作流

```
cron 触发
  ↓
Step 1: 环境检查（skills加载状态、NotebookLM可用性、论文库状态）
  ↓
Step 2: 探测新方向（OpenAlex/arXiv）
  ├── 候选研究方向评分（6维）
  └── NotebookLM不可用时用delegate_task做六维评审
  ↓
Step 3: 追踪项目（absorption-tracked.json状态更新）
  ↓
Step 4: 执行研究（paper-pipeline → 综述/实验/算法）
  ↓
Step 5: 结果记录 + 状态保存
```

详细步骤见 `references/researcher-workflow-steps.md`。

## 六维研究方向评分

| 维度 | 评分(1-5) | 说明 |
|:-----|:---------:|:-----|
| 新颖性 | 1-5 | 领域空白度 |
| 可行性 | 1-5 | 数据和计算资源要求 |
| 影响力 | 1-5 | 潜在引用和应用 |
| 匹配度 | 1-5 | Synthos现有能力匹配 |
| 可持续性 | 1-5 | 可做系列研究 |
| 时效性 | 1-5 | 当前关注度 |

总分≥24 → 立即启动；18-23 → 加入候选列表；<18 → 推迟

## Cron配置

```bash
hermes cronjob create \
  --name "autonomous-researcher" \
  --prompt "Run autonomous-core-researcher workflow" \
  --schedule "every 6h" \
  --skills autonomous-core-researcher \
  --enabled-toolsets terminal,file,web,search,skills
```

## 已知限制

- NotebookLM不可用时: 六维评分用delegate_task代替
- 批量论文产出需触发paper-pipeline
- OpenAlex API有速率限制，搜索间隔≥1s

## 参考文件

- `references/researcher-workflow-steps.md` — 完整5步工作流
- `references/six-dimension-scoring.md` — 六维评分详细协议
- `references/cron-paper-creation-pattern.md` — Cron论文创建模式
