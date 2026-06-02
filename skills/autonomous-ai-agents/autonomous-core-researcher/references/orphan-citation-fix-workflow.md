# 孤儿引用修复工作流（2026-05-29 实战）

## 问题定义

论文有 `\cite{}` 调用但无任何 bibliography：
- 无 `.bib` 文件 (`@article{...}` 条目数 = 0)
- 无 `\begin{thebibliography}` 
- 无 `\bibliography{}` 命令
- BBL 文件仅有模板骨架（0 bibitem）
- pdflatex 编译显示 N 个 "Citation undefined" 警告

## 检测方法

```bash
# 对每个论文目录，检查是否有引用但无参考文献
cd /path/to/paper/dir

# Step 1: 检查有无引用
cite_count=$(grep -c '\\\\cite{' *.tex 2>/dev/null || echo 0)

# Step 2: 检查有无 bib 文件
bib_count=$(grep -c '@' *.bib 2>/dev/null || echo 0)

# Step 3: 检查有无 inline bibliography
thebib_count=$(grep -c 'thebibliography' *.tex 2>/dev/null || echo 0)

# Step 4: 判断是否为孤儿引用
if [ "$cite_count" -gt 0 ] && [ "$bib_count" -eq 0 ] && [ "$thebib_count" -eq 0 ]; then
    echo "🔴 ORPHAN CITATIONS: ${cite_count} cite(s), 0 bib entries"
fi
```

## 修复流程（四步法）

### Step 1: 提取所有唯一引用键

```bash
grep -oP 'cite\{[^}]*\}' article.tex | grep -oP '\{[^}]+\}' | tr -d '{}' | tr ',' '\n' | sed 's/^ *//' | sort -u | grep -v '^$'
```

### Step 2: OpenAlex 串行验证（每篇间隔 ≥2s）

根据论文上下文推断每个 bibkey 对应的真实论文。从上下文提取线索：
- 作者姓氏 + 年份（如 `wu2021` = Wu et al. 2021）
- 论文中描述的发现/方法
- 机构名（Wenzhou People's Hospital → 该组论文）

使用 OpenAlex 单论文/短关键词查询验证：

```python
import requests, time

# 方法A: 按具体作者+年份搜索
r = requests.get(
    'https://api.openalex.org/works?search=wu+semicircular+canal+spatial+attitude&per_page=3',
    timeout=30
)

# 方法B: 按已知 DOI 直接查询（最可靠）
r = requests.get(
    'https://api.openalex.org/works/doi:10.3389/fneur.2021.741948',
    timeout=30
)

time.sleep(2)  # 间隔防限速
```

**验证内容**：年份、作者姓氏、标题关键词、期刊名。至少匹配 2/4 才确认。

### Step 3: 构建 references.bib

每个条目包含：`author`, `title`, `journal`, `year`, `volume`, `pages`, `doi`

条目格式示例：
```bib
@article{wu2021,
  title    = {Measurement of Human Semicircular Canal Spatial Attitude},
  author   = {Wu, Shuzhi and Lin, Ping and others},
  journal  = {Frontiers in Neurology},
  year     = {2021},
  volume   = {12},
  pages    = {741948},
  doi      = {10.3389/fneur.2021.741948}
}
```

**未验证条目处理**：
- 能从上下文确定引用内容的 → 创建条目，加 `note = {DOI verification pending}`
- 完全不确定的 → 留空（比编造 DOI 好）

### Step 4: 插入编译命令 + 三遍编译

```latex
% 在 \end{document} 前添加
\bibliographystyle{IEEEtran}
\bibliography{references}
```

```bash
pdflatex article.tex && bibtex article && pdflatex article.tex && pdflatex article.tex

# 验证 0 undefined citations
grep -c "undefined" article.log || echo "0 undefined — OK"
```

## 实战数据（2026-05-29，3D-Sobel 论文）

| 指标 | 修复前 | 修复后 |
|:-----|:------:|:------:|
| Bib 条目 | 0 | 13 |
| 编译页数 | 10p (全是 [?]) | 11p |
| Undefined citations | 30 | 0 |
| OpenAlex 验证条目 | — | 8/13 |
| 上下文构造条目 | — | 5/13 (标记 pending) |
| D7 估计值 | 0.50 | ~0.85 |

## 引用消除顺序

按上下文确定性从高到低：

1. **同一研究组的论文**（Wenzhou People's Hospital vestibular 组）— 可通过作者+机构验证
2. **知名经典文献**（Sobel operator, Canny 等）— 无法 DOI 验证时可用课本引用
3. **其他组的方法学论文**— 需搜索验证标题+DOI

## 已知陷阱

1. **Bibkey 年份不匹配**：`cheng2019` 可能实际发表于 2018 年。以实际 publication_year 为准，bibkey 是为了引用的一致性，年份字段应该是真实发表年
2. **OpenAlex 搜索噪声高**：通用术语（"Sobel edge detection BPPV"）会返回不相关结果。优先用 + 具体作者名
3. **多个 bibkey 指向同一论文**：如 `yang2021` (preprint) 和 `yang2022` (journal) 指向同一篇论文的不同版本。合并为一个 bibkey
4. **不要编造 DOI**：仅当 OpenAlex 返回明确的 doi 字段时才使用。未验证的条目用 `note = {DOI verification pending}`
