# Self-Citation Audit Workflow

> Added 2026-05-21 after SYNTHOS Pima paper revision
> Context: Paper had 89% self-citation rate (62/70 citations were self-references)

## When to Use

During D7 citation quality review when self-citation rate appears elevated.

## Detection

```bash
# Extract all unique cited keys
grep -oP '\\\\cite\{[^}]+\}' paper.tex | tr ',' '\\n' | sed 's/\\\\cite{//;s/}//' | sed 's/^ *//' | sort -u > /tmp/all_refs.txt

# Count total unique
total=$(wc -l < /tmp/all_refs.txt)

# Identify self-citations — look for bibkeys matching author's known publication patterns
# Common patterns: ProcessDriven, author_surname keywords, specific project codenames
# Manually count self-citations from the list

# Self-citation rate
echo "self_rate = self_count / $total * 100"
```

## Severity Thresholds

| Self-Citation Rate | D7 Cap | Action |
|:------------------:|:------:|:-------|
| 0-15% | 1.0 | Normal |
| 15-30% | 0.85 | Check if justified |
| 30-50% | 0.60 | Must reduce |
| >50% | 0.30 | Desk reject risk |

## Reduction Protocol

### Step 1: Classify each self-citation

| Class | Rule |
|:------|:-----|
| A: Framework-specific claim | Keep (max 5) |
| B: Context/generic claim | Replace with 2-3 independent refs |
| C: Literature summary | Replace with original source |

### Step 2: Find replacement references

Search PubMed/Semantic Scholar for independent papers that cover the same claim. Key search topics for ML/medical papers:
- Data leakage in ML: "Kapoor2024Leakage", "Wen2024Leakage", "Artzi2023DataLeak"
- SMOTE/cross-validation pitfalls: "Batista2004SMOTE", "Blagus2013SMOTE"
- Clinical ML guidelines: "Collins2015TRIPOD", "Norgeot2020MI-CLAIM", "Moons2019PROBAST"
- Missing value imputation: "Stekhoven2012missForest"

### Step 3: Replace in bulk

```python
# Replace all \cite{self_ref, ...} -> \cite{new_ref, ...}
# Replace all \cite{..., self_ref} -> \cite{...}
# Replace all \cite{self_ref} -> \cite{new_ref}
import re
tex = re.sub(r'\\cite\{SelfCiteKey,\s+', r'\\cite{', tex)
tex = re.sub(r',\s+SelfCiteKey\}', r'}', tex)
tex = re.sub(r'\\cite\{SelfCiteKey\}', r'\\cite{NewRef2024}', tex)
```

### Step 4: Add back strategic self-citations

After bulk removal, add back 3-5 A-class self-citations:
- Where the paper IS the original source for a specific claim
- Where describing "our framework/approach/method"
- NOT for generic claims like "data leakage is bad" or "previous work found..."

### Step 5: Verify

```bash
# Self-citation count should be 3-8
grep -c 'SelfCite1\|SelfCite2' paper.tex
# Total cite commands should have increased (replacing 1 self-cite with 2-3 refs)
grep -c '\\\\cite{' paper.tex
```

## Example: SYNTHOS Pima Paper (2026-05-21)

| Before | After |
|:-------|:------|
| 45 ProcessDriven + 17 IllusionOfPerfection = 62 self-cites | 4 ProcessDriven + 1 IllusionOfPerfection = 5 self-cites |
| 89% self-citation rate | 6.1% self-citation rate |
| 18 unique refs | 33 unique refs (37 bib entries) |
| D7 score: 0.25 | D7 score: 0.78 |

## Pitfalls

1. **Over-removal**: Removing ALL self-citations leaves the paper without a connection to the team's prior work. Keep 3-5.
2. **Wrong replacement**: Replacing a self-citation with an irrelevant reference is worse than keeping the self-citation.
3. **Bib key mismatch**: After replacing keys in tex, ensure the new bib keys exist in references.bib.
