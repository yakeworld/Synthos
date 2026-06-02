# 参考文献PDF下载策略（降级方案）

> **核心原则：NotebookLM 是参考文献的真相源。** 论文写作不需要本地PDF。`pdfs/` 是可选离线备份，非写作前提。
> 仅当你想把论文 PDF 目录打包带走时，才需要此文档。

## 数据源优先级

| 来源 | 成功率 | 备注 |
|:-----|:------:|:-----|
| **arXiv** `arxiv.org/pdf/{id}` | ~100% | 最高优先级，最可靠 |
| **Semantic Scholar OA** `api.semanticscholar.org` | 30-50% | 金/绿OA可下载 |
| **PubMed Central** `ncbi.nlm.nih.gov/pmc/` | 30-50% | 医学论文不错 |
| **DOI直接解析** `doi.org/{doi}` | <10% | 大部分被付费墙挡 |
| **→ 记录到 missing.txt** | — | 非致命，NotebookLM已有 |

## 脚本使用

```bash
cd outputs/papers
python3 pdf_collect.py
```

脚本位置：`outputs/papers/pdf_collect.py`

## NotebookLM 文本提取（降级备选）

当无法下载PDF时（大部分付费期刊），可用 NotebookLM 提取全文文字：

```bash
notebooklm use <project_id>          # 论文对应的项目
notebooklm source list                # 所有源文件
notebooklm source fulltext <id> -o pdfs/<key>.txt
```

这是文本不是PDF，但包含完整引用内容，可用于D3数据验证。

## 常见失败模式

| 现象 | 原因 | 处理 |
|:-----|:-----|:-----|
| DOI下载返回2-5KB HTML | 付费墙重定向到登录页 | 标记为 missing |
| Semantic Scholar 返回空 | 该论文无OA版本 | 标记为 missing |
| arXiv 404 | 论文已撤回或ID错误 | 检查 arXiv ID |
| PDF内容为空/乱码 | 下载过程中截断 | 重试 |

## 参考

- `paper-pipeline` skill 的 `references/ref-pdf-collection.md`
- `outputs/papers/pdf_collect.py`
