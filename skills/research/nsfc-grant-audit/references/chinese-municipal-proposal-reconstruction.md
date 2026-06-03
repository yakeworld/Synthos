# Chinese Municipal Proposal Reconstruction Pipeline

> From: 2026-05-16 session — fungal ball sinusitis risk prediction model proposal (温州市科技局)
> Workflow for .doc → quality scan → content correction → reference replacement → verified .docx

## Overview

Chinese municipal science project proposals (市科技局 ~1-5万预算) often have three repeatable quality gaps:
1. **Fabricated references** — English-language references that cannot be verified on PubMed/Semantic Scholar
2. **Inflated statistics** — CT sensitivity, diagnostic accuracy, or epidemiological figures that don't match literature
3. **Missing methodology** — No missing data strategy, sample size justification, or external validation plan

## Pipeline Steps

### Phase 1: Format Conversion

```bash
# .doc (old binary) → .docx (editable)
libreoffice --headless --convert-to docx proposal.doc

# .docx → .txt (for reading/analysis)
libreoffice --headless --convert-to txt proposal.doc
```

### Phase 2: Reference Verification

For each English-language reference, verify against PubMed via E-utilities:

```python
# PubMed E-utilities check — use title + author + journal + year
import requests, time

def verify_ref(title_terms, author_lastname, journal, year):
    """Try multiple search strategies — year-typos are common."""
    for attempt in [year, int(year)-1, int(year)+1]:
        base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": f'({title_terms}) AND {author_lastname}[Author] AND {attempt}[dp]',
            "retmode": "json",
            "retmax": 3
        }
        r = requests.get(base, params=params, timeout=10)
        if r.json()["esearchresult"]["count"] != "0":
            return r.json()["esearchresult"]["idlist"]
        time.sleep(0.5)
    return []
```

**Year-typo pitfall** (2026-05-21实测)：Chinese medical proposals frequently have English references where the stated year is off by 1 (e.g., proposal says 2022 but paper published 2023). This does NOT mean the reference is fabricated — the PubMed entry just has a different year. Always search with year ±1 before flagging as suspect.

Example: `Kim K 2022, CMPB 240:107708` → PubMed search by title found it at `2023` not `2022`. The reference is real (PMID 37473588), just the year was wrong.

**Pattern**: If a search by exact year fails, try the year before and after. Only flag as "suspected fabricated" if no match found across all three year searches AND a broader topic search also fails to locate the paper.

**Real paper replacement strategy**: Search PubMed for the exact topic (e.g., "fungal ball sinusitis risk prediction model") and pick verified papers. Use the found papers' PMID/DOI as evidence.

### Phase 3: CT/Data Accuracy Correction

Common inflated statistics in Chinese medical proposals:

| Claim Type | Typical Inflated Value | Literature Range | Corrected Value |
|:-----------|:----------------------|:-----------------|:----------------|
| CT sensitivity for fungal ball | ~11% negative (89% sensitive) | 20-50% negative (50-80% sensitive) | 20%-40% negative |
| Diagnostic accuracy | 95%+ | Usually 70-85% | Check specific literature |
| Risk factor strength | Often overstated | Check odds ratios | Report with CI |

### Phase 4: Methodology Gap Analysis

Check for these missing items in municipal medical ML proposals:

| Gap | Why It Matters | What to Add |
|:----|:---------------|:------------|
| **Missing data strategy** | Small samples + missing data = biased model | MICE (5 iterations) for <30% missing; exclude ≥30% |
| **Sample size justification** | No power calc → overfitting risk | EPV ≥ 10 (events per variable); Power ≥ 0.80, α=0.05 |
| **Feature selection** | Multi-factor LR without selection → noise inclusion | LASSO (Lambda.1se) + Boruta two-step |
| **External validation** | Internal-only validation → unknown generalizability | Bootstrap 1000x internal + ≥50 independent external cases |
| **Calibration assessment** | AUC-only reporting → ignores probability accuracy | Hosmer-Lemeshow test + calibration plot + Brier score (<0.25) |

### Phase 5: Content Correction

⚠️ **选择策略：XML sed vs python-docx**

**场景一：简单文本替换（不会破坏XML结构）** — 用XML sed
```bash
cd /tmp/docfix
cp proposal.docx fix_tmp.zip
unzip -o fix_tmp.zip word/document.xml
sed -i 's/旧文本/新文本/g' word/document.xml
zip -r ../proposal_corrected.docx .
```

**场景二：复杂替换（引用编号、跨标签文本、引用列表重写）** — 用python-docx run-level操作
```python
from docx import Document
doc = Document(proposal_docx_path)
# Run-level替换，不破坏XML结构
for p in doc.paragraphs:
    if "目标文本" in p.text:
        for run in p.runs:
            if "目标文本" in run.text:
                run.text = run.text.replace("目标文本", "新文本")
doc.save(output_path)
```

**重要pitfall：文本跨多个`<w:t>`标签**

docx中同一段落文本常被分割在多个Run中，中间可能插入`<w:proofErr>`、`<w:fldSimple>`等标签。以下三种情况的搜索替换必须小心：

| 文本类型 | XML表现 | 安全方法 |
|:---------|:--------|:---------|
| 简单文字 | 单个`<w:t>`标签内 | XML sed或run.replace都行 |
| 含拼写检查标记的文字 | 跨`<w:proofErr>`拆分 | 只能run-level逐个替换 |
| 引用编号（如[11，19]） | 可能跨2-3个Run | 逐个检查run.text并分段替换 |
| 含字段代码的文字 | 在`<w:fldSimple>`内 | 避开XML sed，用python-docx |

**真实案例（2026-05-21）**：替换正文中[11，19]→[10，18]时，`[11`和`19]`在分别在不同的Run中，中间还有一个包含" ，"的Run。用`p.text.replace()`无法工作，必须逐run检查。

```python
# 正确做法：跨Run的引用编号替换
for p in doc.paragraphs:
    if '[11' in p.text and '19]' in p.text:
        for run in p.runs:
            if run.text == '[11':
                run.text = '[10'
            elif run.text == '19]':
                run.text = '18]'
            elif '[11' in run.text:
                run.text = run.text.replace('[11', '[10')
                run.text = run.text.replace('19]', '18]')
```

**删除段落**：python-docx的`p.clear()`只清空文本不删除元素。如需彻底移除段落（如清理重复的参考文献条目），需要直接操作用lxml删除element：

```python
from docx import Document
doc = Document('proposal.docx')
# 找到目标段落
for i, p in enumerate(doc.paragraphs):
    if "要删除的内容" in p.text:
        p._element.getparent().remove(p._element)
        break
doc.save('output.docx')
```


### Phase 6: Reference Replacement (GB/T 7714-2015 Format)

Chinese municipal proposals use the GB/T 7714-2015 national standard format:

```
[1] Author1, Author2, et al. Title of article[J]. Journal Name, Year, Volume(Issue): Pages.
```

**Inline citation remapping**: When replacing [1]-[14] with entirely different papers, the inline citations (e.g., [1][2] in the background paragraph) must be remapped to match the NEW reference topics:

| Original Citation Context | Old Refs | New Refs | Reason |
|:-------------------------|:---------|:---------|:-------|
| Rising incidence | [1][2] | [13][14] | Need epidemiological/review papers, not diagnostic |
| FB >95% of non-invasive | [3][4] | [3][4] | Keep if new refs match topic |
| Epidemiology (age/sex) | [5] | [4][5] | Need clinical feature + risk factor papers |

### Phase 7: Section Numbering Fix

Chinese proposals often have inconsistent section numbering. Common fixes:

| Issue | Fix |
|:------|:----|
| Missing "三、" before 研究开发内容 | Add "三、" prefix |
| "预期目标" instead of "四、预期目标" | Add "四、" prefix |
| "研究方案" instead of "五、研究方案" | Add "五、" prefix |

### Phase 8: Output Target — Level-Appropriate Expectation

⚠️ 根据项目级别校准预期成果，不要一刀切"升级"：

| 级别 | 合理期望 | 不需要强行升级 |
|:-----|:---------|:--------------|
| NSFC面上/青年 | SCI论文1-2篇 + 数据集 + 可选软著 | — |
| 省科技厅 | 核心论文1-2篇 + 临床工具 | — |
| **市科技局** | **核心论文1篇 + 临床可用风险评估工具 = 优秀结题** | **不要求软著/SSCI/多篇论文** |

**用户纠正过（2026-05-21）**："科技局的课题，发表论文一篇是可以的。"——对市局项目，1篇论文是合理预期。不要用面上/省科技厅的标准去要求提升产出。

### Phase 9: Hardware-Budget Contradiction Check (2026-05-25新增)

**常见陷阱：UHF RFID声称定位准确率≥99%**

声称UHF RFID可实现≥99%空间定位准确率，同时预算只有1-5万——这是物理上的矛盾。

**事实**：
- UHF RFID（无源）是区域级门禁盘点技术，不是连续空间定位技术。标签0.5-2元，但读写器$500-2000/台。
- BLE AoA可提供房间级定位（0.5-2米），基站$50-200/台，但需要密集部署，布设成本超出1-5万预算。
- UWB可提供厘米级定位，但基站成本$500-2000/台，不适合低预算项目。

**正确做法**：
1. UHF RFID → 诚实标注为"区域级门禁盘点（≥95%可信区间）"
2. 核心创新放在软件/API层面（如事务性业财同步），而非物理定位
3. 预算说明中明确为什么选RFID不选BLE（预算限制），不遮掩

### Phase 10: Format Conformity (格式铁律, 2026-05-25新增)

输出必须严格对标原始模板的七节格式，**不得重塑为非标准格式**。

**原始格式（不可改变）**：
```
一、立项的背景和意义
二、国内外研究现状和发展趋势（包括知识产权状况）
三、研究开发内容和关键技术
四、预期目标（主要技术经济指标、知识产权申请情况、应用前景）
五、研究方案、技术路线、组织方式与课题分解
六、计划进度安排（按5个阶段细化填写）
七、现有工作基础和条件
```

**禁止**：改为空白→假设→原子分解→门控格式；添加额外章节；改变子节编号。
**允许**：通过内容嵌入实现优化（H₃假设嵌入三节、L0.5嵌入四节、门控嵌入六节）。

### Phase 11: Reference Count Standard (2026-05-25新增)

| 项目级别 | 合理引用数 | 验证标准 |
|:---------|:--------:|:---------|
| NSFC面上 | ≥30条 | 全部DOI/PMID |
| NSFC青年 | ≥25条 | 全部DOI/PMID |
| 省科技厅 | ≥15条 | 主要DOI/PMID |
| **市科技局** | **≥20条** | **全部PMID/DOI** |

**2026-05-25实战**：从6条→20条后，D7评分从0.6→1.0。20条覆盖6个方向，每条通过PubMed验证，显著提升标书竞争力。

### Phase 12: Public Dataset Scan (when proposal involves imaging/ML)

When evaluating proposals that involve CT/MRI data + ML, check if public datasets could supplement or validate the work:

**Search strategy (tiered)**:

```
Level 1 — PubMed: ("dataset" OR "public dataset" OR "benchmark") AND (anatomy) AND (imaging)
Level 2 — Zenodo / Figshare: direct keyword search on open repositories
Level 3 — GitHub: search for repo names matching the anatomy + "dataset" or "segmentation"
```

**Known public sinonasal datasets** (updated 2026-05-21):

| Dataset | Host | Size | Content | Label |
|:--------|:-----|:-----|:--------|:------|
| **NasalSeg** | Zenodo (13893419) | 130 CT scans | Nasal cavity, maxillary sinus, nasopharynx segmentation | Pixelwise masks of 5 structures |
| CMF defects | Figshare | ~100 CT | Craniomaxillofacial defects | Repair segmentation |

**Typical finding**: No FBS-specific public dataset exists. All published AI work on fungal ball sinusitis uses institutional private data. This is expected — the proposal must be based on local clinical data.

## Quality Verification Checklist

After reconstruction:

- [ ] All 14+ references verified on PubMed/Semantic Scholar
- [ ] CT/data statistics corrected to match literature range
- [ ] Missing data strategy (MICE) explicitly stated
- [ ] Sample size justification (EPV ≥ 10) added
- [ ] Feature selection (LASSO + Boruta) described
- [ ] External validation plan included
- [ ] Calibration assessment (Hosmer-Lemeshow + Brier) specified
- [ ] English references verified: check year±1 for each (year-typo ≠ fabrication)
- [ ] Public dataset scan performed if imaging/ML involved
- [ ] Section numbering consistent (一、二、三、四、五、六、七)
- [ ] Inline citations remapped to match new reference topics
- [ ] References in GB/T 7714-2015 format, [1]→[14] sequential

## Tools

- `libreoffice` — .doc → .docx conversion
- `python-docx` — `.Paragraph.clear()` + `.add_run()` for safe cross-run replacement
- `xml/sed` — direct sed on `word/document.xml` for guaranteed text replacement
- `PubMed E-utilities` — reference verification via `esearch.fcgi` + `esummary.fcgi`
- `Semantic Scholar API` — reference verification (use API key for higher rate limits)

### PubMed E-utilities: Systematic Search Pattern (validated 2026-05-21)

```python
# Step 1: Search with title terms + author + year (±1)
import requests, time

def verify_ref(title_terms, author, year):
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    for y in [year, year-1, year+1]:
        params = {
            "db": "pubmed",
            "term": f'({title_terms}) AND {author}[Author] AND {y}[dp]',
            "retmode": "json",
            "retmax": 3
        }
        r = requests.get(base, params=params, timeout=10)
        if int(r.json()["esearchresult"]["count"]) > 0:
            return r.json()["esearchresult"]["idlist"]
        time.sleep(0.5)
    return []

# Step 2: If found, fetch details to confirm match
def fetch_details(pmid_list):
    params = {"db": "pubmed", "id": ",".join(pmid_list), "retmode": "xml", "rettype": "abstract"}
    r = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi", params=params, timeout=10)
    return r.text

# Step 3: If NOT found in any year, try broader topic search
# Then flag as suspect only after broader search also fails
```

**Key finding from 2026-05-21 session**: Out of 12 English references verified, 11 were found on PubMed. The one that initially seemed missing (#17 Kim 2022 CMPB) was found when searching by year+1 (2023 instead of 2022). The reference was real — just a year typo. Zero fabricated references found in that proposal.
