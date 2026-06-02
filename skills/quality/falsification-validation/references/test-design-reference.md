# Falsification Test Reference

## Test Design Template

When designing a falsification test, use this template:

```
Test ID: [sequential number]
Name: [descriptive name]
Target Skill: [skill name/directory]
Target Atom: [atom number if applicable]

Test Scenario:
- Input: [real data/query to use]
- Expected: [what should happen if skill works]
- Falsification: [what would prove the skill fails]

Success Criteria:
- [measurable criteria 1]
- [measurable criteria 2]

Quality Metrics to Track:
- Accuracy: [0-1 scale]
- Completeness: [0-1 scale]
- Relevance: [0-1 scale]
- Timeliness: [0-1 scale]
- Authority: [0-1 scale]

Evidence to Collect:
- [specific artifacts to save]
- [comparison against ground truth]

Bayesian Setup:
- Prior Trust: [starting probability]
- Likelihood Function: [how to calculate P(evidence|skill correct)]
- Success Threshold: [what constitutes "evidence" for updating]
```

## Common Test Scenarios

### For Search/Retrieval Skills

**Scenario 1: Empty Query**
- Input: "" (empty string)
- Expected: Empty results, no crash
- Falsification: Returns non-empty results or crashes
- Evidence: Error logs, result count

**Scenario 2: Non-Existent Topic**
- Input: "quantum_entanglement_in_mushrooms_2024"
- Expected: Few/zero relevant results
- Falsification: Hallucinates fake papers
- Evidence: Check DOI validity against source

**Scenario 3: Outdated Information**
- Input: "AI ethics guidelines"
- Expected: Recent sources (last 2-3 years)
- Falsification: Returns only pre-2020 sources
- Evidence: Publication year distribution

### For Analysis/Extraction Skills

**Scenario 1: Contradictory Input**
- Input: Two papers with conflicting claims
- Expected: Both sides represented
- Falsification: Ignores one side, creates false synthesis
- Evidence: Extracted claims comparison

**Scenario 2: Missing Critical Info**
- Input: Complex methodology paper
- Expected: All key methods extracted
- Falsification: Misses primary analysis technique
- Evidence: Checklist of required fields

### For Reasoning Skills

**Scenario 1: Weak Premises**
- Input: Papers with low evidence quality
- Expected: Low confidence in conclusion
- Falsification: High confidence despite weak evidence
- Evidence: Confidence score vs evidence quality

**Scenario 2: Cross-Domain Transfer**
- Input: Knowledge from unrelated fields
- Expected: Clear separation of domains
- Falsification: Spurious connections between unrelated topics
- Evidence: Connection strength and justification

## Falsification Patterns

### Pattern 1: Boundary Testing
Test at edges of expected input:
- Minimum viable input
- Maximum expected input size
- Invalid/malformed input
- Ambiguous input

### Pattern 2: Stress Testing
Push skill to its limits:
- Very large input size
- Multiple concurrent requests
- Very complex query structure
- Highly specialized domain knowledge

### Pattern 3: Adversarial Testing
Try to break the skill:
- Contradictory premises
- Impossible constraints
- Missing critical information
- Conflicting requirements

## Evidence Collection Checklist

For each test, verify you have:

- [ ] Original input data preserved
- [ ] Complete processing log
- [ ] Final output captured
- [ ] Comparison against expected output
- [ ] Quality metrics calculated
- [ ] Evidence saved to test-results/
- [ ] Bayesian update computed
- [ ] Trust score updated

## Example Test: Knowledge Acquisition

```
Test ID: falsification_001
Name: Search Quality Test
Target: knowledge-acquisition (Atom 1)
Test Scenario:
- Input: "ADHD eye-tracking studies 2024"
- Expected: 3+ relevant papers with valid DOIs
- Falsification: <3 results, invalid DOIs, or irrelevant content

Quality Metrics:
- 检索覆盖率: 1.0
- 相关性评分: 0.92
- 时效性: 1.0
- 权威性: 0.9

Bayesian Update:
- Prior: 0.8
- Likelihood: 1.0 (strong evidence)
- Posterior: 1.0
- Result: Trust increased

Outcome: PASS
Evidence: /test-results/test_001_knowledge_acquisition.json
```

## When to Run Tests

1. **Initial Validation**: When creating a new skill
2. **After Updates**: After modifying a skill's implementation
3. **Regular Intervals**: Monthly for production skills
4. **After Failures**: When a skill fails unexpectedly
5. **Before Major Releases**: Before publishing a skill

## Red Flags (Trust < 0.5)

If trust drops below 0.5:
1. Stop using the skill for production
2. Document all failure evidence
3. Analyze root causes
4. Redesign the skill from scratch
5. Test against all failure modes again
6. Only return to production after passing full test suite
