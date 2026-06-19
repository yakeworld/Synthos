# 实验设计方法论检查器

> 理论来源：CONSORT; STROBE; CASP; COREQ; PICOS; COSMIN

## 实验设计五大维度

每个实验/研究设计必须通过以下 5 个维度的检查：

### D1: 样本设计 (权重 0.25)

| 检查项 | 满分 | 合格标准 |
|--------|------|----------|
| 样本量计算 | 3 | 报告 power analysis, α=0.05, 功效≥0.80, effect size 合理 |
| 纳入/排除标准 | 2 | 明确列出纳入和排除标准 |
| 样本代表性 | 3 | 样本覆盖目标总体，抽样方法合理 |
| 统计功效 | 2 | 实际功效≥0.80 或说明原因 |

**不合格**: 样本量 < 30 且无 power analysis justification → WARNING

### D2: 随机化与盲法 (权重 0.20)

| 检查项 | 满分 | 合格标准 |
|--------|------|----------|
| 随机化方法 | 3 | 简单/分层/区组随机化，方法可复现 |
| 盲法设计 | 3 | 单盲/双盲/三盲，实际可行则必须执行 |
| 分配隐藏 | 2 | 分组分配过程对受试者和研究者隐藏 |
| ITT分析 | 2 | 意向性分析 (所有随机化受试者纳入分析) |

**不合格**: 有对照组但无随机化 → FAIL (因果推断无效)
**不合格**: 有盲法设计但实际未执行 → WARNING

### D3: 对照设计 (权重 0.15)

| 检查项 | 满分 | 合格标准 |
|--------|------|----------|
| 对照组类型 | 3 | 安慰剂/活性对照/标准治疗/无对照，类型合理 |
| 对照选择依据 | 2 | 对照选择有文献或临床依据 |
| 基线可比性 | 3 | 组间基线特征可比 (表1), p > 0.05 或非随机研究说明 |

**不合格**: 对照组选择明显不合理 → FAIL

### D4: 变量定义 (权重 0.20)

| 检查项 | 满分 | 合格标准 |
|--------|------|----------|
| 自变量定义 | 3 | 明确定义，操作化 (how measured/manipulated) |
| 因变量定义 | 3 | 明确定义，测量工具信度/效度 (Cronbach's α > 0.7, ICC > 0.6) |
| 混杂因素 | 3 | 已识别主要混杂因素，已控制 (随机化/匹配/回归/分层) |
| 协变量 | 2 | 协变量预注册，避免 p-hacking (Hypothesis → Analysis pipeline) |

**不合格**: 主要混杂因素未控制 → WARNING
**不合格**: 因变量无信效度报告 → WARNING

### D5: 数据分析 (权重 0.20)

| 检查项 | 满分 | 合格标准 |
|--------|------|----------|
| 统计检验选择 | 3 | 检验方法与数据类型/分布/样本量匹配 |
| 多重比较校正 | 2 | Bonferroni / Holm / FDR / BH，避免 Type I error 膨胀 |
| 效应量报告 | 3 | Cohen's d / OR / RR / HR, 不只有 p 值 |
| 置信区间 | 2 | 95% CI 报告 |
| 异常值处理 | 2 | 方法明确 (Grubbs/IQR/M-estimator), 合理性说明 |

**不合格**: 多重比较未校正 → WARNING
**不合格**: 仅有 p 值无效应量 → WARNING

## 方法学框架矩阵

按研究类型选择对应报告规范：

| 研究类型 | 报告规范 | 检查条目数 | 合格线 |
|----------|----------|-----------|--------|
| RCT | CONSORT 2010 | 25 | ≥20 (80%) |
| 观察性研究 | STROBE | 22 | ≥18 (82%) |
| 质性研究 | COREQ | 32 | ≥26 (81%) |
| 仿真研究 | STROBE-Sim / ODE标准 | 15 | ≥12 (80%) |
| 诊断准确性 | STARD | 29 | ≥23 (79%) |
| 系统评价/Meta | PRISMA 2020 | 27 | ≥22 (81%) |

## PICOS 框架

所有实验设计必须明确 PICOS：

```
P — Population: 研究人群/材料/系统
I — Intervention/Exposure: 干预/暴露因素
C — Comparison: 对照
O — Outcome: 主要/次要结局
S — Study Design: 研究设计类型
```

## 不合格判定

```
直接 FAIL (必须修改):
- D2 有对照组但无随机化
- D1 样本量 < 10 且无可接受理由
- D3 对照组选择不合理

WARNING (建议修改):
- D1 样本量 < 30 且无 power analysis
- D2 盲法不可行但未说明
- D4 混杂因素未控制
- D5 多重比较未校正
- D5 仅有 p 值无效应量
- 报告规范检查未达标

PASS (无 FAIL 且 WARNING ≤ 1):
- 所有 FAIL 检查通过
- WARNING 数量 ≤ 1
- 报告规范达标

REVISE (WARNING 2-3 个):
- 警告较多但无直接 FAIL

REJECT (WARNING ≥ 4 或 有 FAIL):
- 需重写实验设计
```

## 理论来源

- Moher D et al. (2010). CONSORT 2010 Statement. *Annals of Internal Medicine*.
- von Elm E et al. (2007). STROBE Statement. *Lancet*.
- Tong A et al. (2007). COREQ checklist. *International Journal for Quality in Health Care*.
- Bossuyt PM et al. (2015). STARD 2015. *Annals of Internal Medicine*.
- Page MJ et al. (2021). PRISMA 2020. *BMJ*.
- Sim J & Wright CC (2003). COSMIN (reliability/validity). *Journal of Clinical Epidemiology*.
- PICOS framework: 临床流行病学标准框架
