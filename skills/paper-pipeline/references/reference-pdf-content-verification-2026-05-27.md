# 参考PDF内容验证实战（2026-05-27）

## 问题

Synthos论文库42篇论文的参考PDF存在系统性命名错乱——文件名暗示的论文与实际PDF内容不符。

## 扫描方法

```bash
# 对每个refs-md/下的PDF提取真实内容
for pdf in /media/yakeworld/sda2/Synthos/outputs/papers/*/refs-md/*.pdf; do
    echo "=== $(basename $pdf) ==="
    pdftotext "$pdf" - 2>/dev/null | head -8 | tr '\n' ' ' | head -200
    echo ""
done
```

## 发现的错乱汇总

### iris-3d-anatomical-opt（5个参考PDF）

| 文件名（bibkey） | 实际内容 | 判定 |
|:-----------------|:---------|:-----|
| kothari2021ellseg | EllSeg论文（arXiv:2007.09600 cs.CV） | ✅ 正确 |
| jia2024condseg | CondSeg论文（arXiv:2408.17231 cs.CV） | ✅ 正确 |
| garbin2019openeds | OpenEDS数据集（arXiv:1905.03702 cs.CV） | ✅ 正确 |
| chaudhary2019opensource | Dedekind半环域（arXiv:1907.07162 math.RA） | ❌ 命名错误 |
| perry2020keypoints | 流行病建模（arXiv:2010.15438 math.OC） | ❌ 命名错误 |

### iris-yolo（9个参考PDF）

| 文件名 | 实际内容 | 判定 |
|:-------|:---------|:-----|
| Daugman1993（DOI命名） | High Confidence Visual Recognition (Daugman) | ✅ 正确 |
| Wildes1997（DOI命名） | Iris Recognition: An Emerging Biometric Technology | ✅ 正确 |
| chaudhary2019 | Even A-cycles edge-Erdos-Posa性质（图论） | ❌ 命名错误 |
| sapkota2026 | 最优码与广义汉明重量（编码理论） | ❌ 命名错误 |
| sulake2026 | 语音表征学习 | ❌ 命名错误 |
| tian2025 | Dirac方程的解（数学物理） | ❌ 命名错误 |

### cuteye-model（3个参考PDF）

| 文件名 | 实际内容 | 判定 |
|:-------|:---------|:-----|
| kothari2021ellseg（DOI命名） | EllSeg论文（正确内容） | ✅ 内容正确，文件名已含bibkey |
| jia2024condseg | CondSeg论文（空文件<1KB） | ❌ 空文件 |
| 10-1109_ICCVW-2019-00271 | 双目立体匹配（人物匹配） | ❌ 应为chaudhary2019ritnet(RITnet) |

### hcs3wt-breast-cancer（1个参考PDF）

| 文件名 | 实际内容 | 判定 |
|:-------|:---------|:-----|
| bischl2025 | JSS统计软件mlr包 | ⚠️ 内容与bibkey匹配，但和论文主题(乳腺癌)无关——mlr包可能是实验工具引用 |

## 根因分析

所有错误PDF都有一个共同模式：
1. **arXiv ID被复制到错误文件的元数据中** — `chaudhary2019opsource.pdf` 和 `chaudhary2019.pdf` 的arXiv ID都是 `1910.00642`，但一个是Dedekind半环域，一个是图论
2. **DOI/arXiv ID被LLM随机赋值** — 同一个arXiv ID（1910.00642）被赋给两个完全不同主题的PDF
3. **PDF文件名基于"看起来对的"bibkey** — 文件名正确，但下载内容是错误的

## 修复策略

1. 对有 `references.bib` 的论文：从bib提取正确的DOI/arXiv ID
2. 用Semantic Scholar API验证DOI对应的论文标题是否与bib中一致
3. 不一致的：从arXiv或OA源重新下载
4. 无法下载的：在manifest中标记为 `paywalled`，保留bib元数据作为可搜索引用

## 工具选择

| 任务 | 工具 | 性能 |
|:-----|:-----|:-----|
| PDF内容提取 | `pdftotext`（poppler-utils） | 最快，arXiv论文提取质量好 |
| PDF内容提取 | `pdfminer.six`（Python） | 较慢但提取更完整 |
| 批量下载 | Semantic Scholar API | 只有OA论文返回PDF URL |
| 批量下载 | `requests.get(doi.org)` | 几乎全部返回HTML（付费墙） |
| 批量下载 | arXiv直接下载 `arxiv.org/pdf/XXXX.XXXXX.pdf` | 免费、稳定、速度快 |
