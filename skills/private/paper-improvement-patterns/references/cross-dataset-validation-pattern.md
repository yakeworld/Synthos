# 跨数据集验证集成模式

> 当实验代码已完成多个数据集的验证，但论文仅展示单一数据集时使用。

## 触发条件

- 实验代码目录 (`03-code/`) 中存在多数据集实验脚本（如 `run_cross_dataset.py`）
- 存在跨数据集结果文件（如 `cross_dataset_results.json`）
- 论文 Discussion/Limitations 中声称"缺乏外部验证"

## 标准集成步骤

### Step 1: 发现所有已实验的数据集

```bash
# 扫描 03-code/ 目录
grep -n "load_\|fetch_\|read_csv\|datasets\." 03-code/experiments/*.py -r 2>/dev/null | grep -v catboost
```

常见模式：
- `sklearn.datasets.load_breast_cancer()` → WDBC
- `pd.read_csv("*diabetes*")` → 各种糖尿病公开数据集  
- `pd.read_csv("*BRFSS*")` → CDC 行为风险监测数据

### Step 2: Methods 添加

在现有 Methods 末尾添加新 subsection：

```latex
\subsection{Cross-Dataset Validation Protocol}
To demonstrate the generalizability beyond [主数据集], we evaluated on [N] additional datasets.
[Dataset 1]: [来源], [样本量] samples, [特征数] features, [患病率] prevalence.
[Dataset 2]: [来源], [样本量] samples, [特征数] features, [患病率] prevalence.
An identical protocol ([CV方案], [模型]) was applied to all datasets.
```

### Step 3: Results 添加

在现有 Results 中添加新 subsection + 跨数据集 Table：

```latex
\subsection{Cross-Dataset Validation}
Table~\ref{tab:cross_dataset} presents the comparison across all datasets.
The magnitude of [关键指标] inflation is proportional to [关键变量].
This pattern confirms that [核心发现] is a general property, not dataset-specific.

\begin{table*}
\centering
\caption{标题}
\label{tab:cross_dataset}
\begin{tabular}{lcccccc}
\toprule
\textbf{Dataset} & \textbf{n} & \textbf{Prevalence} & \textbf{Helix Metric} & \textbf{Leaky Metric} & \textbf{Inflation} \\
\midrule
Dataset A & N & P\% & X.XXX & Y.YYY & +Z.Z\% \\
Dataset B & N & P\% & X.XXX & Y.YYY & -Z.Z\% \\
\bottomrule
\end{tabular}
\end{table*}
```

### Step 4: Discussion/Limitations 更新

**删除或替换**以下类型的自相矛盾声明：

```latex
% 删除（如果已添加跨数据集结果）：
The current study does not evaluate the framework on a distinct, external validation dataset.

% 替换为：
Our cross-dataset validation across [N] datasets confirms that [核心发现] is a general property of [现象], proportional to [关键变量]. [最极端的数据集] shows the most severe [现象], demonstrating that [方法论] is most critical where [临床影响] is greatest.
```

### Step 5: 补充缺失的数据集文献引用

| 数据集 | 标准引用 |
|:-------|:---------|
| PIDD | Smith1988 |
| WDBC/Wisconsin Breast Cancer | Wolberg1990, Street1993 |
| CDC BRFSS | CDC BRFSS 原始文献 |
| Early Diabetes (UCI) | UCIEarlyDiabetes2024 (Sisodia) |
| NHANES | CDC NHANES 原始文献 |
| MIMIC-III | Johnson2016MIMIC |

## 关键陷阱

1. **自相矛盾**：Limitations 中说"缺乏外部验证"但代码已有结果 → 必须修复
2. **缺失引用**：实验用了数据集但论文没有学术依据 → 必须补充 bib 条目
3. **不同 CV 策略**：主实验用 10-fold CV 但跨数据集用 5x2 CV → 必须明确说明区别
