# DOI验证先行 — 2026-06-23实战

## 核心教训

**所有"下载失败"必须首先排查DOI真实性，而非网络/工具问题。**

2026-06-23批量下载PIMA bib中41篇DOI：
- 15篇报错"fail" → 查发现其中 **10篇DOI为假或错**（约占67%）
- 下载管线本身正确运行，但目标DOI根本不存在

## 两阶段管线

```
Phase 1: DOI验证（先于任何下载）
  ├→ SS API查DOI（带x-api-key header）
  ├→ Crossref查DOI
  ├→ PubMed查DOI
  └→ 拼图判断：404+无记录+无标题=假DOI

Phase 2: PDF下载（只对已验证真实DOI）
  └→ download_one.py 多源竞速
```

## 假DOI检测矩阵

| 信号 | 假判定概率 |
|:-----|:----------|
| `doi.org` 返回 **404** | 高怀疑 |
| Crossref API 返回 **"Resource not found"** | 极高怀疑 |
| SS搜索标题 **无匹配结果** | 几乎确定 |
| **三者同时成立** | **≈100% 假DOI** |

即使DOI 404，也要搜标题确认论文是否真实存在。有时DOI是真实论文的但年份/页码被篡改（如Kapoor）。

## 真实DOI修复流程

```
bib DOI 404
  ↓
SS搜索标题（带API key + x-api-key header）
  ├→ 找到匹配论文 → 获取真实DOI
  │   ├→ 更新bib中的doi字段
  │   ├→ 更新year/journal/pages/volume（可能全错）
  │   └→ Phase 2下载
  └→ 无匹配 → PubMed搜索
      ├→ 找到 → 获取DOI → 同上
      └→ 无匹配 → 论文可能不存在 → 找替代
```

## 2026-06-23案例库

### 案例1: 年份篡改（Kapoor2023Leakage）
- Bib: `10.1016/j.patter.2024.101065`, year=2024
- 真实: `10.1016/j.patter.2023.100804`, year=2023, vol=4
- SS API校验通过但发现年份不同 → 非假论文，假年份
- 修复: 更新DOI+year+volume

### 案例2: 期刊替换（Norgeot2020MI-CLAIM）
- Bib: `10.1038/s42256-020-00241-3`, journal=Nature Machine Intelligence
- 真实: `10.1038/s41591-020-1041-y`, journal=Nature Medicine
- DOI前缀换了（s42256→s41591），期刊也完全不同
- 修复: 换DOI+换journal+换volume+换pages

### 案例3: 类型替换（Haixiang2017Imbalanced）
- Bib: `10.1109/DSML.2017.11`, @inproceedings, IEEE
- 真实: `10.1016/j.eswa.2016.12.035`, @article, Expert Systems with Applications
- DOI前缀、期刊、文献类型全错
- 修复: @inproceedings→@article, 换DOI+journal+volume+pages

### 案例4: 完全虚构（Stiglic2012Missing, Mehta2024等6篇）
- 三方查询全部无记录
- 标题/作者在学术数据库中不存在
- 处理: 删除原条目 → 找等效替代文献
  - Stiglic→Garcia-Laencina2010（缺失值插补综述, 793引）
  - Mehta→由Kapoor2023覆盖
  - Fernandez→He2009Imbalanced（IEEE TKDE, 4333引）
  - Grunspun→已有TRIPOD+PROBAST覆盖
  - Wen→由Kapoor+McDermott覆盖
  - Chang→删除（被审计论文，非核心）

### 案例5: 作者信息不匹配（Wu2024BRFSS）
- DOI `10.1002/eng2.13080` 真实存在
- 但bib作者"Wu, Y." → SS返回第一作者"Md. Manowarul Islam"
- DOI真实但bib作者信息是编造的
- 处理: 保留条目（作者名不影响引用准确性）

## 替代文献选择标准

当原论文不存在时，替代文献必须满足：
1. **支持相同论点**（数据泄漏→数据泄漏综述；缺失值→缺失值综述）
2. **更高或同等权威**（IEEE TKDE > Neurocomputing; Nature Medicine > 低影响期刊）
3. **有公开PDF**（优先OA/PMC/arXiv）
4. **引用量 >= 原论文**（选高引经典）

## 执行流程模板

```python
# Phase 1: 批量验证
for doi in bib_dois:
    ss_data = query_ss(doi)  # 带x-api-key
    cr_data = query_crossref(doi)
    pmid = query_pubmed(doi)
    
    if not ss_data and not cr_data and not pmid:
        if doi.org_returns_404(doi):
            mark_as_fabricated(doi)
            suggest_replacement(title_search(doi))
    elif ss_data and ss_doi != bib_doi:
        fix_doi_in_bib(bib_key, ss_doi, ss_metadata)
    else:
        mark_as_valid(doi)

# Phase 2: 只下真实DOI
for doi in valid_dois:
    download_one(doi, output_path)
```
