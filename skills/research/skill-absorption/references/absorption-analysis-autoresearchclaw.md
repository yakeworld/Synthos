# AutoResearchClaw 吸收分析 — 完整案例

**项目**: [aiming-lab/AutoResearchClaw](https://github.com/aiming-lab/AutoResearchClaw)  
**Stars**: 12,038 ⭐ | **语言**: Python | **许可证**: MIT  
**描述**: Fully autonomous & self-evolving research from idea to paper (23-stage pipeline)

## 勘查摘要

AutoResearchClaw 是当前 GitHub 上最热门的自主科研系统（12k⭐），
其 23 阶段流水线涵盖从想法到论文的全流程。与 Synthos 对比：

| 维度 | Synthos (v4.2) | AutoResearchClaw (v0.4) |
|------|---------------|------------------------|
| 架构 | 纯SKILL.md，零Python | Python流水线，23阶段 |
| 执行模型 | Agent原生推理 | Python编排+LLM调用 |
| 知识获取 | 3源(S2+PubMed+OpenAlex) | 3源(OpenAlex+S2+arXiv) |
| 技能吸收 | 内置进化引擎+吸收工作流 | MetaClaw跨运行学习 |
| 记忆系统 | evolution-state.json | 3类记忆(观念/实验/写作) |
| 引用验证 | 新增4层验证(本吸收) | 4层验证(arXiv→CrossRef→S2→LLM) |
| 多智能体辩论 | 无 | 假设生成/结果分析/同行评审 |
| 输出格式 | JSON+Markdown | LaTeX(NeurIPS/ICLR/ICML)+PDF |

## 可吸收项（评分后）

| 优先级 | 特性 | 评分 | 集成成本 | 状态 |
|--------|------|------|---------|------|
| P0 | 引用验证 | 4.8/5 | 低 | ✅ 已吸收 |
| P1 | LaTeX输出 | 4.5/5 | 低 | ✅ 已吸收 |
| P2 | 结构化知识库(6类KB) | 4.0/5 | 低 | ⏳ 待提议 |
| P3 | Lesson进化增强 | 3.8/5 | 中 | ⏳ 待提议 |
| P4 | 新颖性检查 | 3.5/5 | 中 | ⏳ 待提议 |
| 不可吸收 | Docker沙箱/图表生成/Python编排 | — | 高 | 架构不兼容 |

## 实施记录

1. **引用验证** (2026-05-11):
   - 吸收 `literature/verify.py` 的4层验证架构
   - 创建 `references/CITATION_VERIFICATION.md`
   - 修改 `knowledge-acquisition/SKILL.md` 新增 Step 2.5
   - 验证: L1 DOI(Crossref)=200, L3 S2标题搜索=3篇匹配

2. **LaTeX输出** (2026-05-11):
   - 吸收 `templates/conference.py` + `converter.py` 的模板设计
   - 创建新技能 `latex-output/` (SKILL.md + 2 reference文件)
   - 支持 NeurIPS/ICLR/ICML + 中文期刊格式
   - 验证: 生成 paper.tex(3.3KB) + references.bib(3条目) + build.sh
