---
name: project-experience-distillation
description: '⚡P0 从项目/论文经验到可复用skill — 提取模式/设计原则/陷阱。被 paper-pipeline P6 阶段调用。'
license: MIT
allowed-tools:
- terminal
- read_file
- write_file
- patch
metadata:
  synthos:
    version: 2.0.0
    priority: P0
    author: Synthos
    signature: 'paper_name: str -> skills_patched: list[str]'
---

# Project Experience Distillation (P6)

## 核心理念（文言）

**文以验法，技乃所产** — 论文不是终极目标，可复用的技能才是系统真正产出。
**投完不弃，检之改之** — 投稿后仍可自检修订、提炼模式。

## 触发条件

论文通过双质检（T2 或以上）后，P6 强制执行。在 `paper-pipeline` 中调用。

## P6 流程

```
P6入口: 论文通过质量门 (calibrated ≥ 0.80 或 T2+)
  ↓
Step 1: 阅读质量报告
    读取 07-quality/quality-report.md (或 quality-report.md)
    找出: (a) 最低分维度及修复方案
          (b) Layer B (Gemini) 的 actionable fixes
          (c) 独特的审稿反馈模式
  ↓
Step 2: 提炼可复用模式
    从质检报告中提取能推广到其他论文的经验:
    - 常见弱项 → Patch: 哪个 skill 最相关?
    - 审稿人关注点 → Patch: 审稿对应的 skill
    - 特殊技法/工具用法 → Patch/Add: 对应的 infrastructure skill
  ↓
Step 3: 执行 patch
    按优先级选择目标:
    (a) quality-gate — 质检弱项模式
    (b) paper-pipeline — 管线步骤/陷阱
    (c) notebooklm-cli — 知识提取方法
    (d) 其他 domain-specific skill
  ↓
Step 4: 更新 agent-tracker
    - 在 notes 中记录 P6 产出
    - 标记 P6 完成
  ↓
Step 5: 记录进化
    - 向 evolution 输出: 新模式、patch 列表、评估周期
```

## 常见提炼模式

### 模式 A: 质检弱项 → 质量门

来自 Layer B Gemini 评审的弱点模式，通常有跨论文共性：

| 弱项 | 典型初始分 | 常见原因 | 修复方案 | 推至 |
|:-----|:---------:|:---------|:---------|:----:|
| D2 方法学 | 0.75 | 仅理论/仿真，缺临床验证 | 加算法伪代码/形式化推导 | 0.78 |
| D3 结果可信度 | 0.70-0.75 | 量化声明来自外推/仿真 | +MC验证/敏感性分析/数据来源标注 | 0.75-0.77 |
| D4 完整性 | 0.75 | 缺 PRISMA 引用/Supplementary表 | +PRISMA 2020 TikZ流程图+Page2021引用 | 0.85 |
| D7 引用质量 | 0.75-0.80 | 部分 bib 未引用/格式化瑕疵 | 逐篇引用+标记核心纳入研究 | 0.85 |

### 模式 B: 工作流改进 → 管线 skill

- 编译链优化 → `paper-pipeline` 的编译部分
- 参考文献管理 → `research-paper-search` 或 `pdf-download-racing`

### 模式 C: 工具技法 → infrastructure skill

- API 使用技巧 → 对应的工具 skill
- CLI 参数/陷阱 → 对应 CLI skill

## 参考文件

- `references/*.md` — 历史 P6 提取记录
