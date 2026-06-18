# Knowledge Graph Infrastructure Reference

## Location

```
~/Synthos/knowledge-graph/
├── nodes/           # Each .md file = one knowledge node with YAML frontmatter
├── relations/       # Relation type definitions
└── INDEX.md         # Master index
```

## Node Frontmatter Format

```yaml
---
id: "unique-kebab-case-id"
type: "knowledge-node"
status: "TEMPLATE"  # UNREAD | READING | EXTRACTED | TRANSFORMED | STABILIZED | INTEGRATED
created: "YYYY-MM-DD"
last_review: "YYYY-MM-DD"
S: 2.5          # stability in days
D: 5.0          # difficulty [1,10] — mean-reverts to w4(~5.0)
R: 1.0          # retrievability — (1 + t/(9*S))^(-1)
reviews: 0
connections:
  - target: "another-node-id"
    type: "extends"  # uses | supports | contradicts | extends | part_of | example | based_on | improves
source: "user-input | session-YYYY-MM-DD | paper-DOI | skill-absorption"
domain: "philosophy | skill-design | methodology | research"
---
```

## FSRS Core Computation

```python
def fsrs_retrievability(S_days, elapsed_days):
    return 1.0 / (1.0 + elapsed_days / (9.0 * S_days))

def fsrs_should_review(S_days, elapsed_days, threshold=0.7):
    return fsrs_retrievability(S_days, elapsed_days) < threshold
```

## Weekly Consolidation Cron

- Job: `memory-consolidation` (ID: 41f32dd5f5ac)
- Schedule: `0 4 * * 0` (Sunday 4:00 AM)
- Flow: check all nodes → R<0.7→review list, R<0.3→demote, connections<2→find links
