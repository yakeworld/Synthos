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

## 四、参考命令速查

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
