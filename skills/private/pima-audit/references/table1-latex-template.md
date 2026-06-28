% Table 1: Literature Comparison — Data Leakage Analysis
% Template for PIMA / Diabetes prediction methodology audit papers
% Copy this file into 01-manuscript/ and \input{table1_literature_audit.tex}

\begin{longtable}{p{2.2cm} p{2.5cm} p{1.3cm} c c c c c c c p{2.5cm} p{2.8cm} c}
\caption{Literature comparison of \dataset{} machine learning studies with data leakage analysis.}
\label{tab:literature_audit} \\
\toprule
\textbf{Reference} & \textbf{Journal} & \textbf{Dataset} &
\textbf{Acc (\%)} & \textbf{F1} & \textbf{Sens. (\%)} &
\textbf{Spec. (\%)} & \textbf{AUC} & \textbf{Zero Handling} &
\textbf{SMOTE} & \textbf{CV Method} & \textbf{Leakage Path} &
\textbf{Severity} \\
\midrule
\endfirsthead
\multicolumn{13}{c}{{\bfseries Table 1 continued from previous page}} \\
\toprule
\textbf{Reference} & \textbf{Journal} & \textbf{Dataset} &
\textbf{Acc (\%)} & \textbf{F1} & \textbf{Sens. (\%)} &
\textbf{Spec. (\%)} & \textbf{AUC} & \textbf{Zero Handling} &
\textbf{SMOTE} & \textbf{CV Method} & \textbf{Leakage Path} &
\textbf{Severity} \\
\midrule
\endhead
\midrule
\multicolumn{13}{r}{\footnotesize{\textit{Continued on next page\ldots}}} \\
\endfoot
\bottomrule
\multicolumn{13}{l}{\footnotesize{Note. Acc = Accuracy; Sens. = Sensitivity; Spec. = Specificity; AUC = Area Under Curve.}} \\
\multicolumn{13}{l}{\footnotesize{NR = Not Reported; Zero Handling: $\checkmark$Correct / $\times$Incorrect / NR; SMOTE: Global/Within-fold/No.}} \\
\bottomrule
\endlastfoot

% ============================================================
% CRITICAL — Global SMOTE/Preprocessing Before CV
% ============================================================
% Row template:
% Author \cite{key} & JournalAbbr & Dataset & AccValue & F1Value & SensValue & SpecValue & AUCValue & ZeroMark & SMOTEMark & CVMethod & LeakChain & CRITICAL \\
% \midrule
% ... add rows here ...

% ============================================================
% MODERATE — Partial preprocessing before split/CV
% ============================================================

% ============================================================
% MILD — Minor leakage risk
% ============================================================

% ============================================================
% NONE — Correct methodology
% ============================================================

\hline
\textbf{This study} & \textbf{—} & \textbf{\dataset{}} &
\textbf{\ourAcc{}} & \textbf{\ourFOne{}} &
\textbf{---} & \textbf{---} & \textbf{---} &
\textbf{$\checkmark$} & \textbf{Within-fold} &
\textbf{\ourCV{}} &
\textbf{All preprocessing inside CV folds} &
\textbf{NONE} \\

\end{longtable}
