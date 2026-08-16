---
name: paper-literature-supplement
category: pipeline
description: 论文文献补充管道 — ACQ→EXT→下载→质检。输入论文目录，输出补齐至30篇引用+PDF。
version: 2.0.0
signature: 'paper_dir: path, topic_queries: list[str] -> papers/*.pdf (30+), paper.tex/.bbl
  (DOI 核对), quality-gate result (D8≥80%, D10a≥90%)'
chain:
- knowledge-acquisition
- knowledge-extraction
- download
- quality-gate
license: MIT
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


## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[PAPE-001]** 当论文数量庞大（如80篇）且需补充文献时 → 按主题聚类为5个方向，每方向仅执行1次检索并分发结果，避免逐篇检索导致的超时
- **[PAPE-002]** 当解析论文引用列表时 → 优先读取 `.bbl` 文件，若不存在则解析 `paper.tex` 中的内联 `\bibitem` 格式
- **[PAPE-003]** 当获取到 Crossref 自动匹配的 DOI 时 → 必须人工核对标题与年份以验证准确性，因自动匹配常返回无关论文
- **[PAPE-004]** 当引用对应的 PDF 文件未通过 `%PDF-` 魔数验证时 → 直接删除该引用，确保保留的有效引用数不低于 20 篇
- **[PAPE-005]** 当执行文献检索任务时 → 仅使用 `literature.py` 单一入口，禁止编写第二套检索逻辑或跨论文批量脚本
- **[PAPE-006]** 当通过 MedData 获取无 DOI 论文的全文时 → 必须使用搜索接口返回的真实 PMID，严禁使用 `pmid=1` 等占位符
- **[PAPE-007]** 当通过 delegate_task 委派子 Agent 执行任务时 → 仅传递 goal（用户原话），禁止添加 context 微操指令

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


## Golden 集合 · GOLDEN SET

- **Golden Input**: `paper_dir: "outputs/papers/pima-crispdm"`（引用经 .bbl 解析，22 篇），`topic_queries: ["corneal biomechanics ODE", "vestibular VOR nystagmus BPPV"]`
- **Golden Output**: 引用补齐至 ≥30 篇且每篇 PDF 过 `%PDF-` 魔数验证；quality-gate 结论 D8 ≥80%、D10a ≥90%、无 undefined citation；无 PDF 引用已删除且剩余 ≥20 篇
- **Golden Error**: Crossref 自动匹配返回不相关论文 → 必须人工核对标题+年份后修正 DOI；MedData `pmid=1` 占位 PDF（非真实全文）→ 视为下载失败，不得计入

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
|