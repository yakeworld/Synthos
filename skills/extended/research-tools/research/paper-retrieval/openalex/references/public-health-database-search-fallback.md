# CDC/NIH 公共卫生调查数据库搜索回退方案

## 问题

OpenAlex 对 CDC BRFSS、NHANES、MMWR 报告、NIH 调查类文献的检索质量极低。搜索任何 BRFSS 相关关键词都返回低引用论文、经济类论文或完全不相关的结果。

## 为什么

- OpenAlex 数据库的医学分类标记对公共卫生调查类文献标注不完整
- PubMed 论文在 OpenAlex 中的引用数通常偏低
- CDC 官方出版物（MMWR、报告）在 OpenAlex 中可能被标记为非学术文档

## 搜索流程

### Step 1: 优先用 PubMed eutils

```bash
# 搜索 BRFSS + diabetes 论文
curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=\"BRFSS\"[Title/Abstract] AND \"diabetes\"[Title/Abstract]&retmax=10&sort=cited&retmode=json"
```

然后获取详细信息：
```bash
curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid1},{pmid2}&retmode=json"
```

### Step 2: 用 PubMed 找到的 PMID 反查 OpenAlex

```bash
curl "https://api.openalex.org/works?filter=external_ids.pmid:{pmid}"
```

### Step 3: 如果仍然找不到 — 用 Google 搜索论文标题/作者

用发现的 DOI 反查 OpenAlex：
```bash
curl "https://api.openalex.org/works/doi:10.xxx/xxxxx"
```

### Step 4: 如果 Google 也被屏蔽 — 直接用已知 DOI

对于已知的公共卫生数据库参考文献，直接硬编码 DOI 查询。

## 已知高引用 BRFSS 参考文献

### 1. Pierannunzi et al. 2013 — BRFSS 方法论验证
- **Title:** A systematic review of publications assessing reliability and validity of the Behavioral Risk Factor Surveillance System (BRFSS), 2004–2011
- **Authors:** Carol Pierannunzi, Shaohua Sean Hu, Lina S. Balluz
- **Journal:** BMC Medical Research Methodology
- **Year:** 2013
- **Citations:** 545 (OpenAlex)
- **DOI:** 10.1186/1471-2288-13-49
- **OA PDF:** https://bmcmedresmethodol.biomedcentral.com/counter/pdf/10.1186/1471-2288-13-49
- **PubMed:** 23516290
- **适用场景:** 引用 BRFSS 调查方法的通用参考文献

### 2. Zhang et al. 2015 — MRPM 方法验证
- **Title:** Validation of Multilevel Regression and Poststratification Methodology for Small Area Estimation of Health Indicators From the Behavioral Risk Factor Surveillance System
- **Authors:** Xingyou Zhang, James B. Holt, Shumei Yun, Hua Lu, Kurt J. Greenlund, Janet B. Croft
- **Journal:** American Journal of Epidemiology
- **Year:** 2015
- **Citations:** 191 (OpenAlex)
- **DOI:** 10.1093/aje/kwv002
- **OA PDF:** https://academic.oup.com/aje/article-pdf/182/2/127/213981/kwv002.pdf
- **PubMed:** 25851996
- **备注:** 作者包含 CDC 研究人员 (Holt, Greenlund, Croft)
- **适用场景:** 引用 BRFSS 统计方法/小区域估计

### 3. 其他常见引用
- **CDC BRFSS Survey Facts:** 官方文档页，通常作为直接引用
  - URL: https://www.cdc.gov/brfss/technical/index.html
  - 格式: Centers for Disease Control and Prevention. (2015). Behavioral Risk Factor Surveillance System 2015. Atlanta, GA: U.S. Department of Health and Human Services.
- **National Diabetes Statistics Report:** CDC 周期性报告，2017 年版覆盖 2015 数据

## 验证清单

- [ ] 搜索 BRFSS 相关论文时，OpenAlex 结果数量 > 3 且引用数 ≥ 50
- [ ] 所有 BRFSS 引用论文都通过 PubMed 交叉验证
- [ ] 高引用数 + PubMed 返回 0 = 几乎确定假阳性
- [ ] 对公共卫生调查类文献，优先使用 PubMed 而非 OpenAlex