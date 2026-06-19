# 同行评审模拟 (多角色评审)

> 理论来源：Nature/Science 审稿标准; Bédard et al. (2020) 同行评审研究;
> MacCoun (1998) "Difficulties encountered in the scientific process"

## 多角色评审框架

模拟真实审稿流程，每个角色从不同专业视角评估论文：

### Reviewer A: 方法学专家

```
评审维度:
1. 研究设计适当性     0-10  (是否回答了研究问题?)
2. 统计方法正确性     0-10  (统计检验选择? 假设检验前提?)
3. 样本量/功效       0-10  (n 是否足够? 功效分析?)
4. 偏差控制          0-10  (混杂因素/选择偏差/信息偏差)
5. 可复现性          0-10  (数据/代码/流程是否可复现?)
6. 伦理合规          0-10  (IRB/知情同意/动物伦理)

Verdict:
  ≥ 70: Accept with minor revisions
  50-69: Major revision needed
  < 50: Reject
```

### Reviewer B: 领域专家

```
评审维度:
1. 文献覆盖度       0-10  (关键文献是否覆盖?)
2. 领域定位准确性   0-10  (Related Work 是否准确?)
3. 创新性           0-10  (与已有工作的区别?)
4. 技术深度         0-10  (是否深入领域核心问题?)
5. 实际意义         0-10  (对领域/实践的贡献?)
6. 写作质量         0-10  (清晰度/逻辑/结构?)

Verdict:
  ≥ 70: Accept with minor revisions
  50-69: Major revision needed
  < 50: Reject
```

### Reviewer C: 统计专家

```
评审维度:
1. 统计模型选择     0-10  (模型适合数据类型?)
2. 假设检验         0-10  (假设合理? 前提满足?)
3. 多重比较校正     0-10  (是否校正?)
4. 效应量报告       0-10  (有效应量+CI?)
5. 结果解释         0-10  (统计显著 ≠ 实际显著?)
6. 敏感性分析       0-10  (稳健性检查?)

Verdict:
  ≥ 70: Accept
  50-69: Revision on statistics required
  < 50: Reject
```

### Senior Editor: 最终裁决

```
综合三个 Reviewer 评分:

decision_matrix:
  A ≥ 70 AND B ≥ 70 AND C ≥ 70:     ACCEPT
  A ≥ 50 AND B ≥ 50 AND C ≥ 50:     MAJOR REVISION
  任一 < 50:                          MAJOR REVISION
  两及以上 < 30:                      REJECT

额外考虑:
  - 领域 Editor 偏好 (创新性 vs 稳健性)
  - 期刊定位 (T1=要求高创新; Q2-Q3=要求稳健即可)
  - 版面/时间约束 (不直接评分)
```

## 评审冲突检测

```
当 Reviewer 评分差异 > 30 分:
  → 触发"仲裁机制"
  → 检查差异原因 (方法分歧/标准差异/理解错误)
  → Senior Editor 需给出详细理由
```

## 模拟输出

```
最终报告包含:
1. 各 Reviewer 详细评分 + 评语
2. Senior Editor 最终决定
3. 必须修改项 (Must-fix)
4. 建议修改项 (Nice-to-have)
5. 预估期刊级别建议
```

## 不合格标准

```
1. 任一 Reviewer < 30 → 直接建议 REJECT
2. A (方法学) < 40 → 方法有根本缺陷
3. B (领域) < 40 → 对领域理解偏差
4. C (统计) < 40 → 统计方法有严重问题
5. 评审冲突未仲裁 → 报告不完整
```

## 理论来源

- Bédard M et al. (2020). "Peer review." *Nature Human Behaviour*, 4, 116-118.
- MacCoun R (1998). "Difficulties encountered in the scientific process." *Journal of Experimental Psychology*, 24, 44-51.
- Ioannidis JPA (2006). "Why most discovered true associations are inflated." *Epidemiology*, 19(5), 640-648.
- Fleming C et al. (2015). "Peer review in clinical research." *Journal of Clinical Oncology*, 33(30), 3432-3438.
