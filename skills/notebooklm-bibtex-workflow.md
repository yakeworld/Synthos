# NotebookLM BibTeX → PDF 工作流

## 核心原理

```
NotebookLM源文件（网页/PDF）
    ↓ Ask: "生成BibTeX"
BibTeX 元数据（作者/标题/DOI/arXiv ID）
    ↓ 用DOI或arXiv ID下载
PDF 文件（{bibkey}.pdf 统一命名）
    ↓ source add 上传
NotebookLM源文件（PDF格式）
```

## 分步流程

### Step 1: NotebookLM生成BibTeX
```bash
notebooklm ask "为所有源文件生成BibTeX条目，包含DOI或arXiv ID"
```
输出保存到论文目录：`notebooklm-sources.bib`

### Step 2: 用BibTeX元数据下载PDF
```bash
# 方法A: arXiv ID → 直接下载
# https://arxiv.org/pdf/2408.06292.pdf → lu2024aiscientist.pdf

# 方法B: DOI → 下载
# https://doi.org/10.48550/arXiv.2212.08073 → bai2022constitutional.pdf

# 方法C: Semantic Scholar API → 搜索+下载
# curl "https://api.semanticscholar.org/graph/v1/paper/search?query=..." 
```

### Step 3: 统一命名 → 上传
```bash
# 下载到 pdfs/{bibkey}.pdf
# 然后 source add 上传到NotebookLM
notebooklm source add pdfs/lala2023paperqa.pdf --title "lala2023paperqa"
```

## 与旧流程的区别

| 旧流程（问题） | 新流程（正确） |
|:--------------|:--------------|
| `add-research` 搜索→导入网页 | NotebookLM生成BibTeX→独立下载PDF |
| `source add` 直接传本地文件名 | 先按bibkey重命名再上传 |
| 文件名与bibkey不匹配 | 文件名=bibkey |
| 参考文献验证靠猜 | 有全文PDF可交叉核对 |

## 已有工具链

1. `notebooklm-sources.bib` — 从NotebookLM生成的BibTeX元数据
2. `bibkey-map.json` — 手动维护的bibkey↔文件名映射
3. `notebooklm-sources.json` — 已上传源文件清单
4. `notebooklm-sources-sync.py` — 同步脚本
