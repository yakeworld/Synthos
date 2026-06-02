---
name: argument-expression
description: "Transform hypotheses into structured academic arguments: paper sections, evidence chains, and literature support. Writes content in academic style with proper citations. Use when the user asks to write a research paper section, draft an argument, create an academic outline, or write content for a paper, thesis, or proposal."
version: 1.1.0
author: Synthos Agent
license: MIT
allowed-tools: task_delegation (agent, inline), Read (view, read), Write (write), Execute (bash, code execution)
signature: "hypotheses: list[Hypothesis], structure: str -> sections: list[Section], references: list[Reference]"
tags: [argument-expression, academic-writing, paper-sections, evidence-chains, literature-support, citation]
metadata:
  synthos_atom_type: "cognitive"
  synthos_version: "1.1.0"
  synthos_skill_md_hash: "982e9b14203fe63c9edbf492ad315f8063b6cb031b1a2027f780d96acf4df1ec"
  synthos_model_version_pin: "deepseek/deepseek-v4-pro@2026-05-10"
  synthos_model_tested_on: "2026-05-10T00:00:00Z"
  synthos_io_contract_ref: "references/IO_CONTRACT.md"
  synthos_evidence_schema_ref: "references/EVIDENCE_SCHEMA.md"
  synthos_golden_set_ref: "golden/GOLDEN_SET.md"
  synthos_golden_set_origin: "self_defined"
  synthos_pass_threshold: "0.80"
  synthos_boundary_proof_ref: "references/BOUNDARY.md"
  synthos_change_log_ref: "references/CHANGE_LOG.md"
  synthos_asserted_compliance: "P0,P1,P2"
  synthos_depends_on: "hypothesis-generation,knowledge-acquisition"
  synthos_author: "Synthos Agent"
  synthos_data_access_level: "verified_only"
---

# 论证表达 (Argument Expression) - 认知原子 #5

## 原理层·文言

> 「太上有立德，其次有立功，其次有立言。」
> 「论如析薪，贵能破理。」
> 先立后行，不混不乱。引言设问，方法答之，结果证之，讨论释之。
> CARS开篇，金字塔立论，沙漏收束。

### 论辩之道

> 言之有序，论之有据。假说须论证，观点须表达。
> 三段论法：立论、举证、推演，缺一不可。
> 言必有中，引必有据。不主若若，不浮夸虚辞。
> 一事一段，一段一义。义尽则止，语毕乃终。
> 为读者着想，代审稿立心。

**核心理念**：论证表达是认知链的第五步。将假设转化为结构化学术文本。采用IMRaD结构，每段一个主张，每主张必有证据支持。以"疲劳审稿人"为读者，让贡献一目了然。

### 论证表达四要义

| 要义 | 文言释 | 含义 |
|:-----|:-------|:-----|
| 有序 | 言之有序 | 结构清晰，按IMRaD组织 |
| 有据 | 论之有据 | 每项主张有文献或数据支撑 |
| 有度 | 义尽则止 | 不冗余、不偏离 |
| 有为 | 代审稿立心 | 为读者着想，突出贡献 |

## 方法层·白话

### 触发条件

在以下情况加载本技能：

- 上游 hypothesis-generation 已产出假设，需要结构化论文论证
- 用户要求"写论文/写段落/构建论证/写综述"
- 需要将研究结果转化为符合TRIPOD+AI标准的报告
- 下游 viewpoint-verification 等待待验证的论点

### 验证清单

- [ ] 论证结构完整（背景→问题→方法→结果→讨论）
- [ ] 每项主张有文献引用支撑（符合P0证据可溯性）
- [ ] 引用的DOI可访问
- [ ] 输出符合学术写作规范
- [ ] 无虚构论文或捏造数据
- [ ] 每段通过"熵减检查"：能明确回答它在降低读者关于什么的认知不确定性
- [ ] 日损编辑检查已执行并输出了精简报告
- [ ] 类比映射（如有使用）声明了显式映射对和失效边界
- [ ] 输出包含 standpoint_declaration 字段

### 1. 职责（Scope）

将上游假设（来自 `hypothesis-generation`）转化为结构化学术论证文本。根据目标结构生成 IMRaD 论文章节、论证链（claim/evidence/reasoning）、参考文献列表。输出符合学术写作规范的文本段落。

本原子**不做**假设生成（那是 `hypothesis-generation` 的职责），**不做**知识获取（那是 `knowledge-acquisition` 的职责）。它只回答一个问题：**"如何将这些假设和证据写成可发表的学术文本？"**

### 2. 输入输出（Contract Summary）

详见 `references/IO_CONTRACT.md`。

| 方向 | 字段 | 来源 |
|------|------|------|
| 输入 | `hypotheses` (list[Hypothesis]) | 上游 `hypothesis-generation` |
| 输入 | `structure` (string) | 用户指定或默认 `"full_paper"` |
| 输入 | `raw_papers` (list[Paper]) | 上游 `knowledge-acquisition` |
| 输出 | `sections` (list[Section]) | 本原子生成 |
| 输出 | `arguments` (list[Argument]) | 本原子生成 |
| 输出 | `references` (list[Reference]) | 本原子生成 |

### 3. 推理流程（Procedure）

1. **读取输入**：检查 `input_dict` 中是否存在 `hypotheses`。若为空或不存在，返回 `_err("Missing hypotheses")`。`raw_papers` 为可选输入，若无则仅基于假设文本生成。

2. **结构确定**：根据 `structure` 参数确定输出结构：
   - `"introduction"`: 背景、研究空白、研究问题/假设
   - `"methods"`: 提议的研究设计、人群、测量、分析计划
   - `"results"`: 预期结果（基于假设）
   - `"discussion"`: 解释、对比、局限、结论
   - `"full_paper"`: 完整 IMRaD + 参考文献

3. **证据匹配**：为每个假设的主张寻找支持证据：
   a. 从 `raw_papers` 中匹配相关论文作为引用支持
   b. 构建 claim → evidence → reasoning 三元组
   c. 区分"已有证据支持"与"待验证假设"
   d. **Step 3a: 类比映射检查** — 如果论证中使用了跨领域类比：
      i. 必须输出显式的映射对："源领域要素A1→目标领域要素B1"
      ii. 必须声明失效边界："这个类比在什么条件下不成立"
      iii. 示例："VOR与陀螺仪的类比适用于[惯性测量]，不适用于[感觉整合]"

4. **章节组合**：按结构顺序生成各章节文本：
   a. 每个 section 包含：章节标题、段落内容、内嵌引用标记
   b. 每个 paragraph 关联其支持的 argument
   c. 保持学术写作风格：第三人称、过去时（方法/结果）、现在时（讨论/结论）

5. **参考文献生成**：汇总所有内嵌引用，生成规范的参考文献列表（APA 7th 格式）。

6. **构建证据链**：每个 Argument 的 evidence 节点引用上游 Hypothesis.id 或 Paper.doi。详见 `references/EVIDENCE_SCHEMA.md`。

7. **输出**：返回 `_ok({"sections": [...], "arguments": [...], "references": [...], "standpoint_declaration": {...}})` 信封。
   `standpoint_declaration` 包含以下字段：
   ```yaml
   standpoint_declaration:
     position_in_chain: "认知原子#5: 论证表达"
     writing_lens: "默认：中立学术写作——以最大化信息传递效率为目标"
     model_boundary: "本论证基于上游HYP假设，不验证假设本身的有效性（那是VER的职责）"
   ```

8. **日损编辑检查（大道至简）**：写作完成后执行精简检查：
   a. 逐段检查："这段删掉后，论文的论证完整性是否受影响？"
   b. 逐图检查（如有图表）："这个图提供了文字中没有的信息吗？"
   c. 输出 `精简报告：{removed_sections: [], removed_figures: [], 精简率: x%}`

### 4. 边界判断（When NOT to use this atom）

详见 `references/BOUNDARY.md`。典型排除场景：
- 如果用户只需要生成假设（不需要写成论文段落）→ 仅用 `hypothesis-generation`，不需要本原子。
- 如果用户只需要提取论文知识 → 仅用 `knowledge-extraction`，不需要本原子。
- 如果用户需要的是会议摘要/海报而非完整论文 → 可以考虑使用但需指定 `structure: "abstract"`。
- 如果用户需要的是非学术写作（博客、新闻稿）→ 本原子不适用。

### 5. 证据链输出要求（Evidence Summary）

详见 `references/EVIDENCE_SCHEMA.md`。每个 `Argument` 必须携带：
- `claim`: 主张文本
- `evidence`: 引用 `Hypothesis.id` 或 `Paper.doi`
- `reasoning`: 推理过程
- 证据链节点类型：`atom_output`（引用上游）或 `doi`（引用论文）

### 6. 示例（Minimal Example）

**输入**：
```json
{
  "hypotheses": [
    {
      "id": "hyp_001",
      "text": "Eye tracking saccade metrics differ significantly across ADHD subtypes",
      "rationale": "Contradiction in existing literature may be explained by subtype heterogeneity",
      "source": "gap_001",
      "novelty_score": 0.72,
      "feasibility_score": 0.65,
      "testability": "testable"
    }
  ],
  "structure": "introduction",
  "raw_papers": [
    {
      "title": "AI-based eye tracking for ADHD screening",
      "doi": "10.3389/fpsyt.2023.1260031",
      "year": 2023,
      "authors": ["Chen X", "Wang S"]
    }
  ]
}
```

**输出**（简化）：
```json
{
  "sections": [
    {
      "section_type": "introduction",
      "heading": "Introduction",
      "paragraphs": [
        "Attention-Deficit/Hyperactivity Disorder (ADHD) affects approximately 5% of children worldwide...",
        "Recent advances in eye tracking technology have shown promise for ADHD screening (Chen & Wang, 2023)...",
        "However, existing studies report inconsistent findings regarding eye tracking effectiveness...",
        "This inconsistency may be explained by unaccounted ADHD subtype heterogeneity...",
        "The present study hypothesizes that eye tracking saccade metrics differ significantly across ADHD subtypes..."
      ]
    }
  ],
  "arguments": [
    {
      "claim": "Eye tracking effectiveness for ADHD screening is inconsistent across studies",
      "evidence": "hyp_001",
      "reasoning": "Contradiction between Chen & Wang (2023) and other studies suggests moderating variables"
    }
  ],
  "references": [
    {
      "id": "ref_001",
      "text": "Chen, X., & Wang, S. (2023). AI-based eye tracking for ADHD screening. Frontiers in Psychiatry, 14, 1260031.",
      "doi": "10.3389/fpsyt.2023.1260031"
    }
  ]
}
```

### 7. 质量要求

- **逻辑性**：论证链条的连贯性（claim → evidence → reasoning）
- **完整性**：每个主张都有支持证据或标注为假设
- **可读性**：语言表达的清晰和准确
- **规范性**：符合学术写作标准（引用格式、段落结构）
- **[PW-Bench吸收] 文献综述六轴质量门控**：Introduction/Related Work 章节输出前，使用 `references/litreview-quality-gate.md` 的 6 轴评分体系进行自检。门控标准：
  - **≥ 55** → 直接输出 ✅
  - **40-54** → 输出 + 标注改进点 ⚠️
  - **< 40** → 标记为"需要重写"，输出改进建议 🔴

### 8. 约束

- 不得编造引用或数据
- 必须区分事实（已有文献支持）和观点（待验证假设）
- 必须遵循学术写作规范（第三人称、客观语气）
- 引用必须可追溯到上游 `raw_papers`

### 9. 失败模式

- **逻辑断裂** → 重新梳理论证链条，确保每个 claim 有 evidence
- **证据不足** → 请求补充文献或标注为推测性陈述
- **重复冗余** → 使用奥卡姆剃刀原则精简表达

### 10. 依赖

- 上游：`hypothesis-generation`、`knowledge-acquisition`
- 下游：无（这是输出环节，直接面向用户）

### 11. Synthos 维度

- **系统思维**：整体论证结构设计
- **第一性原理**：每个论点都可追溯到基本原理
- **奥卡姆剃刀**：用最简洁的方式表达

### 12. 注意事项

假设的表达和论证——输出通常是论文/报告/提案的一部分。需要人类审核最终文本。本原子生成的是"可发表的草稿"，而非最终成品。

### 13. 参考文件索引（References）

- IO 契约：`references/IO_CONTRACT.md`
- 证据链 schema：`references/EVIDENCE_SCHEMA.md`
- 边界证明：`references/BOUNDARY.md`
- 金标准：`golden/GOLDEN_SET.md`
- 变更日志：`references/CHANGE_LOG.md`
- **[PW-Bench吸收] 文献综述六轴质量门控**：`references/litreview-quality-gate.md`

---

### 写作增强·纳外法

This section augments the basic IMRaD structure support above with advanced paper writing guidance adapted from external knowledge bases. It provides concrete formulas, narrative frameworks, and writing philosophy from leading ML/AI researchers, absorbed into native expression.

#### 1. 叙事原则：三问叙事

Every strong academic paper tells a coherent story built on three narrative questions. Every section should serve at least one of these:

| 问 | 英文对位 | 问题 | 作用 |
|:---|:---------|:-----|:-----|
| **所作何事？** | The What | 你做了什么？ | 陈述方法、系统、贡献的核心内容 |
| **因何重要？** | The Why | 为什么重要？ | 驱动工作的问题、空白、异常 |
| **于谁有益？** | The So What | 读者为何关心？ | 阐明影响、含义、后继意义 |

**Application**: Before writing any section, ask: *Does this paragraph advance The What, The Why, or The So What?* If a paragraph does none of the three, cut it or reframe it.

#### 2. 摘要五句法

Structured abstracts dramatically improve clarity and reviewer experience. Each sentence has a specific rhetorical job:

| # | 句 | 作用 | 模板示例 |
|---|-----|-----|---------|
| 1 | **背景与问题** | 建立领域、已知、空白 | "Recent advances in X have shown Y, but Z remains challenging." |
| 2 | **所作之事** | 一句说清方法/途径 | "We propose A, a novel method that does B." |
| 3 | **关键结果** | 报告最重要的发现或指标 | "On benchmark C, A achieves D% improvement over baselines." |
| 4 | **解释/洞察** | 说明结果为何重要，超越数字 | "This improvement stems from E, which addresses the core limitation of prior work." |
| 5 | **广泛影响/展望** | 连接更大图景，一个展望式断言 | "Our findings suggest that F could generalize to G, opening new directions for H." |

**Constraint**: The entire abstract must fit within 5–8 sentences total. Each sentence must pass the "delete test": if you remove it, the abstract loses essential information.

#### 3. Section-by-Section Writing Guidance

| Section | Narrative Focus | Key Strategy | Common Pitfall |
|---------|----------------|--------------|----------------|
| **Abstract** | The What + The Why + The So What (condensed) | Use the 5-sentence formula above. No citations (except in rare cases). Write it *last*. | Trying to cram every result; overwhelming the reader. |
| **Introduction** | The Why (establish gap + motivation) | Inverted pyramid: broad context → specific gap → your contribution. End with a clear roadmap paragraph ("In this work, we..."). Use 1–2 figures / diagrams if helpful. | Literature dump without narrative arc; burying the contribution on page 2. |
| **Methods / Approach** | The What (precise, reproducible) | Top-down: first give the high-level intuition / architecture diagram, then formalize in equations or pseudocode, then detail training/hyperparameters. Use bullet-style paragraphs for implementation details. | Starting with equations before the big picture; missing reproducibility-critical details (seed, learning rate schedule, hardware). |
| **Experiments** | The What (evidence) + The So What (proof) | Set up the question first: "To evaluate X, we..." Present results in tables/figures, then interpret *in prose*. Always compare to a meaningful baseline. Always report variance. Include ablation studies for design choices. | Cherry-picking results; no error bars; qualitative claims without quantitative evidence. |
| **Related Work** | The Why (positioning) | Position your work *after* explaining your approach — or place it after the introduction. Group by theme, not by paper. End each paragraph with how your work differs or improves upon that theme. | Laundry-list summaries ("Paper A did X, Paper B did Y..."); failing to distinguish your contribution. |
| **Discussion / Conclusion** | The So What (implications + limitations) | Summarize the core finding in one sentence. Discuss limitations honestly (reviewers respect this). Outline 2–3 concrete future directions. End with a strong final sentence that circles back to the introduction's motivation. | Repeating results verbatim; writing a weak or generic closing sentence. |

#### 4. Key Writing Philosophy from Top Researchers

Adapted from widely shared advice by researchers including Neel Nanda, Sebastian Farquhar, and others in the ML research community:

1. **Write for the tired reviewer (Nanda, Farquhar)** — Your reviewer has 15 papers to read. Be kind. Make your contribution obvious in the first page. Put figures where they are seen. Use informative section headings. Don't make them hunt for the main idea.

2. **Narrative first, results second (Nanda)** — Decide the story before running final experiments. Figure out: "What is the one thing I want the reader to remember?" Then design every figure, every table, every paragraph to serve that one thing. The narrative *determines* which numbers belong in the paper, not the other way around.

3. **Every paragraph is a claim (Farquhar)** — A paragraph that makes no claim is a waste of ink. Each paragraph should: (a) state a claim, (b) support it with evidence or reasoning, and (c) connect it to the paper's central argument. If a paragraph fails any of these, rewrite or remove.

4. **The first draft is allowed to be bad** — "The only way to write a good paper is to write a bad one first and improve it" (common wisdom, often attributed to various researchers). Get a structurally complete draft on the page, then iterate on clarity. Don't try to write perfectly sentence-by-sentence.

5. **Figures are the paper (Nanda, Farquhar)** — Many reviewers jump to figures first. Each figure must be self-contained: clear caption, readable fonts, labeled axes, statistical annotations. A good figure tells the story. A bad figure creates confusion. Spend as much time on figures as on prose.

6. **The "So what?" hammer (multiple researchers)** — After every sentence, ask: *So what?* If the answer adds nothing new, delete the sentence. This is the most powerful editing tool you have.

| 7. **Acknowledge limitations preemptively (Farquhar)** — Don't wait for reviewers to find your weaknesses. Discuss limitations in the paper itself. This builds trust and shows intellectual maturity. Frame limitations as *opportunities for future work* where possible.

| 8. **熵减律·生生之谓易 — 每段必问"这段在降低读者关于什么的熵？"** — 写作不是尽可能多地塞信息，而是降低读者对某个特定问题的认知不确定性。每段写完自问：
|    - 如果读者只读这段，ta对论文核心问题的理解有什么变化？
|    - 如果删掉这段，读者会丢失什么关键信息？
|    - 如果答案是否定的（不降低任何特定不确定性），这段可以删。

#### 5. Anti-Hallucination Rule for Citations

**CRITICAL RULE**: Never generate BibTeX entries, citation keys, or inline citations (`\cite{...}`) from memory. Every citation must derive from one of:

1. Papers explicitly listed in the `raw_papers` input
2. Papers the user has provided or confirmed
3. Papers retrieved from a verified source (e.g., Semantic Scholar API, arXiv)

**Violation examples** (DO NOT DO):
```bibtex
% BAD — Hallucinated from memory:
@inproceedings{vaswani2017attention,
  author    = {Ashish Vaswani and ...},
  title     = {Attention Is All You Need},
  ...
}
```

**Correct behavior**:
1. If the user says "cite Transformer paper" and you know it exists → respond: *"I know of this paper (Vaswani et al., 2017, 'Attention Is All You Need') but I should not generate BibTeX from memory. Please provide the DOI or use a citation retrieval tool to get the correct entry."*
2. Or use a tool to fetch the real citation data (e.g., query Semantic Scholar API).
3. Default citation format in generated prose: `(Author, Year)` — only use this format, never generate BibTeX keys.

**Rationale**: Hallucinated citations erode trust in the entire paper. A single fake reference can get a paper desk-rejected or retracted. Accuracy > convenience.

## 命令层·English

- **Signature**: `hypotheses: list[Hypothesis], structure: str -> sections: list[Section], references: list[Reference]`
- **Allowed tools**: `task_delegation`, `Read`, `Write`, `Execute`
- **Input**: `hypotheses` (list[Hypothesis]) from upstream `hypothesis-generation`, `structure` (str, one of: `introduction`, `methods`, `results`, `discussion`, `full_paper`), `raw_papers` (optional)
- **Output**: `sections` (list[Section] with heading + paragraphs + argument refs), `arguments` (list[Argument] with claim/evidence/reasoning), `references` (list[Reference] in APA 7th), `standpoint_declaration` (dict with position_in_chain, writing_lens, model_boundary)
- **Narrative pillars**: The What, The Why, The So What — every paragraph must serve at least one
- **熵减律 (Entropy Reduction)**: Every paragraph must reduce reader uncertainty about a specific question. If uncertain what entropy it reduces, delete or rewrite.
- **日损编辑 (Daily Pruning)**: After writing, run the delete test paragraph-by-paragraph and figure-by-figure. Output a pruning report.
- **类比映射 (Analogy Mapping)**: If using cross-domain analogies, output explicit source→target mapping pairs and declare failure boundaries.
- **Abstract formula**: 5-sentence (Background → Method → Result → Interpretation → Impact)
- **Quality gate (lit review)**: ≥55 pass, 40-54 warn, <40 rewrite
- **Anti-hallucination**: Never generate citations from memory — only from verified sources
- **Do NOT**: generate hypotheses, acquire knowledge, write non-academic content
