---
name: pidd-leakage-audit
description: '1. Never cite CRISP-DM without citing Shearer (2000) or Wirth & Hipp (2000). These are the original '
signature: 'pidd-leakage-audit -> private: synthetic skill for pidd leakage audit'
allowed-tools:
- terminal
- read_file
- write_file
- session_search
version: 1.0.0
license: MIT
metadata:
  synthos:
    atom_type: mechanical
    description: '1. Never cite CRISP-DM without citing Shearer (2000) or Wirth & Hipp (2000). These are the original '
    signature: 'pidd-leakage-audit -> private: synthetic skill for pidd leakage audit'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---


|
| Varoquaux | Olivier | 2018 | arXiv:1806.04876 |
| Shearer | Chris | 2000 | CRISP-DM Consortium |
| Wirth & Hipp | R. & J. | 2000 | Data-Mining |
| Kapoor | S. & A. | 2024 | Patterns 5(9):101065 |
| Chawla | N.V. et al. | 2002 | JAIR 16:321-357 |
| Stiglic | G. et al. | 2012 | Journal of Medical Systems |
| Lundberg | S.M. & S.I. | 2017 | NeurIPS |
| Collins | G.S. et al. | 2015 | Annals of Internal Medicine (TRIPOD) |
| Moons | K.G.M. et al. | 2019 | Annals of Internal Medicine (PROBAST) |
| Norgeot | B. et al. | 2020 | Nature Machine Intelligence (MI-CLAIM) |
| Smith | J.W. et al. | 1988 | CAMC |

## Pitfalls
- 
- 

## Verification
- 
- 

1. Never cite CRISP-DM without citing Shearer (2000) or Wirth & Hipp (2000). These are the original papers.
2. Never run CV without isolating preprocessing inside folds. This is the core of the methodology.
3. SMOTE before splitting = severe leakage. Recall collapses to ~0.50, Precision inflates to 1.00.
4. PIDD has 768 samples. Best model only reaches F1~0.71. Claims of F1>0.90 are always suspicious.
5. Global imputation = minor leakage. Only +0.6% F1 inflation. Technically incorrect.
6. Use imblearn.Pipeline, NOT sklearn.Pipeline. sklearn.Pipeline does NOT support SMOTE properly.
7. For SHAP analysis, use venv with numpy>=2.0. System Python on Debian has numpy 1.x compiled packages (numexpr, bottleneck) that crash with numpy 2.x. Create isolated venv.
8. CatBoost needs compilation from pip. Takes ~4 minutes. Install separately in venv.

## Output Contracts

- cv_results.csv: 10-fold CV metrics per model
- comprehensive_results.json: all results including CV, ensemble, SHAP
- run_shap.py: SHAP analysis script
- report.py: summary report generation

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 验证清单 · VERIFICATION
## 原则 (Principles)

- **凡引必溯**：CRISP-DM 必并引 Shearer (2000) 或 Wirth & Hipp (2000) 之原典，单引 CRISP-DM 者，非学术之诚。
- **预处入折**：交叉验证必使预处理（含 SMOTE、imputation）落入 fold 之内；折外预处即泄漏，Recall 崩、Precision 虚高。
- **知界而警**：PIDD 768 样本，最佳模型 F1 不过 0.71；凡 F1>0.90 之声称，皆疑，必查泄漏。
- **工具择用**：SMOTE 用 `imblearn.Pipeline`，勿用 `sklearn.Pipeline`（不支持 SMOTE）；SHAP 用独立 venv（numpy≥2.0）。


1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引


## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[PIDD-001]** 执行交叉验证时 → 必须将预处理（含 SMOTE、imputation）隔离在 fold 内部，严禁在数据分割前执行
- **[PIDD-002]** 处理类别不平衡数据时 → 必须使用 `imblearn.Pipeline` 而非 `sklearn.Pipeline`，以确保 SMOTE 正确支持
- **[PIDD-003]** 评估 PIDD 数据集模型性能时 → 若 F1 分数超过 0.90，必须视为异常并立即排查数据泄漏
- **[PIDD-004]** 进行 SHAP 可解释性分析时 → 必须创建独立 venv 并安装 numpy>=2.0，以避免系统 Python 编译包冲突
- **[PIDD-005]** 引用 CRISP-DM 方法论时 → 必须同时引用 Shearer (2000) 或 Wirth & Hipp (2000) 原始文献
- **[PIDD-006]** 处理缺失值时 → 禁止使用全局 imputation，必须在验证折内独立计算填充值以消除轻微泄漏

## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

# Pidd Leakage Audit---





|
| Varoquaux | Olivier | 2018 | arXiv:1806.04876 |
| Shearer | Chris | 2000 | CRISP-DM Consortium |
| Wirth & Hipp | R. & J. | 2000 | Data-Mining |
| Kapoor | S. & A. | 2024 | Patterns 5(9):101065 |
| Chawla | N.V. et al. | 2002 | JAIR 16:321-357 |
| Stiglic | G. et al. | 2012 | Journal of Medical Systems |
| Lundberg | S.M. & S.I. | 2017 | NeurIPS |
| Collins | G.S. et al. | 2015 | Annals of Internal Medicine (TRIPOD) |
| Moons | K.G.M. et al. | 2019 | Annals of Internal Medicine (PROBAST) |
| Norgeot | B. et al. | 2020 | Nature Machine Intelligence (MI-CLAIM) |
| Smith | J.W. et al. | 1988 | CAMC |

## Pitfalls
- 
- 

## Verification
- 
- 

1. Never cite CRISP-DM without citing Shearer (2000) or Wirth & Hipp (2000). These are the original papers.
2. Never run CV without isolating preprocessing inside folds. This is the core of the methodology.
3. SMOTE before splitting = severe leakage. Recall collapses to ~0.50, Precision inflates to 1.00.
4. PIDD has 768 samples. Best model only reaches F1~0.71. Claims of F1>0.90 are always suspicious.
5. Global imputation = minor leakage. Only +0.6% F1 inflation. Technically incorrect.
6. Use imblearn.Pipeline, NOT sklearn.Pipeline. sklearn.Pipeline does NOT support SMOTE properly.
7. For SHAP analysis, use venv with numpy>=2.0. System Python on Debian has numpy 1.x compiled packages (numexpr, bottleneck) that crash with numpy 2.x. Create isolated venv.
8. CatBoost needs compilation from pip. Takes ~4 minutes. Install separately in venv.

## Output Contracts

- cv_results.csv: 10-fold CV metrics per model
- comprehensive_results.json: all results including CV, ensemble, SHAP
- run_shap.py: SHAP analysis script
- report.py: summary report generation

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引

## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

