---
name: falsification-validation
description: Systematic approach to validating AI agent skills through falsification
version: 1.0.0
  tests and Bayesian trust estimation. Instead of trying to prove a skill works, actively
  try to prove it fails, then update trust probability based on evidence. Use when
  creating, updating, or assessing the reliability of any skill. Must produce quantifiable
  quality metrics and evidence.
allowed-tools:
- terminal
- read_file
- write_file
- search_files
license: MIT
metadata:
  synthos:
    version: 1.0.0
    signature: 'skill_name: str -> test_results: dict'
    related_skills:
    - bib-integrity-audit
    - dual-quality-check-v2
    - golden-test-methodology
    - post-compile-dual-quality-check
    - quality-gate

---

## IO_CONTRACT

- **input**: `hypothesis: str, test_data: str` — 用户请求描述、上下文信息
- **output**: `validation_result: dict — 证伪验证结果`

> 对应原则：P2（机械原子暴露输入输出规范）




## 原理层·文言

> 「或也者，不尽也。然者，是也。」欲证其立，先求其破。
> 「以指喻指之非指，不若以非指喻指之非指也。」
> 反证三得，贝叶斯累进。不证不称，运行即证。

# Falsification-Driven Skill Validation

## Scope

Systematic approach to validating AI agent skills through falsification tests and Bayesian trust estimation. Instead of trying to prove a skill works, actively try to prove it fails, then update trust probability based on evidence.

## Philosophy

1. **Falsificationism (Popper)**: Don't seek to confirm skills work — actively seek disproof through rigorous testing. A skill that survives falsification attempts gains credibility.
2. **Bayesian Thinking**: Trust is a probability that updates with evidence. Start with prior trust, collect evidence, compute posterior trust.
3. **Quantification**: Every skill must have measurable quality metrics, not subjective "looks good" assessments.

## Core Principles

- Every cognitive atom (or any skill) must be tested with real-world tasks, not theoretical inspection
- Collect concrete evidence: JSON outputs, quality scores, comparison against ground truth
- Update trust scores systematically using Bayes theorem
- A skill surviving multiple falsification attempts gains trust; failing loses trust rapidly
- Low-trust skills get redesigned or replaced, not patched indefinitely

## Testing Workflow

### Step 1: Design Falsification Test
For each skill, create a test scenario that could potentially DISPROVE it works:

1. Define a realistic input (real query, real data)
2. Set explicit pass/fail criteria
3. Define measurable metrics (accuracy, completeness, relevance, timeliness)
4. Specify what evidence must be collected

### Step 2: Execute Test
Run the skill against the test case:
1. Input real data
2. Execute the skill's workflow
3. Collect all outputs and intermediate results
4. Compare against expected output

### Step 3: Collect Evidence
Document everything:
1. Input data (real, not synthetic mock data)
2. Processing results (intermediate outputs)
3. Final output
4. Comparison with ground truth
5. Metric calculations
6. Save all evidence to `test-results/` directory

### Step 4: Bayesian Update
Update trust probability using Bayes theorem:
```
P(skill correct | evidence) = P(evidence | skill correct) × P(skill correct) / P(evidence)
```

### Step 5: Decision
Based on updated trust:
- High trust (0.9-1.0): Continue using as-is
- Medium trust (0.7-0.9): Increase monitoring frequency
- Low trust (0.5-0.7): Redesign or major improvement needed
- Very low trust (<0.5): Replace the skill entirely

## Testing Framework Components

### Falsification Tests
Design tests around these failure modes:

**For Search/Retrieval Skills (like knowledge-acquisition):**
- Returns zero results when results exist
- Returns irrelevant results
- Returns stale/outdated information
- Misses high-authority sources
- Has poor deduplication

**For Analysis/Extraction Skills (like knowledge-extraction):**
- Extracted content conflicts with source text
- Misses critical information
- Produces poor structured output
- Cannot trace back to source

**For Reasoning Skills (like hypothesis-generation):**
- Generates non-testable hypotheses
- Contradicts existing knowledge
- Lacks novelty
- Missing reasoning steps

**For Verification Skills (like viewpoint-verification):**
- Fails to find counterarguments
- Ignores negative results
- Overstates confidence
- Produces non-reproducible results

### Quality Metrics

Track these metrics for each test:
- **Accuracy**: How close results are to ground truth (0-1)
- **Completeness**: Coverage of all required fields (0-1)
- **Relevance**: How relevant results are to input (0-1)
- **Timeliness**: How current information is (0-1)
- **Authority**: Source credibility (0-1)

## Trust Management

### Trust Update Rules

| Event | Trust Change |
|-------|-------------|
| Successful test | +0.05 to +0.1 |
| Failed test | -0.1 to -0.2 |
| 3+ consecutive successes | Additional +0.02 |
| 3+ consecutive failures | Additional -0.05 |

### Trust States

| Range | Status | Action |
|-------|--------|--------|
| 0.9-1.0 | High Trust | Continue using |
| 0.7-0.9 | Medium Trust | Increase monitoring |
| 0.5-0.7 | Low Trust | Redesign needed |
| < 0.5 | Unreliable | Replace skill |

## Evidence Requirements

Every test must produce:

1. **Input Data**: Real task input (not mock/synthetic)
2. **Processing Log**: Intermediate results from skill execution
3. **Output Results**: Final output from the skill
4. **Comparison**: Analysis of how output matches expectations
5. **Metric Calculations**: Quantitative quality scores
6. **Evidence Storage**: All artifacts saved to `test-results/` directory

## Anti-Patterns to Avoid

- Testing with mock data instead of real data
- Subjective "looks good" assessments without metrics
- Only running tests that you expect to pass
- Updating trust based on single data points
- Ignoring failure evidence
- Using inconsistent metric thresholds across tests
- Not collecting evidence for tests that pass
- Assuming skill works because it "seems right"

## Related

- Bayesian probability theory
- Karl Popper's falsificationism
- Scientific method and hypothesis testing
- ML model evaluation and validation
- A/B testing and experimental design
