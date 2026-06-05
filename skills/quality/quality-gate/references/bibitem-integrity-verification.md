# Bibitem 完整性验证技术（2026-05-30实战）

> 背景：SCC对数螺旋论文43篇引用的DOI验证中发现3篇引用的bibitem信息与数据库实际记录严重不符。

---

## 一、核心原则

每个bibitem必须满足：**存在性 + 一致性**。

- **存在性**：该论文必须在至少一个学术数据库（Semantic Scholar、Crossref、PubMed）中可查
- **一致性**：bibitem中的作者/标题/期刊/年/卷/页必须与数据库记录匹配

**例外**：经典著作（Thompson1942 "On Growth and Form"）、教科书（Epp2010 "The Senses"）、在准备手稿（Yang2025）——标注类型后可跳过。

---

## 二、实战案例

### 案例1：Smith2021 — 数据库不存在（🔴）

**bibitem声称**：
> C.M. Smith, et al., Human bony labyrinth extraction and centerline analysis using micro-CT, PLoS One 16 (2021) e0248560.

**验证结果**：SS/PubMed/Crossref 全部查不到。无任何数据库有此标题/作者/DOI的论文。

**根因推测**：
1. DOI `10.1371/journal.pone.0248560` 实际可能对应其他论文
2. 可能是 LLM 生成的虚构引用（仿照 Chacko2018 的格式但改了作者和标题）
3. 实际数据来源可能是 Wimmer2019 或 Gerber2017

**修复**：删除或替换为该数据的实际出版论文。

### 案例2：Damiano1996 — 关键信息全部不符（🔴）

**bibitem声称**：
> E.R. Damiano, R.D. Rabbitt, A numerical model of the semicircular canal: steady-state canalithiasis, Ann. Biomed. Eng. 24 (1996) 136--149.

**数据库中的实际论文**：
> Damiano & Rabbitt, A singular perturbation model of fluid dynamics in the vestibular semicircular canal and ampulla, Journal of Fluid Mechanics, 307 (1996) 333--372. DOI: 10.1017/s0022112096000146

**差异**：
| 维度 | bibitem | 实际 | 
|:-----|:--------|:-----|
| 标题 | "numerical model ... steady-state canalithiasis" | "singular perturbation model ... fluid dynamics" |
| 期刊 | Ann. Biomed. Eng. | J. Fluid Mechanics |
| 卷/页 | 24, 136-149 | 307, 333-372 |

**根因**：bibitem的标题和期刊名可能被 LLM 从 Damiano 的另一篇论文（Ann Biomed Eng 2003 "Three-Dimensional Biomechanical Model of BPPV"）和 Damiano & Rabbitt 正确论文的年份错误拼接。

### 案例3：Boselli2014 — 标题偏差（🟡）

**bibitem声称**：
> F. Boselli, et al., A computational model of the semicircular canal geometry for otoconia settling simulation, Biomech. Model. Mechanobiol. 13 (2014) 1199--1211.

**数据库中的Boselli 2014论文**：
> F. Boselli, L. Kleiser, C. Bockisch, Quantitative analysis of benign paroxysmal positional vertigo fatigue under canalithiasis conditions, J. Biomech. 47 (2014) 1841--1847. DOI: 10.1016/j.jbiomech.2014.03.019

**差异**：标题完全不同，期刊不同。

**仍需确认**：bibitem中是否真的存在一篇 Boselli 的论文「computational model ... otoconia settling」在 Biomech Model Mechanobiol 2014？还是说这是另一篇 Boselli 论文的标题被错误记错了年份和期刊？

---

## 三、检测流程

### 1. 提取可疑信号

| 信号 | 示例 | 触发优先级 |
|:-----|:-----|:----------|
| SS搜索无结果 + 标题关键词不够具体 | Smith2021 | 🔴 立即 |
| 期刊名与DOI前缀不匹配 | Ann Biomed Eng含DOI:10.1017/...（剑桥） | 🔴 立即 |
| 标题包含过于通用的词汇（"model" "analysis" "study"） | — | 🟡 |
| 第一作者姓氏极常见（Smith, Chen, Wang, Li） | Smith2021 | 🟡 |

### 2. 三重验证

```
Step 1: SS搜索 → 有结果且标题匹配 → ✅ PASS
                     标题不匹配 → Step 2
                     无结果 → 标记「不存在」
                     
Step 2: Crossref搜索 → 有结果且标题匹配 → ✅ PASS
                       标题不匹配 → 查作者+年份过滤
                       无结果 → 标记「不存在」
                       
Step 3: PubMed搜索 → 有结果且标题匹配 → ✅ PASS
                     无结果 → 🔴 添加到异常报告
```

### 3. 验证通过标准

一篇bibitem通过的条件：**至少一个数据库中有匹配记录，且关键字段（标题前40字 + 期刊 + 年份）完全一致。**

通过 → 在审计报告中标记为 `✅ verified`
不通过 → 按异常分类处理

---

## 四、修复工作流：检测 → 替换 → 验证

当 bibitem 被确认为虚构（数据库无匹配），执行以下修复流程：

### 阶段1：确认虚构范围

```bash
# Step 1a: D10a扫描找出所有僵尸引用（有cite无PDF）
# Step 1b: 对每个僵尸引用，用OpenAlex搜索标题 + 第一作者
# Step 1c: 如果数据库无匹配 → 标记为「FABRICATED」
```

**虚构引用特征**（2026-06-05实战总结）：
| 特征 | 示例 | 危险等级 |
|:-----|:-----|:--------:|
| 无DOI字段 | `Chua2024`（无doi=） | 🔴 |
| 作者列为"and others"（非标准格式） | `author = {Chua, K. and others}` | 🔴 |
| 作者名为单字母缩写 | `Gr, S.` | 🔴 |
| 期刊名与常见的该领域论文模式不符 | `J. Healthc. Eng.` 发表综述 | 🟡 |
| 年份极近/未来 | `2024`, `2025` | 🟡 |
| OpenAlex搜索0结果 | 精确标题搜索无匹配 | 🔴 确认虚构 |

### 阶段2：搜索验证替代引用

搜索真实论文替换每个虚构引用。使用OpenAlex（无速率限制）：

```python
# 搜索策略：提取虚构引用的核心概念 + 上下文需求
# 例：Chua2024声称"PD患者吸入性肺炎风险3.30倍"
# → 搜索 "aspiration pneumonia risk factors Parkinson's disease"
# → 找到 Langmore1998 (Predictors of Aspiration Pneumonia, Dysphagia, 859 cites)
```

**替换原则**：
1. **上下文匹配**：新引用必须支持原文中同一论证点（不要改变正文论证逻辑）
2. **引用影响优先**：选高引用论文（Cited-by count高，知名期刊）
3. **OA优先**：优先选Open Access（方便PDF下载）
4. **年份合理**：新引用年份应早于论文写作年份

### 阶段3：更新Bib文件

```python
# 用OpenAlex获取新引用的完整元数据
url = f"https://api.openalex.org/works/doi:{doi}"
data = json.loads(urllib.request.urlopen(url).read())

# 构建标准BibTeX条目
# 关键字段：author, title, journal, year, volume, pages, doi
```

**规范**：
- 所有字段使用大括号 `{...}` 
- journal名用 `{\\textit{Journal Name}}`
- doi字段用小写，不带 `https://doi.org/` 前缀
- 作者格式：`Last, First and Last, First`

### 阶段4：更新Tex引用键

```bash
# 全局替换\cite{OLD_KEY} → \cite{NEW_KEY}
# 检查文件：sections/*.tex 和主 paper.tex
sed -i 's/\\\\cite{OLD_KEY}/\\\\cite{NEW_KEY}/g' sections/*.tex paper.tex
```

### 阶段5：重编译验证

```bash
# 全流程编译
pdflatex paper.tex && bibtex paper && pdflatex paper.tex && pdflatex paper.tex

# 验证：无 undefined citation
grep -i "undefined" paper.log  # 应无输出

# 验证：旧虚构引用不再出现
grep -c "OLD_KEY" paper.bbl paper.aux  # 应 = 0
```

### 阶段6：更新审计记录

```
D10a变更: X% → Y%
僵尸引用: N → 0
虚构引用替换: M个
新增PDF: K个
```

### 实战案例：pd-dysphagia-2026（2026-06-05）

| 虚构引用 | 替换引用 | 替换依据 |
|:---------|:---------|:---------|
| Chua2024 | Langmore1998 (Dysphagia, 859 cites) | PD吸入性肺炎风险预测 |
| Kalf2023 | Suttrup2015 (Dysphagia, 466 cites) | PD吞嚥障礙流行病學 |
| MarieSainte2021 | Brodsky2016 (Chest) | 吞嚥篩查準確性 |
| Dey2023 | Costantini2023 (Sensors, OA) | ML用於吞嚥障礙預測 |
| Gr2024 | Volkert2019 (Clin Nutr, OA) | 老年營養指南 |
| Cabral2025 | Varoquaux2022 (npj Digital Med, OA) | ML數據泄漏方法學失誤 |

**结果**：6个虚构引用→6个已验证引用，编译通过，0 undefined。

## 五、参考命令速查

```bash
# SS搜索
curl -s -H "x-api-key: $KEY" \
  "https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit=3&fields=title,externalIds,venue,year"

# DOI直接查
curl -s -H "x-api-key: $KEY" \
  "https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=title,externalIds,venue,year"

# Crossref搜索
curl -s "https://api.crossref.org/works?query={query}&rows=3"

# Crossref DOI查
curl -s "https://api.crossref.org/works/{doi}"

# PubMed ESearch
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}&retmax=5&retmode=json"

# PubMed ESummary（用上一步得到的PM_ID）
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
```
