# Evolution Engine — Evidence Chain Schema

## Evidence Node Types

| Type | Description | Fields |
|------|-------------|--------|
| `probe_result` | Atom quality probe output | `atom_name`, `overall_score`, `issues` |
| `api_health_check` | API endpoint health test | `source`, `http_status`, `latency_ms` |
| `diagnosis_finding` | Degradation or critical finding | `atom`, `issue`, `severity`, `delta` |
| `patch_applied` | Skill file modification | `atom`, `file`, `change_summary`, `status` |
| `verification_result` | Post-patch verification | `atom`, `pre_score`, `post_score`, `improved` |
| `state_update` | evolution-state.json change | `field`, `old_value`, `new_value` |
| `log_entry` | evolution-log.md update | `timestamp`, `message` |

## Evidence Chain Format

Each action in the evolution cycle produces evidence that links to the previous step:

```json
{
  "evidence_id": "evol_001_probe_ka",
  "type": "probe_result",
  "timestamp": "2026-05-11T06:00:00Z",
  "atom": "knowledge-acquisition",
  "data": {
    "structural_score": 0.95,
    "api_health_score": 1.0,
    "overall_score": 0.96
  },
  "links_to": ["evol_001_load_state"]
}
```
