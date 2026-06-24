# Table 1 文献对比表制作协议

> 2026-06-24 实战确认。PIMA 案例中 Table 1 暴露 3 个核心问题：虚构文献混入、自身指标留空、用 Ensemble 而非最佳单模型。

## 铁律一：文献存在性验证

```
凡文献对比表（Table 1）中的每条引用，必须在进入论文前通过三级过滤器：

Level 1: 查本地 PDF 目录
  06-references/pdfs/ 或 enhanced_bibtex/pdfs/
  有 PDF = 高可信
  无 PDF = 高危，必须进入 Level 2

Level 2: SS/Crossref API 搜索
  搜索作者+标题+年份（三字段同时匹配）
  有记录 = 待 Level 3 复核
  无记录 = 虚构 ❌

Level 3: pdftotext 读 PDF 首页
  确认期刊名、DOI、实际性能指标
  防止下载到同名不同内容的论文（如 DOI 相似但主题不同）

保留策略:
  只保留有 PDF + 可验证的论文
  3-4 篇高质量期刊即可，不必填满表
  被 PLOS ONE 发 Expression of Concern 的论文需标注或删除

虚构信号:
  Acc > 95% (PIDD 数据集)
  Acc = 100%
  所有指标同时最优 (Acc>95, F1>0.95, AUC>0.99)
  Semantic Scholar 无记录
  多篇同主题论文均无 PDF
```

## 铁律二：自身指标必须全填

```
"Ours" 行的 Acc/F1/Sen/Spe/AUC 列必须全部填入实际数值，不可留空：
  - Acc: 取 best model 的 Accuracy
  - F1: 取 best model 的 F1
  - Sen: 取 best model 的 Recall
  - Spe: 从混淆矩阵推导 TN/(TN+FP)
  - AUC: 取 best model 的 AUC
脚注注明数值来源（如 "CatBoost, no leakage baseline"）
```

## 铁律三：最佳单模型为对比基线

```
Table 1 的 "Ours" 行使用最佳单模型（如 CatBoost）而非 Ensemble。
理由：读者问"你们最好的模型是多少"时，答案是 CatBoost F1=0.707，
不是 Ensemble F1=0.697。Ensemble 不超越最佳单模型时不应作为宣传数值。
论文其他位置（ablation study）可保留 Ensemble 结果。
```

## 铁律四：论文规范路径

```
Synthos 论文标准路径:
  /media/yakeworld/sda2/Synthos/outputs/papers/<paper-name>/
  01-manuscript/paper.tex  （主文件）
  06-references/           （参考文献 PDF + bib）
  state.json               （论文状态）

不可操作 academic_writer/ 或 yakeworld/akne/ 下的版本。
outputs/papers/ 是权威发布版本。
```
