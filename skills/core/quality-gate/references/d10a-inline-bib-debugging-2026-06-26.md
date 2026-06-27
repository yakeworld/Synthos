# D10a Inline Bibliography Debugging — HCS-3WT Case

## Date
2026-06-26

## Scenario
HCS-3WT 论文同时存在：
- `hcs3wt-breast-cancer.tex` — 使用 inline `thebibliography` 环境（29个bibitem）
- `references.bib` — 外部BibTeX文件（32个条目）

## Problem
D10a检查工具错误地用 references.bib 的键集合匹配 paper.tex 的 `\cite{}` 键：
- 6个 inline thebibliography 键不在 references.bib 中
- 报告 D10a = 23/29 = 79.3%
- 实际 D10a = 29/29 = 100%（cite ↔ bibitem 完全匹配）

## Root Cause
D10a 工具假设外部 bib 引用模式，但论文使用 inline thebibliography。
两个不同的引用来源被错误地比较。

## Fix
1. 从 inline thebibliography 提取 6 个缺失条目
2. 转为 BibTeX 格式并添加到 references.bib
3. 从 references.bib 删除 9 个未使用条目
4. 重新编译验证：`pdflatex` 0 errors, 0 warnings, 0 undefined citations

## Files Modified
- references.bib: 32→29 entries
- hcs3wt-breast-cancer.tex: 添加 Acknowledgments，修复重复段落
- experiment_results_wbc_original.json: 添加 hcs_fn_std
- wbc_original_results.json: 归档为 .DELETED

## Prevention
当 D10a < 100% 时，首先检查论文是否使用 inline thebibliography。
如果是，必须用 cite ↔ bibitem 计算而非 cite ↔ bib文件。