# HCS-3WT 假DOI检测 + 修复实录 (2026-06-25)

## 背景

HCS-3WT乳腺癌论文的检查员报告中，"凡引必查清单"声称30/30 PASS（全部引用有DOI且有效）。实际验证后发现7篇DOI返回404。

## 根因

原检查员报告只检查bib文件/paper.tex thebibliography中是否存在`doi`字段——有字段就标记`DOI?=✅`。**从未向doi.org发HTTP请求验证DOI是否可解析。**

## 检测流程

```bash
# 对每篇引用
for key in $(grep '\\bibitem{' paper.tex | sed 's/.*{//;s/}.*//'); do
    # 从 bib 或 thebibliography 提取 DOI
    doi=$(grep -A5 "\\bibitem{$key}" paper.tex | grep -oP 'doi\s*=\s*\{?[^}]*\}' | sed 's/.*{//;s/}.*//')
    if [ -n "$doi" ]; then
        status=$(curl -sI "https://doi.org/$doi" 2>/dev/null | head -1)
        echo "$key: DOI=$doi → $status"
    fi
done
```

HTTP 302 = ✅ 真实存在
HTTP 404 = 🚨 假DOI（LLM虚构）

## 7篇假DOI详情

| 引用键 | bib中的DOI | doi.org结果 | 修复方式 |
|--------|-----------|:-----------:|---------|
| Elmore2021Artificial | 10.1001/jamanetworkopen.2021.5934 | 404 | 删除（EBCTCG2018单独足够） |
| Peacock2016Inter | 10.1007/s10549-016-4012-6 | 404 | 替换为Rabe2019 (Human Pathology) |
| Ahmad2020Performance | 10.1109/ACCESS.2020.3041722 | 404 | 替换为Agarap2018 (ACM) |
| Ghosh2023Comparative | 10.1007/s11042-023-15005-z | 404 | 合入Agarap |
| Chakravarthy2021Deep | 10.1007/s11831-021-09552-7 | 404 | 合入Agarap |
| Reeder2024Uncertainty | 10.1016/j.jbi.2023.104562 | 404 | 替换为Begoli2018 (Nature MI) |
| Dembia2022Statistical | 10.1109/OJEMB.2022.3191158 | 404 | 替换为Demsar2006 (JMLR) |

## 替代文献验证

每篇替代文献通过以下三渠道验证：
1. DOI解析：`curl -sI "https://doi.org/<DOI>"` → 302
2. Crossref元数据：`https://api.crossref.org/works/<DOI>` → title/author/year匹配
3. 体裁确认：title关键词与论文使用场景一致

| 替代键 | DOI | 验证 | 语境 |
|--------|-----|:----:|------|
| Rabe2019Interobserver | 10.1016/j.humpath.2019.09.006 | ✅302 | 病理专家间变异 |
| Agarap2018Breast | 10.1145/3184066.3184080 | ✅302 | WBC数据集ML >95% |
| Begoli2018Need | 10.1038/s42256-018-0004-1 | ✅302 | AI临床不确定性管理 |
| Demsar2006Statistical | 无DOI(JMLR), jmlr.org OA | ✅PDF | Wilcoxon比较分类器 |
| Collins2024TRIPODAI | 原10.1136/bmj-2023-076534 → 修正为10.1136/bmj.q824 | ✅302 | 报告规范 |

## 教训

1. **bib中有DOI字段 ≠ DOI可解析** — LLM生成的bib条目可能有完整的DOI格式但指向不存在的论文
2. 检查员报告必须加`Resolved?`列，逐篇发HEAD请求验证
3. 假DOI检测可在15分钟内完成（32篇引用的批量curl检测）
4. 替代文献优先使用Crossref/doi.org验证后的真实文献
