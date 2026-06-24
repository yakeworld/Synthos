# EuropePMC PDF 下载备用通道

## 场景

当出版商官网有 Cloudflare 防护，且 Sci-Hub/LibGen/MedData 不可用时，EuropePMC 是绕过防护的可靠通道。

## 前提条件

论文必须有 PubMedCentral (PMC) ID。通过 Semantic Scholar API 获取：

```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/DOI:10.1016/j.patter.2023.100804?fields=externalIds"
# → {"externalIds":{"PubMedCentral":"10499856",...}}
```

## 下载命令

```bash
curl -sL -o output.pdf \
  "https://europepmc.org/articles/PMC${PMC_ID}?pdf=render"
```

## 验证

```bash
file output.pdf       # → "PDF document, version 1.7, 38 page(s)"
strings output.pdf | grep -i "论文标题关键词"  # 确认内容匹配
```

## 实测案例

| 论文 | DOI | PMC ID | 结果 |
|:-----|:----|:------:|:-----|
| Kapoor2023Leakage | 10.1016/j.patter.2023.100804 | PMC10499856 | ✅ 2.9MB，38页，Patterns期刊，标题正确 |
