---
name: synthos-writing-workflow
description: "杨晓凯写作方法论 — PDF→MD管线 + 引用铁律 + 09-dir标准化 + 双质检闭环。核心：凡引必验、凡写必检、凡投必整。"
version: 1.0.0
author: Synthos
license: MIT
metadata:
  hermes:
    tags: [writing, paper, workflow, quality, references]
---

---

## 原理层·文言

> 「述而不作，信而好古。」凡引必验，凡写必检，凡投必整。
> 「致广大而尽精微。」PDF转文，逐问而作，双检为门。
> 技术为器，哲学为魂，文以载道。# 杨晓凯写作方法论 — Synthos Writing Engine

> **核心原则**: 凡引必验，凡写必检，凡投必整。
> 所有步骤自动化执行，不等确认，一次完成。

## P0 预检阶段（引用系统清理）

### 0.1 D10a 僵尸/孤儿检测

**必须执行**，不跳过。在标准化 09-dir 前先清引用。

```python
import re
with open('paper.tex') as f: tex = f.read()
with open('references.bib') as f: bib = f.read() if '\\begin{thebibliography}' not in tex else ''

if '\\begin{thebibliography}' in tex:
    # thebibliography mode: extract bibitems
    bib_keys = set(re.findall(r'\\bibitem\{([^}]+)\}', tex))
else:
    bib_keys = set(re.findall(r'@\w+\{([^,]+),', bib))

tex_cites = set()
for m in re.finditer(r'\\cite[tp]?\s*\{([^}]+)\}', tex):
    for k in m.group(1).split(','): tex_cites.add(k.strip())

orphan = tex_cites - bib_keys   # 零容忍
zombie = bib_keys - tex_cites   # 需清理
print(f"引用: {len(tex_cites & bib_keys)} | 孤儿: {len(orphan)} | 僵尸: {len(zombie)}")
```

**阈值**: 孤儿=0（必须修复），僵尸=0（清理）。
**行动**: 孤儿→补 bib 或删 \\cite；僵尸→删 bibitem。

### 0.2 DOI 注入

使用 thebibliography 时，为每条 bibitem 追加 DOI：

```python
doi_map = {
    'Key2023': '10.xxxx/xxxxx',
    # ...
}
```

模式：在 bibitem 末尾的 `.` 前插入 `\\href{https://doi.org/{doi}}{DOI: {doi}}`。

### 0.3 目录标准化（09-dir）

| 目录 | 内容 |
|:-----|:------|
| `01-manuscript/` | 主手稿 `.tex` + `.pdf` |
| `02-submission/` | 投稿包（手稿+图表+cover letter） |
| `03-code/experiments/` | 实验代码 + 结果JSON + README |
| `04-data/` | 数据文件（或symlink） |
| `05-figures/` | 所有 Figure（PDF+PNG） |
| `06-references/` | `references.bib` + `pdfs/` + `pdfs_md/` |
| `07-quality/` | Layer A/B 质检报告 |
| `08-records/` | `CHANGE_LOG.md` + `TODO.md` |
| `09-background/` | 旧版本 + 评阅材料 |

```bash
for d in 01-manuscript 02-submission 03-code 04-data 05-figures 06-references 07-quality 08-records 09-background; do
    mkdir -p "$d"
done
mkdir -p 03-code/experiments 06-references/pdfs 06-references/pdfs_md
```

**铁律**: TeX 编译时在 `01-manuscript/` 内执行，用 symlink 链接外部资源：
```bash
cd 01-manuscript/
ln -sf ../figures figures
ln -sf ../references.bib .
```

## P1 参考文献全链条

### 1.1 PDF → MD 标准管线

**每次下载PDF后自动执行**，不做选择。

```bash
uvx markitdown input.pdf > pdfs_md/{bibkey}.md
```

| 结果 | 成功率 | 应对 |
|:-----|:------:|:-----|
| MarkItDown 成功 | ~87% | 直接保存 |
| 无文本层（0 chars） | ~13% | 标记 `[PDF无可提取文本]`，后续手动补摘要 |
| PDF 损坏（xref破损） | ~3% | 同上 |

**验证**：
```bash
file input.pdf | grep -q "PDF document"  # 确认是PDF
pdftotext input.pdf - | wc -c            # >100 → 可提取
```

### 1.2 NotebookLM 上传（全文优先）

上传 MD 而非 PDF。MD 100% 索引成功，PDF 经常 error。

```bash
# 小文件用 $(cat) 直接传
notebooklm source add "$(cat file.md)" --type text --title "{bibkey}" --timeout 120

# 大文件拆分（>80K chars 自动分块）
python3 -c "
with open('file.md') as f: content = f.read()
chunks = [content[i:i+80000] for i in range(0, len(content), 80000)]
for i, chunk in enumerate(chunks):
    subprocess.run(['notebooklm', 'source', 'add', '--type', 'text',
        '--title', f'Batch {i+1}/{len(chunks)}', chunk])
"
```

### 1.3 DOI 验证（引用铁律）

**凡引必验，不验不刊。**
- 每篇引用必须有 DOI（thebibliography 模式也必须加）
- 无全文的尽量不引（arXiv + PMC 优先）
- 未发表的绝不引（包括自己的 "in preparation"）
- LLM 生成的 bibitem 必须经 SS/Crossref/PubMed 三方验证

## P2 质量检查（双质检）

### 2.1 Layer A（自动门）

| 维度 | 阈值 | 检查 |
|:-----|:----:|:-----|
| D8 参考文献数 | ≥30 | Bib条目计数 |
| D9 PDF覆盖率 | ≥80% | `pdfs_md/` 文件数 / bib条目数 |
| D10a 引用一致性 | 0孤儿/0僵尸 | P0.1 检测结果 |
| 编译 | 0 error | `pdflatex` 两次编译 |

### 2.2 PDF → MD 转换（Layer B 前置）

**Layer B 有效的前置条件**：所有参考文献必须在 NotebookLM 中以 MD 形式存在。
- PDF 上传→status=error（无可提取文本）
- MD 上传→100% ready ✅

### 2.3 Layer B（NotebookLM 7维评审）

创建 Owner 项目，上传论文全文 + 所有参考文献 MD，调用：

```
请对论文进行全面7维SCI质量评审，每维评分(0-1)和改进建议：
D1 科学贡献(Scientific Contribution)
D2 方法学严谨性(Methodological Rigor)
D3 结果可信度(Results Credibility)
D4 完整性(Completeness) — IMRaD+表≥2+Limitations≥3
D5 清晰性(Clarity) — CARS Introduction
D6 新颖性(Novelty) — 非"没人做过"而是"有理由必须做"
D7 引用质量(Citation Quality) — DOI完整性

请逐维评分并给出具体改进建议。最后计算平均分。
```

**评分校准**：NotebookLM 评分偏高 +0.05~0.15，视为上限。

## P3 投稿准备

### 3.1 提交包

```bash
mkdir -p 02-submission/
cp 01-manuscript/hcs3wt-breast-cancer.pdf 02-submission/manuscript.pdf
cp 01-manuscript/hcs3wt-breast-cancer.tex 02-submission/manuscript.tex
cp 05-figures/*.pdf 02-submission/figures/
tar czf 02-submission/submission-package.tar.gz 02-submission/
```

### 3.2 投稿前检查清单

- [ ] Layer A: D8≥30 ✅ | D9≥80% ✅ | D10a=0 ✅ | 编译=0 ✅
- [ ] Layer B: avg≥0.80 (T2) 或 ≥0.85 (T1)
- [ ] 所有L0.5 问题已修复（若有检出）
- [ ] CHANGE_LOG.md 完整
- [ ] 09-dir 结构就绪
- [ ] REFERENCES.md 含DOI列表
- [ ] 投稿包 `.tar.gz` 已生成

## Tool-Specific Knowledge

### MarkItDown
```bash
# 安装
uv tool install markitdown --with markitdown[pdf]

# 单文件
uvx markitdown input.pdf > output.md

# 批量
for f in pdfs/*.pdf; do
    uvx markitdown "$f" > "pdfs_md/$(basename $f .pdf).md"
done
```

### NotebookLM CLI
```bash
# 创建项目
notebooklm create "项目名称"

# 上传MD（全文）
notebooklm source add "$(cat file.md)" --type text --title "标题" --timeout 120

# 7维评审
notebooklm ask "7维SCI评审prompt（见P2.3）" --timeout 300

# 上传大文件（>80K chars）
notebooklm source add file.md --type file --title "标题" --json
# status=3 (preparing) 正常，几秒后自动ready
```

## Pitfalls

1. **$() 参数超长**: `source add "$(cat file.md)"` 在文件>100KB时报 `参数列表过长`。改用 `--type file` 或 Python subprocess。
2. **PDF xref 损坏**: 部分下载的PDF头正确但xref表破损，pdftotext=0且pdfinfo报错。这类PDF无法提取文本，必须找替代源。
3. **arXiv PDF 无文本层**: ~15%的旧arXiv PDF也是扫描版。先 `pdftotext arXiv.pdf - | wc -c` 检查。
4. **DOI 误注入**: 部分thebibliography条目末尾不是 `.` 而是 `)`。DO注入前先检查：`if content.rstrip().endswith('.'): ...`
5. **09-dir 后编译路径错**: TeX中 `\includegraphics{figures/xxx.pdf}` 在01-manuscript/下找不到figures/。必须 `ln -sf ../figures figures`。
6. **thebibliography 中的 DOI**: 用 `\\href{https://doi.org/{doi}}{DOI: {doi}}` 而非 `\\doi{...}`，elsarticle模板已有hyperref。
7. **NotebookLM Shared 项目无法删除 source**: Shared项目 `source delete` 报告成功但实际不生效。必须Owner项目才能删除。
8. **数据泄露：CSV副本列**: PIDD 等数据集常同时有 `Outcome` 和 `Diabetes_binary`（目标副本），加载时只 drop `Outcome` 则 `Diabetes_binary` 仍作为特征泄露目标。详见 `references/data-leakage-detection.md`。
9. **Layer B D5 误判**: pdftotext 提取的 PDF 文本含 ligature 断裂（`ff`→乱码），导致 Gemini 误评 D5 清晰性低。上传 `.tex` 源文件而非 pdftotext 提取文本到 NotebookLM。

## Reference Files

- `references/data-leakage-detection.md` — 数据泄露检测：CSV副本列污染审计与修复

8. **🔴 CSV 数据文件中的重复目标列**: 预处理阶段可能意外在数据集中保留目标变量的副本列（如 `Outcome` 和 `Diabetes_binary` 同时存在）。当 `drop('Outcome')` 后 `Diabetes_binary` 仍作为特征保留，所有模型获得 F1=1.0 的虚假性能。加载数据时检查：`feat = [c for c in df.columns if c not in ('target', 'label', 'Outcome', 'Diabetes_binary', 'ID', 'Unnamed: 0')]` + 打印 `print('Target leak detected:', 'Diabetes_binary' in df.columns and 'Outcome' in df.columns)`。
9. **🔴 CDC 全量基准过慢**: CDC BRFSS (253K 行) 跑 34 模型 × 3×2 CV 需要 10+ 小时。SVC/RadiusNeighbors/LabelPropagation 是 O(n²) 瓶颈。修复：采样 10% (25K 行) 足够估算泄漏天花板，或跳过 SVC 等慢模型。采样代码：`df = df.sample(frac=0.1, random_state=42)`。
