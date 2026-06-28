# HCS-3WT 数值不一致修复实录

**Date**: 2026-06-29
**Skill**: paper-experiment-audit, quality-gate
**Category**: G7 数值验证 / numerical consistency audit

## 问题发现

HCS-3WT 论文综合质量检查发现 P0 级别数值不一致：

### P0-1: 单分类器数值偏差 >2%

| 模型 | Table 2 论文值 | JSON 实际值 | 偏差 |
|------|---------------|------------|------|
| LR   | 0.9591 | 0.9360 | +2.31% |
| CatBoost | 0.9640 | 0.9438 | +2.02% |
| SVC  | 0.9622 | 0.9329 | +2.93% |
| RF   | 0.9635 | 0.9387 | +2.48% |
| ET   | 0.9622 | 0.9422 | +2.00% |

### P0-2: 自动化率差异 8pp
- 论文声称: 79.07%
- JSON 实际: 70.93%

### 根因
代码中 `SelectKBest(f_classif, k=15)` 但论文声称 k=6。不同 k 值导致完全不同的精度结果。

## 修复过程

### Step 1: 代码参数修正
```bash
# run_hcs3wt.py: SelectKBest k=15 → k=6
```

### Step 2: 重新运行实验
```bash
python3 run_hcs3wt.py
# 输出: k=6 单分类器 ACC 范围 0.930-0.951
# HCS-3WT: accuracy=0.9510, auto_rate=0.6821, auto_acc=0.9885
```

### Step 3: 更新论文所有位置（15处）

| 位置 | 原值 | 新值 |
|------|------|------|
| Abstract | 79.07% | 68.21% |
| Abstract | 99.35% | 98.85% |
| Abstract | 0.9657 | 0.9510 |
| Abstract | 42.22% | 25.57% |
| Abstract | n=699, 9 features | n=569, 30 features |
| Introduction | 79.07% | 68.21% |
| Table 2 (6 rows) | 旧值 | k=6 JSON 值 |
| Table 3 (9 rows) | 旧值 | k=6 JSON 值 |
| Data Source | 699, 9 features | 569, 30 features |
| Results/FN | -28% | -38.7% |
| Discussion | 79.07%, 99.35% | 68.21%, 98.85% |
| Conclusion | 79.07%, 99.35% | 68.21%, 98.85% |

### Step 4: 修复图脚本硬编码
- `generate_fig3_confusion_matrices.py`: 硬编码 → 从 experiment_results.json 读取
- `generate_fig4_feature_importance.py`: 重写为从 JSON/catboost_info 读取

### Step 5: LaTeX 编译验证
```bash
pdflatex -interaction=nonstopmode paper.tex
# 结果: 成功，PDF 290KB
# 发现: Table 3 最后一行缺 `\\`，已修复
```

### Step 6: 验证
```bash
grep '79.07' paper.tex    # 0 results ✅
grep '99.35' paper.tex    # 0 results ✅
grep '0.9657' paper.tex   # 0 results ✅
grep '699' paper.tex      # 0 results ✅
```

### Step 7: 更新 state.json
- score: 0.73 → **0.88**
- status: → **healthy**
- last_modification: 完整文件清单

## 关键教训

1. **代码是真理源**：paper 数字必须匹配 experiment_results.json
2. **参数一致性优先**：k 值、CV 策略、样本量必须在代码和论文中一致
3. **全文 grep 检查**：关键数字出现在 6+ 个位置，必须逐位置更新
4. **图脚本也要改**：硬编码的数字是技术债，迟早被发现
5. **编译后立即检查**：Table 最后一行 `\\` 缺失是最常见的 LaTeX 错误
6. **更新 JSON 而非反向**：如果实验结果与论文不符，修改论文以匹配 JSON
