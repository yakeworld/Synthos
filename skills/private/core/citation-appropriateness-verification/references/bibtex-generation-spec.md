# BibTeX 生成规范

> 从 Crossref/PubMed 搜索结果生成正确的 BibTeX 条目。2026-07-01 经验总结。
> 与 paper-knowledge-extraction 共享此文件。

## 关键更新：Crossref 不再支持 `format=bibtex`

**2026-07-01 确认**：Crossref API 的 `format=bibtex` 参数已被弃用/移除。必须使用 JSON 响应手动构建 BibTeX。

**旧方式（已失效）**：
```bash
curl -s "https://api.crossref.org/works/<DOI>?format=bibtex"
```

**新方式**：
```bash
curl -s "https://api.crossref.org/works/<DOI>?select=title,author,published-print,DOI,container-title"
```
然后用 Python 从 JSON 构造 BibTeX。

## BibTeX 生成陷阱

| 陷阱 | 错误表现 | 修复 |
|------|---------|------|
| 键名包含 `{` | `@article{spalton2014computational{` | 用 `re.sub(r'[^a-zA-Z0-9_-]', '', key)` |
| 标题截断 | `title = {Computational...` 只有一半 | 验证 `len(title) >= 20` |
| abstract 字段 | BibTeX 中出现 `abstract = {...}` | 标准 BibTeX 不含 abstract |
| journal=年份 | `journal = {2024}` | 正确填入 `year` 字段 |
| 自引用检测 | 条目标题≈论文标题 | 字符串相似度 > 0.9 时标记 |

## 查询长度限制

- **Crossref：查询 ≤ 100 字符**，超过返回 HTTP 400
- 必须截断：`query[:100]`
- 优先使用短关键词而非完整标题
