# PaperJury 引擎原理 v3 — 消化吸收笔记

## 核心创新

PaperJury 的核心创新不是「多跑几个 LLM 审稿」，而是确定性脚本 + 语义 agent 分工。

### 关键设计原则

1. **防漂移**：spine.js 冻结核心声明，anchor-diff.js 追踪 anchor
2. **防泄漏**：评审日志只在作者侧，绝不进入论文
3. **最小改动**：每条可修复问题只改必要的最小部分
4. **人类最终决策**：未经确认绝不改手稿

### 问题分类与路由

- significance: major（威胁 claims） vs minor（局部）
- kind: substantive（需要判断） vs mechanical（copy-edit）
- mechanical/minor → polish（快路径）
- substantive-major → trial（开庭审议，5→12 人陪审团）

### 编辑安全护栏

编辑前通过：anchor-diff → cross-ref → meaning-audit / edit-audit
结果：LOW→直接应用，RISKY→回滚+排队

### 与 Synthos 的关系

PaperJury 是质量审查工具，与 quality-gate 互补：
- quality-gate: 结构检查（D8/D10a/DOI/编译）
- paperjury: 语义审查（claim/论证/实验支撑）

Token 消耗：完整庭审约 10k tokens/轮，多轮 auto 30-50k。建议 maxRounds=3-5。
