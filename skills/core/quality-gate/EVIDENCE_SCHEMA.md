# Quality Gate — Evidence Chain Schema

## Evidence Node Types

| Type | Description | Fields |
|------|-------------|--------|
| `gate_check` | 单道质量门检查结果 | `gate_name`, `score`, `passed`, `issues` |
| `direction_check` | L0动灵方向检查 | `aligned`, `system_growth_direction`, `deliverable_direction` |
| `data_honesty_check` | L0.5数据诚实门检查 | `claim`, `has_source_file`, `source_path` |
| `d10a_scan` | D10a覆盖率扫描结果 | `cite_to_ref_ratio`, `orphan_count`, `zombie_count` |
| `doi_check` | DOI元数据检查 | `total_refs`, `with_doi`, `coverage_pct` |
| `citation_appropriateness` | 引用恰当性审查 | `ref_title`, `paper_context`, `appropriately_cited`, `score` |
| `l1_drift_check` | L1响应级漂移检测 | `drift_detected`, `drift_description`, `score` |
| `l2_deliverable_check` | L2交付物检查 | `deliverable_type`, `complete`, `quality_score` |
| `sci_seven_dim` | L4 SCI七维评审 | `dimension`, `score`, `comments` |
| `gate_pass` | 门通过通知 | `gate_name`, `score`, `threshold`, `next_gate` |
| `gate_fail` | 门不通过通知 | `gate_name`, `score`, `threshold`, `issues`, `retry_count` |

## Evidence Chain Format

```json
{
  "evidence_id": "qgate_G5_001",
  "type": "gate_check",
  "timestamp": "2026-06-18T00:00:00Z",
  "gate": "G5",
  "data": {
    "d10a_coverage": 0.972,
    "orphan_count": 0,
    "zombie_count": 0,
    "doi_coverage": 0.059,
    "overall_score": 0.85,
    "passed": false,
    "blocking_issue": "DOI覆盖率严重不足 (5.9% < 90%)"
  },
  "links_to": ["qgate_G4_003", "qgate_G6_001"]
}
```

## Evidence Chain Rules

1. 每道质量门必须产生至少一个 `gate_check` 证据节点
2. L0.5数据诚实门必须在所有L1-L4检查之前执行
3. G5引用质量的证据链必须包含形式检查和实质检查两个层级
4. 门不通过的证据链必须包含 `gate_fail` + 修复建议
5. 连续3次不通过同一道门，升级为 `critical` 级别
