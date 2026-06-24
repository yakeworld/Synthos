# Quality Gate — I/O Contract

## Input

| Source | Path | Format | Required |
|--------|------|--------|----------|
| 论文文件 | `outputs/papers/*/01-manuscript/*.tex` | LaTeX | Yes (L2-L4) |
| 论文状态 | `outputs/papers/*/state.json` | JSON | Yes (L2-L3) |
| 论文参考文献 | `outputs/papers/*/06-references/` | Bib/MD | Yes (G5) |
| 论文数据源文件 | 论文目录下的数据/实验记录 | 多种 | Yes (L0.5) |
| 交付物 | 项目产出文件 | 多种 | Yes (L2) |
| 当前会话 | 会话消息上下文 | Text | Yes (L1) |
| 技能SKILL.md | `skills/<name>/SKILL.md` | Markdown | Yes (L0) |

## Output

| Destination | Path | Format |
|-------------|------|--------|
| 质量评估报告 | `outputs/researchaudit/<paper>/quality_report.json` | JSON |
| 问题清单 | `outputs/researchaudit/<paper>/issues.json` | JSON |
| 修复建议 | `outputs/researchaudit/<paper>/fixes.md` | Markdown |
| 门状态更新 | `outputs/papers/*/state.json` | JSON |
| 提交材料 | `outputs/papers/*/submission/` | 多种 |

## Key Data Structures

### QualityReport (单篇论文)
```json
{
  "paper_name": "str",
  "gate_version": "2.9.2",
  "assessment_date": "2026-06-18T00:00:00Z",
  "overall_score": 0.0-1.0,
  "gate_scores": {
    "G1": {"score": 0.0-1.0, "passed": true, "issues": []},
    "G2": {"score": 0.0-1.0, "passed": true, "issues": []},
    "G3": {"score": 0.0-1.0, "passed": true, "issues": []},
    "G4": {"score": 0.0-1.0, "passed": true, "issues": []},
    "G5": {"score": 0.0-1.0, "passed": true, "issues": []},
    "G6": {"score": 0.0-1.0, "passed": true, "issues": []},
    "G7": {"score": 0.0-1.0, "passed": true, "issues": []}
  },
  "l0_direction_check": {"aligned": true, "reason": "str"},
  "l0.5_data_honesty": {"passed": true, "unsupported_claims": []},
  "l1_response_quality": {"score": 0.0-1.0, "drift_detected": false},
  "l2_project_quality": {"score": 0.0-1.0, "deliverables_complete": true},
  "l4_content_quality": {"score": 0.0-1.0, "seven_dimensions": {}}
}
```

### GateStatus
```json
{
  "gate_name": "G1|G2|...|G7",
  "status": "not_started|in_progress|passed|failed",
  "score": 0.0-1.0,
  "threshold": 0.85,
  "pass": true,
  "issues": [{"severity": "critical|major|minor", "description": "str", "fix": "str"}]
}
```

## Non-guarantees

- Quality gate does NOT guarantee that all scientific claims are true
- Quality gate does NOT guarantee experimental results are reproducible
- Quality gate does NOT guarantee the paper will be accepted by any journal
- Quality gate does NOT write paper content or design experiments
- Quality gate does NOT replace human judgment on scientific merit
- Citation appropriateness verification requires reading PDF full text (not automated beyond format checks)
