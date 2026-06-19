# 可重复性/开放科学框架

> 理论来源：Ioannidis (2005) "Why Most Published Research Findings Are False";
> Open Science Framework; Campbell et al. (2020) "Guidelines for reporting reliability and repeatability"

## 可重复性六大维度

### D1: 数据可用性声明

```
必须包含:
- 数据是否公开? (Yes/No/Conditional)
- 公开平台: (GitHub, Figshare, Zenodo, Dryad, OSF)
- 访问权限: (Open/Restricted/Available on request)
- DOI: 数据集是否有 DOI?

评分:
  Open + DOI → 1.0
  Open + no DOI → 0.7
  Restricted but available → 0.4
  Not available → 0.0
```

### D2: 代码可用性声明

```
必须包含:
- 代码是否公开? (Yes/No/Conditional)
- 代码仓库: (GitHub, GitLab, Bitbucket)
- 版本锁定: (commit hash/tag)
- 运行环境: (Docker, conda env, requirements.txt)
- 示例数据: 是否有可运行的示例?

评分:
  Open + Docker + 示例 → 1.0
  Open + requirements → 0.7
  Code available on request → 0.4
  Not available → 0.0
```

### D3: 预注册 (Preregistration)

```
必须包含:
- 是否在数据收集前注册研究计划?
- 注册平台: (OSF, AsPredicted, ClinicalTrials.gov, ECF)
- 预注册号: DOI 或 ID
- 研究类型: (RCT/观察性/仿真/其他)

评分:
  预注册 + DOI → 1.0
  预注册 + no DOI → 0.7
  计划预注册 → 0.4
  未预注册 → 0.0

注意:
  - 回溯性研究可豁免
  - 案例报告可豁免
  - 方法论论文可部分豁免
```

### D4: 报告指南符合度

```
按研究类型检查:
  RCT → CONSORT (25 items)
  观察性 → STROBE (22 items)
  质性 → COREQ (32 items)
  仿真 → STROBE-Sim (15 items)
  诊断 → STARD (29 items)
  系统评价 → PRISMA (27 items)

符合度 = 通过项 / 总项

评分:
  ≥ 80% → 1.0
  60-79% → 0.5
  < 60% → 0.0
```

### D5: 效应量与置信区间

```
必须包含:
- 主要结果的效应量 (Cohen's d, OR, RR, HR, r)
- 95% 置信区间
- 统计检验 p 值 (但不应仅有 p 值)

评分:
  效应量 + 95% CI + p 值 → 1.0
  效应量 + CI → 0.7
  效应量 only → 0.4
  无效应量 → 0.0
```

### D6: 负结果报告

```
必须包含:
- 所有预注册结局是否报告? (包括阴性结果)
- 是否报告不符合预期的发现?
- 是否报告实验失败/数据质量问题?

评分:
  所有预注册结局报告 → 1.0
  大部分报告 → 0.6
  选择性报告 → 0.2
  仅报告阳性结果 → 0.0
```

## 可重复性综合评分

```
reproducibility_score =
  D1(数据可用性) × 0.20 +
  D2(代码可用性) × 0.20 +
  D3(预注册) × 0.15 +
  D4(报告指南) × 0.15 +
  D5(效应量+CI) × 0.20 +
  D6(负结果报告) × 0.10

verdict:
  score ≥ 0.70: HIGHLY REPRODUCIBLE (高度可重复)
  0.40 ≤ score < 0.70: MODERATELY REPRODUCIBLE (部分可重复)
  score < 0.40: LOW REPRODUCIBILITY (可重复性差)
```

## Ioannidis 警告信号

```
以下信号增加"研究可能为假"的概率:
- 小样本 (n < 30) → ×2 风险
- 无预注册 → ×1.5 风险
- 多个结局测试 → ×1.3 风险
- 灵活性 (选 p-hacking) → ×2 风险
- 利益冲突 → ×1.2 风险
- 领域共识低 → ×2 风险
- 热领域 (追逐热点) → ×1.5 风险

风险信号越多，越需要独立验证。
```

## 理论来源

- Ioannidis, JPA (2005). "Why Most Published Research Findings Are False." *PLoS Medicine*, 2(8), e124.
- Campbell ML et al. (2020). "Guidelines for reporting reliability and repeatability." *Br J Sports Med*, 54, 1025-1026.
- Open Science Framework: https://osf.io/
- Nosek B et al. (2018). "The preregistration revolution." *PNAS*, 115(11), 2600-2606.
