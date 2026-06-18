# Elsevier/BSPC 投稿准备清单

> 论文双质检通过后，提交到 Elsevier Editorial System 前所需的配套文件

## 必备文件

| # | 文件 | 格式 | 说明 |
|:--|:-----|:-----|:-----|
| 1 | Manuscript (PDF) | PDF | 编译后的最终版 |
| 2 | Cover Letter | PDF | 投稿信：简述贡献、声明原创性、无利益冲突 |
| 3 | Graphical Abstract | PDF/JPEG | 已嵌入 tex 或单独文件 |
| 4 | Highlights | 文本（3-5条） | 通常嵌入 tex 的 `\\begin{highlights}` |
| 5 | Figures | TIFF/JPEG/PDF | ≥300 dpi，彩色RGB |
| 6 | CRediT Author Statement | PDF | 每位作者的贡献角色（Conceptualization, Methodology, Software, Validation, Formal Analysis, Investigation, Data Curation, Writing, Visualization, Supervision, Project Administration, Funding Acquisition） |
| 7 | Declaration of Competing Interest | PDF | 声明无利益冲突 |
| 8 | Data Availability Statement | PDF | 数据集和代码的公开访问方式 |
| 9 | Funding Statement | PDF | 资助项目名称和编号 |

## Cover Letter 模板要点

```markdown
[Date]

Dear Editor,

We are pleased to submit our manuscript entitled "[Title]" for consideration 
for publication in [Journal Name].

[2-3 paragraph summary: problem, gap, method, key results, significance]

This manuscript is original, has not been published previously, and is not 
under consideration for publication elsewhere. All authors have approved the 
submission and have no conflicts of interest to declare.

Thank you for considering our manuscript.

Sincerely,

[Corresponding Author Name]
[Affiliation]
[Address]
[Email]
```

## CRediT 角色速查

| 角色 | 说明 |
|:-----|:------|
| Conceptualization | 研究构思和设计 |
| Methodology | 方法开发 |
| Software | 代码实现 |
| Validation | 验证/复现 |
| Formal Analysis | 统计分析 |
| Investigation | 实验执行 |
| Data Curation | 数据整理 |
| Writing - Original Draft | 初稿撰写 |
| Writing - Review & Editing | 修改润色 |
| Visualization | 可视化/制图 |
| Supervision | 指导监督 |
| Project Administration | 项目管理 |
| Funding Acquisition | 经费获取 |

## 常见注意事项

- Cover letter 不要超过一页
- CRediT 声明可放在 manuscript 末尾也可单独文件
- 部分 Elsevier 期刊支持在投稿系统中在线填写 CRediT
- Funding 信息若有多项，按重要性排列
- Data availability 常用的表述：\"The data that support the findings of this study are openly available in [repository name] at [DOI/URL].\"
- 若使用了第三方Kaggle版本数据集，需声明版本差异

## 实战案例（2026-05-26 BSPC投稿）

论文：3D Eyeball Model-Constrained Iris Segmentation
目标期刊：Biomedical Signal Processing and Control
Funding 来源（从实验室网站提取）：
- 浙江省自然科学基金 LTGY24H090011
- 温州市科技局 ZY2023018

### 投稿文件目录结构

```
paper-dir/
├── article20250830.pdf          ← 正文
├── article20250830.tex          ← 源码
├── reference4.bib               ← 参考文献
├── cover-letter.pdf             ← 投稿信
├── credit-author-statement.pdf  ← CRediT 作者贡献
├── declarations.pdf             ← 利益冲突 + 数据可用性 + 资助
├── submission-checklist.md      ← 投稿检查清单
├── quality-report.md            ← 质检报告
├── Figure_1.jpg / 2 / 3       ← 图文件
└── figures/graphical_abstract.pdf
```

### 资金来源调查方法

当需要在实验室网站提取资助信息时（实战已验证）：

```bash
# 1. 获取页面内容
curl -s "https://lab-website/about/" | python3 -c "
import sys, re
html = sys.stdin.read()
html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
text = re.sub(r'<[^>]+>', '\\n', html)
lines = [l.strip() for l in text.split('\\n') if l.strip() and len(l.strip()) > 5]
for l in lines:
    if any(kw in l for kw in ['课题', '项目', '基金', '资助', '自然', '科技', 'NSFC']):
        print(l)
"
# 2. 提取项目编号模式（如 Y2023xxx, LTGY24Hxxx, ZY2023xxx）
grep -oP '[A-Z]+[0-9]{6,}' output.txt | sort -u
```
