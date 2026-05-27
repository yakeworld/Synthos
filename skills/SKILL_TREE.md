# Synthos 技能树 v4.0 — 纯技能驱动架构

> 最后更新: 2026-05-23 | 架构: pure_skill_driven_zero_python
> 所有原子均通过 SKILL.md 加载并由 Agent 直接执行，零 Python 依赖。

## 架构概览

```
                     ┌──────────────────────────┐
                     │  Layer 0: 任务编排 (Router) │
                     │  task-router SKILL.md      │
                     │  structural_score=1.0  ✅ │
                     └────────────┬─────────────┘
                                  │
            ┌─────────────────────┼─────────────────────┐
            ▼                     ▼                     ▼
┌────────────────────┐ ┌──────────────────┐ ┌────────────────────┐
│ Layer 1: 知识获取   │ │ Layer 2: 知识提取  │ │ Layer 3: 关联发现   │
│ knowledge-acquisition││ knowledge-extraction││ association-discovery│
│ structural=1.0 ✅   │ │ structural=1.0 ✅  │ │ structural=1.0 ✅  │
│ API health=healthy  │ │ golden=3 cases    │ │ golden=4 cases     │
│ golden=5 cases      │ │ refs=5 files      │ │ refs=4 files       │
│ refs=5 files        │ └────────┬──────────┘ │ refs=4 files       │
└────────┬────────────┘          │            └────────┬───────────┘
         │                      │                      │
         └──────────────────────┼──────────────────────┘
                                ▼
                     ┌──────────────────────────┐
                     │ Layer 4: 科学假设生成      │
                     │ hypothesis-generation     │
                     │ structural=1.0 ✅         │
                     │ golden=5 cases            │
                     │ refs=4 files              │
                     └────────────┬──────────────┘
                                  │
                 ┌────────────────┼────────────────┐
                 ▼                                 ▼
    ┌──────────────────────┐         ┌──────────────────────┐
    │ Layer 5: 论证表达     │         │ Layer 5: 观点验证     │
    │ argument-expression  │         │ viewpoint-verification│
    │ structural=1.0 ✅    │         │ structural=1.0 ✅     │
    │ golden=5 cases       │         │ golden=4 cases        │
    │ refs=5 files         │         │ refs=6 files          │
    └──────────────────────┘         └──────────────────────┘
```

## 7 核心认知原子

| 层级 | 原子名 | 类型 | 结构分 | Golden | 参考文件 | 依赖 |
|:-----|:-------|:-----|:------:|:------:|:--------:|:-----|
| 0 (路由) | task-router | router | 1.0 | 5 cases | 4 files | ACQ, EXT, ASC, HYP, ARG, VER |
| 1 (获取) | knowledge-acquisition | cognitive | 1.0 | 5 cases | 5 files | 外部API |
| 2 (提取) | knowledge-extraction | cognitive | 1.0 | 3 cases | 5 files | ACQ |
| 3 (关联) | association-discovery | cognitive | 1.0 | 4 cases | 4 files | EXT |
| 4 (假设) | hypothesis-generation | cognitive | 1.0 | 5 cases | 4 files | EXT, ASC |
| 5 (论证) | argument-expression | cognitive | 1.0 | 5 cases | 5 files | HYP, ACQ |
| 5 (验证) | viewpoint-verification | cognitive | 1.0 | 4 cases | 6 files | HYP, ARG |

## 扩展技能

| 技能名 | 用途 | 来源 | 
|:-------|:-----|:-----|
| paper-workflow | 论文写作管线 | Synthos原创 |
| patent-disclosure | 专利交底书生成 | 外部吸收(AKNE) |
| nsfc-grant-audit | 课题评审 | 外部吸收 |
| latex-output | LaTeX输出 | 外部吸收 |
| figure-generation | 科技图表 | 外部吸收(Nature) |
| scientific-database-lookup | 科学数据库统一路由 | 外部吸收(K-Dense) |
| nature-paper2ppt | Nature论文→PPT | 外部吸收(GARCH-QUANT) |
| bppv-expert | BPPV医学知识 | 吸收(yakeworld/AKNE) |
| research-thinking-framework | 研究方法论 | 吸收(yakeworld/AKNE) |
| research-ideation | 研究方向构思 | Synthos原创 |
| experiment-recipes | 实验设计配方 | Synthos原创 |

## DAG 依赖关系

```
ACQ (知识获取) ──→ EXT (知识提取) ──→ ASC (关联发现) ──→ HYP (假设生成) ──┬──→ ARG (论证表达)
                                                                           └──→ VER (观点验证)
```

- **ACQ**: 无上游，下游为 EXT、ASC（直接供给）
- **EXT**: 上游 ACQ，下游 ASC
- **ASC**: 上游 EXT，下游 HYP（含 GAP 空白发现功能）
- **HYP**: 上游 EXT+ASC，下游 ARG、VER
- **ARG**: 上游 HYP+ACQ（可回取原文），下游无
- **VER**: 上游 HYP+ARG（同时需要假设和论证），下游无

## Synthos 八维覆盖

| 维度 | 覆盖原子 | 评分(原) | 评分(当前) |
|:-----|:---------|:--------:|:----------:|
| 第一性原理 | ACQ, EXT, HYP, ARG | 95% | 95% |
| 系统思维 | ACQ, ASC, ARG | 95% | 95% |
| 贝叶斯思维 | HYP, VER | 90% | 90% |
| 类比 | HYP | 70% | 80% |
| 奥卡姆剃刀 | EXT, ARG, ROUTE | 80% | 85% |
| 证伪主义 | VER | 70% | 85% |
| 模型依赖实在论 | ASC | 50% | 55% |
| 自由能原理 | VER | 40% | 55% |
| **综合** | | **75%** | **85%** |

## 吸收里程碑

| 日期 | 来源 | 评分 | 类型 |
|:----|:-----|:----:|:-----|
| 2026-05-18 | K-Dense/scientific-agent-skills ⭐23K | 4.0 | 扩展技能 |
| 2026-05-18 | Orchestra-Research/AI-research-SKILLs (双循环) | 4.3 | 核心增强 |
| 2026-05-17 | Orchestra-Research/AI-research-SKILLs (ARA 6D) | 4.5 | 核心增强 |
| 2026-05-17 | SkyworkAI/DeepResearchAgent ⭐3.4K (SEPL) | 4.2 | 核心增强 |
| 2026-05-14 | PaperOrchestra/PaperWritingBench (PW-Bench) | 4.0 | 能力增强 |
| 2026-05-13 | Imbad0202/academic-research-skills ⭐6.4K | 4.5 | 能力增强 |
| 2026-05-12 | AKNE (yakeworld/.knowledge/) | 4.0 | 扩展知识 |
| 2026-05-11 | Yuan1z0825/nature-skills (Nature图表) | 4.5 | 扩展技能 |

## 外部吸收候选

| 项目 | ⭐ | 评分 | 状态 | 吸收潜力 |
|:-----|:--:|:----:|:----:|:---------|
| 724-office (wangziqi06) | 1,028 | 4.0 | tracking | 自进化修正机制(nudge/circuit breaker) |
| DATAGEN (starpig1129) | 1,736 | 4.0 | tracking | 假设生成引擎方法论 |
| EvoMap/awesome-agent-evolution | 124 | 3.0 | tracking | 进化资源列表 |
| gpt-researcher (assafelovic) | 27,000 | 3.5 | tracking | 通用研究助手 |
| RD-Agent (Microsoft) | 13,000 | 3.8 | tracking | 研究驱动开发 |
| khoj (khoj-ai) | 34,000 | 3.0 | tracking | 个人AI研究助手 |
| PaperForge (QJHWC) | 554 | 4.0 | tracking | 论文生成 |
| ResearcherSkill (krzysztofdudek) | 218 | 5.0 | evaluating | 科研技能方法论 |

## 统计

| 指标 | 值 |
|:-----|:---:|
| 核心原子 | 7 (路由器+6认知) |
| 扩展技能 | 12 |
| 吸收来源 | 10 |
| Golden用例总数 | 31 |
| 参考文件总数 | 34 |
| 结构分均值 | 1.0 |
| 基准通过率 | 100% |
| 综合健康分 | 0.97 (EXCELLENT) |
| 最新进化周期 | Cycle 44 |

## 架构原则

- **Zero Python**: 所有原子通过 Agent 加载 SKILL.md 执行
- **Pure Skill-Driven**: Agent 是运行时的编排者
- **Minimal Overlap**: 原子边界精确，功能不重叠
- **Self-Documenting**: 每个原子有完整的 frontmatter + IO契约 + 金标准
