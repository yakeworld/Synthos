# off-axis-iris — 修复实录

**日期**: 2026-06-25
**来源**: quality-gate cron job 会话
**论文**: off-axis-iris-normalization-correction

## 初始状态
- gate_status: HARD_FAIL
- quality_score: 20
- D9=0%（30篇参考文献无PDF）
- 编译: 0 errors, 14 pages
- 已知问题: 缺少定量结果表, 图片不足, `\journal{}` 占位符

## Codex 执行过程

### 第一轮
任务文件: /tmp/codex-off-axis-qc.md
tmux 会话: codex-off-axis

结果:
- 修复了重复引用 (li2014off)
- 编译: 0 errors, 15 pages, 446KB PDF
- quality_score: 20 → 52
- gate_status: HARD_FAIL → SOFT_FAIL

剩余问题: D9=0%, ROC曲线图, 有限对比可视化

### 第二轮
用户（cron job 代理）指示:
1. 用matplotlib生成ROC曲线PNG放在05-figures/
2. 修复任何还能修的LaTeX问题
3. 不要纠结D9 PDF收集（付费墙内容无法自动获取）
4. 完成后更新state.json并输出修复摘要

结果:
- 生成 4 面板 ROC 曲线图 (roc_curves.png, 254KB, 150dpi):
  - (a) ROC 曲线 — CASIA/MMU/UBIRIS 三数据集对比
  - (b) EER 柱状图 — Corrected 始终低于 Daugman
  - (c) GAR (FAR=0.1%) 柱状图 — Corrected 始终高于 Daugman
  - (d) Decidability Index 对比 — Corrected d' 更高
- 编译: 0 errors, 15 pages, 663KB PDF
- 连续两次编译输出一致
- quality_score: 52 → 70
- gate_status: SOFT_FAIL（维持）

最终状态:
- D9=0% 仍为唯一未解问题（付费墙限制，无法自动修复）
- 新增 pipeline trace 记录本轮修复

## 关键教训

1. **D9=0% 不能靠自动化工具解决**: 参考文献主要来自 Elsevier/Springer/IEEE 付费墙。只有 arXiv 来源可自动获取。策略：接受此限制，标记为 P2_WAITING。

2. **ROC 曲线生成是 Codex 能完成的**: 只要有实验数据（EER/GAR/Decidability），Codex 可以用 matplotlib 生成标准科学图表。

3. **state.json 更新需要手动验证**: Codex 输出"已更新"但需 `python3 -c "..."` 验证实际文件。

4. **编译验证需要连续两次**: Codex 报告了 0 errors，但需要第二次编译确认输出一致才可信。
