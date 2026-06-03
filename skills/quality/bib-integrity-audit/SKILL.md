---
name: bib-integrity-audit
description: "检测并自动修复参考文献.bib中的LLM生成假DOI条目。逐条Crossref/SS验证→僵尸清理→三源搜索替换→PDF下载→Manifest更新。pima-crispdm实战(2026-05-31)提炼。"
signature: "bib_path: str -> audit_report: dict"
allowed-tools: [terminal, read_file, write_file, search_files]
version: 2.0.0
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

参见 `references/pima-crispdm-2026-05-31-case-study.md` 获取完整实战数据。

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

## 机构报告PDF豁免规则

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

## 不可自动修复的情况

1. **SS+OpenAlex均搜不到**（4条/44条=9%无法自动修复）
2. **有真实DOI但meddata不支持**（IEEE/BMJ/Lancet=强付费墙）
3. **正文引用依赖论文的精确数值**（如"99.81%"需要相同数值论文替换）

这些需要标记在manifest中，由用户手动处理。

## 相关技能

- `quality-gate` → G5a引用审计子门
- `paper-reference-pipeline` → PDF下载管线
- `pdf-download-racing` → 竞速下载引擎
- `autonomous-execution-threshold` → 直接执行阈值（假DOI自动修复已列入🟢区）
