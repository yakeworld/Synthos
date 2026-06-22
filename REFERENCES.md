# References — 外部项目吸收与引用

> **不搬不抄，取法乎上。动灵在内，不假外求。**
>
> Synthos 对以下项目进行了方法论层面的学习与吸收。所有吸收都经过五层验证（思想→规范→规律→能力→任务），以 Synthos 原生三语体系（文言→白话→英文）重新表达。
>
> 没有一行代码被逐字复制。每个吸收项的来源、许可证和注入目标均有记录。

---

## ✅ 已完成吸收注入

| # | 项目 | ⭐ | 许可证 | 吸收了什么 | 注入目标 |
|:-:|:-----|:-:|:-------|:------------|:---------|
| 1 | [AutoResearchClaw](https://github.com/aiming-lab/AutoResearchClaw) | 12k | MIT | 引用验证四层架构、LaTeX 输出模板 | `knowledge-acquisition`, `latex-output` |
| 2 | [ARS / Academic-Research-Skills](https://github.com/Imbad0202/academic-research-skills) | 6.3k | CC BY-NC 4.0 | 反谄媚门控、5类幻觉分类法、数据访问分级P6、进化引擎PROBE | `viewpoint-verification`, `CONSTITUTION.md`, `evolution` |
| 3 | [OpenClaw](https://github.com/openclaw/openclaw) | 376k | MIT | 57个技能合并入库，51个新技能归一化导入 | Synthos 技能目录 |
| 4 | [STORM](https://github.com/stanford-oval/STORM) | 28k | MIT | 多视角角色生成协议、知识策展流水线 | `ACQ→EXT→ASC` 原子链 |
| 5 | [scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | 21k | MIT | 78个数据库查找模式（纯API调用） | `EXT` 数据访问 |
| 6 | [AI-Research-SKILLs](https://github.com/Orchestra-Research/AI-research-SKILLs) | 8.4k | MIT | 双循环编排协议、ARA Compiler | `ROUTE+HYP+VER` |
| 7 | [patent-disclosure-skill](https://github.com/handsomestWei/patent-disclosure-skill) | — | Apache-2.0 | 专利点挖掘、技术揭示书模板、CNIPA查新 | `patent-disclosure` |
| 8 | [nature-paper2ppt](https://github.com/GARCH-QUANT/garch-nature-paper2ppt) | 1 | MIT | Figure-first PPTX布局规则、论文类型→演示逻辑 | `nature-paper2ppt` |
| 9 | [PaperSpine V2](https://github.com/WUBING2023/PaperSpine) | — | MIT | Writing Rationale Matrix、Motivation-First写作门 | `paper-workflow` |
| 10 | [autoresearch (karpathy)](https://github.com/karpathy/autoresearch) | 18k | MIT | 自动研究循环概念 | `research-ideation` |
| 11 | [GenericAgent](https://github.com/lsdefine/GenericAgent) | 12k | MIT | 事后技能结晶、种子→树增长模式 | `evolution` |

## 🔶 仅方法论 / 思想参考（无代码注入）

| # | 项目 | ⭐ | 许可证 | 参考了什么 |
|:-:|:-----|:-:|:-------|:------------|
| 12 | [Claude Code](https://github.com/anthropics/claude-code) | 123k | Proprietary | Hook事件规范(8种)、触发条件+验证清单、哲学免疫系统、Karma moderation、Assertion-based reliability |
| 13 | [ARIS](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep) | 9.3k | 未标注 | Cross-model adversarial review、Research Wiki 持久知识库、13个命名工作流(W1-W6) |
| 14 | [autocontext](https://github.com/greyhaven-ai/autocontext) | 1.1k | Apache-2.0 | improvement_loop_policy(3次成功→自动结晶)、knowledge_inheritance_contract、trace_continuity |
| 15 | [PaperDebugger](https://github.com/PaperDebugger/paperdebugger) | 1.5k | AGPL-3.0 | Conference-style structured review、section-level review、verify_citations机制 |
| 16 | [Agent4S](https://arxiv.org/abs/2506.23692) (arXiv论文) | — | arXiv | 5级层级理论框架(LLM科研自动化)、Context Engineering概念 |
| 17 | [hermes-agent-self-evolution](https://github.com/NousResearch/hermes-agent-self-evolution) | 3.4k | MIT | GEPA (Genetic-Pareto Evolution)、轨迹→失败归因方法论 |

## 👀 已分析，待吸收候选

| 项目 | ⭐ | 备选原因 | 状态 |
|:-----|:-:|:---------|:-----|
| [RD-Agent](https://github.com/microsoft/RD-Agent) (微软) | 13k | 量化/Kaggle自动化 | 范型不兼容，暂缓 |
| [AI-Scientist](https://github.com/SakanaAI/AI-Scientist) (Sakana) | 13.5k | 端到端论文自动化 | gap-fit 弱 |
| [AI-Scientist-v2](https://github.com/SakanaAI/AI-Scientist-v2) (Sakana) | 8k | BFTS 树搜索 | P1 待评估 |
| [DeepScientist](https://github.com/ResearAI/DeepScientist) | 800 | Findings Memory + 贝叶斯优化 | P1 待评估 |
| [PaperQA2](https://github.com/Future-House/paper-qa) | 10k | 科学RAG高精度 | 追踪中 |
| [gpt-researcher](https://github.com/assafelovic/gpt-researcher) | 27k | Deep research | 追踪中 |
| [ChatPaper](https://github.com/kaixindelele/ChatPaper) | 13k | arXiv摘要 | 追踪中 |
| [PaperBanana](https://github.com/dwzhu-pku/PaperBanana) | 200 | 多Agent图表生成 | P2 待评估 |

## 🔄 自我反射（从自身经验提炼）

| 技能 | 来源 | 说明 |
|:-----|:-----|:-----|
| `reflexive-abstraction` | 竞赛项目工作区搭建经验 | 从操作经验→通用技能的方法论 |
| `project-experience-distillation` | 多次项目经验积累 | 项目经验→技能提炼的通用流程 |

---

> 完整机器可读台账：`absorption-ledger.json`
> 各项目详细吸收记录见 `skills/.../evolution/absorption-*.md` 和 `skills/.../skill-absorption/references/*`
> 最后更新：2026-06-23
