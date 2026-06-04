---
name: bib-integrity-audit
description: "检测并自动修复参考文献.bib中的LLM生成假DOI条目。逐条Crossref/SS验证→僵尸清理→三源搜索替换→PDF下载→Manifest更新。pima-crispdm实战(2026-05-31)提炼。"
signature: "bib_path: str -> audit_report: dict"
allowed-tools: [terminal, read_file, write_file, search_files]
version: 2.1.0
tags: [bibtex, doi, quality, audit, references, fake-doi]
related_skills: [paper-reference-pipeline, quality-gate, pdf-download-racing]
---

---

## 原理层·文言

> 「述而不作，信而好古。」信者，引以为实也。DOI必溯，假者必诛。
> 「究天人之际，通古今之变，成一家之言。」
> 一查Crossref，二验SS，三搜OpenAlex。逐条过堂，不留伪物。存真去伪。# BibTeX 完整性审计技能

## 触发条件

执行paper-pipeline的引用审计步骤时，或者收到"下载全文"、"检查引用"、"假DOI"等信号时自动触发。

## 核心理念

**LLM生成的bib条目中，假DOI比例极高（33%+）。** pima-crispdm实战(2026-05-31)发现：
- 45条引用中 ~15条为LLM生成的假DOI
- 假DOI在Crossref查不到（直接不存在）
- 真DOI错配（指向完全不同主题的论文，如Tong2024→胸片识别）
- 作者/标题/卷页全部虚构
- 伪PDF（HTML伪装，如Gr2024的`<!DOC`头）

**凡引必验，不验不刊。** 不做DOI验证的引用审计不可信。

参见 `references/pima-crispdm-2026-05-31-case-study.md`（单篇全修复实战）、`references/pima-reference-cleanup-2026-06-04.md`（Pima D7 0.85→1.0全流程）和 `references/bulk-scan-iris-papers-2026-06-05.md`（批量扫描+新增可疑信号）获取完整实战数据。

## 完整流程（7步）

```
P0: 备份原文
  ↓
Step 1: DOI批量验证 (Crossref)
  ↓
Step 2: 僵尸引用检测 (grep \cite vs bibkeys)
  ↓
Step 3: 三源搜索替换 (SS → OpenAlex → PDF元数据)
  ↓
Step 4: Bib条目更新 (保持bibkey不变)
  ↓
Step 5: PDF下载 (OA→meddata→arXiv→Sci-Hub)
  ↓
Step 6: 引用挖掘 (从已有PDF的SS引用图谱找OA替代)
  ↓
Step 7: Manifest更新 + 报告产出
```

---

### Step 0: 备份

```bash
cp references.bib references.bib.bak
```

### Step 1: DOI批量验证

对bib中每条有DOI的条目，用Crossref API验证：

```python
import requests, json
# 每条验证
r = requests.get(f"https://api.crossref.org/works/{doi}", timeout=10)
d = r.json()
status = d.get('status', 'ERROR')
if status == 'ok':
    title = d['message'].get('title', [''])[0][:80]
    venue = d['message'].get('container-title', [''])[0] if d['message'].get('container-title') else 'N/A'
    year = d['message'].get('published-print', {}).get('date-parts', [[None]])[0][0]
```

结果分类：
- `status=ok` ✅ 真DOI — 进一步验证标题是否匹配bib中的标题
- `Resource not found` ❌ **假DOI**（LLM生成的虚构DOI）
- 标题不匹配 ⚠️ **真DOI错配**（DOI指向不同论文）

### Step 1.5: 非学术引用清理（arXiv预印本无ID / Kaggle论坛 / 自引）

> **2026-06-04 实战发现（Pima CRISP-DM）：** references.bib 中包含3类不应存在的条目：arXiv预印本无ID（自引 `ProcessDriven`, `IllusionOfPerfection`）、Kaggle数据集页（`KagglePIDD`）、Kaggle论坛帖（`KaggleZeroValues`）。这些条目既无DOI又非已发表学术文献，应替换为已发表替代或删除。

> **2026-06-04 Pima CRISP-DM实战补充：** 替换后需注意D8可能下降（Pima从35→31）。只要D8仍≥30阈值，不需额外补引。同时将替换经验记录为REFERENCE_MANIFEST的注释。

#### 检测信号

| 信号 | 示例 | 判定 |
|:-----|:------|:------|
| `@article{` + `journal = {arXiv preprint}` + 无arXiv ID | `ProcessDriven` | 自引预印本 → 删除或补arXiv ID |
| `@misc{` + `author = {Kaggle}或{Kaggle Community}` | `KagglePIDD` | 数据集/论坛引用 → 替换为学术文献 |
| `@misc{` + `howpublished = {\\url{https://www.kaggle.com/...}}` | `KaggleZeroValues` | 论坛帖 → 替换为学术文献 |
| `@article{` + 作者是用户自己 + `journal = {arXiv preprint}` | `IllusionOfPerfection` | 未发表自引 → 删除（正文语义用其他引用支撑） |
| DOI为明显占位符（如`123456789`后缀、全0或重复数字） | `Wang2023` | 🔴 疑似LLM假条目 → 用OpenAlex标题搜索验证 |
| journal含"Journal of {IEEE} Access"等非标准前缀 | `Wang2023` | 🔴 IEEE Access本身是期刊名，"Journal of IEEE Access"不存在 |
| `year`字段含URL（如`year={http://...}`） | `CASIA2019` | ⚠️ 字段错误：year被填成了URL，需修复 |
| DOI的journal前缀与bib中journal不匹配 | `kothari2021ellseg` | ⚠️ DOI写错期刊前缀。例：bib写IEEE TVCG但DOI含`TMI.`（IEEE Trans Med Imaging） |
| arXiv条目有arXiv ID但无DOI | `garbin2019openeds` | ✅ 可补 `10.48550/arXiv.XXXX.XXXXX`（arXiv官方DOI格式） |

#### 替换策略

| 原条目类型 | 替代方案 | 实战示例 |
|:-----------|:---------|:----------|
| 自引预印本（论文自己的结果） | 直接删除 \cite — 本论文的结果无需自引 | `ProcessDriven` → 删除 |
| 自引预印本（文献观察） | 找其他已发表引用替代 | `IllusionOfPerfection` 的"92%论文泄漏" → `Kapoor2024Leakage` 已覆盖 |
| Kaggle数据集页 | 用原始发表论文替代 | `KagglePIDD` → `Smith1988`（PIDD原始论文） |
| Kaggle论坛帖 | 找研究同一问题的学术论文 | `KaggleZeroValues` → `Stiglic2012Missing`（J Med Syst, DOI: 10.1007/s10916-012-9822-z） |

#### 执行命令

```bash
# 1. 在正文中删除/替换 \cite{key}
python3 -c "
tex = open('paper.tex').read()
tex = tex.replace('\\\\cite{BadKey}', '\\\\cite{ReplacementKey}')
tex = tex.replace('\\\\cite{BadKey, GoodKey}', '\\\\cite{GoodKey}')
with open('paper.tex', 'w') as f: f.write(tex)
"

# 2. 从 references.bib 删除对应条目
python3 << 'PYEOF'
import re
bib = open('references.bib').read()
entries = re.split(r'\n(?=@\w+\{)', bib)
to_delete = {'ProcessDriven', 'IllusionOfPerfection', 'KagglePIDD', 'KaggleZeroValues'}
kept = [e for e in entries if not any(k in e for k in to_delete)]
# 更精确的方式是按key匹配
# kept = [e for e in entries if re.match(r'@\w+\{', e) and re.match(r'@\w+\{([^,]+),', e).group(1).strip() not in to_delete]
open('references.bib', 'w').write('\n'.join(kept))
PYEOF

# 3. 验证
grep -c 'BadKey' paper.tex        # 应为0
grep -c 'BadKey' references.bib   # 应为0
```

#### 验证（D10a + 编译）

```bash
rm -f paper.aux paper.bbl paper.blg
pdflatex -interaction=nonstopmode paper.tex 2>&1 | tail -1
bibtex paper 2>&1 | tail -1
pdflatex -interaction=nonstopmode paper.tex 2>&1 | tail -1
pdflatex -interaction=nonstopmode paper.tex 2>&1 | tail -1
strings paper.log | grep -c 'undefined on input'
# 应输出 0
```

**删除非学术引用后，D8可能下降**（Pima从35→31）。确认 D8 ≥ 30 阈值仍在，否则需补引。

### Step 2: 僵尸引用检测

```bash
used=$(grep -oP '\\\\cite\{[^}]+\}' manuscript.tex | sed 's/\\\\cite{//;s/}//' | tr ',' '\n' | sed 's/^ *//' | sort -u)
bibkeys=$(grep -oP '@\w+\{\K\w+' references.bib | sort -u)
# 僵尸条目（在bib但不在正文中 — 直接删除）
zombies=$(comm -13 <(echo "$used") <(echo "$bibkeys"))
# 孤儿引用（在正文但不在bib中 — 需补充）
orphans=$(comm -23 <(echo "$used") <(echo "$bibkeys"))
```

**⚠️ 僵尸处理规则**：Zombie条目直接删除。不需要询问用户——它们不在正文中被引用所以删了不影响。

### Step 2.5: DOI补全（从旧备份找回 + OpenAlex搜索）

当文献的DOI缺失但条目本身真实时，按以下顺序补全：

**Tier 0: 旧版bib备份找回**（最快，零API调用）
```bash
# 从.bib.bak提取已知DOI
python3 << 'PYEOF'
import re
bak = open('references.bib.bak').read()
new = open('references.bib').read()
bak_entries = {}
for m in re.finditer(r'@\w+\{([^,]+),([^@]+?)\n\}', bak, re.DOTALL):
    key = m.group(1).strip()
    doi_m = re.search(r'doi\s*=\s*\{([^}]+)\}', m.group(2))
    if doi_m: bak_entries[key] = doi_m.group(1)
for key, doi in bak_entries.items():
    if f'doi = {{{doi}}}' not in new and f'@{key}' in new:
        new = new.replace(f'}}\n@', f',\n  doi = {{{doi}}}\n}}\n@')
open('references.bib', 'w').write(new)
PYEOF
```

**Tier 1: 已知经典文献直接写DOI**
```python
KNOWN_DOIS = {
    'Chawla2002': '10.1613/jair.953',
    'Dietterich1998': '10.1162/089976698300017197',
    'Lundberg2017SHAP': '10.48550/arXiv.1705.07874',
    'Saeedi2019': '10.1016/j.diabres.2019.107843',
    'Zheng2018': '10.1038/nrendo.2017.151',
    'Collins2015TRIPOD': '10.7326/M14-0698',
    'Moons2019PROBAST': '10.7326/M18-1376',
    'Feurer2025OpenML': '10.1016/j.patter.2025.101317',
}
```

**Tier 2: OpenAlex精确标题搜索**
```python
params = urllib.parse.urlencode({
    'search': 'exact title keywords',
    'sort': 'relevance_score:desc', 'per_page': 3
})
url = f'https://api.openalex.org/works?{params}'
req = urllib.request.Request(url)
req.add_header('User-Agent', 'mailto:ghfdshgf79@gmail.com')
resp = urllib.request.urlopen(req, timeout=10)
data = json.loads(resp.read())
```

**Pima CRISP-DM实战**：19个DOI找回（旧版备份6 + 知识库10 + OpenAlex 3），覆盖率0%→94%

### Step 3: 三源搜索替换

对假DOI条目，按优先级搜索真实论文：

**Tier 1: Semantic Scholar API**（首选，对CS/AI/医学论文覆盖好）
```python
import requests
url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit=5&fields=title,externalIds,venue,year,openAccessPdf"
r = requests.get(url, timeout=15)
papers = r.json().get('data', [])
for p in papers:
    doi = p.get('externalIds', {}).get('DOI', '')
    oa  = p.get('openAccessPdf', {}).get('url', '') if p.get('openAccessPdf') else ''
```

**Tier 2: OpenAlex API**（SS搜不到时——覆盖更广，对低层次期刊更好）
```python
url = f"https://api.openalex.org/works?search={query}&filter=type:article&sort=relevance_score:desc&per_page=5"
r = requests.get(url, timeout=12)
for item in r.json().get('results', []):
    doi = item.get('doi', '').replace('https://doi.org/', '')
```

**Tier 3: PDF元数据提取**（已有PDF但DOI错误的）
```bash
pdfinfo paper.pdf | grep -i 'Subject\|doi'
pdftotext -f 1 -l 1 paper.pdf - | grep -oiP '10\.\d{4,}/[^\s)}]+'
```

### Step 4: Bib条目更新

保持bibkey不变，只替换DOI：

```python
import re
pattern = r'(' + re.escape(key) + r'.*?)doi\s*=\s*\{[^}]*\}'
replacement = r'\1doi = {' + new_doi + r'}'
bib_text = re.sub(pattern, replacement, bib_text, count=1, flags=re.DOTALL)
```

**关键规则**：只改DOI字段。bibkey不变则正文中 `\cite{key}` 不需要修改。

### Step 5: PDF下载

按优先级尝试，每次设30-45s timeout：

| 优先级 | 方法 | 适用场景 | 成功率 |
|:------:|:-----|:---------|:------:|
| 1 | OA直连 | 有 `openAccessPdf.url` | 高 |
| 2 | arXiv直链 | 有arXiv ID | 高 |
| 3 | meddata | Springer/Nature/Elsevier/Ann Intern Med | 中 |
| 4 | download_one.py(全通道) | 其他有DOI的 | 低 |
| 5 | 标记为blocked | 上述均失败 | - |

**meddata出版社支持矩阵（2026-05-31实测）：**

| 出版社 | 支持？ | 示例 |
|:-------|:------:|:-----|
| Springer/Nature | ✅ | BMC, SpringerOpen, Nature Portfolio |
| Elsevier | ✅ | Computers in Biology and Medicine, Artificial Intelligence in Medicine |
| Ann Intern Med | ✅ | Collins2015, Wolff2019 |
| PLOS | ✅ | PLOS ONE (但已有OA直连) |
| MDPI | ✅ | 但已有OA直连 |
| **IEEE** | ❌ | Ali2025, Tong2024 |
| **BMJ** | ❌ | collins2024tripod |
| **The Lancet** | ❌ | Futoma2020 |
| **Hindawi/Wiley** | ❌ | Liao2023 (收购后封禁) |
| **JOIV/印尼期刊** | ❌ | Gr2024, Kurniawan2026 |

**不可下载的条目**：保留在bib中，只在manifest标记为"paywall"。不删除——有些标准引用（如TRIPOD+AI）即使无PDF也需保留。

### Step 6: 引用挖掘（从已有PDF找OA替代）

当D9覆盖率不足时，从已有PDF的SS引用图谱中挖掘OA论文来替代无PDF条目：

```python
# 获取每篇已有PDF的参考文献列表
r = requests.get(f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}/references?limit=25&fields=title,externalIds,openAccessPdf")
for item in r.json().get('data', []):
    paper = item.get('citedPaper', {})
    ref_doi = paper.get('externalIds', {}).get('DOI', '')
    oa_url = paper.get('openAccessPdf', {}).get('url', '')
    if ref_doi and oa_url and ref_doi not in existing_dois:
        candidates.append((paper.get('title',''), ref_doi, oa_url))
```

用SS `/references` 端点的 `citedPaper` 字段。2026-05-31实测：4篇核心PDF挖出18条OA候选（3篇已验证可下载）。

### Step 7: Manifest更新

产出 `REFERENCE_MANIFEST.md`，包含每条引用的：
- BibKey | DOI | PDF状态 | 异常标记 | 备注

**必须包含的异常标记：**

| 标记 | 含义 |
|:-----|:------|
| ✅ | 正常，有PDF |
| 🔴 FAKE DOI | DOI在Crossref查不到（LLM虚构） |
| ⚠️ WRONG PAPER | DOI存在但指向不同论文 |
| 🗑️ ZOMBIE | 在bib但正文未引用 |
| 🟡 PAYWALL | 有真实DOI但无法下载 |
| ❌ NOT FOUND | 论文在SS/OpenAlex均不存在 |

## 引用上下文验证（重要！）

替换假条目后，必须验证正文中用 `\cite{key}` 引用的上下文是否与新论文内容一致。

**方法**：提取正文中包含该bibkey的句子，判断其中的数值/声明是否在新论文中合理。

```bash
# 提取引用上下文
grep -B1 -A1 "\\\\cite{Key2024}" manuscript.tex
```

**pima-crispdm实战案例**：
- Chinnababu2024替换前：正文引用"99.81% accuracy using PSRNN"
- 替换后：新论文是EURASIP 2020的Deep NN论文（也报告高准确率）→ 上下文合理
- Hossain2025替换前：正文引用"96.8% using ensemble methods"
- 替换后：新论文是Heliyon 2024的stacking ensemble论文 → 上下文合理

## ⚡ 陷阱：bib文件符号链接错位

**现象**：pdflatex编译通过，bibtex报 `I didn't find a database entry for "Key2024"` 警告，`grep` 确认b文件中有该条目。

**根因**：`.tex` 目录下的 `references.bib` 是符号链接，指向了错误的路径。

**排查命令**：
```bash
# 从tex目录检查bib符号链接指向
ls -la $(dirname $(grep -rl 'bibliography{' *.tex 2>/dev/null | head -1))/references.bib

# 典型错误：链接指向了不存在的 ../references.bib
# 正确：指向 ../06-references/references.bib

# 修复
cd $(dirname manuscript.tex)
rm references.bib
ln -sf ../06-references/references.bib references.bib

# 重新编译
pdflatex manuscript && bibtex manuscript && pdflatex manuscript && pdflatex manuscript
```

**验证**：编译后 `grep -c 'undefined' manuscript.log` 应为0。

## 扫描模式（Scan-Only）

当任务要求"扫描、检测、报告但不修改"时，使用扫描模式而非全修复管线。

### 扫描模式流程

```
Step S0: 定位bib文件（单片或批量）
  ↓
Step S1: 解析所有条目（key, type, doi, title, author, journal, year）
  ↓
Step S2: 对每条有DOI的条目 → 分类器（真/假/错配/可疑）
  ↓
Step S3: 对无DOI条目 → 检测可疑信号（arXiv无ID/Kaggle/占位符/字段错误）
  ↓
Step S4: 对已知经典文献 → 标记"可补"（不自动写入）
  ↓
Step S5: 批量验证（可选）：OpenAlex抽样验证DOI真伪
  ↓
Step S6: 产出报告（表格：论文|条目数|DOI覆盖率|可疑条目|可补DOI）
```

### 批量扫描多个bib文件

```python
# 多文件逐批分析
for name, path in BIB_FILES.items():
    text = open(path).read()
    entries = parse_bib_entries(text)
    
    # 统计
    total = len(entries)
    doi_count = sum(1 for e in entries if e['doi'])
    
    # 检测可疑
    for e in entries:
        flags = detect_suspicious(e)
        if flags:
            suspicious.append((name, e['key'], flags))
    
    # 检测可补已知DOI
    for e in entries:
        if not e['doi'] and e['key'] in KNOWN_DOIS and KNOWN_DOIS[e['key']]:
            missing_doi_known.append((name, e['key'], KNOWN_DOIS[e['key']]))
```

### 扫描模式输出格式

```markdown
🧹 Bib标准化报告 (YYYY-MM-DD)

| 论文 | 条目数 | DOI覆盖率 | 可疑条目 | 已补DOI |
|:-----|:-----:|:--------:|:--------:|:-------:|
| paper-abc | 33 | 94% | 0 | 0 |

可疑条目明细:
- paper-xyz: Key2024 (placeholder DOI, journal不存在)

可补DOI明细:
- paper-abc: Key2020 → 10.XXXX/...

汇总统计:
- 总计扫描论文: N
- 总计条目: N
- 总计有DOI: N (XX%)
- 总计可疑: N
- 总计可补已知DOI: N
```

大型全球卫生机构报告（如 **IDF糖尿病地图集**、WHO全球报告、CDC统计报告）通常：
- 有正式发表（DOI、卷、页）
- 但PDF受限于出版社付费墙或文件过大无法下载
- 在领域内是标准引用文献（审稿人皆知）

**处理规则**：
1. 保留在bib中（不删除，同Wirth2000/Thompson1942）
2. 在 `REFERENCE_MANIFEST.md` 标记为 `📋 INSTITUTIONAL REPORT`
3. **不计入D9分母**（D9分母仅统计期刊/会议/预印本论文）
4. 正文\cite位置不变

```python
# 判断是否为机构报告
INSTITUTIONAL_REPORTS = {'IDF2021', 'WHO2022', 'CDC2023'}  # 按需扩展
if key in INSTITUTIONAL_REPORTS:
    d9_denom -= 1  # 不计入分母
```

### 🚩 API返回的论文与期望不符（DOI真但指向不同论文）

**现象**：用 bib 中记录的 DOI 查 SS API，返回的论文标题完全不同（如 `10.1016/j.patter.2024.100974` 返回 "Privacy preservation for federated learning" 而非期望的 "Leakage and the reproducibility crisis"）。

**根因**：bib 中的 DOI 字段写错了——指向同作者不同论文。

**处理**：
1. 不信任 bib 的 DOI 字段——用 SS 搜索论文标题来验证
2. 对比 SS 返回标题 vs bib 标题
3. 标题不匹配时，用标题搜索找正确 DOI
4. 只更新 DOI 字段，bibkey 不动

```bash
# 验证
curl -s "https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=title,year"

# 搜索正确DOI
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query={title}&limit=3&fields=title,externalIds"
```

**2026-06-04 实战**：Kapoor2024 bib中记录 `10.1016/j.patter.2024.100974`，正确应为 `10.1016/j.patter.2023.100804`。

1. **SS+OpenAlex均搜不到**（4条/44条=9%无法自动修复）
2. **有真实DOI但meddata不支持**（IEEE/BMJ/Lancet=强付费墙）
3. **正文引用依赖论文的精确数值**（如"99.81%"需要相同数值论文替换）

这些需要标记在manifest中，由用户手动处理。

## 相关技能

- `quality-gate` → G5a引用审计子门
- `paper-reference-pipeline` → PDF下载管线
- `pdf-download-racing` → 竞速下载引擎
- `autonomous-execution-threshold` → 直接执行阈值（假DOI自动修复已列入🟢区）
