# PIMA CRISP-DM 论文引用三验记录 (2026-06-23)

## 背景
对 `pima-crispdm` 论文执行完整的三位一体验证（citation-verification v2.0.0）。

## Phase 1: 是否存在

### 初始状态
- Bib含41个DOI
- 15篇下载失败 → 验证发现10篇DOI假或错（67%）

### 假DOI分布

| 类型 | 数量 | 案例 |
|:-----|:-----|:-----|
| 完全虚构（论文不存在） | 6 | Stiglic2012Missing, Mehta2024, Wen2024Leakage, Fernandez2018Imbalanced, Grunspun2019Quality, Chang2024 |
| DOI篡改（论文真实但元数据错） | 3 | Kapoor2023Leakage, Norgeot2020MI-CLAIM, Haixiang2017Imbalanced |
| 作者编造（DOI真实但作者错） | 1 | Wu2024BRFSS |

### 修复行动
- Kapoor: DOI `10.1016/j.patter.2024.101065` → `10.1016/j.patter.2023.100804`, 年2024→2023, 卷5→4
- Norgeot: DOI `10.1038/s42256-020-00241-3` → `10.1038/s41591-020-1041-y`, 期刊Nat Mach Intell→Nat Med
- Haixiang: DOI `10.1109/DSML.2017.11` → `10.1016/j.eswa.2016.12.035`, 类型inproceedings→article
- Stiglic → 删除，Garcia-Laencina2010替代（缺失值插补综述, 793引）
- Mehta → 删除，由Kapoor覆盖
- Wen → 删除，由Kapoor+McDermott覆盖
- Fernandez → 删除，He2009Imbalanced替代（IEEE TKDE, 4333引）
- Grunspun → 删除，已有TRIPOD+PROBAST覆盖
- Chang → 删除（被审计论文，非核心）

### PDF覆盖率（最终）
- 初始: 41个DOI, 15篇下载失败 → 10篇假DOI
- Phase 1修复后: 37个DOI, 32篇有PDF (86%)
- Haixiang移除后: 36个引用DOIs, 31篇有PDF (86%)
- 无PDF的5篇: 4篇可弃 + 1篇Norgeot（PMC有全文HTML）

### 额外发现（Phase 1 第二阶段）
- **UCI数据集DOI也错了**: `10.24432/C5QG71` → `10.24432/C5VG8H`（末位字符不同），年份2024→2020，作者Sisodia→UCI Repository。数据集页面确认DOI和年份均错误。
- **Haixiang2017Imbalanced**: DOI真实(Elsevier付费), 无PDF。功能已被He2009Imbalanced覆盖(IEEE TKDE, 4333引, 有PDF)。**删除Haixiang**，tex中由He2009替代。
- **🔴 Char2018Clinical DOI完全虚构！**: 原DOI `10.1056/NEJMp1703288` 在Crossref/SS/PubMed三端全404。然而metadata（标题"Implementing machine learning in health care—addressing the challenges and opportunities"、期刊NEJM、作者Char/Shah/Magnus）看似合理。SS标题搜索找到真实论文DOI `10.1056/NEJMp1714229` (NEJM 2018, 1204引, 标题为"Implementing Machine Learning in Health Care — Addressing Ethical Challenges")。PDF已通过Sci-Hub下载。**教训：metadata正确 ≠ DOI真实。无PDF的论文必须先怀疑DOI造假。**

### 关键教训
1. 假DOI是主要问题：67%的下载失败源于假DOI而不是网络
2. 重要性判断必须由Agent做，不问用户
3. D10a在bib修改后必然下降，必须修tex
4. Nature/Springer DOI内容会漂移，必须pdfinfo验证
5. 数据集DOI同样容易造假
6. **metadata正确但DOI完全虚构是新的假DOI模式，比完全虚构更隐蔽**
7. **用户提问"没有全文可能是虚假论文"是正确的直觉——验证后发现确实如此**

## Phase 2: 是否得当（扩展）
- Kapoor2023Leakage PDF ✅ 内容匹配（标题：Leakage and the reproducibility crisis...）
- **Norgeot2020MI-CLAIM PDF ❌ 内容错误！** 
  - 下载到的是Eric Topol的评论文章"Welcoming new guidelines for AI clinical research"(DOI 10.1038/s41591-020-1042-x)而非MI-CLAIM原文
  - 根因：SS OA链接指向PMC（非OA），下载管线回退到Springer直链时串到相邻文章
  - 识别：`pdfinfo`显示Title和Author与bib不符
  - 修复尝试：PMC OA服务确认非OA (`idIsNotOpenAccess`)，无免费PDF
  - 结论：保留bib条目，标注"PDF暂缺—PMC有全文HTML"
- Varoquaux2018CV ✅ 内容匹配

### PDF内容验证的关键发现
`pdfinfo`比`strings`更可靠——Norgeot的错误就是通过`pdfinfo`标题字段直接发现的。建议Phase 2中优先用`pdfinfo`验证标题/作者，再深入语义比对。

## Phase 3: 是否全面
- 🔴 关键遗漏: Martinez-Plumed 2021 "CRISP-DM Twenty Years Later" (IEEE TKDE, 332引)
- 🟡 建议补充: Schröer 2020 "CRISP-DM: A Systematic Literature Review" (555引)

## 关键教训
1. 假DOI是主要问题：67%的下载失败源于假DOI而不是网络
2. 重要性判断必须由Agent做，不问用户
3. D10a在bib修改后必然下降，必须修tex
4. Nature/Springer DOI内容会漂移，必须pdfinfo验证
5. **数据集DOI同样容易造假** — UCI数据集DOI `C5QG71`→`C5VG8H`（末位字符差异），肉眼难辨，必须三方验证

## 最终状态
- D10a: 36/36 = 100%（零孤儿引用）
- PDF覆盖率: 31/36 = 86%
- Bib总条目: 45（36引用 + 9僵尸-未引用的bib条目）
- 三个数据集: PIDD ✅ / Early Diabetes(UCI) ⚠️已修复 / CDC BRFSS ✅
