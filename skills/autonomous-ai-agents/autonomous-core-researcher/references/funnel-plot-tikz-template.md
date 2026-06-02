# Publication Bias Funnel Plot — TikZ/pgfplots Template

## Usage
Add to paper.tex preamble:
```latex
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
```

## Template: Funnel plot for systematic review publication bias

```latex
\begin{figure}[htbp]
\centering
\begin{tikzpicture}
\begin{axis}[
    width=0.85\textwidth,
    height=0.6\textwidth,
    xlabel={Effect size (standardized mean difference)},
    ylabel={Standard error},
    y dir=reverse,
    xmin=-2, xmax=2,
    ymin=0, ymax=1.2,
    grid=both,
    minor grid style={gray!20},
    major grid style={gray!50},
    legend pos=north east,
    legend style={font=\footnotesize, draw=none, fill=white, fill opacity=0.8},
    tick label style={font=\footnotesize},
    label style={font=\small},
    title={Publication bias assessment}
]
% Pseudo 95% CI funnel boundary
\addplot[domain=-2:2, samples=100, thick, blue!50, dash pattern=on 5pt off 2pt]
    {1.2 - abs(x - 0.5) * 0.5};
\addlegendentry{Pseudo 95\% CI}

% Pooled estimate line
\addplot[domain=-0.2:0.2, samples=2, thick, red!70, dashed]
    {0};
\addlegendentry{Pooled estimate}

% Study points (replace with actual extracted data)
\addplot[only marks, mark=*, mark size=2, mark options={fill=black!40, draw=black!60}] 
    coordinates {
    (-0.15, 0.12) (0.35, 0.15) (0.65, 0.18) (-0.45, 0.22)
    (0.85, 0.28) (-0.25, 0.32) (0.15, 0.35) (-0.65, 0.38)
    (0.05, 0.42) (-0.35, 0.48) (0.55, 0.52) (-0.12, 0.55)
    (0.45, 0.60) (-0.55, 0.65) (0.25, 0.70) (-0.08, 0.75)
    (-0.85, 0.82) (0.15, 0.88) (-0.30, 0.95) (0.42, 1.05)
};
\addlegendentry{Included studies}
\end{axis}
\end{tikzpicture}
\caption{Funnel plot of included studies. Asymmetry toward positive findings may suggest publication bias.}
\label{fig:funnel}
\end{figure}
```

## Customization

- **Funnel boundaries**: Adjust `{1.2 - abs(x - 0.5) * 0.5}` to match your pooled estimate and SE scale
- **Study points**: Replace coordinates with actual extracted (effect size, SE) pairs from your meta-analysis
- **Labels**: Update xlabel/ylabel to match your effect size metric (SMD, logOR, Hedges' g, etc.)
- **Cron usage (simulated data)**: When no actual meta-analysis data is available (cron mode), use representative coordinates that show a realistic distribution — larger studies (low SE) are clustered near the pooled estimate, smaller studies (high SE) are more spread out. Label the figure caption accordingly: "Simulated funnel plot for illustrative purposes."

## Known issues

- `y dir=reverse` is required — funnels plot larger (more precise) studies at the top
- The funnel boundary formula `max_SE - abs(x - pooled_ES) * slope` must produce positive values for all x in the domain
- Use `ln()` not `log()` for natural log in pgfplots math expressions
