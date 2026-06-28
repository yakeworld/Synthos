---

name: journal-selection-medical-ai
description: Systematic methodology for evaluating and ranking SCI journals as publication
version: 1.0.0
  targets for medical AI / computational health papers.
allowed-tools:
- terminal
- read_file
- write_file
- search_files
license: MIT
author: Synthos
metadata:
  hermes:
    tags:
    - Research
    - Journal
    - SCI
    - Publication
    - Medical-AI
    - Computational-Health
    related_skills: []
  synthos:
    author: Hermes Agent
    signature: 'input: dict -> output: dict'
    related_skills:
    - academic-paper-completion
    - adhd-eye-tracking-review
    - arxiv
    - biorxiv
    - blogwatcher
    version: 1.0.0


---


## IO_CONTRACT

- **input**: `paper_topic: str, quality_metrics: dict` — 用户请求描述、上下文信息
- **output**: `journal_recommendations: list — 期刊推荐`


> 对应原则：P2（机械原子暴露输入输出规范）


# Journal Selection for Medical AI Papers

Systematic methodology for evaluating and ranking SCI journals as publication targets for medical AI / computational health papers. Combines metric-based filtering (IF, Q1/Q2, scope) with content-fit analysis (similar papers, topic overlap).

## Trigger

Load when:
- User asks to select a target journal for submitting a manuscript
- User is preparing a paper for submission and needs journal recommendations
- User wants to compare journals in a specific domain (biomedical, clinical AI, bioinformatics)
- Any task involving "where should I publish this" or "which journal is best for X"

## 触发条件

以下任一条件满足时,系统应装载此Skill并进入期刊筛选流程:

1. **期刊推荐请求**
   - 用户明确询问:"帮我推荐期刊""哪个期刊适合投稿""选择目标期刊"等
   - 用户上传/描述论文内容后要求返回候选期刊列表

2. **投稿准备阶段**
   - 用户提及"正在准备投稿""准备提交论文""写 cover letter"等
   - 用户询问"这个水平能投什么期刊"或"该投 Q1 还是 Q2"

3. **期刊对比需求**
   - 用户要求比较两个或多个期刊(IF、审稿周期、接受率、OA费用等)
   - 用户询问"A期刊还是B期刊更适合我这篇文章"

4. **拒稿后策略调整**
   - 用户说"被拒稿了,接下来投哪里""需要备选期刊"
   - 用户反馈审稿意见后要求调整目标期刊

5. **主题匹配询问**
   - 用户询问"XX期刊收医疗AI/计算健康的文章吗"
   - 用户想确认自己的研究主题是否在某个期刊的 scope 内

6. **相关上下文线索**
   - 对话中出现了论文摘要、方法论关键词(CNN, Transformer, survival analysis, medical imaging)、数据集名称(MIMIC, TCGA, BraTS)等,且无当前激活的期刊选择Skill
   - 上一条消息包含"期刊""SCI""IF""Q1"等词语

## Verification Checklist

验证条目,供本Skill执行完毕后自查:

- [ ] 已评估论文质量等级(A-/B+/B)并明确优劣势
- [ ] 已通过PubMed或OpenAlex搜索相似论文并提取候选期刊
- [ ] 已为每个候选期刊获取最新IF、JCR Quartile、出版商、OA状态、DOAJ/CORE信息
- [ ] 已按5项标准(主题匹配30%、质量匹配25%、方法论偏好20%、实际因素15%、先例10%)对候选期刊评分
- [ ] 已将期刊归入TIER 1-4排名体系
- [ ] 已验证目标期刊近期有类似论文发表(近6个月)
- [ ] 已查阅读者指南(字数、图表、参考文献格式、必需章节)
- [ ] 已识别备选/保底期刊
- [ ] 已排除掠夺性期刊(核实Scopus/WoS/DOAJ索引)
- [ ] 已考虑OA版面费及预印本策略(arXiv/bioRxiv)

## Method

### Step 1: Assess Paper Quality

Before selecting journals, objectively grade the paper:

- **Strengths**: Innovation, experimental rigor, result quality, literature support, structure
- **Weaknesses**: Single dataset, missing validation, narrow scope, limited clinical depth
- **Quality Tier**: A- (strong but has flaws), B+ (solid but needs more), B (fundamental gaps)

*Example*: Paper with novel architecture, complete ablation, excellent results, but only one dataset → A-

### Step 2: Identify Candidate Journals

1. **Search similar papers** using PubMed/OpenAlex:
   - PubMed: `esearch.fcgi?db=pubmed&term=YOUR+TOPIC+&retmode=json`
   - OpenAlex: `works?search=YOUR+TOPIC&per_page=10&select=title,primary_location`
   - Extract journal names from top results
   - Count frequency — journals publishing many similar papers are good targets

2. **Compile known journals** in the domain (use internal knowledge):
   - Top-tier medical AI: *Artificial Intelligence in Medicine*, *npj Digital Medicine*
   - Computational biology: *Computers in Biology and Medicine*, *Bioinformatics*
   - IEEE: *IEEE JBHI*, *IEEE TMI*
   - Open access: *BMC Medical Informatics*, *Scientific Reports*, *PLOS ONE*

3. **Get journal metrics**:
   - Impact Factor (current and 2-year)
   - JCR Quartile (Q1/Q2/Q3/Q4)
   - Publisher (Elsevier, Springer, IEEE, Nature, BMC, etc.)
   - Open Access status
   - DOAJ/CORE membership
   - H-index, i10-index
   - Typical submission-to-acceptance time

### Step 3: Evaluate Fit

For each candidate journal, score on:

| Criterion | Weight | Notes |
|-----------|--------|-------|
| Topic match | 30% | Does the journal's Aims & Scope include your topic? |
| Paper quality match | 25% | Does the journal's typical paper quality match yours? |
| Methodology preference | 20% | Does the journal favor your approach (e.g., clinical vs. technical)? |
| Practical factors | 15% | IF tier, speed, OA cost, acceptance rate |
| Precedent | 10% | Have similar papers been published here? |

### Step 4: Rank and Tier

Group into tiers:

- **TIER 1 (Reach)**: IF >= 7.0, Q1, strong topic match. Submit first.
- **TIER 2 (Target)**: IF 5.0-7.0, Q1/Q2, good match. Submit if Tier 1 rejects.
- **TIER 3 (Safety)**: IF 3.0-5.0, Q2/Q3, adequate match. Last resort before OA options.
- **TIER 4 (OA/Backup)**: Broad scope, lower prestige but guaranteed acceptance quality.

### Step 5: Prepare Submission

Before submitting to any journal:
- Verify recent similar papers exist (proves the journal accepts this work)
- Read 2-3 recent papers in the target journal to understand tone/depth expectations
- Check Author Guidelines for: word limits, figure limits, reference style, required sections
- Prepare supplementary material for potential reviewer requests
- Have a fallback journal pre-identified

## Referen

---
*详细内容已移至 references/ 目录。*

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
