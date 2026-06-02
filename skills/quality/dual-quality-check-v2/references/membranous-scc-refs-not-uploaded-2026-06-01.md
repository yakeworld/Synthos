# 膜性SCC重建论文 — 参考文献未上传NotebookLM案例

> 2026-06-01 实战教训

## 问题

膜性SCC重建论文（`membranous-scc-reconstruction`）通过了双质量评审（校准分0.81，T2），但参考文献全文从未上传到NotebookLM。

## 检查结果

| 项目 | 值 |
|:-----|:---:|
| D8（参考文献数） | 33 |
| D9（本地PDF覆盖率） | ~28/33 = 80% |
| **NotebookLM参考文献源** | **0篇** |
| NotebookLM中仅有 | 3份手稿版本（v1/v2/v3） |
| Layer B依据 | 仅手稿文本，无引用全文交叉验证 |
| 校准分 | 0.81（可能因缺乏上下文而不准确） |

## 根因

1. `dual-quality-check-v2` skill没有Layer B的前置闸门检查参考文献上传
2. 膜性论文与HSMM论文共用同一组PDF，但HSMM的参考文献已上传到另一个Notebook
3. 流程上「P4质量门」的描述未强调「必须上传参考文献到NotebookLM」是强制步骤

## 修复

1. 在`dual-quality-check-v2`新增「P0前置闸门」章节，明确Layer B前置条件为参考文献上传到达D8×80%
2. 在`paper-pipeline`的P4节新增引用此闸门
3. 本文档作为参考案例保存

## 后续行动（待执行）

- [ ] 将膜性论文的28篇PDF转Markdown上传到NotebookLM
- [ ] 重跑Layer B，比较有/无参考文献全文的评分差异
- [ ] 如果评分变化 > 0.03，更新投稿包
