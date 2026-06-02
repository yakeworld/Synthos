# Task Templates per Dimension and Priority

## Experiment Completeness Tasks

### HIGH priority (score < 50)
1. "补充缺失的SOTA对比方法（目标：5+个）"
   - Add at least 5 SOTA comparison methods
   - Run cross_validate on each method
   - Record accuracy, F1, AUC per method
2. "完善消融实验（目标：5+组）"
   - Design 5+ ablation configurations (remove Expert B, remove Expert A, single expert, etc.)
   - Run each ablation and record results
   - Generate ablation results JSON
3. "补充泛化性验证（目标：2+个数据集）"
   - Add at least 2 additional datasets (e.g., Pima Diabetes, Wisconsin Prognostic)
   - Run 5-fold CV on each
   - Cross-domain evaluation: train on one dataset, test on another

### MEDIUM priority (50-70)
1. "检查并修复自动化率计算逻辑"
   - Verify predict() uses correct feature selection
   - Verify cross_val_predict receives correct X subset
   - Test with small dataset first

### LOW priority (>70)
1. "增加独立验证集测试"
   - Split data into train/val/test
   - Report test-only metrics
2. "补充统计显著性检验"
   - Add t-tests or Wilcoxon tests between methods

## Methodological Rigor Tasks

### HIGH priority (score < 50)
1. "检查Pipeline封装完整性"
   - Ensure all preprocessing steps are in ImbPipeline
   - Verify no data leakage from train to test
2. "验证数据泄漏防护措施"
   - Check that feature selection is done inside CV folds
   - Check that SMOTE is applied only to training fold data

### MEDIUM priority (50-70)
1. "确保特征选择独立于CV流程"
   - Compute f_scores on training fold only
   - Apply to both training and test folds
2. "添加错误处理和边界情况检查"
   - Add try/except around cross_val_predict
   - Handle single-class splits gracefully

### LOW priority (>70)
1. "增强Pipeline封装（添加更完整的实验记录）"
2. "添加更详细的实验可复现性说明"
3. "增加边界情况测试"

## Writing Quality Tasks

### HIGH priority (score < 50)
1. "全文语言润色"
2. "调整结构逻辑"
3. "统一术语使用"

### MEDIUM priority (50-70)
1. "优化逻辑流和段落过渡"
2. "确保字数达标（目标：5000+）"
3. "检查术语一致性"

### LOW priority (>70)
1. "全文语言润色" — polish academic tone
2. "检查术语一致性" — verify HCS-3WT, Expert A/B/C, Gray Zone etc. are used consistently
3. "优化逻辑流和段落过渡" — improve transitions between sections

## Citation Integrity Tasks

### HIGH priority (score < 50)
1. "补充缺失的bib条目"
   - For each paper citation not in bib, add the entry
   - Use consistent key format: AuthorYearShortTitle
2. "统一引用格式"

### MEDIUM priority (50-70)
1. "验证所有论文引用在bib中存在"
2. "检查引用格式一致性"

### LOW priority (>70)
1. "验证所有论文引用在bib中存在" — quick check only
2. "检查引用格式一致性" — verify all @Article, @InProceedings etc.

## Figure Completeness Tasks

### HIGH priority (score < 50)
1. "生成缺失图表"
2. "确保所有图表有PDF和PNG版本"

### MEDIUM priority (50-70)
1. "确保所有图表在论文中正确引用"
2. "检查图表数量是否充足（目标：8+）"
3. "确保所有图表有PDF和PNG版本"
4. "提升图表质量和可读性"

### LOW priority (>70)
1. "确保所有图表在论文中正确引用"
2. "检查图表数量是否充足（目标：8+）"
3. "提升图表质量和可读性"
