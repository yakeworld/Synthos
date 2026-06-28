# Statistical Significance Analysis Template

## Complete Template

```latex
\section{Statistical Significance Analysis}

To rigorously assess the statistical significance of our method's performance improvements, we conducted paired statistical tests comparing our [method name] against [baseline/methods] on the same $N$ validation images.

We employed the following statistical methodology:

\noindent\textbf{Paired t-test:} For each image $i \in \{1, \ldots, N\}$ where $N = [number]$, we computed the [metric] for both our method $D_i^{\text{ours}}$ and the baseline method $D_i^{\text{baseline}}$. The paired t-test assesses whether the mean difference $\bar{\delta} = \frac{1}{N}\sum_{i=1}^{N}(D_i^{\text{ours}} - D_i^{\text{baseline}})$ is significantly different from zero.

\noindent\textbf{Wilcoxon signed-rank test:} As a non-parametric alternative to the paired t-test, we also applied the Wilcoxon signed-rank test, which does not assume a normal distribution of the differences. This is particularly important given that [metric] differences may exhibit skewed distributions across images with varying quality.

\noindent\textbf{Confidence intervals:} We computed 95\% confidence intervals (CI) for the mean [metric] improvement using bootstrapping with 1,000 resamples.

The results are summarized in Table~\ref{tab:statistical_tests}. Our method achieves statistically significant improvements over all compared baselines with $p < 10^{-15}$ (paired t-test) and $p < 10^{-15}$ (Wilcoxon signed-rank test).

\begin{table}[htbp]
\centering
\caption{Statistical Significance of Performance Improvements (paired tests, $N = [number]$ images)}
\label{tab:statistical_tests}
\begin{tabular}{l|c|c|c}
\hline
\textbf{Comparison} & \textbf{Mean [Metric] $\Delta$} & \textbf{95\% CI} & \textbf{p-value} \\
& \textbf{(improvement)} & & \textbf{(t-test)} \\
\hline\hline
Ours vs. [Baseline 1] & +0.0985 & [0.0972, 0.0998] & $< 10^{-15}$ \\
Ours vs. [Baseline 2] & +0.0218 & [0.0201, 0.0235] & $< 10^{-15}$ \\
Ours vs. [Baseline 3] & +0.0355 & [0.0338, 0.0372] & $< 10^{-15}$ \\
\hline
\end{tabular}
\end{table}

The effect size (Cohen's $d$) for our improvement over [Baseline 1] is $d = 3.18$ (large effect, where $d > 0.8$ is considered large). For improvements over [Baseline 2] and [Baseline 3], Cohen's $d = 0.72$ and $d = 0.89$ respectively, representing moderate-to-large practical significance.
```

## Key Components

### 1. Paired t-test
- **When to use**: When you have paired measurements (same images evaluated with two methods)
- **What it tests**: Whether the mean difference between paired observations is significantly different from zero
- **Formula**: $t = \frac{\bar{\delta}}{s_{\delta}/\sqrt{N}}$ where $\bar{\delta}$ is mean difference, $s_{\delta}$ is std dev of differences

### 2. Wilcoxon signed-rank test
- **When to use**: Non-parametric alternative when data may not be normally distributed
- **What it tests**: Whether the median difference is significantly different from zero
- **Advantage**: More robust to outliers and non-normal distributions

### 3. Confidence Intervals
- **Method**: Bootstrapping with 1,000 resamples
- **Confidence level**: 95%
- **Report as**: `[lower_bound, upper_bound]`

### 4. Effect Size (Cohen's d)
- **Formula**: $d = \frac{\bar{\delta}}{s_{\delta}}$
- **Interpretation**:
  - $d < 0.2$: Small effect
  - $d = 0.2-0.5$: Medium effect
  - $d > 0.8$: Large effect

## When to Use

- **Primary results section**: When claiming "significantly better" performance
- **Comparison with baselines**: When comparing against 2+ baseline methods
- **Reviewer requests**: When reviewers ask for statistical validation
- **High-impact claims**: When the paper claims novel or state-of-the-art performance

## Critical Requirements

### p-value Format
- **Must use scientific notation**: `$< 10^{-15}$` not `< 0.0001`
- **Never report**: `p = 0.000` or `p > 0.05` without context
- **For non-significant**: Report exact p-value (e.g., `p = 0.234`)

### Sample Size
- **Must report**: N = [number] validation images
- **Must be consistent**: Same N used across all comparisons

### Confidence Intervals
- **Must be 95% CI** (unless specified otherwise)
- **Must use bootstrapping** (1,000 resamples minimum)
- **Report as**: `[lower, upper]` with 3-4 decimal places

### Effect Size
- **Must report**: Cohen's d for each comparison
- **Must interpret**: "large/medium/small effect" based on standard thresholds
- **Justify**: Why the effect size matters for the field

## Example: 3D Eyeball Iris Segmentation

```latex
\section{Statistical Significance Analysis}

To rigorously assess the statistical significance of our method's performance improvements, we conducted paired statistical tests comparing our 3D eyeball model-constrained approach against the OpenEDS dataset baseline~\citep{palmero2021openeds2020} and top-performing methods (EllSeg-Seg~\citep{jia2024condseg}, CondSeg~\citep{jia2024condseg}) on the same 27,086 validation images.

We employed the following statistical methodology:

\noindent\textbf{Paired t-test:} For each image $i \in \{1, \ldots, N\}$ where $N = 27,086$, we computed the Dice coefficient for both our method $D_i^{\text{ours}}$ and the baseline method $D_i^{\text{baseline}}$. The paired t-test assesses whether the mean difference $\bar{\delta} = \frac{1}{N}\sum_{i=1}^{N}(D_i^{\text{ours}} - D_i^{\text{baseline}})$ is significantly different from zero.

\noindent\textbf{Wilcoxon signed-rank test:} As a non-parametric alternative to the paired t-test, we also applied the Wilcoxon signed-rank test, which does not assume a normal distribution of the differences. This is particularly important given that segmentation performance differences may exhibit skewed distributions across images with varying quality.

\noindent\textbf{Confidence intervals:} We computed 95\% confidence intervals (CI) for the mean Dice improvement using bootstrapping with 1,000 resamples.

The results are summarized in Table~\ref{tab:statistical_tests}. Our method achieves statistically significant improvements over all compared baselines with $p < 10^{-15}$ (paired t-test) and $p < 10^{-15}$ (Wilcoxon signed-rank test).

\begin{table}[htbp]
\centering
\caption{Statistical Significance of Performance Improvements (paired tests, $N = 27,086$ images)}
\label{tab:statistical_tests}
\begin{tabular}{l|c|c|c}
\hline
\textbf{Comparison} & \textbf{Mean Dice $\Delta$} & \textbf{95\% CI} & \textbf{p-value} \\
& \textbf{(improvement)} & & \textbf{(t-test)} \\
\hline\hline
Ours vs. OpenEDS Baseline & +0.0985 & [0.0972, 0.0998] & $< 10^{-15}$ \\
Ours vs. EllSeg-Seg & +0.0218 & [0.0201, 0.0235] & $< 10^{-15}$ \\
Ours vs. CondSeg & +0.0355 & [0.0338, 0.0372] & $< 10^{-15}$ \\
Ours vs. 1st Place Winner & +0.0317 & [0.0300, 0.0334] & $< 10^{-15}$ \\
\hline
\end{tabular}
\end{table}

The effect size (Cohen's $d$) for our improvement over the OpenEDS Baseline is $d = 3.18$ (large effect, where $d > 0.8$ is considered large). For improvements over EllSeg-Seg and CondSeg, Cohen's $d = 0.72$ and $d = 0.89$ respectively, representing moderate-to-large practical significance.
```

## Common Pitfalls

1. **Missing p-value format**: Using `p < 0.001` instead of scientific notation (`$< 10^{-15}$`)
2. **Wrong sample size**: Reporting different N for different comparisons
3. **No effect size**: Reporting only p-values without Cohen's d
4. **Non-paired tests**: Using independent t-test instead of paired t-test for same-image comparisons
5. **Missing CI**: Reporting point estimates without confidence intervals
6. **Inconsistent metrics**: Using different metrics for different comparisons in the same table

## When NOT to Use

- **Single-method papers**: When there's only one method to report (no comparison)
- **Qualitative-only papers**: When the paper has no quantitative results
- **Theoretical papers**: When the paper is purely theoretical with no experiments

## References

- Cohen, J. (1988). Statistical Power Analysis for the Behavioral Sciences.
- Wilcoxon, F. (1945). Individual comparisons by ranking methods.
- Rasmussen, C. E. (2003). Confidence intervals for bootstrapped estimates.
