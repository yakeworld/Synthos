# HCS-3WT 论文图片完整性审计

## 发现问题

`05-figures` 目录有 6 张图（fig1-fig6），但论文正文只引用了 1 张（fig1），5 张缺失：

| 图 | 状态 | 说明 |
|---|------|------|
| fig1_system_architecture.pdf | ✅ 已引用 | 系统架构图 |
| fig2_roc_curves.pdf | ❌ 缺失 | ROC 曲线 |
| fig3_confusion_matrices.pdf | ❌ 缺失 | 混淆矩阵 |
| fig4_feature_importance.pdf | ❌ 缺失 | 特征重要性 |
| fig5_ablation_study.pdf | ❌ 缺失 | 消融实验 |
| fig6_threshold_sensitivity.pdf | ❌ 缺失 | 阈值敏感性 |

## 检测方法

```bash
# 1. 从 LaTeX 提取所有 \includegraphics 路径
grep -n 'includegraphics' hcs3wt-breast-cancer.tex

# 2. 列出 05-figures 目录
ls 05-figures/*.pdf

# 3. 对比：目录存在但论文未引用 = 缺失
# 使用 Python 或 shell 脚本对比两组路径
```

## 修复步骤

1. 在 LaTeX 正文中为每张缺失图添加 `\begin{figure}...\includegraphics...\end{figure}` 块
2. 确保图片有 caption、label、和正文引用（`\ref{fig:xxx}`）
3. 更新 `05-figures/` 目录与 LaTeX 引用的一致性
4. 重新编译验证图片出现在 PDF 中

## 关键规则

- 每次审计论文必须同时检查：数值一致性 + 图片完整性（论文引用 vs 目录存在）
- 图片缺失不仅是"少了张图"，更是"数据支持不够"——每张数据图都应有对应的生成脚本
- 检查 `03-code/experiments/` 目录中生成脚本数量是否 >= `05-figures/` 中 PDF 数量
- 每张图必须有对应的生成脚本（铁律：图↔脚本1对1）