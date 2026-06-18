---
name: viewpoint-verification
description: >-
version: 1.0.0
  多角度验证假说/论证——反证、证伪检验、鲁棒性检查、贝叶斯置信度评分。
metadata:
  synthos:
    priority: P0
    atom_type: cognitive-atom
    description: Multi-angle verification of hypotheses/arguments — counterproof, falsification tests, robustness checks, Bayesian confidence scoring.
    signature: "hypothesis: str, evidence: list[Evidence] -> verification_result: dict -> verification_result: dict (confidence_score, counterarguments, robustness_checks, falsification_tests)"
    related_skills: ["knowledge-acquisition", "knowledge-extraction", "association-discovery", "hypothesis-generation", "argument-expression"]

---



# Viewpoint Verification

详细内容请加载此skill后按需执行。核心流程和命令已提炼如下：

## 快速参考
## IO_CONTRACT

- **input**: hypothesis: str
- **input**: evidence: list[Evidence]
- **output**: verification_result: dict (confidence_score, counterarguments, robustness_checks, falsification_tests, weaknesses, recommendations)
> 对应原则：P2（机械原子暴露输入输出规范）

详细文档和完整命令列表已被移至 `references/` 目录以保持简洁。
This skill has been compressed. Full content is available in references/.
