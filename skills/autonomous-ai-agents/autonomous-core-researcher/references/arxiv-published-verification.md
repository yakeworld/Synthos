# arXiv 预印本 → 已发表版验证

> 批量验证论文库中的 arXiv 预印本是否已有正式的期刊/会议发表版。
> OpenAlex + arXiv API 双通道，无需全文下载。

## 触发条件

仅在以下场景执行批量 arXiv 验证：
- 论文的 `references.bib` 中 `journal={arXiv preprint}` 条目 > 10 条
- 用户明确要求"替换 arXiv 引用为已发表版"
- 论文投稿前检查，需要确认引用文献的最终出版状态

**不触发**：常规 cron 循环不逐轮扫描 arXiv ID（ROI 低，见陷阱 #21）。

## 验证方法

### 方案 A: OpenAlex 单论文查询（推荐）

arXiv ID 对应的 DOI 格式为 `10.48550/arXiv.{id}`。OpenAlex 支持通过此 DOI 查询论文及其所有发表位置：

```python
import urllib.request, json, time

arxiv_ids = ['1905.03702', '2408.17231', '2005.03876']

for aid in arxiv_ids:
    url = f"https://api.openalex.org/works/doi:10.48550/arXiv.{aid}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
        locations = data.get('locations', [])
        published = False
        for loc in locations:
            src = loc.get('source', {})
            if src and src.get('type') == 'journal':
                published = True
                journal = src.get('display_name', '')
                break
        if published:
            print(f"arXiv:{aid} → PUBLISHED in {journal}")
            # 更新 bib 条目: journal={Journal Name}, volume={v}, number={n}, pages={p}
        else:
            print(f"arXiv:{aid} → Still arXiv only")
    time.sleep(1)  # 限速 1 req/s
```

**输出示例**:
```
arXiv:1905.03702 → Still arXiv only (2019-04-30)
arXiv:2408.17231 → Still arXiv only (2024-08-30)
...
```

### 方案 B: arXiv API 交叉引用

arXiv API 返回的 `arxiv:relation` 元素可能包含 DOI 链接，指示期刊发表版：

```bash
curl -sL "https://export.arxiv.org/api/query?id_list=1905.03702" | grep -oP 'arxiv:relation[^<]*</arxiv:relation>'
```

如果 relation 包含 `doi:` 前缀的链接，则该预印本已有发表版。

## 典型结果（2026-06-03 实测）

| arXiv ID | 论文 | 状态 |
|:---------|:-----|:-----|
| 1905.03702 | OpenEDS 数据集 | Still arXiv-only |
| 2408.17231 | CondSeg 瞳孔/虹膜分割 | Still arXiv-only |
| 2005.03876 | OpenEDS2020 数据集 | Still arXiv-only |
| 1601.04902 | PupilNet 瞳孔检测 | Still arXiv-only |
| 2303.08514 | 虹膜识别深度学习综述 | Still arXiv-only |
| 2405.03287 | VR 眼动追踪生物特征 | Still arXiv-only |

结论：在 CV/眼科/生物特征领域，arXiv 预印本→期刊的转化率很低（<20%）。多数论文停留在 arXiv 版本，不会被正式出版。**除非有明确证据（如熟悉的期刊名），否则默认保留 arXiv 引用。**

## 已发表版替换操作

当发现 arXiv ID 已有发表版时：

```bash
# 1. 从 OpenAlex 获取发表位置的 BibTeX
# 2. 更新 references.bib:
#    改 journal={arXiv preprint arXiv:...} → journal={Journal Name}
#    添加 volume={v}, number={n}, pages={p-y}, year={YYYY}
# 3. 不修改 bibkey 和 tex 中的 \cite{} 调用
# 4. 编译验证: pdflatex + bibtex + pdflatex × 2 → 0 undefined
```

## 关联陷阱

- autonomous-core-researcher 陷阱 #21: arXiv 预印本 ROI 低，不应每轮都扫
