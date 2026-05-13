---
name: argument-expression
description: "Transform hypotheses into structured academic arguments: paper sections, evidence chains, and literature support. Writes content in academic style with proper citations. Use when the user asks to write a research paper section, draft an argument, create an academic outline, or write content for a paper, thesis, or proposal."
license: MIT
metadata:
  synthos_atom_type: "cognitive"
  synthos_version: "0.1.0"
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
  synthos_mechanical_atoms: ""
  synthos_depends_on: "hypothesis-generation,knowledge-acquisition"
  synthos_author: "Synthos Agent"
allowed-tools: delegate_task Read Write Execute
metadata:
  synthos_data_access_level: "verified_only"

# 论证表达 (Argument Expression)

## 1. 职责（Scope）

将上游假设（来自 `hypothesis-generation`）转化为结构化学术论证文本。根据目标结构生成 IMRaD 论文章节、论证链（claim/evidence/reasoning）、参考文献列表。输出符合学术写作规范的文本段落。

本原子**不做**假设生成（那是 `hypothesis-generation` 的职责），**不做**知识获取（那是 `knowledge-acquisition` 的职责）。它只回答一个问题：**"如何将这些假设和证据写成可发表的学术文本？"**

## 2. 输入输出（Contract Summary）

详见 `references/IO_CONTRACT.md`。

| 方向 | 字段 | 来源 |
|------|------|------|
| 输入 | `hypotheses` (list[Hypothesis]) | 上游 `hypothesis-generation` |
| 输入 | `structure` (string) | 用户指定或默认 `"full_paper"` |
| 输入 | `raw_papers` (list[Paper]) | 上游 `knowledge-acquisition` |
| 输出 | `sections` (list[Section]) | 本原子生成 |
| 输出 | `arguments` (list[Argument]) | 本原子生成 |
| 输出 | `references` (list[Reference]) | 本原子生成 |

## 3. 推理流程（Procedure）

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
4. **章节组合**：按结构顺序生成各章节文本：
   a. 每个 section 包含：章节标题、段落内容、内嵌引用标记
   b. 每个 paragraph 关联其支持的 argument
   c. 保持学术写作风格：第三人称、过去时（方法/结果）、现在时（讨论/结论）
5. **参考文献生成**：汇总所有内嵌引用，生成规范的参考文献列表（APA 7th 格式）。
6. **构建证据链**：每个 Argument 的 evidence 节点引用上游 Hypothesis.id 或 Paper.doi。详见 `references/EVIDENCE_SCHEMA.md`。
7. **输出**：返回 `_ok({"sections": [...], "arguments": [...], "references": [...]})` 信封。

## 4. 边界判断（When NOT to use this atom）

详见 `references/BOUNDARY.md`。典型排除场景：
- 如果用户只需要生成假设（不需要写成论文段落）→ 仅用 `hypothesis-generation`，不需要本原子。
- 如果用户只需要提取论文知识 → 仅用 `knowledge-extraction`，不需要本原子。
- 如果用户需要的是会议摘要/海报而非完整论文 → 可以考虑使用但需指定 `structure: "abstract"`。
- 如果用户需要的是非学术写作（博客、新闻稿）→ 本原子不适用。

## 5. 证据链输出要求（Evidence Summary）

详见 `references/EVIDENCE_SCHEMA.md`。每个 `Argument` 必须携带：
- `claim`: 主张文本
- `evidence`: 引用 `Hypothesis.id` 或 `Paper.doi`
- `reasoning`: 推理过程
- 证据链节点类型：`atom_output`（引用上游）或 `doi`（引用论文）

## 6. 示例（Minimal Example）

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

## 7. 质量要求

- **逻辑性**：论证链条的连贯性（claim → evidence → reasoning）
- **完整性**：每个主张都有支持证据或标注为假设
- **可读性**：语言表达的清晰和准确
- **规范性**：符合学术写作标准（引用格式、段落结构）

## 8. 约束

- 不得编造引用或数据
- 必须区分事实（已有文献支持）和观点（待验证假设）
- 必须遵循学术写作规范（第三人称、客观语气）
- 引用必须可追溯到上游 `raw_papers`

## 9. 失败模式

- **逻辑断裂** → 重新梳理论证链条，确保每个 claim 有 evidence
- **证据不足** → 请求补充文献或标注为推测性陈述
- **重复冗余** → 使用奥卡姆剃刀原则精简表达

## 10. 依赖

- 上游：`hypothesis-generation`、`knowledge-acquisition`
- 下游：无（这是输出环节，直接面向用户）

## 11. Synthos 维度

- **系统思维**：整体论证结构设计
- **第一性原理**：每个论点都可追溯到基本原理
- **奥卡姆剃刀**：用最简洁的方式表达

## 12. 注意事项

假设的表达和论证——输出通常是论文/报告/提案的一部分。需要人类审核最终文本。本原子生成的是"可发表的草稿"，而非最终成品。

## 13. 参考文件索引（References）

- IO 契约：`references/IO_CONTRACT.md`
- 证据链 schema：`references/EVIDENCE_SCHEMA.md`
- 边界证明：`references/BOUNDARY.md`
- 金标准：`golden/GOLDEN_SET.md`
- 变更日志：`references/CHANGE_LOG.md`

---

## 学术写作增强 Academic Writing Enhancement [SYNTHOS_P0_ABSORBED_FROM: NanoResearch ml-paper-writing]

This section augments the basic IMRaD structure support above with advanced paper writing guidance adapted from the ml-paper-writing knowledge base. It provides concrete formulas, narrative frameworks, and writing philosophy from leading ML/AI researchers.

### 1. The Narrative Principle: Three Pillars

Every strong academic paper tells a coherent story built on three narrative pillars. Every section should serve at least one of these:

| Pillar | Question | What It Does |
|--------|----------|--------------|
| **The What** | What did you do? | States the method, approach, or system clearly. Establishes the concrete contribution. |
| **The Why** | Why does it matter? | Motivates the work — the problem being solved, the gap being filled, the anomaly being explained. |
| **The So What** | Why should the reader care? | Articulates the impact, implications, and downstream consequences. Connects the work to broader significance. |

**Application**: Before writing any section, ask: *Does this paragraph advance The What, The Why, or The So What?* If a paragraph does none of the three, cut it or reframe it.

### 2. Five-Sentence Abstract Formula (Sebastian Farquhar / DeepMind)

Structured abstracts dramatically improve clarity and reviewer experience. Each sentence has a specific rhetorical job:

| # | Sentence | Job | Example Template |
|---|----------|-----|-----------------|
| 1 | **Background & Problem** | Establish the domain, the known, and the gap. | "Recent advances in X have shown Y, but Z remains challenging." |
| 2 | **What You Did** | State your method/approach in one clear sentence. | "We propose A, a novel method that does B." |
| 3 | **Key Result** | Report the single most important finding or metric. | "On benchmark C, A achieves D% improvement over baselines." |
| 4 | **Interpretation / Insight** | Say *why* the result matters. Go beyond the number. | "This improvement stems from E, which addresses the core limitation of prior work." |
| 5 | **Broader Impact / Outlook** | Connect to the bigger picture. One forward-looking claim. | "Our findings suggest that F could generalize to G, opening new directions for H." |

**Constraint**: The entire abstract must fit within 5–8 sentences total. Each sentence must pass the "delete test": if you remove it, the abstract loses essential information.

### 3. Section-by-Section Writing Guidance

| Section | Narrative Focus | Key Strategy | Common Pitfall |
|---------|----------------|--------------|----------------|
| **Abstract** | The What + The Why + The So What (condensed) | Use the 5-sentence formula above. No citations (except in rare cases). Write it *last*. | Trying to cram every result; overwhelming the reader. |
| **Introduction** | The Why (establish gap + motivation) | Inverted pyramid: broad context → specific gap → your contribution. End with a clear roadmap paragraph ("In this work, we..."). Use 1–2 figures / diagrams if helpful. | Literature dump without narrative arc; burying the contribution on page 2. |
| **Methods / Approach** | The What (precise, reproducible) | Top-down: first give the high-level intuition / architecture diagram, then formalize in equations or pseudocode, then detail training/hyperparameters. Use bullet-style paragraphs for implementation details. | Starting with equations before the big picture; missing reproducibility-critical details (seed, learning rate schedule, hardware). |
| **Experiments** | The What (evidence) + The So What (proof) | Set up the question first: "To evaluate X, we..." Present results in tables/figures, then interpret *in prose*. Always compare to a meaningful baseline. Always report variance. Include ablation studies for design choices. | Cherry-picking results; no error bars; qualitative claims without quantitative evidence. |
| **Related Work** | The Why (positioning) | Position your work *after* explaining your approach — or place it after the introduction. Group by theme, not by paper. End each paragraph with how your work differs or improves upon that theme. | Laundry-list summaries ("Paper A did X, Paper B did Y..."); failing to distinguish your contribution. |
| **Discussion / Conclusion** | The So What (implications + limitations) | Summarize the core finding in one sentence. Discuss limitations honestly (reviewers respect this). Outline 2–3 concrete future directions. End with a strong final sentence that circles back to the introduction's motivation. | Repeating results verbatim; writing a weak or generic closing sentence. |

### 4. Key Writing Philosophy from Top Researchers

Adapted from widely shared advice by researchers including Neel Nanda, Sebastian Farquhar, and others in the ML research community:

1. **Write for the tired reviewer (Nanda, Farquhar)** — Your reviewer has 15 papers to read. Be kind. Make your contribution obvious in the first page. Put figures where they are seen. Use informative section headings. Don't make them hunt for the main idea.

2. **Narrative first, results second (Nanda)** — Decide the story before running final experiments. Figure out: "What is the one thing I want the reader to remember?" Then design every figure, every table, every paragraph to serve that one thing. The narrative *determines* which numbers belong in the paper, not the other way around.

3. **Every paragraph is a claim (Farquhar)** — A paragraph that makes no claim is a waste of ink. Each paragraph should: (a) state a claim, (b) support it with evidence or reasoning, and (c) connect it to the paper's central argument. If a paragraph fails any of these, rewrite or remove.

4. **The first draft is allowed to be bad** — "The only way to write a good paper is to write a bad one first and improve it" (common wisdom, often attributed to various researchers). Get a structurally complete draft on the page, then iterate on clarity. Don't try to write perfectly sentence-by-sentence.

5. **Figures are the paper (Nanda, Farquhar)** — Many reviewers jump to figures first. Each figure must be self-contained: clear caption, readable fonts, labeled axes, statistical annotations. A good figure tells the story. A bad figure creates confusion. Spend as much time on figures as on prose.

6. **The "So what?" hammer (multiple researchers)** — After every sentence, ask: *So what?* If the answer adds nothing new, delete the sentence. This is the most powerful editing tool you have.

7. **Acknowledge limitations preemptively (Farquhar)** — Don't wait for reviewers to find your weaknesses. Discuss limitations in the paper itself. This builds trust and shows intellectual maturity. Frame limitations as *opportunities for future work* where possible.

### 5. Anti-Hallucination Rule for Citations

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
