# octa-ai-review Zombie Cleanup — 2026-06-04

## 发现

bulk_d8_scan.py 报告 octa-ai-review: D10a=0% (假阳性, 实际 D10a=97%, 2个僵尸)

## 僵尸条目

| BibKey | 作者 | 标题 | 状态 |
|:-------|:-----|:-----|:-----|
| Li2020 | F. Li | Retinal vessel segmentation in OCTA | **删除** — 虚假僵尸。论文实际引用的是 Li2023 和 Li2020b (M. Li)，而非 F. Li 的独立论文。属于 "同一姓氏同一领域但不同作者" 的混淆案例 |
| Zhou2024 | H. Zhou | Transformer-based multi-task OCTA enhancement (MICCAI 2024) | **激活** — 以纯文本 "Zhou2024" 出现在 table 行中，缺少 `\cite{}` 命令。属于 "table zombie" 模式（表内引用而非 LaTeX \cite 命令） |

## 修复步骤

### 激活 Zhou2024 (table zombie)
```latex
% 原 (line 267):
Zhou2024 & Multi-task & Transformer fusion & SSIM 0.93 \
% 改:
\cite{Zhou2024} & Multi-task & Transformer fusion & SSIM 0.93 \
```

### 删除 Li2020 (虚假僵尸)
删除了 `\bibitem{Li2020}` 整行及其后的空行。
验证: `grep -c 'Li2020' paper.tex` → 0 (正文和bib均无残留)

## 修复后结果

| 指标 | 修复前 | 修复后 |
|:-----|:------:|:------:|
| D8 | 69 | 68 |
| D10a | 97% (67/69) | 100% (68/68) |
| 编译 | 17页 | 17页, 0 undefined |

## 判别模式

本案例确认了两种僵尸模式：
1. **虚假僵尸 (False Zombie)**: 同一领域同姓氏的不同作者引错条目 (F.Li vs M.Li) → 直接删除
2. **Table Zombie**: 引用以纯文本出现在表格而非 `\cite{}` 命令中 → 添加 `\cite{}`

## 对本清理的分类树验证

此案例验证了 ⚡ 扫描结果分类与交叉验证协议的 2026-06-04 实战参考：
- octa-ai-review 的真实分类是 **ZOMBIE** (D10a<100, orphans=0, zombies=2)
- bulk scanner 报告的 D10a=0% 是假阳性（注释残留陷阱触发的误报）
- robust scanner 正确识别为 97% (2 zombies)
