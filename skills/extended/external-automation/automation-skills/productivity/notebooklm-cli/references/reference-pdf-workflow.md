# Bibliographic Reference PDF Workflow

> 从NotebookLM生成BibTeX → 下载PDF → 命名规范 → 上传验证

## 完整工作流

```
┌─ 阶段1：元数据获取 ──────────────────────────────┐
│ notebooklm ask "为所有源文件生成BibTeX条目，含DOI │
│ 或arXiv ID"                                       │
│ → 保存为 notebooklm-sources.bib                   │
└──────────────────────┬────────────────────────────┘
                       ↓
┌─ 阶段2：PDF下载 ─────────────────────────────────┐
│ arXiv ID → wget https://arxiv.org/pdf/{id}.pdf    │
│ DOI → curl -L -o {bibkey}.pdf "https://doi.org/..."│
│ Semantic Scholar → API search + download          │
│ → 保存到 pdfs/{bibkey}.pdf                        │
└──────────────────────┬────────────────────────────┘
                       ↓
┌─ 阶段3：命名规范 ─────────────────────────────────┐
│ bibkey-map.json 记录 filename → bibkey 映射       │
│ 文件名 = {bibkey}.pdf                             │
│ 小写，无空格/连字符/下划线                         │
└──────────────────────┬────────────────────────────┘
                       ↓
┌─ 阶段4：上传到NotebookLM ────────────────────────┐
│ notebooklm source add pdfs/{bibkey}.pdf           │
│   --title "{bibkey}"                              │
│ → 更新 notebooklm-sources.json                    │
└──────────────────────┬────────────────────────────┘
                       ↓
┌─ 阶段5：D7验证 ──────────────────────────────────┐
│ ≥3篇参考PDF已上传（硬闸门检查）                    │
│ notebooklm ask "核对数值声明 vs 参考PDF"           │
│ → D7评分可信                                       │
└───────────────────────────────────────────────────┘
```

## BibTeX → DOI/arXiv 提取

从BibTeX条目中提取下载标识符：

| 源类型 | BibTeX字段 | 下载URL |
|:-------|:-----------|:--------|
| arXiv | eprint = {2408.06292} | https://arxiv.org/pdf/2408.06292 |
| DOI | doi = {10.1038/s41586-023-06747-5} | https://doi.org/10.1038/... |
| PubMed | pmid = {37253956} | https://pubmed.ncbi.nlm.nih.gov/37253956/pdf/ |

## 命名对照表（实战验证）

| 旧名 | 新名 | bibkey | arXiv |
|:-----|:-----|:-------|:------|
| Lala2023.pdf | lala2025paperqa.pdf | lala2025paperqa | — |
| Bai2022.pdf | bai2022constitutional.pdf | bai2022constitutional | 2212.08073 |
| Lu2024.pdf | lu2024ai.pdf | lu2024ai | 2408.06292 |
| Wei2022.pdf | wei2022chain.pdf | wei2022chain | 2201.11903 |
| Yao2023.pdf | yao2023tree.pdf | yao2023tree | 2305.10601 |
| Shao2024.pdf | shao2024storm.pdf | shao2024storm | 2402.14207 |

## D7验证中参考PDF的作用

| 可验证项 | 无PDF | 有PDF |
|:---------|:-----:|:-----:|
| 数值声称验证（"Method X achieves 99.3%"） | 凭标题猜 | 逐字核对 |
| 引用链传播检测（引原始论文但数值来自复现论文） | 无法发现 | 交叉比对 |
| 归因准确性（论文是否准确反映参考文献结论） | 无法判断 | 原文对质 |
| 筛选偏倚（是否忽略矛盾文献） | 无法发现 | 需专业知识 |
