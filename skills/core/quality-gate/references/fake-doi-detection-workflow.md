# Fake DOI Detection — 实战教训总结

> 2026-06-25 HCS-3WT论文检查：32篇引用中7篇(22%)为假DOI
> bib文件中有DOI字段，但doi.org解析返回404

## 问题的本质

**LLM生成论文时习惯性虚构引用**。这些引用的：
- 作者名和标题往往看起来合理（LLM模仿真实论文风格）
- DOI字段存在但指向不存在的页面
- 期刊名、卷号、页码可能来自其他真实论文的片段拼凑

传统检查只确认"bib文件有DOI字段"就判通过，这是假阴性的根源。

## 检测方法（已固化到凡引必验铁律）

### 方法A：批量curl验证（推荐，无API限制）
```bash
for doi in $(grep 'doi\s*=' references.bib | sed 's/.*{//;s/}.*//'); do
  code=$(curl -sI "https://doi.org/$doi" | head -1 | grep -oP '\d{3}')
  echo "$code $doi"
done | sort
```
结果解读：
- `302` → 真实引用（doi.org重定向到出版商页面）
- `200` → 真实引用（部分OA站点直接响应）
- `404` → **虚构引用**，需替换或删除
- 连接超时 → 检查网络，非引用问题

### 方法B：Semantic Scholar API（速率限制，需key）
```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/DOI:$doi?fields=title,year"
# 有title返回 → 真实
# 无数据 → 可疑
```

### 关键陷阱

| 陷阱 | 说明 | 修复 |
|:-----|:------|:-----|
| bib有DOI但404 | bib字段可能是LLM编造 | 必须向doi.org发HEAD请求，不可信任bib |
| DOI存在但内容不匹配 | DOI指向另一篇论文 | 需下载PDF验证首页主题关键词 |
| 无DOI的经典论文 | 2006前会议无DOI（如ICML/JMLR） | 标注"无DOI，OA可获取"通过 |
| 出版商403 | 反爬拦截，非引用问题 | 用Playwright浏览器验证 |

## HCS-3WT实战数据

| 指标 | 值 |
|:-----|:---:|
| 总引用数 | 32 |
| 假DOI数 | 7 (22%) |
| 纯虚构（查不到对应论文） | 5 |
| DOI错误（论文存在但DOI写错） | 2 |
| 替换为真实文献 | 7/7 (100%) |
| 处理时间 | ~2小时（含查找替代文献） |

## 替换决策树

```
假DOI
├── DOI错误 → 搜索正确DOI → 修正bib → ✅
└── 纯虚构
    ├── 该论点有其他真实引用支撑 → 删除 → ✅
    ├── 有同主题真实论文可替代 → 搜索替换 → ✅
    └── 找不到替代 → 从论文中删除相关句子 → ✅
```

## 相关技能

- `quality-gate` — 凡引必验铁律（v2.32.0+）
- `citation-integrity-fix` — 引用替换协议（v1.1.0+）
- `reference-pdf-collection-workflow.md` — PDF批量下载四层协议
