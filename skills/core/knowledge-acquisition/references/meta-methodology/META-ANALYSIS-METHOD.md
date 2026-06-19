# 系统评价/Meta-分析方法论

> 理论来源：PRISMA 2020; Cochrane Handbook; Higgins et al. (2019)

## PRISMA 2020 流程图

系统评价必须遵循 PRISMA (Preferred Reporting Items for Systematic Reviews and Meta-Analyses) 流程：

```
ID — Identification
  ├── 数据库检索 (PubMed, Embase, Cochrane, Web of Science)
  ├── 去重 (Deduplication)
  └── 记录各数据库命中数

SC — Screening
  ├── 标题/摘要筛选 (至少 2 人独立)
  ├── 纳入/排除标准应用
  └── 记录排除原因

EL — Eligibility
  ├── 全文评估
  ├── 至少 2 人独立评估
  └── 记录排除原因及文献

IN — Inclusion
  ├── 最终纳入文献
  └── 数据提取

┌──────────────────────────────┐
│     PRISMA Flow Diagram      │
│                              │
│  Records identified: N       │
│  ↓ Duplicates removed: -M    │
│  Records screened: N-M       │
│  ↓ Excluded: -X              │
│  Full-text assessed: N-M-X   │
│  ↓ Excluded: -Y              │
│  Studies included: N-M-X-Y   │
└──────────────────────────────┘
```

## 质量评估工具

| 研究类型 | 工具 | 评估内容 | 来源 |
|----------|------|----------|------|
| RCT | Cochrane RoB 2.0 | 随机化/偏离干预/缺失数据/选择性报告/其他偏倚 | Higgins et al. (2011) |
| 非随机干预 | ROBINS-I | 混杂/受试者选择/干预分类/缺失数据/报告偏倚 | Sterne et al. (2016) |
| 队列/病例对照 | Newcastle-Ottawa Scale (NOS) | 样本代表/匹配/结局 | Wells et al. (2000) |
| 诊断准确性 | QUADAS-2 | 受试者选择/诊断/参考标准/流程 | Whiting et al. (2011) |
| 质性研究 | CASP | 研究适合性/方法论/严谨性/伦理/结果解读 | CASP (2018) |

## Meta-分析统计

```
固定效应模型 (Fixed Effect):
  - 假设所有研究估计同一效应
  - 适用于研究同质性高 (I² < 50%)
  - 权重: 逆方差法

随机效应模型 (Random Effects):
  - 假设效应大小在研究间分布
  - 适用于研究存在异质性 (I² ≥ 50%)
  - 权重: DerSimonian-Laird / REML

异质性检验:
  - Q 统计量: p < 0.10 表示异质性显著
  - I²: 25% 低 / 50% 中 / 75% 高
  - τ²: 研究间标准差

森林图 (Forest Plot):
  - 每个研究的效应量 + CI
  - 总体效应量 (菱形)
```

## 偏倚评估

```
发表偏倚检测:
  - 漏斗图 (Funnel Plot): 对称性
  - Egger's 检验: p < 0.05 表示偏倚
  - Begg's 检验: 秩相关
  - Fail-safe N: 需要多少未发表阴性结果才能推翻结论

敏感性分析:
  - 逐一篇剔除 (Leave-one-out)
  - 亚组分析 (按设计/人群/质量)
  -  meta-regression
```

## 不合格标准

```
1. 无 PRISMA 流程图 → FAIL
2. 检索 < 3 个数据库 → WARNING
3. 无质量评估工具 → FAIL
4. 异质性高 (I² > 75%) 仍做 Meta → WARNING
5. 无发表偏倚检测 → WARNING
6. 仅 1 名筛选者 → FAIL
7. 无敏感性分析 → WARNING
```

## 理论来源

- Page MJ et al. (2021). "The PRISMA 2020 statement." *BMJ*, 372, n71.
- Higgins JPT et al. (2019). *Cochrane Handbook for Systematic Reviews of Interventions* (2nd ed.).
- Sterne JAC et al. (2016). "ROBINS-I: A tool for assessing non-randomised studies." *BMJ*, 355, i4909.
- Wells GA et al. (2000). "The Newcastle-Ottawa Scale."
- Whiting PF et al. (2011). "QUADAS-2." *Annals of Internal Medicine*, 155(9), 529-536.
