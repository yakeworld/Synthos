# Bibitem 交叉验证快速参考

> 2026-05-30 实战经验：SCC论文审计发现 Smith2021 为虚构引用、Damiano1996 信息全错。

## 三步验证流程

```
对每个 bibitem  →  至少2个独立来源交叉验证  →  标记异常（不存在/全错/偏差/冗余）
```

## 快速命令集

### 方法A：Semantic Scholar（有API key时首选）
```bash
# 搜索
curl -s -H "x-api-key: $SEMANTIC_SCHOLAR_API_KEY" \
  'https://api.semanticscholar.org/graph/v1/paper/search?query=author+year+keyword&limit=3&fields=title,externalIds,venue,year' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); [print(f'{p.get(\"title\",\"\")} | DOI:{p.get(\"externalIds\",{}).get(\"DOI\",\"\")} | {p.get(\"venue\",\"\")} Y:{p.get(\"year\",\"\")}') for p in d.get('data',[])]"

# 已知DOI直查
curl -s -H "x-api-key: $SEMANTIC_SCHOLAR_API_KEY" \
  "https://api.semanticscholar.org/graph/v1/paper/DOI:10.xxxx/xxxxx?fields=title,externalIds,venue,year"
```

### 方法B：Crossref API（无key可用）
```bash
# 搜索
curl -s "https://api.crossref.org/works?query=author+year+keyword&rows=3" | python3 -c "
import sys,json; d=json.load(sys.stdin)
for i in d.get('message',{}).get('items',[]):
    print(f'{i.get(\"title\",[\"\"])[0][:80]} | D:{i.get(\"DOI\",\"\")} | {i.get(\"container-title\",[\"\"])[0] if i.get(\"container-title\") else \"\"}')"

# 已知DOI直查
curl -s "https://api.crossref.org/works/10.xxxx/xxxxx"
```

### 方法C：PubMed E-utilities（医学论文）
```bash
# 搜索
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=author+keyword&retmax=5&retmode=json"
# 取详情（用pmid）
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=PM_ID&retmode=json"
```

## 验证维度速查

| 维度 | bibitem值 | 数据库值 | 判定 |
|:-----|:----------|:---------|:----|
| 第一作者 | Smith | Wimmer | ❌ |
| 标题 | "Human bony labyrinth extraction..." | "Human bony labyrinth dataset..." | ❌ |
| 期刊 | PLoS One | Data in Brief | ❌ |
| 年份 | 2021 | 2019 | ❌ |
| 卷/页 | 16, e0248560 | 27, 104782 | ❌ |

## 异常分类速查

| 类型 | 信号 | 处理 | 示例 |
|:-----|:-----|:-----|:-----|
| 🔴 不存在 | 所有数据库都查不到 | 删除或核实 | Smith2021 |
| 🔴 全错 | 作者/标题/期刊/卷页全不同 | 替换为正确论文 | Damiano1996（实际在J Fluid Mech） |
| 🟡 偏差 | 标题接近但不同，或卷页偏差 | 确认同一论文的不同版本 | Boselli2014 |
| 🟢 冗余 | 教科书代原始研究 | 移除教科书 | Epp2010 |
