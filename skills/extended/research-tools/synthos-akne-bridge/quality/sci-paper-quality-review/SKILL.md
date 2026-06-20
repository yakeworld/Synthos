---



name: sci-paper-quality-review
description: "Directory index for sci-paper-quality-review: sci-paper-quality-review"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "paper_path: str -> quality_report: dict (g1_score, g2_score, g3_score, overall_grade, recommendations)"
    atom_type: skill
    priority: P1
    related_skills: []
---




## IO_CONTRACT

- **input**: `manuscript: str, review_type: str` — 用户请求描述、上下文信息
- **output**: `review_report: dict — 质量审查报告`

> 对应原则：P2（机械原子暴露输入输出规范）



# Sci Paper Quality Review

详细内容请加载此skill后按需执行。核心流程和命令已提炼如下：

## 快速参考

详细文档和完整命令列表已被移至 `references/` 目录以保持简洁。
This skill has been compressed. Full content is available in references/.

**Key references specific to your role:**
- `references/g7-deep-quality-review-workflow.md` — **Start here for autonomous G7 reviews.** Covers candidate selection (scan library → pick lowest quality), 7-dimension evaluation criteria with diagnostic questions, post-fix score estimation, pipeline_trace false-positive detection, 07-quality/ cross-reference, and critical pitfalls (score-scale confusion, self-rating bias, stale review detection, auto-gate score inflation).
- `references/d2-formal-proof-boost.md` — Tighten mathematical arguments and equivalence claims.
- `references/d7-bibtex-metadata-audit.md` — Fix DOI accuracy, orphan/zombie references.
- `references/experimental-verification-protocol.md` — Verify numerical claims against code output.
- `references/system-paper-metric-verification.md` — Detect metric inconsistencies between paper sections.
