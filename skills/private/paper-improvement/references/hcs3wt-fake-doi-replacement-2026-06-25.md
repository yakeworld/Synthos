# HCS-3WT 虚假引用替换实战记录（2026-06-25）

## 背景
HCS-3WT乳腺癌诊断论文32篇参考文献，通过DOI实际解析发现7篇假DOI（22%检出率）。

## 诊断过程
1. 全面质量检查发现报告中"DOI通过率28/30"仅检查bib是否有DOI字段
2. 实际向doi.org发HEAD请求 → 7篇返回404
3. Crossref/SS标题搜索 → 2篇可修正DOI，5篇需替换为语义等价文献

## 替换清单

| 旧引用 | 问题 | 替代文献 | DOI/来源 | 验证 |
|:-------|:-----|:---------|:---------|:----:|
| Elmore2021Artificial | DOI 404，JAMA虚构 | 删除，EBCTCG单独引用 | — | ✅ |
| Peacock2016Inter | DOI 404，Cancer虚构 | Rabe2019Interobserver | 10.1016/j.humpath.2019.09.006 | ✅302 |
| Ahmad2020Performance | DOI 404，IEEE虚构 | Agarap2018Breast | 10.1145/3184066.3184080 | ✅302 |
| Ghosh2023Comparative | DOI 404，虚构 | 合入Agarap | — | ✅ |
| Chakravarthy2021Deep | DOI 404，虚构 | 合入Agarap | — | ✅ |
| Reeder2024Uncertainty | DOI 404，Radiology虚构 | Begoli2018Need | 10.1038/s42256-018-0004-1 | ✅302 |
| Dembia2022Statistical | DOI 404，IEEE OJEMB虚构 | Demsar2006Statistical | jmlr.org OA | ✅ |
| Collins2024TRIPODAI | DOI错误 | 修正为10.1136/bmj.q824 | BMJ | ✅302 |

## 关键教训
1. **凡引必查必须实际解析DOI** — 仅查bib中有无DOI字段是假阴性
2. **patch工具反斜杠污染** — 编辑LaTeX后`\\cite`可能变成`\\\\cite`，需sed或Python清理
3. **sed比patch更可靠** — 引用替换等简单文本操作优先用sed
4. **无DOI经典论文** — JMLR/ICML早期论文标注"OA可获取"通过
