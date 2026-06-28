# Ablation Study Template

## Standard Structure

```latex
\section{Ablation Study: Component-wise Performance Analysis}

To systematically evaluate the contribution of each component in our pipeline, we conducted an ablation study. We progressively removed key components from our full method and measured the performance degradation on the $N$ validation images.

\noindent\textbf{V1 (基础方法):} 仅使用核心方法，不包含任何附加组件。

\noindent\textbf{V2 (+ 组件A):} 在基础方法上添加组件A（如：梯度优化、3D约束等）。

\noindent\textbf{V3 (+ 组件B):} 在V2基础上添加组件B（如：眼裂处理、自适应权重等）。

\noindent\textbf{V4 (完整方法):} 包含所有组件的完整pipeline。

The results are presented in Table~\ref{tab:ablation}.

\begin{table}[htbp]
\centering
\caption{Ablation study: Component-wise performance on $N$ validation images}
\label{tab:ablation}
\begin{tabular}{l|c}
\hline
\textbf{Variant} & \textbf{Performance Metric} \\
\hline\hline
V1 (基础方法) & $X.XXXX$ \\
V2 (+ 组件A) & $X.XXXX$ \\
V3 (+ 组件B) & $X.XXXX$ \\
V4 (完整方法) & \textbf{$X.XXXX$} \\
\hline
\end{tabular}
\end{table}

The ablation results demonstrate that each component contributes meaningfully to the final performance:

\begin{itemize}
\item[\textbf{--}] The addition of Component A (V1 $\to$ V2) improves performance by $+\Delta$, confirming that Component A provides complementary signals to the core method.

\item[\textbf{--}] Component B (V2 $\to$ V3) improves performance by $+\Delta$, validating the importance of Component B in handling [specific challenge].

\item[\textbf{--}] Data cleaning and validation (V3 $\to$ V4) improves performance by $+\Delta$, demonstrating the value of removing low-quality samples and correcting inaccurate labels.

\item[\textbf{--}] The cumulative improvement from V1 to V4 of $+\Delta$ demonstrates that our full pipeline synergistically combines multiple constraints.
\end{itemize}

## Key Principles

1. **Each variant must show positive contribution** — If a component shows no improvement or negative impact, it should be removed or reconsidered.

2. **Incremental building** — Each variant builds on the previous one, not independently. This shows the marginal contribution of each component.

3. **Quantitative + Qualitative** — Report both the numerical improvement and the reason WHY each component helps.

4. **Final variant is the full method** — Always include the complete method as the final variant (V4 or higher) to show the best performance.

5. **Consistent evaluation** — All variants must be evaluated on the same dataset with the same metrics.

## Example: 3D Eyeball Iris Segmentation

```latex
\section{Ablation Study: Component-wise Performance Analysis}

To systematically evaluate the contribution of each component in our pipeline, we conducted an ablation study. We progressively removed key components from our full method and measured the performance degradation on the 27,086 validation images.

\noindent\textbf{V1 (3D model only):} Using only the 3D eyeball model with Powell optimization, without gradient-based refinement.

\noindent\textbf{V2 (3D + gradient):} Full method with 3D model, Powell optimization, and gradient-based boundary refinement.

\noindent\textbf{V3 (3D + gradient + eyelid):} Complete method with 3D model, gradient refinement, and eyelid occlusion handling.

\noindent\textbf{V4 (3D + gradient + eyelid + data cleaning):} Full pipeline including data cleaning and validation.

The results are presented in Table~\ref{tab:ablation}.

\begin{table}[htbp]
\centering
\caption{Ablation study: Component-wise performance on 27,086 validation images}
\label{tab:ablation}
\begin{tabular}{l|c}
\hline
\textbf{Variant} & \textbf{Dice} \\
\hline\hline
V1 (3D model only) & 0.9682 \\
V2 (3D + gradient refinement) & 0.9745 \\
V3 (+ eyelid occlusion handling) & 0.9791 \\
V4 (Full pipeline) & \textbf{0.9834} \\
\hline
\end{tabular}
\end{table}

The ablation results demonstrate that each component contributes meaningfully to the final performance:

\begin{itemize}
\item[\textbf{--}] The gradient-based refinement (V1 $\to$ V2) improves Dice by +0.0063, confirming that gradient information provides complementary signals to the 3D geometric constraints.

\item[\textbf{--}] Eyelid occlusion handling (V2 $\to$ V3) improves Dice by +0.0046, validating the importance of fair evaluation on visible iris regions only.

\item[\textbf{--}] Data cleaning and validation (V3 $\to$ V4) improves Dice by +0.0043, demonstrating the value of removing low-quality samples and correcting inaccurate labels.

\item[\textbf{--}] The cumulative improvement from V1 to V4 of +0.0152 demonstrates that our full pipeline synergistically combines multiple constraints.
\end{itemize}
```

## When to Use

- **Multiple pipeline components**: When your method has 3+ distinct stages or components
- **Novel contributions**: When you want to highlight the marginal contribution of each novel component
- **Reviewer request**: When reviewers ask for ablation studies to justify design choices
- **High-impact claims**: When you claim "significantly better" performance, ablation strengthens the claim

## When NOT to Use

- **Single-method papers**: If your paper proposes one unified method with no components to ablate
- **Theoretical papers**: If the paper is purely theoretical with no experimental pipeline
- **Too many components**: If you have >5 components, consider grouping them into logical categories

## Common Pitfalls

1. **Negative contribution**: If a component shows no improvement, do NOT include it in the final method or explain why it's still useful (e.g., for robustness, not accuracy).

2. **Non-incremental variants**: Each variant must build on the previous one. V2 should include V1's components + new ones.

3. **Missing analysis**: Don't just list numbers — explain WHY each component helps.

4. **Inconsistent evaluation**: All variants must use the same dataset, same metrics, same evaluation protocol.

5. **Forgotten full method**: Always include the complete method as the final variant to show the best performance.
