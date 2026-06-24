# 乳腺癌论文质量审计实战 — 2026-06-21

## 背景

HCS-3WT 乳腺癌论文（article10_breast），Codex 执行完整质量审计闭环。

## 审计过程

### 阶段 1：初始审计（11 分钟）

Codex 扫描了论文目录（.tex, .bib, .md, JSON），发现：
- SOTA 数据全部 null（12 条记录，6 模型×2 数据集）
- 消融实验结果全部为空
- 5 个 CRITICAL + 7 个 MAJOR + 7 个 MINOR 问题

### 阶段 2：纠正与重新审计（20 分钟）

**关键纠正**：Auditor 误判 WDBC 的 SOTA 数据为 null。实际验证：
```python
# WDBC SOTA 数据是完整的
# Coimbra 的 SOTA 数据才是 nan（数据集加载问题）
```

**修复**：
1. 安装了缺失的依赖：seaborn 0.13.2, statsmodels 0.14.6, openml 0.15.1
2. 修复 Coimbra 数据集加载（OpenML 返回 Classification 而非 class 列）
3. 修复 numpy.ndarray.value_counts() 错误 → pd.Series(y).value_counts()
4. 修复 Coimbra 特征数不匹配（代码硬编码索引 20,23,25，但 Coimbra 只有 9 特征）

### 阶段 3：完整实验运行（32 分钟）

**3 数据集 × 8 模型 = 24 条 SOTA 数据全部成功**

关键发现：
- **WDBC**: HCS-3WT 与 SOTA 相当（p>0.05）
- **Coimbra**: HCS-3WT **显著优于** XGBoost（p=0.0061, Recall +9.49%）

统计显著性检验使用 scipy ttest_rel（配对 t 检验，相同 CV folds）。

### 阶段 4：审计报告更新

严重问题从 5 个降为 **0**，剩余 10 个（4 Major + 6 Minor）：
- M2.1: 作者信息占位符
- M2.2: 25 个引用中仅 1 个有 DOI
- M2.6: 模型超参数未报告
- M2.7: overfull hbox

## 经验教训

1. **审计前验证数据源** — 不要假设 JSON 文件一定是 null，实际读取验证
2. **Codex 可能误判** — Auditor 把 WDBC 说成全 null，实际完整
3. **依赖缺失是常见根因** — imbalanced-learn 导致 cross_validate 返回 null
4. **数据集特征数变化** — Coimbra 只有 9 特征，硬编码索引 20,23,25 会 IndexError
5. **统计检验用 scipy** — statsmodels 0.14.6 的 alternative 参数可能有问题
6. **OpenML 列名变化** — 某些数据集返回 'Classification' 而非 'class'
7. **numpy vs pandas** — numpy.ndarray 没有 value_counts()，需要 pd.Series() 包装