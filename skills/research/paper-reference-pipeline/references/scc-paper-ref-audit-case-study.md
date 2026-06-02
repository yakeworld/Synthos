# SCC论文参考文献审计实战案例（2026-05-30）

> 43篇引用逐篇DOI核查 + PDF下载 + 引用准确性验证
> 论文: SCC Mathematical Morphology (v4)

---

## 一、审计流程速览

```
Step 1: 提取bibitem列表（43篇） → grep \\bibitem
Step 2: 提取正文引用列表（42篇唯一引用） → grep \\cite
Step 3: 对比 → 发现1个僵尸引用（Sieber2019）
Step 4: 搜索DOI → SS API（38/40成功）
Step 5: 验证bibitem准确性 → SS + Crossref + PubMed三源交叉
Step 6: 下载PDF → paper-manager enhance（3级竞速：Sci-Hub → LibGen → MedData）
Step 7: 产出审计报告
```

## 二、关键发现

### 🔴 虚构引用：Smith2021

| 维度 | bibitem中的值 | 数据库实际记录 | 判定 |
|:-----|:--------------|:--------------|:-----|
| 第一作者 | Smith, C.M. | **无匹配** | ❌ 不存在 |
| 标题 | "Human bony labyrinth extraction and centerline analysis using micro-CT" | **无匹配** | ❌ 不存在 |
| 期刊 | PLoS One | — | ❌ |
| 卷/页 | 16, e0248560 | — | ❌ |

**处理**：从所有数据库（Semantic Scholar, PubMed, Crossref）均查不到。标记为「可能引用虚构」，需人工核实修正或删除。

**根因推测**：LLM在写作时生成了看起来真实但实际不存在的参考文献。bibitem信息看起来专业（PLoS One、DOI格式e0248560）但所有字段均为虚构。

### 🔴 信息全错：Damiano1996

| 维度 | bibitem中的值 | 数据库实际记录 | 判定 |
|:-----|:--------------|:--------------|:-----|
| 第一作者 | Damiano, E.R. | ✅ Damiano | ✅ OK |
| 合作者 | Rabbitt, R.D. | ✅ Rabbitt | ✅ OK |
| 标题 | "A numerical model of the semicircular canal: steady-state canalithiasis" | "A singular perturbation model of fluid dynamics in the vestibular semicircular canal and ampulla" | ❌ 完全不同 |
| 期刊 | Ann. Biomed. Eng. 24 | J. Fluid Mech. 307 | ❌ 完全不同 |
| 年份 | 1996 | 1996 | ✅ 年份对了 |

**处理**：可能是LLM将Damiano与Rabbitt的合作论文搞混了。正确论文：DOI:10.1017/s0022112096000146。

### 🟡 标题偏差：Boselli2014

| 维度 | bibitem | 数据库 | 判定 |
|:-----|:--------|:-------|:-----|
| 标题 | "A computational model of the semicircular canal geometry for otoconia settling simulation" | "Quantitative analysis of benign paroxysmal positional vertigo fatigue under canalithiasis conditions" | 🟡 不同 |
| 期刊 | Biomech. Model. Mechanobiol. 13 | J. Biomech. 49(9) | 🟡 不同 |
| 年份 | 2014 | 2014 | ✅ |
| 作者 | Boselli, F. | ✅ Boselli | ✅ |

**处理**：DOI:10.1016/j.jbiomech.2014.03.019。可能是同一作者同年不同论文被错误引用。

### 🟢 冗余引用：Epp2010

教科书《The Senses: A Comprehensive Reference》被引用为cochlear螺旋率数据源(b≈0.02-0.08)，该数据实际来自Manoussaki2008（已独立引用）。建议移除Epp2010引用。

## 三、PDF下载实战经验

### 环境限制
- 中国网络环境下，Springer/Elsevier/Nature/PNAS直接PDF下载全部返回HTML而非PDF
- Sci-Hub（sci-hub.ee / sci-hub.wf / sci-hub.al）可用，约60%成功率
- MedData（中国医学数据平台）需 `MEDDATA_USERNAME=<MEDDATA_USERNAME>` + `MEDDATA_PASSWORD`

### 推荐命令
```bash
cd /media/yakeworld/sda2/Synthos/tools/paper-manager
MEDDATA_USERNAME="<MEDDATA_USERNAME>" MEDDATA_PASSWORD="<MEDDATA_PASSWORD>" \
  python3 main.py enhance /tmp/refs.bib -o /tmp/pdfs
```

### 结果
- 37篇尝试下载 → 约15篇成功（Sci-Hub）
- 成功PDF大小：0.9MB~20MB（Rabbitt2019的20MB含补充材料）
- 失败原因：Sci-Hub无收录的较新论文、Elsevier出版社论文、Pre-1990论文

## 四、实践教训总结

| 教训 | 细节 |
|:-----|:------|
| 手写thebibliography是万恶之源 | 43篇全部无DOI，无法批量管理 |
| LLM会生成看着专业的假引用 | Smith2021有完整bibitem格式但论文不存在 |
| 引用链传播导致归属错误 | Damiano1996正确论文在J Fluid Mech但被归到Ann Biomed Eng |
| 教科书不能代原始研究 | Epp2010不能作为cochlear数据的首要来源 |
| 同一作者论文易混淆 | Boselli2014的标题/期刊与实际发表的论文不符 |
