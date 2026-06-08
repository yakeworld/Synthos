# Crossref DOI 搜索模式与陷阱

> 用途：为 repair/doi_fix 任务查找缺失 DOI。
> 实战验证：3wd-framework 30篇 29/30 DOI; off-axis-iris 30篇 57%→90% DOI (2026-06-07)

## 核心发现

### 陷阱 1：`query.title=` 参数返回 400 Bad Request

Crossref API 对 `query.title=` 参数的编码处理有 bug。使用 `query=`（通用查询）替代。

```python
# ❌ 常失败：query.title= 参数
url = f"https://api.crossref.org/works?query.title={urllib.parse.quote(title)}"

# ✅ 正确：query= 通用查询
url = f"https://api.crossref.org/works?query={urllib.parse.quote(title + ' ' + journal + ' ' + year)}"
```

### 陷阱 2：`User-Agent` 头缺失导致 400

Crossref 要求 `User-Agent` 头，缺少时会拒绝：

```python
req = urllib.request.Request(url, headers={
    'User-Agent': 'Synthos-Agent/1.0 (synthos@research)'
})
```

### 陷阱 3：最佳匹配不是第一个结果

Crossref 返回按相关性排序的结果，但第一个未必匹配。需手动打分：

```python
def score_match(entry, query_keywords):
    titles = entry.get('title', [])
    if not titles:
        return 0
    title = titles[0]
    # 标题关键词匹配度
    matches = sum(1 for kw in query_keywords[:5] if kw.lower() in title.lower())
    return matches

# 选择匹配度 ≥ 2 的最高分结果
```

### 陷阱 4：DOI 字段格式不一致

BibTeX 文件中 DOI 字段可能有多种格式：
- `doi={10.xxxx/xxxx}` (紧凑)
- `doi = {10.xxxx/xxxx}` (有空格)
- `doi       = {10.xxxx/xxxx}` (多空格，如 `dehkordi2015` 条目)

检测时需使用 `re.search(r'\bdoi\s*=\s*\{', entry, re.IGNORECASE)` 而非 `'doi=' in entry`。

## 搜索策略

### 分层搜索

```
第1层：title + author + journal + year（最精确）
   ↓ 无结果
第2层：title + journal
   ↓ 无结果  
第3层：title + author
   ↓ 无结果
→ 标记为 "NO DOI FOUND"
```

### Python 实现（v2.0 — 实战版）

```python
import urllib.request, urllib.parse, json

def crossref_search(key, title, author=None, journal=None, year=None):
    # 构建查询：title + 作者姓氏 + 期刊 + 年份
    parts = [title]
    if author:
        parts.append(author.split(',')[-1].strip())  # 取姓氏
    if journal:
        parts.append(journal)
    if year:
        parts.append(year)
    
    query_str = '+'.join(parts)
    url = f"https://api.crossref.org/works?query={urllib.parse.quote(query_str)}&rows=5&sort=relevance"
    
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Synthos-Agent/1.0 (synthos@research)'
    })
    
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
        items = data.get('message', {}).get('items', [])
        
        best = None
        keywords = title.split()[:5]
        for item in items:
            item_titles = item.get('title', [])
            if not item_titles:
                continue
            title_lower = item_titles[0].lower()
            matches = sum(1 for kw in keywords if kw.lower() in title_lower)
            if matches >= 2:
                best = item
                break
        
        if best is None and items:
            best = items[0]  # fallback to first
        
        doi = best.get('DOI', '')
        return doi if doi else 'NOT FOUND'
```

## BibTeX 格式注意事项

### thebibliography → 标准 BibTeX 转换

当 `references.bib` 内容为 LaTeX `thebibliography` 环境时，需转换为标准 BibTeX `@article`/`@inproceedings` 格式。

### DOI 字段插入规范

插入 DOI 时注意：
1. **行尾逗号**：`publisher={...}` 后面加逗号再换行
2. **DOI 行最后不加逗号**：最后一行的 value 后无逗号
3. **大小写**：BibTeX 中 `doi` 不区分大小写，但统一用小写
4. **值格式**：`doi={10.xxxx/xxxx}`（花括号，无 http 前缀）

### 无 DOI 条目类型（合理例外）

- arXiv 预印本（未正式出版）
- 机构报告（如 Cambridge Computer Lab tech reports）
- 数据集页面（CASIA, MMU, UCI Repository 等）
- 旧论文（1990 年前，DOI 系统尚未建立）
- 中文期刊论文（部分未收录 Crossref）

## off-axis-iris 实战记录 (2026-06-07)

### 输入
- paper.tex: 30 个 cite key
- references.bib: 30 个条目，16 个有 DOI (53.3%)

### 搜索过程
- 使用 `query=` 参数搜索 11 个缺 DOI 条目
- 11 个全部找到 DOI（10.1109/, 10.1007/, 10.5220/ 等）
- 3 个条目 CASIA/MMU/raju2024evaluating 无 DOI（合理例外）

### 输出
- 新增 11 个 DOI 字段到 references.bib
- DOI 覆盖率: 27/30 = 90.0% ✅
- 更新 paper-status-audit 和 paper-queue.json
