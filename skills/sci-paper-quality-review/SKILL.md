---
name: sci-paper-quality-review
description: >-
  论文7维SCI质量评审：科学贡献/方法学严谨性/结果可信度/完整性/清晰性/新颖性/引用质量。
  期刊感知门(T1-T4)：avg<阈值自动修订循环。反模拟铁律：评分基于实际读到的论文内容。
version: 1.10.0
author: Synthos
license: MIT
priority: P1
related_skills: [quality-gate, evolution, paper-pipeline, project-experience-distillation]
execution_rule: >-
  Run AFTER pipeline G7 passes. 反模拟：所有评分基于read_file实际论文内容。
  每维评分附证据引用。avg<目标期刊阈值则自动触发修订循环。
  双质量检查铁律：P2完成后自动触发本地7维+NotebookLM Gemini7维，校准分=两方最低分。
references:
  dual-quality-check-protocol.md: 双质量检查完整协议
  sci-quality-rubric.md: 7维评分细则
  revision-cycle-example.md: 修订循环示例
  self-citation-audit.md: 自引率检测协议
  experimental-verification-protocol.md: 实验验证协议(EVP)
  system-paper-metric-verification.md: 系统论文指标验证
  protocol-paper-revision-pattern.md: 协议类论文修订模式
metadata:
  synthos:
    priority: P1
    atom_type: pipeline
    description: 7-dim SCI paper quality review — structural contribution/methodology/results/integrity/novelty/citation.
    signature: |
      paper: str, quality_matrix: dict -> review_result: dict | review_result: dict (scores: [D1-D7], overall_score)
    related_skills: ['quality-gate', 'evolution', 'paper-pipeline', 'project-experience-distillation']

---

## IO_CONTRACT

- **input**: `paper: str` — 论文标识符（路径或目录名），`quality_matrix: dict` — 质量评审矩阵（目标期刊阈值等）
- **output**: `review_result: dict` — 包含 scores (D1-D7七个维度), overall_score, gaps, revision_plan 的评审结果
- **side_effects**: 更新论文目录下的 quality_review.md，触发修订循环（如需要）

# SCI 论文质量评审技能

## 原理层·文言

> 论文之质，七维可量。
> G1-G7审其行，此技察其文。
> 凡评必核，不核不议。凡数必源，不源不取。
> 分不及则自修，不复问。
> 宁降期不造假，宁退稿不敷衍。

**核心理念**：G1-G7查"论文做得对吗？"——本技能查"论文写得好吗？"前者过程正确，后者结果优秀，二者皆需。

## 触发条件

- 写作管线G7已通过，或P2写作完成
- 用户要求检查论文质量
- **P2完成后自动触发（强制流程，不等用户问）**

## 前置条件

- paper.tex存在且非空
- references.bib ≥30条目
- pdfs/目录≥30有效PDF
- pipeline_trace.json显示G7=pass

---

## 评审7维

### D1 科学贡献

| 分数 | 含义 |
|:---
  io_contract: input: ['paper: str, quality_matrix: dict -> review_result: dict', 'output: ['review_result: dict (scores: [D1-D7], overall_score, improvement_plan)']
-:|:-----|
| 0.0-0.3 | 无新贡献，重复已知 |
| 0.4-0.6 | 增量贡献，有局限 |
| 0.7-0.8 | 新方法/洞察，子领域有价值 |
| 0.9-1.0 | 突破性，可改变范式 |

问：解决了什么gap？比现有工作更好？有量化证据？

### D2 方法学严谨性

| 分数 | 含义 |
|:----:|:-----|
| 0.0-0.3 | 模糊不可复现 |
| 0.4-0.6 | 基本描述缺关键细节 |
| 0.7-0.8 | 清晰，大部分可复现 |
| 0.9-1.0 | 完整+开源代码/数据 |

问：架构充分解释？形式化定义？开源声明？

Revision boosts: 详见 `references/d2-methodology-boost.md`, `references/d2-formal-proof-boost.md`, `references/d2-theory-framework-boost.md`

### D3 结果可信度

**NotebookLM源文件验证**：当pdfs/中PDF不全时，用NotebookLM验证关键引用。
```bash
notebooklm use <project_id>
notebooklm source list
notebooklm source fulltext <source_id> -o /tmp/verify.txt
```

**🔴 系统/架构类论文D3铁律：**
1. 不虚构外部对比数据 — 用真实管线产出替代（项目数/完成率/质量分布/域覆盖）
2. 诚实声明"无同类端到端系统可直接比较"
3. 如果缺失，从上传PDF调研同类论文验证方法论（用NotebookLM问）

| 验证证据 | D3上限 |
|:---------|:------:|
| 只有架构描述+形式化定义 | 0.60 |
| + 内部运行指标(cycles, pass rate) | 0.70 |
| + **真实管线产出质量分布统计** | **0.80** |
| + 外部第三方基准或人类评估 | 0.90+ |

**数据真实性交叉验证（P0）**：
```bash
cd pdfs/ && file *.pdf | grep -v 'PDF document'
du -sh pdfs/
grep -c '\\\\cite{' paper.tex
grep -oP '\\\\\\\\bibitem\{([^}]+)\}' paper.tex | wc -l
```

**🔴 双质检D7铁律**：D7评分前必须上传≥3篇参考文献全文到NotebookLM。无全文则D7=不可信。

### D4 完整性

| 分数 | 含义 |
|:----:|:-----|
| 0.0-0.3 | 缺关键部分 |
| 0.4-0.6 | IMRaD结构不全 |
| 0.7-0.8 | 所有必需部分存在 |
| 0.9-1.0 | 额外补充材料+代码 |

问：IMRaD？实验代码/数据？局限性？伦理声明？

### D5 清晰性

| 分数 | 含义 |
|:----:|:-----|
| 0.0-0.3 | 不可读 |
| 0.4-0.6 | 段落混乱，术语不一致 |
| 0.7-0.8 | 清晰的目标/方法/结论 |
| 0.9-1.0 | 图表达发表级 |

问：摘要独立可读？术语定义？图表自解释？

### D6 新颖性

| 分数 | 含义 |
|:----:|:-----|
| 0.0-0.3 | 完全已知 |
| 0.4-0.6 | 已知方法用于新场景 |
| 0.7-0.8 | 新组合/新洞察 |
| 0.9-1.0 | 全新范式或理论 |

问：本文前该方向状态？反方向论证？

### D7 引用质量

**🔴 关键前置检查：参考PDF存在性**

只有上传了参考PDF，D7的"数值核对"和"引用链检测"才可信。
```bash
notebooklm use <project_id>
notebooklm source list | grep -c pdf
# 如果≥3: D7可信。否则: D7标记为"insufficient_sources"
```

NotebookLM D7工作流：
```bash
notebooklm source add-research --query "comparison OR baseline" --no-wait  # 并行检索
notebooklm ask "List all papers that claim [数值X], verify actual value"
notebooklm ask "Create comparison table between [论文] and [对比论文], note any discrepancies"
```

| 分数 | 含义 |
|:----:|:-----|
| 0.0-0.3 | 引用不足/不相关 |
| 0.4-0.6 | 相关引用但缺关键文献 |
| 0.7-0.8 | 充分覆盖，角度平衡 |
| 0.9-1.0 | 核心引用无遗漏+对比分析 |

特别检查：
- [ ] 所有 `\\cite{}` 有对应 `\\bibitem{}`
- [ ] 被引论文主题与正文上下文匹配
- [ ] 自引率 < 20%
- [ ] 引用最新（近3年占比≥40%）

---

## 期刊感知门

| 期刊层 | 目标avg | 最低维度 | 修订策略 |
|:------:|:-------:|:---------|:---------|
| T1 (Nature/Science/Cell) | ≥0.85 | 无<0.70 | 逐维提升至达标 |
| T2 (Nature子刊/NeurIPS) | ≥0.80 | 无<0.60 | 聚焦最低维 |
| T3 (SCI 1-2区) | ≥0.75 | 无<0.50 | 降维打击 |
| T4 (SCI 3-4区/中文核心) | ≥0.70 | 无<0.40 | 最小改动 |

avg<目标阈值 → 自动触发修订循环（不限次数，有进展一直循环，连续3次无进展降级）。

---

## 双质量检查铁律（强制流程）

P2写作完成后，不等用户问 → **立即自动执行**：

1. **Layer A**: 本地7维评审（本技能）
2. **Layer B**: NotebookLM上传PDF → Gemini 7维评审
3. **校准分** = 两方最低分
4. **校准分 < 阈值** → 自动进入修订循环（不提问）

---

## 验证清单

- [ ] 7维评分全部完成，每维附证据引用
- [ ] D3数源验证通过（PDF文件有效）
- [ ] D7有≥3篇参考PDF全文
- [ ] 校准分计算完成
- [ ] 校准分 ≥ 目标期刊阈值 → 输出报告
- [ ] 校准分 < 目标期刊阈值 → 自动启动修订循环
