# BibTeX 条目格式参考

> 吸收自 AutoResearchClaw `literature/verify.py` 的 BibTeX 格式

## 条目类型映射

| 论文来源 | BibTeX 类型 | 说明 |
|---------|------------|------|
| 期刊论文 | `@article` | 有 journal 字段 |
| 会议论文 | `@inproceedings` | 有 booktitle 字段 |
| arXiv 预印本 | `@misc` | 无正式发表信息 |
| 书籍 | `@book` | 仅当直接从知识获取提取 |

## 字段生成规则

```
@article{cite_key,
  title     = {完整论文标题},
  author    = {作者姓氏, 名字 and 作者2姓氏, 名字2},
  journal   = {期刊名},
  year      = {2024},
  volume    = {15},
  pages     = {1337595},
  doi       = {10.3389/fpsyt.2024.1337595}
}
```

### 引用键生成

```
规则: {第一作者姓氏}{年份}
示例: yoo2024, andreou2025, bozkurt2024

冲突解决: 如果同作者同年多篇，追加 a/b/c
示例: yoo2024a, yoo2024b
```

### 作者名格式

```
中文/英文: 从 paper.authors 数组提取
格式: {姓氏}, {名字首字母}.
示例: Yoo, J. H. and Kang, C. and Lim, J. S.

中文拼音保护: 用 {{}} 包围
示例: author = {{杨}晓凯 and {王}小明}
```

## 只包含已验证的引用

仅包含 `citation_verification.status == "verified"` 的论文。
对 SUSPICIOUS 的论文标记 `% UNVERIFIED: {details}` 注释。
不包含 HALLUCINATED 的论文。

## 输出文件

写入 `outputs/runs/<run_id>/latex/references.bib`
