# Synthos SCI 论文 — 对照分析与文献综述

> 用途: 论文 Related Work 和对比表的数据源。37项目对比矩阵 + 功能维度分析。
> 完整文档: `/media/yakeworld/sda2/Synthos/outputs/synthos-sci-paper-analysis.md`

## 精选15强对照

| 排名 | 项目 | ⭐ | 类别 | 与Synthos的关系 |
|:----:|:-----|:-:|:-----|:----------------|
| 1 | Sakana AI Scientist | 13,548 | 全自动科研 | 端到端论文生成，但Python-heavy |
| 2 | gpt-researcher | 27,000 | 研究助手 | 多源搜索，无进化引擎 |
| 3 | AutoGen | 57,916 | 多Agent协作 | 对话式框架，无认知架构 |
| 4 | DATAGEN | 1,736 | 假设生成 | AI驱动假设生成+分析 |
| 5 | PaperForge | 554 | 论文生成 | 端到端从idea到LaTeX |
| 6 | NanoResearch | 979 | Agent技能 | 模块化技能生态系统 |
| 7 | ResearcherSkill | 218 | 单一技能 | skill.md+codex集成 |
| 8 | Kosmos | 510 | AI科学家 | 自主发现+实验设计 |
| 9 | Mimosa-AI | 22 | 自进化 | MCP+达尔文进化 |
| 10 | SkillWeaver | 123 | 技能综合 | 环境探索→技能合成 |
| 11 | SkillLens | 57 | 技能评估 | Rubric评分+审查 |
| 12 | BioAgents | 152 | 多Agent科学 | 专业Agent分工 |
| 13 | ADM-3 Discovery | 3 | 假设闭环 | 迭代实验设计 |
| 14 | 724-office | 1,028 | 自进化Agent | Nudge+Circuit breaker |
| 15 | hermes-agent-self-evolution | 3,446 | 自进化 | [已吸收] GEPA方法论 |

## Synthos独有创新点

| 创新点 | 说明 | 无竞品实现 |
|:-------|:-----|:-----------|
| 纯SKILL.md驱动（零Python） | Agent即运行时 | 全部Python-heavy |
| 7认知原子+DAG | 严格认知管道 | 线性或对话式 |
| 自进化引擎 v2.12 | 12步循环+反射式分析 | 无自进化 |
| 宪法P0-P6+哲学免疫 | 可执行约束+漂移检测 | 无 |
| 三语层级（文言/白话/英文） | 认知语言学 | 无 |

## 九维功能对比

| 维度 | Synthos | Sakana | AutoGen | GPT-Res. | DATAGEN |
|:-----|:-------:|:------:|:-------:|:--------:|:-------:|
| 纯SKILL驱动 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 认知原子+DAG | ✅ | ❌ | ❌ | ❌ | ❌ |
| 自进化引擎 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 宪法约束 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 漂移检测 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 反射式分析 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 多源检索 | ✅ | ❌ | ❌ | ✅ | ❌ |
| 引用验证 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 多模式执行 | ✅ | ❌ | ✅ | ❌ | ❌ |
| 吸收管线 | ✅ | ❌ | ❌ | ❌ | ❌ |

## 已吸收项目

| 项目 | 评分 | 吸收内容 |
|:-----|:----:|:---------|
| AutoResearchClaw ⭐12K | 4.5 | 4层引用验证 + LaTeX |
| AI-research-SKILLs ⭐8.5K | 4.3 | 6D认识论评分 + 双循环 |
| DeepResearchAgent ⭐3.4K | 4.2 | SEPL回滚机制 |
| hermes-agent-self-evolution ⭐3.4K | **4.8** | GEPA反射式分析+自动数据集+Pareto |
| KILO-KIT ⭐24 | 5.0 | 可组合行为单元 |
