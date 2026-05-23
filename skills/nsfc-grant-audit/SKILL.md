---
name: nsfc-grant-audit
description: "Review, critique, and reconstruct Chinese scientific grant proposals — NSFC (国家自然科学基金), provincial (省科技厅), and municipal (市科技局) levels. Covers 青年/面上/重点 and local government projects. 8-dimension review matrix, literature gap analysis, OA PDF download, and NotebookLM project population."
version: 1.0.0
author: Synthos Agent
license: MIT
metadata:
  synthos_atom_type: "extended_skill"
  synthos_version: "1.0.0"
  synthos_skill_md_hash: "nsfc-grant-audit-v1.0.0"
  synthos_model_tested_on: "2026-05-13T00:00:00Z"
  synthos_io_contract_ref: "references/IO_CONTRACT.md"
  synthos_asserted_compliance: "P0,P2"
  synthos_depends_on: "pubmed, semantic-scholar, research-paper-search, notebooklm-cli"
  synthos_data_access_level: "raw"
  synthos_author: "Hermes Agent → Synthos absorption (2026-05-13)"
allowed-tools: terminal web Read Write skill_view delegate_task
---

# NSFC Grant Audit & Reconstruction (Synthos 吸收版)

## 原理层·文言

『评审之道，九维可量。科学性为骨，创新性为魂，可行性为肉，团队为脉，平台为基。』

## 方法层·白话

> [吸收自] Hermes Agent skill: `nsfc-grant-audit` (v1.0.0)
> 吸收日期: 2026-05-13 | 吸收方式: 直接复制 + Synthos 前导标准化
> 定位: Synthos extended skill — 基金标书评审与重构

## 触发条件

加载此技能当用户：
- 请求评审/批判一份 NSFC 风格或省/市科技项目的基金标书
- 希望从笔记或大纲重构一份完整的申请书
- 发送一份可行性分析报告要评估
- 需要对标书做文献增强（替换弱引用、补充缺失数据引用）

## 工作流

### Phase 1: 文档接收

1. 通读整个标书（直接读文件或用 NotebookLM）
2. 如果使用 NotebookLM: `notebooklm metadata`, `notebooklm summary`, `notebooklm source list`, `notebooklm note list`, 然后分短问题多轮 `notebooklm ask`
3. 总结: 标题、研究主题、来源数量、结构

### Phase 2: 8维评审矩阵

每个维度评分 1-10，附带具体评语：

| # | 维度 | 检查要点 |
|---|------|---------|
| 1 | 立项依据 | 科学问题清晰度、文献综述深度、临床需求→机制的逻辑链 |
| 2 | 研究内容 | 完整性、与科学问题的对齐度、亚型特异性 |
| 3 | 技术路线 | 可行性、过拟合风险、多模态融合策略、验证方案 |
| 4 | 创新性 | 从"工程创新"重新定位为"病理机制创新" |
| 5 | 研究基础 | 团队专长、与项目的相关性、前期工作链接 |
| 6 | 预期成果 | 必须多维：数据集+技术/IP+学术产出 |
| 7 | 预算与进度 | 预算须匹配NSFC标准（青年~30万, 面上~50万） |
| 8 | 其他 | 风险评估、伦理、可视化、参考文献格式 |

详见 `references/grant-review-dimensions.md`。

### Phase 3: 文献差距分析

对标书引用的每篇文献做4型分类（Direct / Tangential / Weak / Irrelevant），识别缺失引用的数据点，搜索替换文献。

详见 `references/literature-gap-analysis.md`。

### Phase 3.5: OA PDF下载

尝试下载替换/新增文献的全文PDF：

| 来源 | 成功率 | 方法 |
|:-----|:------:|:-----|
| BioMedCentral/BMC | ✅ ~100% | `/counter/pdf/`URL模式 |
| Frontiers | ✅ ~100% | 直接PDF URL |
| MDPI/Springer/Wiley/Elsevier | ❌ 403 | 回退到PubMed摘要 |

详见 `references/oa-pdf-download.md`。

### Phase 3.6: NotebookLM项目填充

```
notebooklm create "项目名+评估"
notebooklm source add 01_原始标书.docx
notebooklm source add 02_评估报告.md
notebooklm source add 03_文献增强包.md
...
notebooklm source add N_AuthorYear_Paper.pdf
```

### Phase 4: 交付物

1. 评审意见书 — 打分、详细、可操作
2. 重构申请书 — 逐节改写

## 参考文件

- `references/grant-review-dimensions.md` — 8维评分细则
- `references/literature-gap-analysis.md` — 引用差距分析方法论（2026-05-13在PD误吸标书上验证）
- `references/oa-pdf-download.md` — OA PDF下载技术
- `references/nsfc-budget-templates.md` — NSFC预算模板（注意：市级科技局项目预算可能低至1万元，属正常范围）
- `references/notebooklm-review-workflow.md` — NotebookLM集成工作流

## 验证清单

在执行此技能前，请确认以下条件已满足：

- [ ] 输入：一份完整的基金标书（NSFC/省科技厅/市科技局级别），格式为 PDF、DOCX 或 Markdown
- [ ] 输入：已明确标书的资助来源和预算级别
- [ ] 工具可用：terminal（用于文献搜索和 PDF 下载）、Read（读取标书文件）、Write（输出评审报告）
- [ ] 依赖技能可用：pubmed、semantic-scholar、research-paper-search、notebooklm-cli
- [ ] 数据访问级别：raw（允许原文引用和引用文献全文下载）
- [ ] 前置条件：如使用 NotebookLM，确保 NotebookLM CLI 已配置

## 已知陷阱

- ⚠️ **经费级别检测**：先确认项目来源。NSFC面上项目~50万，青年~30万。**市级科技局项目预算可能低至1万元**，这是正常的，不是错误。根据经费调整样本量和方法学范围。
- **成果厚度不足**："1-2篇论文"对300例前瞻性队列不够，应扩展为数据集+技术/IP+学术多维产出。
- **评估工具与结局不匹配**：参考 `references/measurement-tool-adequacy.md` 检查提案所用的测量工具能否真正捕获其声称的结局变量。这是最常见的隐性缺陷。
- **先用PubMed搜索验证后断定**：当怀疑标书的测量工具不充分时，先用 `pubmed` 技能搜索该工具在目标人群中的诊断准确性文献，不要仅凭直觉下结论。

## 变更日志
2026-05-13: v1.0.0 — 从 Hermes Agent 吸收为 Synthos extended skill。
  吸收内容: 完整的8维评审矩阵 + 文献差距分析 + OA PDF下载 + NotebookLM集成
  验证: 已在PD误吸风险预测模型标书上通过实测算例验证（2026-05-13）

## 命令层·English

### Quick Start
- **Load**: Activate when user submits an NSFC/provincial/municipal grant proposal for review or reconstruction.
- **Trigger Keywords**: grant review, NSFC, 国自然, 基金标书, proposal critique, literature gap analysis, proposal reconstruction.
- **Core Workflow**:
  1. **Phase 1 — Document Intake**: Read proposal (direct or via NotebookLM); summarize title, topic, source count, structure.
  2. **Phase 2 — 8-Dimension Review Matrix**: Score 1-10 per dimension (Scientific Basis, Content, Technical Route, Innovation, Team Foundation, Expected Outputs, Budget & Schedule, Other). Provide specific comments.
  3. **Phase 3 — Literature Gap Analysis**: Classify each citation as Direct/Tangential/Weak/Irrelevant; find replacement references; attempt OA PDF download.
  4. **Phase 3.6 — NotebookLM Population**: Create project, add proposal + review + literature enhancement as sources.
  5. **Phase 4 — Deliverables**: Review report (scored, detailed, actionable) + reconstructed proposal (section-by-section rewrite).
- **Depends On**: `pubmed`, `semantic-scholar`, `research-paper-search`, `notebooklm-cli`.
- **Known Pitfalls**: Check budget level first (municipal can be as low as 10K RMB); expand thin output sections; verify measurement tools against claimed outcomes via PubMed.
- **Checklist**: Run all 6 verification items before starting.
