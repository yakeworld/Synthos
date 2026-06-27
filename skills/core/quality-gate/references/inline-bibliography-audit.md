# Inline Bibliography Audit Pattern

> 当 06-references/ 下无 .bib 文件时，paper-references-scanning 子技能会静默跳过（不报错）。
> 必须手动检测 inline bibliography 并改用不同审计方法。

## 检测

```bash
# 检测论文是否使用 inline bibliography
grep -l thebibliography 01-manuscript/paper.tex
# 或直接在 paper.tex 中搜索
grep thebibliography /path/to/paper.tex
# 或检查 06-references 是否有 .bib 文件
ls *.bib 06-references/
```

如果 `thebibliography` 存在于 paper.tex 且 06-references/ 无 .bib → inline bib 模式。

## 审计方法

### 提取引用键

```bash
# 从 paper.tex 提取所有 cite keys
grep -oP '\\cite\{[^}]+\}' paper.tex | sort -u
```

### 提取引用条目（从 thebibliography）

```bash
# 提取 thebibliography 块
sed -n '/thebibliography/,/end(thebibliography)/p' paper.tex
# 提取每个 \bibitem{key}
grep -oP '\\bibitem\{[^}]+\}' paper.tex | sort -u
```

### D10a 计算

```bash
# 总引用数（thebibliography 中的条目数）
total=$(grep -c '\\bibitem' paper.tex)

# 被引用的条目数
cited=$(grep -oP '\\cite\{[^}]+\}' paper.tex | sed 's/.*{//;s/}.*//' | tr ',' '\n' | sort -u | wc -l)

echo "D10a: $cited/$total = $((cited * 100 / total))%"
```

### 引用验证

对于 inline bib，引用验证需要：
1. 检查每条 thebibliography 条目的 DOI 是否可解析（DOI 可能在条目内）
2. 检查每条 thebibliography 条目是否在 paper.tex 中被引用
3. 检查每条引用的文献是否真实存在（SS API / doi.org）

### 典型陷阱

- stroke-prediction: 10 篇 inline 文献，全部无 PDF，D10a=100%（无孤儿/僵尸），但引用量仅 10 篇（T2 期刊建议 15-20+）
- 有些论文用 bibTeX 命令但在文件头，不在 thebibliography 环境中
- 部分管线在 06-references/ 下放 .bib 文件，但 paper.tex 用 thebibliography（不同步）

## stroke-prediction 实例

```bash
# 10 篇 inline 引用
# NINDS1995, Lindley2015, Boden-Albala2005, Chen2019, Mollakarimi2020
# Ho2020, Kavakiotis2017, Moody2020, class_imbalance_survey, he2009

# D10a 检查
total=10  # 10 bibitem 条目
cited=10  # 10 个 \cite 键全部在 bibitem 中
D10a = 10/10 = 100%

# 孤儿引用: 0
# 僵尸引用: 0

# 但引用总量偏少: T2 期刊建议 15-20+ 篇
```
