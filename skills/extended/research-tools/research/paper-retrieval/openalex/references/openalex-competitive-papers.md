# OpenAlex 竞争性论文识别 — 关键文献

## PMID 39810187 (J Transl Med 2025) — PD 眼动诊断

**标题**: Diagnosis of Parkinson's disease by eliciting trait-specific eye movements in multi-visual tasks.
**DOI**: 10.1186/s12967-024-06044-3
**PMC**: PMC11731183
**年份**: 2025
**机构**: Dalian University of Technology

**方法**: VR 环境中的眼动数据 → 从 fixations/saccades/smooth pursuit 提取特征 → SVM/Random Forest/NN 诊断模型
**性能**: recall=97.65%, accuracy=92.73%, ROC-AUC=97.08%

**关键发现** — 特征分析:
- ✅ 提到 saccade, smooth pursuit, fixation
- ✅ 使用 ML 模型 (SVM, RF, NN)
- ❌ **未使用具体运动学指标**: peak velocity, amplitude, latency, velocity profile, acceleration
- ❌ 只使用通用"eye movement features"

**对 PD-saccade-ML 方向的含义**:
- 该方向已不是白空间 — 有竞争论文
- 但"具体运动学 saccade 指标 + ML" 仍然是部分开放的缺口
- 区别于通用眼动特征, 聚焦于 kinematic metrics 是差异化空间

## 搜索方法 (用于类似场景)

```bash
# PubMed: 检查具体论文的摘要内容
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=39810187&retmode=text&rettype=abstract" -o /tmp/paper-abstract.txt

# 检查是否使用了特定指标:
# - peak velocity, amplitude, latency → kinematic metrics
# - fixation, saccade, smooth pursuit → generic features
# - velocity profile, acceleration, gain → 更详细的运动学

# PMC 全文获取 (XML 格式便于解析)
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=11731183&retmode=xml" -o /tmp/paper.xml
```

## BPPV-ML 竞争论文 (弱竞争)

1. **"Deep Learning for Accurate Diagnosis of Benign Paroxysmal Positional Vertigo"** — 2024 书籍章节, cited=1
2. 4 篇低引用论文 (9-15 citations, 2021-2024): LAD, Multimodal-BPPV, Nystagmus-DL, CAVA-ensemble

**状态**: 弱竞争 — 有论文但引用很低, 仍可发表有影响力的 BPPV-ML 论文
