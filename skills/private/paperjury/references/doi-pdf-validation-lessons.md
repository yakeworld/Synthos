# DOI + PDF 验证经验教训（2026-06-18 更新）

## DOI 验证

| 源 | 状态 | 说明 |
|:---|:-----|:-----|
| CrossRef | ✅ 可靠 | 200 正常返回，可验证 DOI 是否存在 |
| Semantic Scholar | ❌ 404 | 常返回 404，不适合 DOI 验证 |
| OpenAlex | ✅ 可用 | 200 正常返回，可搜索论文 |
| PubMed | ✅ 可用 | 生物医学论文首选 |

## BibTeX 匹配陷阱

**关键教训**: BibTeX entry 的格式是 `@Article{key,` 不是 `@key{`。

```python
# WRONG — 永远匹配不到
bib.find(f"@{key}")  # 返回 -1

# CORRECT — 直接搜索 key
bib.find(key)  # 返回正确位置
```

## PDF 下载状态（2026-06-18 实测）

| 源 | HTTP 状态 | 可用性 |
|:---|:---------|:-------|
| medbooks.com.cn | 200 | ✅ 可达 |
| sci-hub.ee | 200 | ✅ 可达 |
| sci-hub.st | 403 | ❌ 被封锁 |
| sci-hub.ru | 超时 | ❌ 不可达 |
| sci-hub.se | DNS失败 | ❌ 不可达 |
| Semantic Scholar API | 404 | ❌ 不可用 |
| CrossRef API | 200 | ✅ 正常 |
| OpenAlex API | 200 | ✅ 正常 |

## PDF 下载优先级

1. arXiv 直链 → 最稳定
2. PMC efetch → 开放获取
3. CrossRef DOI → 有限支持
4. Semantic Scholar → 不稳定（404）
5. Unpaywall → 混合OA

## Sci-Hub 域状态

- ✅ `sci-hub.ee` — 当前可用
- ❌ `sci-hub.st` — 403
- ❌ `sci-hub.ru` — 超时
- ❌ `sci-hub.se` — DNS失败

> 注意：Sci-Hub 域状态可能随时变化，每次使用前应探测可用性。
