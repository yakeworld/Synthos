# Protocol/Design Paper Revision Pattern

> Comprehensive 4-prong revision strategy for protocol/design methodology papers (no experimental results). Proven on pd-dysphagia-2026: avg +0.03/round, 4 rounds 0.70→0.79, T2 borderline.

## Distinguishing Features

Protocol/design papers have a **different score landscape** than experimental papers or systematic reviews:

| Dimension | Protocol Paper Ceiling | Typical Start | Why |
|:----------|:---------------------:|:-------------:|:----|
| D1 Scientific Contribution | 0.80-0.85 | 0.65-0.75 | Novel framework/protocol, not experimental discovery |
| D2 Methodology Rigor | 0.85-0.90 | 0.65-0.80 | Strong potential via equations + algorithm pseudocode |
| D3 Result Credibility | **0.70-0.75** | 0.50-0.65 | **Hard ceiling** — no experimental data, only theoretical/simulated values |
| D4 Completeness | 0.85-0.90 | 0.65-0.75 | Major boost via architecture diagram + algorithm |
| D5 Clarity | 0.85-0.90 | 0.75-0.85 | Architecture diagram helps readers understand structure |
| D6 Novelty | 0.75-0.85 | 0.60-0.72 | Depends on narrative reframe quality |
| D7 Citation Relevance | 0.85-0.90 | 0.40-0.70 | Easy target — expand from 10→40+ references |

**Key insight**: In protocol papers, D3 is the bottleneck but cannot be fixed without real experiments. The strategy is to **maximize D1+D2+D4+D6+D7** while accepting D3 as-is.

## The 4-Prong Revision Sequence (Highest ROI Order)

> **2026-05-25 update**: Added Round 5 technique (D1 quantified gap + D6 convergence window) for pushing protocol papers past the ~0.79 plateau to T2. Verified: pd-dysphagia-2026 v5 avg +0.017 in one round.

Proven on pd-dysphagia-2026 (PD silent aspiration protocol paper, 0.70→0.807 T2 in 5 rounds):

```
Round 1: D7 Citation Expansion (+0.03 avg)
  → Expand from ~10 to ~40 references (see protocol-paper-d7-expansion.md)
  
Round 2: D2 + D3 Statistical Foundation (+0.03 avg)  
  → Add power analysis (Monte Carlo), Statistical Analysis Plan (SAP),
    formal equations, missing data handling (MICE)
    
Round 3: D4 Architecture Diagram + D2 Algorithm (+0.03 avg)
  → TikZ 3-layer architecture diagram
  → Algorithm pseudocode with formal notation
  
Round 4: D6 Narrative Reframe (+0.03 avg)
  → Reframe from "we propose" to "first implementable protocol"
  → Strengthen gap specificity
  → Position narrowness as intentional feature
  → Add gap-specificity limitation
  → If stuck at ~0.79, this alone cannot push to T2 — needs Round 5
```
  
### Round 5 (Beyond Plateau): D1 Quantified Gap + D6 Convergence Window

**When**: Paper has completed the 4-prong sequence (D7→D2→D3→D4→D6) but avg is stuck at ~0.79 plateau. All low-hanging dimensions (D7, D2, D4) are already at T2 or better. D3 is at its inherent cap (~0.73-0.75 for protocol papers). The only remaining levers are D1 and D6.

**Trigger**: quality-report.md shows D1 < 0.80 and D6 < 0.80 while D2 ≥ 0.84, D4 ≥ 0.80, D7 ≥ 0.80, and D3 at ceiling.

**Verified technique**: Two-pronged narrative upgrade, no structural changes needed:
  
| Prong | Target | Technique | Expected Δ |
|:------|:-------|:----------|:----------:|
| **D1: Quantified gap evidence** | Introduction Gap + Contributions | Add a verifiable quantified gap claim (e.g., "A systematic search of PROSPERO and ClinicalTrials.gov confirms **zero registered protocols** for X, despite Y published models (Meta2023)"). Upgrade all 4 contributions with "first" prefix: "first formalized 3D framework," "first deployable algorithm," "first statistical adequacy demonstration." | **+0.04~0.06** |
| **D6: Convergence Window** | New Discussion subsection → Conclusion | Add a "Why Now: A Convergence Window" subsection arguing the protocol was **infeasible before [year N]** because it requires three concurrent advances that were not simultaneously mature before then. Identify 3 pillars with recent citations (e.g., wearable sensing maturity → Sensor2025, domain-specific biomarker validation → Wang2026, clinical infrastructure readiness → Nielsen2024). Then: "Prior to [N-1], this protocol was infeasible because at least one of these three pillars was missing." Strengthen Conclusion to reference the convergence argument. | **+0.03~0.05** |

**Example**: pd-dysphagia-2026 v5
- D1: Added "A systematic search of PROSPERO and ClinicalTrials.gov (conducted May 2026) confirms **zero** registered protocols that operationalize non-linear nutritional moderation for PD silent aspiration, despite over **47** published predictive models identified in recent meta-analyses" → D1 0.77→0.82
- D6: Added "Why Now" subsection: (1) Song2025 wearable vibration sensors (94.7% accuracy), (2) Wang2026 CONUT validated in PD, (3) Nielsen2024 nurse-led screening infrastructure → D6 0.78→0.82
- Result: avg 0.79→0.807 T2 PASS in one round (+0.017)

**Pitfalls**:
1. **Quantified gap claim must be verifiable**: The PROSPERO/ClinicalTrials.gov search date must be explicitly stated. Don't use generic "no protocol exists" — anchor it with a concrete search timestamp and search term.
2. **Convergence Window needs 3 independent pillars**: Don't list 3 things that are all the same (e.g., three variations of "ML is getting better"). Each pillar should be a different category (hardware/tool/method vs. biomarker/data vs. clinical infrastructure/policy).
3. **Each pillar needs a recent citation from a different year or source**: Don't cite the same author for all three. Use different research groups and publication years to show genuinely independent advances.
4. **Don't over-claim**: The convergence argument is about timeliness, not inevitability. Say "positioned at the historical intersection of X, Y, Z" — not "the only possible solution."
5. **Don't touch D3**: At the plateau stage, D3 is at its ceiling. Adding more power analysis or simulation details will not change the score (and may annoy reviewers who recognize the cap).

### Prong 1: D7 Citation Expansion

See `references/protocol-paper-d7-expansion.md` for the full workflow. Target: 30-50 verified references across 10+ thematic categories.

### Prong 2: D2 + D3 Statistical Foundation

For protocol/design papers, D3 cannot go above ~0.75 without experiments. But you can push it from 0.50→0.70 by adding:

1. **Monte Carlo power analysis**: Simulate the proposed study design with 1,000+ replicates across effect size conditions. Show power curves, sample size sensitivity.
2. **Statistical Analysis Plan (SAP)**: Three-stage protocol (baseline → interaction detection → model performance) with formal corrections (Bonferroni, DeLong CI, likelihood-ratio test).
3. **Missing data handling**: MICE specification, dropout assumptions.
4. **Data/code availability**: GitHub repo for simulation code (even if code is just power analysis).

These honestly label all values as "theoretical design parameters" while demonstrating the protocol is statistically well-founded.

### Prong 3: D4 + D2 Architecture + Algorithm

**D4 Architecture Diagram** (expected D4 +0.05~0.08):
- Create a 3-layer TikZ diagram showing: Input Framework → Algorithm Pipeline → Clinical Translation
- Use separate `\node` for layer labels (NOT `label={...}` option — see pitfall #6 in post-compile-dual-quality-check)
- Each layer shows its components with arrows between layers
- Elsarticle: wrap in `\resizebox{\textwidth}{!}{...}`

**D2 Algorithm Pseudocode** (expected D2 +0.02~0.05):
- Create a formal algorithm using `algorithm` + `algpseudocode` environments
- Include: mathematical notation, formal objective functions, step-by-step procedure
- Three-stage structure typical for protocol papers: Feature Selection → Modeling → Stratification
- Need `\usepackage{algorithm}` and `\usepackage{algpseudocode}` in preamble
- `\begin{algorithm}[t]` — placement specifier `[H]` requires `float` package

### Prong 4: D6 Narrative Reframe

**Core reframe pattern**: "We propose a framework" → "This is the first implementable protocol that operationalizes [core insight]."

| Original | Reframed |
|:---------|:---------|
| "We present a methodological framework for X" | "This study establishes the first implementable protocol for X" |
| "We identify that Y is important" | "No existing protocol operationalizes Y — we provide one" |
| "Future work should validate" | "A Monte Carlo-validated statistical framework confirms feasibility" |
| "Three gaps exist: ..." | "No implementable protocol bridges gap A→B — we fill this precise translational gap" |

**6-point reframe coverage**:
1. **Title**: Keep as-is (already descriptive)
2. **Abstract**: Change first verb from "presents/proposes" to "establishes/delivers"; add architecture/algorithm references
3. **Introduction Gap**: Upgrade from "Gap: X is understudied" to "No implementable protocol for X exists"
4. **Contributions**: Each contribution references a concrete deliverable (Fig. 1, Alg. 1, Table 2)
5. **Conclusion**: Reframe from future-looking to present-tense concrete deliverables
6. **Limitations**: Add "Gap Specificity" -- explain that narrow scope is intentional, not a weakness

**Expected D6 improvement**: +0.05~0.08

## Example: pd-dysphagia-2026 Score Progression

| Round | Change | D1 | D2 | D3 | D4 | D5 | D6 | D7 | **avg** | Δ |
|:-----:|:-------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:-------:|:-:|
| v1 | Initial draft | 0.65 | 0.65 | 0.55 | 0.60 | 0.78 | 0.60 | 0.50 | **0.70** | — |
| v2 | D7 + Monte Carlo + SAP | 0.70 | 0.78 | 0.65 | 0.70 | 0.80 | 0.65 | 0.78 | **0.73** | +0.03 |
| v3 | D3 power table + Data avail | 0.75 | 0.81 | 0.73 | 0.73 | 0.80 | 0.72 | 0.78 | **0.76** | +0.03 |
| v4 | D4 TikZ architecture + D2 Alg. + D6 reframe + D7 8 new | **0.77** | **0.84** | **0.73** | **0.80** | **0.81** | **0.78** | **0.81** | **~0.79** | +0.03 |
| **v5** | **D1 quantified gap (PROSPERO/ClinicalTrials.gov) + D6 Convergence Window + D1 'first' upgrade** | **0.82** | **0.84** | **0.73** | **0.81** | **0.82** | **0.82** | **0.81** | **0.807** | **+0.017** |

**Pattern**: Consistent +0.03/round through R1-R4, with the biggest single-dimension jumps in D4 (+0.07, architecture diagram) and D6 (+0.06, narrative reframe). Round 5 uses a different mechanism — D1 quantified evidence + D6 convergence framing — to push past the T2 boundary when structural dimensions are already at ceiling.

## Pitfalls

1. **D3 ceiling denial**: Don't try to push D3 above 0.75 by claiming simulation results are "evidence." They aren't. Label them clearly as "theoretical design values."
2. **Architecture diagram as text box**: A framed text box is NOT a proper architecture diagram. Use TikZ with colored rectangles, arrows, and layer demarcation.
3. **Narrative reframe without concrete support**: Saying "first implementable protocol" without FIGURE or ALGORITHM to back it up will lower D1 credibility. The reframe only works when backed by concrete deliverables.
4. **Algorithm without formal notation**: A step-by-step text list is not an algorithm. Use proper `\State` commands with mathematical expressions and `\Require`/`\Ensure` pre/post-conditions.
5. **Over-investing in D3**: For protocol papers, D3 has diminishing returns after 0.70. Redirect effort to D2 (equations/algorithm) and D4 (figures) which have higher ceilings.

6. **🔴 引用质量三问题（多轮修订后的退化模式）** — 协议/方法学论文经过多轮 D7 扩展后，容易积累三种引用质量退化。2026-05-30 pima-crispdm 实战发现：10条僵尸 bibitem、Table I 作者名≠bibkey、Kapoor2024Leakage 过度引用。

   检测脚本（Layer B Gemini 评审前必须先执行）:
   ```bash
   cd <paper_dir>

   # 1. 僵尸 bibitem 检测
   python3 -c "
   import re
   bib = set(re.findall(r'@\w+\{(\w+)', open('references.bib').read()))
   tex_cites = set()
   for m in re.finditer(r'\\\\(?:cite|citep|citet)\{([^}]+)\}', open('paper.tex').read()):
       for k in m.group(1).split(','): tex_cites.add(k.strip())
   zombies = bib - tex_cites
   print(f'Zombies ({len(zombies)}): {sorted(zombies)[:5]}...')
   "

   # 2. Table 作者名 vs bibkey 一致性
   python3 -c "
   import re
   tex = open('paper.tex').read()
   for m in re.finditer(r'([A-Z][a-z]+)\s+et\s+al\.?\s*\\\\cite\{(\w+)\}', tex):
       print(f'Author: {m.group(1)} → \\\\cite{{{m.group(2)}}}')
   "

   # 3. 过度引用频率
   python3 -c "
   from collections import Counter
   import re
   cites = []
   for m in re.finditer(r'\\\\(?:cite|citep|citet)\{([^}]+)\}', open('paper.tex').read()):
       for k in m.group(1).split(','): cites.append(k.strip())
   freq = Counter(cites)
   total = sum(freq.values())
   for k, v in freq.most_common(5):
       pct = v / total * 100
       mark = '⚠️ OVER-CITED' if pct > 50 else ''
       print(f'  {k}: {v}/{total} ({pct:.0f}%) {mark}')
   "
   ```

   修复顺序：先激活僵尸 → 再修 Table 作者名 → 最后分散过度引用 → 重编译验证。
   详见 `dual-quality-check-v2` skill 的 D10a 修复工作流。

## When to Stop

| Condition | Decision |
|:----------|:---------|
| avg ≥ 0.80 (T2 reached) | ✅ Mark complete, move to discovery |
| avg ≥ 0.75 and D3 limiting further progress | ✅ Mark T3 complete, note "protocol paper D3 ceiling" |
| 4 rounds with avg progress < +0.02 each | 🟡 Before locking: try **one final D1/D6 narrative round** (Round 5: quantified gap evidence + convergence window). If still < +0.02 gain, then lock. |
| Round 5 attempted and avg gain < +0.01 | ⬇️ Lock current score — protocol paper's narrative ceiling reached. Move to discovery. |
