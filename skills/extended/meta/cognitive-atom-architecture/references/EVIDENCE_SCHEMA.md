# Cognitive Atom Architecture EVIDENCE_SCHEMA

## Validation Criteria

1. Each cognitive atom has single, testable responsibility
2. DAG has no cycles (verified by topological sort)
3. IO_CONTRACT is complete for each atom
4. No overlapping responsibilities between atoms

## Verification
- Run: `skills/{atom}/SKILL.md` validation
- Check: `evolution-state.json` structural integrity