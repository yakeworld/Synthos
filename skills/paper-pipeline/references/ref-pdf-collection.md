# Reference PDF Collection — 各论文独立 pdfs/ 目录

> 2026-05-22 确立规范。每个论文目录独立 `pdfs/`，不共享不symlink。

## 目录规范

每篇顶层论文（完整SCI论文）的目录结构：

```
论文名称/
├── paper.tex
├── paper.pdf
├── references.bib
├── pdfs/             # ← 参考文献全文PDF，独立副本
│   ├── Author2024.pdf
│   ├── Author2023.pdf
│   ├── ...
│   └── missing.txt   # 无法免费获取的引用清单
└── fig_*.pdf
```

**铁律**：
- 每个论文独立持有PDF副本，不跨论文 symlink
- PDF文件名 = `{FirstAuthor}{Year}.pdf`（与BibTeX key 一致）
- 无法自动下载的引用记录到 `pdfs/missing.txt`

## 自动下载优先级（pdf_collect.py 模式）

优先使用基于 `pdf_collect.py` 的自动化脚本。优先级链：

| 优先级 | 来源 | 成功率 | 适用 |
|:------:|:-----|:------:|:-----|
| **1** | arXiv API (`arxiv.org/pdf/{id}`) | ~100% | arXiv预印本 |
| **2** | Semantic Scholar OA API (`api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=openAccessPdf`) | ~30-50% | 金/绿OA论文 |
| **3** | 直接 DOI 解析 (`doi.org/{doi}`) | ~10% | 部分开放获取 |
| **4** | 标记为缺失 → `missing.txt` | — | IEEE/Elsevier/Springer 付费期刊 |

### 已知DOI补录

许多 `.bib` 文件缺少 `doi` 字段。对于常见论文，需在脚本的 `KNOWN_DOIS` 字典中补充。查找方式：
- Semantic Scholar API：`https://api.semanticscholar.org/graph/v1/paper/search?query={title}&limit=1`
- Crossref API：`https://api.crossref.org/works?query={title}`

## 覆盖期望

| 论文类型 | 合理覆盖 | 说明 |
|:---------|:--------:|:-----|
| AI/ML 系统论文 | 50-60% | arXiv/LNCS/OpenReview 多为开放获取 |
| 医学/AI 应用 | 30-50% | IEEE/Elsevier付费期刊多 |
| 临床医学 | 20-40% | Lancet/NEJM/JAMA 付费严格 |
| BPPV/VOR/解剖 | 40-60% | PubMed Central有相当OA存档 |

## NotebookLM 降级方案

对于无法下载PDF的付费期刊论文，NotebookLM 项目已有源文件（通过 `notebooklm source add file.pdf` 或 `notebooklm source add-research` 导入的PDF）：

```bash
# 提取全文文字（降级方案，非原PDF）
notebooklm use <project_id>
notebooklm source fulltext <source_id> -o pdfs/Author2024.txt
```

注意：
- 仅能做文本提取，无法从NotebookLM导出原始PDF文件
- 适合已有NotebookLM项目的论文做批量文本回补
- 输出为 .txt 文件，非 PDF

## pdfs/missing.txt 格式

```
# Papers not freely available online
# 论文名称.pdfs - N of M missing

Author2023    # doi:10.xxxx/yyyy  (IEEE T-PAMI, paywalled)
Author2021    # doi:10.xxxx/zzzz  (Elsevier, paywalled)
```

用户可通过机构订阅（大学/医院图书馆）手动下载这些论文。

## 参考脚本位置

`outputs/papers/pdf_collect.py` — 可复用脚本。使用方法：

```bash
cd outputs/papers
python3 pdf_collect.py
```
