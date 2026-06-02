# 编造 bib 条目替换实战案例（2026-05-30）

## 场景
论文 `3d-sobel-edge-detection` 在 D8 检查中显示 13 条 bib 条目，全数被 `\cite{}` 引用（D10a=100%），表面正常。但 5/13 条目标记为 "DOI verification pending"。

## 检测过程

### Step 1: 识别可疑条目
```bash
grep -i "pending" references.bib
```
返回 5 条：
- `yang2023` — "Virtual simulation analysis of BPPV repositioning maneuver mechanics"
- `schmittwilken2022` — "Edge detection processes in human vision"
- `tang2023` — "Effectiveness of combining Sobel operators with deep learning for breast mass"
- `alshayeji2017` — "Domain-specific edge detection methods for retinal imaging"
- `yang2017` — "Otsu's method for membranous labyrinth segmentation from MRI"

### Step 2: OpenAlex 验证（全部失败）
对每条条目执行 OpenAlex 搜索（按标题关键词搜索）：
```python
import requests
r = requests.get("https://api.openalex.org/works?search=前6个关键词&per_page=3", timeout=30)
```

**结果：5/5 全部返回错误论文。** 无任何条目在学术数据库中存在。
- yang2023 返回了 VR rehabilitation 论文（无关）
- schmittwilken2022 返回了裂纹检测论文（无关）
- tang2023 返回了叶片分割论文（无关）
- alshayeji2017 返回了数据增强综述（无关）
- yang2017 返回了结肠镜分割论文（无关）

**附加搜索：** 尝试通过 Semantic Scholar API 验证 → 同样无结果。

### Step 3: 替换策略
无法找到原本描述的真实论文 -> 选择主题匹配但真实的论文替换：

| 被替换键 | 新键 | 论文 | DOI | 选择理由 |
|:---------|:-----|:-----|:----|:---------|
| yang2023 | vaidyanathan2021inner | Inner ear MRI segmentation | 10.1038/s41598-021-82289-y | 内耳MRI自动分割，主题匹配 |
| schmittwilken2022 | ahmadi2021iemap | IE-Map inner ear atlas | 10.1038/s41598-021-82716-0 | 内耳解剖标准化空间 |
| tang2023 | gerb2020volt | VOLT endolymphatic pipeline | 10.1007/s00415-020-10062-8 | 内耳MRI处理管线 |
| alshayeji2017 | wang2021temporal | Temporal bone CT segmentation | 10.1186/s12880-021-00698-x | 颞骨医学影像分割 |
| yang2017 | lorensen1987marching | Marching cubes 3D | 10.1145/37401.37422 | 经典3D表面重建 |

### Step 4: tex 上下文重写
每个替换必须同时修改 `.tex` 中对应的引用句子。

### Step 5: 编译验证
```bash
rm -f article.aux article.bbl article.blg
pdflatex article.tex && bibtex article && pdflatex article.tex && pdflatex article.tex
grep -c "undefined citation" article.log  # 应为 0
```

### 额外添加的经典文献
| BibKey | 论文 | 引用数 |
|:-------|:-----|:------|
| canny1986 | Canny edge detection | 29,014 |
| marr1980 | Theory of edge detection | 6,187 |
| otsu1979 | Otsu thresholding | 42,981 |

## 关键教训

1. **pending = 编造** — 2026-05-30 实战中 5/5 的 pending 条目全部不真实。
2. **D10a=100% 也不安全** — 编造条目可以被完美引用而 D10a 完全通过。
3. **替换必须改 tex 上下文** — 保留旧引用句子但换 bibkey 会导致内容与引用不符。
4. **优先加经典文献** — Canny 1986、Otsu 1979、Marr 1980 等可通过单论文 DOI 查询快速验证，不会编造。
5. **单论文 DOI 查询是唯一可靠验证方式** — OpenAlex 主题搜索可能返回噪声。
