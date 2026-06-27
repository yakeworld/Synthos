# PDF替代搜索协议

> 当参考文献无法获取PDF全文时，优先搜索替代文献而非仅标注"不可获取"
> 2026-06-25 HCS-3WT实战经验

## 核心原则

**没有不可替代的文献，只有未找到的替代。** 每篇PDF不可达的引用，目标是找到一篇可验证（有PDF）的等价引用替换。

## 替代搜索优先级

### 第一优先：同作者同主题的期刊论文
- 书（如Topol 2019 Deep Medicine）→ 同作者的期刊综述（Topol 2019 Nature Medicine "High-performance medicine"）
- 会议论文（如Freund 1997 JCSS）→ 同作者的预印本或扩展版
- 旧期刊文章（如Wolberg 1993 UCI）→ 描述同一数据集的原始论文（Wolberg 1990 PNAS）

### 第二优先：覆盖同论点的开放获取论文
- EU报告（HighLevel2019Ethics）→ Jobin 2019 Nature Machine Intelligence 综述或 Floridi 2018 AI4People
- 数据仓库URL（Wolberg UCI）→ 描述该数据集的原始发表论文

### 第三优先：不可替代的标准引用
- 标准化数据库（UCI Machine Learning Repository — Dua2019UCI）— 可保留，无替代
- 工具/框架引用（如 sklearn, numpy）— 可保留

### 早期DOI 404 的常见原因与处理

**经验模式（2026-06-27 bppv-canalith-relocation-ode 审计确认）**：

| DOI前缀 | 出版社 | Crossref状态 | 处理 |
|---------|--------|-------------|------|
| 10.1177/ | SAGE | 404 (early 2010s DOI) | [WARN] 保留，经典文献 |
| 10.1007/ | Springer | 404 (pre-2007 DOI) | [WARN] 保留，经典文献 |
| 10.1152/ | AJP/Physiological Society | 404 (pre-2007 DOI) | [WARN] 保留，经典文献 |
| 10.1179/ | Maney Publishing | 404 (early 2010s DOI) | [WARN] 保留，经典文献 |
| 10.1288/ | Lippincott/Ovid | PARTIAL (redirect) | [OK] 保留 |
| 10.1371/ | PLOS | 200 | [OK] |
| 10.1016/ | Elsevier | 200 | [OK] |
| 10.48550/ | arXiv | 200 | [OK] |
| 10.1038/ | Nature | 200 | [OK] |

**判定规则**：
- 所有12个引用中，7/12 (58%) 返回正常200
- 5/12 (42%) 返回404/403 — 但都是真实论文
- 判定为 [WARN] SOFT，非 [FAIL]
- 不删除任何引用，在报告中注明"早期DOI元数据不完整"

**判断是否为"早期DOI"**的标准：
- DOI注册年份早于2010年 → 大概率 Crossref 未收录
- DOI前缀对应出版社在2010年后才开始完整注册 → 大概率 Crossref 未收录
- 如果论文被领域内广泛引用，即使DOI 404 也不删

**判断是否为"虚构DOI"**的标准（需删除）：
- 论文不存在（PubMed/Google Scholar/SS 均搜不到）
- DOI 指向错误文献（标题/作者完全不匹配）
- DOI格式错误（如 10.xxxx/invalid）
- 所有引用中唯一不匹配者（其他同类论文DOI都正常）

1. Semantic Scholar API 搜索同一作者+同主题
2. PubMed/arXiv 搜索
3. 不满足上述任一条件时，再降级为"书面说明"

## 论文中替换步骤

找到替代文献后：
1. 下载替代文献PDF到 06-references/pdfs/
2. 在 references.bib 中添加新条目
3. 在 paper.tex 中替换 `\cite{OldKey}` → `\cite{NewKey}`
4. 重新编译验证
