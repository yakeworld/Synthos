---
name: paper-literature-supplement
category: pipeline
description: "论文文献补充管道 — ACQ→EXT→下载→质检。输入论文目录，输出补齐至30篇引用+PDF。"
version: 2.0.0
chain:
  - knowledge-acquisition
  - knowledge-extraction
  - download
  - quality-gate
---

# Paper Literature Supplement — 论文文献补充管道

> 凡文必配30引。不足则补，缺源则索。

## IO_CONTRACT

- **input**: `paper_dir: path` — 论文目录（含 `paper.tex`，引用经 `.bbl` 或内联 `\bibitem` 解析）
- **input**: `topic_queries: list[str]` — 按主题聚类的检索词（每方向 1 次，替代逐篇检索）
- **input**: `MEDDATA_PASSWORD: env` — MedData 机构库 SSO 凭证（用于无 DOI 论文的 PMID 全文获取）
- **output**: `papers/*.pdf` — 补齐至 30+ 篇引用对应的 PDF 全文（%PDF- 魔数验证，无 PDF 引用删除）
- **output**: `paper.tex` / `.bbl` — 修正后的引用清单（DOI 已 Crossref/PubMed 人工核对）
- **output**: `quality-gate result` — D8 引用完整性 ≥80%、D10a bib-tex 匹配 ≥90%、无 undefined citation 的质检结论

## 原则 (Principles)

- **凡文必配30引**：引用不足则补，缺源则索；无 PDF 之引用（%PDF- 魔数不验）必删，留 20 篇以上即止，宁缺毋滥。
- **聚类以省工**：逐篇检索则 80 次费时超时，聚为 5 方向各检索 1 次，分发其果；一维一修，检索只走 `literature.py` 一途，不写第二。
- **凡引必核**：Crossref 自动匹配不可信（或返无关论文），DOI 必人工核标题与年份；凡数必源，每数据点可溯至原文。
- **运行即证**：每步执行后验证，不通则停；管道所产当为可用 PDF 与可编译 tex（去形留神），不留中间文件。

## 聚类检索优化（2026-07-11）

替代逐篇检索。80 篇论文按主题聚为 5 个方向，每方向 1 次检索：

```bash
# 5 个聚类各搜一次，结果分发到聚类内所有论文
for query in "corneal biomechanics ODE" "vestibular VOR nystagmus BPPV" \
             "iris pupil segmentation" "saccade eye movement fixation" \
             "clinical machine learning breast cancer"; do
  literature search "$query" --sources crossref pubmed --max 100 > cluster_result.json
done
# 之前: 80 次检索 × 30s = 40 分钟 → 超时
# 现在: 5 次检索 × 30s = 2.5 分钟 → 可行
```

## 批量修复（batch_fix_all.py）

对所有论文批量补 DOI + 下载 PDF。脚本位置: `scripts/batch_fix_all.py`

```bash
python3 /media/yakeworld/sda2/Synthos/skills/extended/paper-literature-supplement/scripts/batch_fix_all.py
```

实测结果: 88 篇论文, ~430 引用, DOI 覆盖率 0%→82%, PDF 464→887

## 2026-07-11 实测更新

- **default max**: 100（之前 10）。`literature search "topic"` 默认返回 100 篇。
- **年份**: 默认不限。需按需加 `--year-range 2021-2026`。
- **DOI 验证**: Crossref 自动匹配不可靠。对无 inline DOI 的引用（如 `\\bibitem{key}` 无 `\\url{10.xxx}`），需手动查 PubMed/Crossref 验证。
- **引用格式**: inline thebibliography（71%）和 .bbl（29%）两种。优先读 .bbl，没有则解析 paper.tex 内的 `\\bibitem`。
- **子 Agent**: delegate_task 时只传 goal 不加 context。子 Agent 会自动找 `literature` CLI 或 fallback 到 `standalone-literature-search`。

## 哲学约束

- **一维一修** — 文献检索只有一条路：literature.py。不写第二个。
- **凡数必源** — 每个数据点可追溯到原始论文或代码输出。
- **去形留神** — 管道产出的是可用的 PDF + 可编译的 tex，不是中间文件。
- **运行即证** — 每步执行后验证，不通则停。

## 管道流程

```
输入: 论文目录 (含 paper.tex)
│
├─ Step 1: ACQ — 文献检索
│   literature search "关键词" --sources crossref pubmed --max 100
│   → 候选论文
│
├─ Step 2: EXT — 提取引用
│   从 paper.tex 解析 \\bibitem{key} + DOI
│   查 .bbl（有）或 paper.tex 内联（无 .bbl）
│   → 已有引用列表
│
Phase 3: 全文下载
    │   Sci-Hub CDN: https://sci.bban.top/pdf/{doi}.pdf（直连 PDF，无需 HTML 中转）
    │   唯一有效入口，所有有 DOI 的论文自动通过 bban.top 直连下载
│   → PDF 文件
│
├─ Step 4: 验证引用
│   逐篇查 Crossref/PubMed 验证 DOI 正确性
│   → 修正错误匹配
│
├─ Step 5: quality-gate
│   D8: 引用完整性 ≥ 80%
│   D10a: bib-tex 匹配 ≥ 90%
│   无 undefined citation
│
└─ 输出: 补齐至 30+ 篇引用
```

## 调用方式

```bash
# literature CLI 全局安装
literature search "topic" --sources crossref pubmed --max 100

# 下载单个 DOI
curl -sL "https://sci.bban.top/pdf/{doi}.pdf" -o paper.pdf
```

## 成熟脚本

| 步骤 | 脚本 | 路径 |
|------|------|------|
| ACQ | literature CLI | `literature search`（全局命令） |
| 下载 | Sci-Hub CDN | `sci.bban.top/pdf/{doi}.pdf` |
| 验证 | Crossref API | `api.crossref.org/works?query=` |
| 质检 | quality-gate | `core/quality-gate` |

## MedData 搜索集成（2026-07-12 验证）

MedData 支持全文关键词搜索，返回真实 PMID → 可下载真实 PDF。已完整验证 5/5 成功。

### 完整流程（Python）

```python
# 1. SSO → token → 搜索 → 获取 PMID
body = {"exp":"bppv nystagmus","current":1,
        "filter":[{"searchWorld":50,"searchValueList":[]}],
        "filterRang":[],"token":token,"conn":0}
url = f"http://www.meddata.com.cn/api/result/search?current=1&size=10&token={token}"
# → 返回 records: [{pmid, doi, articleTitle, abstractText}]

# 2. full_look(pmid=真实PMID, doi=DOI) → status=2, fileName=xxx
# 3. wait 10s → viewtext(fileName=xxx) → 真实 PDF ✅
```

### 已验证
- 5/5 全部返回真实 PDF（187KB~5299KB）
- 无 DOI 仅 PMID 也能下载
- SPA 页面的 REST API，不需要浏览器

### 注意
- `~/.secrets` 密码可能被截断。验证：`echo ${#MEDDATA_PASSWORD}` 应 ≥ 6
- `pmid=1` 不工作（占位 PDF）。必须用真实 PMID
- 搜索接口返回的 DOI 可能带 HTML 高亮标签 `<span style='color:#F2A620'>`

## 陷阱

1. **不要写批量脚本** — 每篇论文单独处理。83 篇批量被证实不可行。
2. **S2 限流** — literature.py 含 S2 时 429 阻塞 60s+。去掉 S2 用 crossref+pubmed。
3. **CDN 命中率 ~10%** — 2020+ 新论文不在 CDN 上。接受低命中率。
4. **delegate_task 不加微操** — 只传 goal（用户原话），不加 context 指令。
5. **无 PDF 的引用一律删除** — 保留引用数不低于 20 篇即可。
6. **Crossref 自动匹配不可靠** — 一个查询可能返回完全不相关的论文。必须人工核对标题和年份。
7. **context-compression 阈值** — 当前配置 700K/1M（threshold=0.7），不要手动改 config.yaml，用 `hermes config set`。

## 验证清单 (Verification)

- [ ] 检索经聚类（每方向 1 次 × 5 聚类）而非逐篇 80 次检索
- [ ] 引用优先读 .bbl；无 .bbl 时解析 paper.tex 内联 `\bibitem`
- [ ] Crossref 自动匹配的 DOI 已人工核对标题+年份（匹配不可靠）
- [ ] 无 PDF 的引用已删除，保留引用数 ≥ 20 篇
- [ ] quality-gate 通过：D8 引用完整性 ≥80%、D10a bib-tex 匹配 ≥90%、无 undefined citation
- [ ] delegate_task 子 Agent 只传 goal 不加 context 微操
