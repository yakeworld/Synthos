# OpenAlex 完整使用指南（2026-06-05 更新）

## 核心陷阱

### 1. sort=cited_by_count 不等于"按引用数排序"

OpenAlex 数据库中约 80%+ 论文 cited_by_count=0。`sort=cited_by_count` 将零引用论文放在顶部，前20条通常全为零引用，排序实质无效。

**解决方案**：必须使用 `filter=cited_by_count:N-` 过滤掉零引用论文：

```bash
# ✅ 显示有引用的论文（按引用数降序）
curl "https://api.openalex.org/works?search=your+query&filter=cited_by_count:1-&sort=cited_by_count&per_page=5"
```

### 2. count 字段位置

`count` 在 `meta.count`，不在根级别：

```python
count = data.get("meta", {}).get("count", data.get("count", 0))
```

### 3. sort=relevancy 永远返回 0

```bash
# 永远返回 0
curl "https://api.openalex.org/works?search=your+query&sort=relevancy&per_page=5"
```

## 使用模式

### 查询格式

```bash
# ✅ 推荐 — 全部用 + 编码空格，用 search= 参数
curl "https://api.openalex.org/works?search=vestibulo+ocular+reflex+neural+network&sort=cited_by_count&per_page=5"

# ✅ 也有效 — title= 参数（比 search= 更窄，只匹配标题）
curl "https://api.openalex.org/works?title=saccade+velocity+profile+PINN&select=title,cited_by_count&per_page=5"

# ❌ 混合编码可能 400 — %20 不兼容，+ 和 %20 不要混用
# ❌ 避免用 quote() 将空格转为 %20（urllib.parse.quote 默认行为）
```

### 参数选择

- `search=` — 标题+摘要全文搜索，范围广
- `title=` — 仅标题搜索，更精确
- `select=` — 只返回需要的字段，减少响应大小（推荐始终使用）

**重要**：`search=` 和 `title=` 对 URL 编码行为相同 — 必须用 `+` 编码空格，不能用 `quote()` 产生的 `%20`。

### 过滤参数

```bash
# 按引用数过滤（获取有意义的论文）
filter=cited_by_count:1-      # 至少1次引用
filter=cited_by_count:5-      # 至少5次引用

# 按年份过滤（注意：与特定查询组合可能返回0）
filter=from_publication_date:2020

# 组合使用
filter=cited_by_count:1-,from_publication_date:2022
```

### 解析结果

```python
import json
import subprocess

def search(query, per_page=5):
    url = f"https://api.openalex.org/works?search={query}&per_page={per_page}&sort=cited_by_count&filter=cited_by_count:1-"
    r = subprocess.run(["curl", "-s", url], capture_output=True, text=True)
    data = json.loads(r.stdout)
    
    total = data.get("meta", {}).get("count", 0)
    results = data.get("results", [])
    
    for d in results:
        title = d.get("title", "")
        cited = d.get("cited_by_count", 0)
        year = d.get("publication_year")
        doi = d.get("doi", "")
        keywords = [k["display_name"] for k in d.get("keywords", [])]
        print(f"[{year}] cited={cited}: {title}")
        print(f"  keywords={keywords[:5]}")
```

## 数据库特性

- 2.5 亿+ 论文
- 80%+ 论文 cited_by_count=0
- 大多数新论文（2024-2026）引用尚未积累
- 中文论文、医学临床论文引用通常较低
- 免费使用，无 API key，无速率限制（但建议搜索间隔≥1s）

## 白空间验证协议

1. 宽泛计数：`search=query&sort=cited_by_count` → 获取 `meta.count`
2. 引用过滤：`search=query&filter=cited_by_count:1-` → 检查有意义论文
3. 相关性：对引用过滤后的前5条检查标题相关性
4. 交叉验证：用3-4种措辞变体搜索
5. 判定：
   - 宽泛计数>100 但引用过滤后=0 → 白空间
   - 引用过滤后>0 但标题不相关 → 间接竞争
   - 引用过滤后>0 且标题相关 → 直接竞争