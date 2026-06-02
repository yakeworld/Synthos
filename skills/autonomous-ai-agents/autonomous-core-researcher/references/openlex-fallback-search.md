# OpenAlex Fallback Literature Search Pattern

> 当 `research/research-paper-search` 和 `writing/notebooklm-cli` skill 都不可用时，用 `execute_code` + OpenAlex API 做文献搜索的实战模式。2026-05-25 在 kappa-angle-calibration 论文中首次使用并验证。

## 何时用

| 条件 | 决策 |
|:-----|:-----|
| 启动时报告 "Skills not found: research/research-paper-search" | ✅ 必须用 |
| 启动时报告 "Skills not found: writing/notebooklm-cli" | ✅ 必须用（且按 cron-paper-creation-pattern 写论文） |
| notebooklm-cli 存在但 auth 失败 | ❌ 用 paper-pipeline 的 notebooklm-access-troubleshooting.md |
| 所有工具正常 | ❌ 用 notebooklm-cli / research-paper-search 的标准流程 |

## 核心 API 调用

```python
import urllib.request
import json
import urllib.parse

url = f"https://api.openalex.org/works?filter=title_and_abstract.search:{urllib.parse.quote(QUERY)}&sort=cited_by_count:desc&per_page=10&select=id,title,authorships,doi,publication_year,primary_location,cited_by_count,abstract_inverted_index"
req = urllib.request.Request(url)
req.add_header('User-Agent', 'mailto:research@example.com')
with urllib.request.urlopen(req, timeout=15) as resp:
    data = json.loads(resp.read())
```

**特点**: 无速率限制（相比 Semantic Scholar 的 429 错误），返回格式规范，支持 `title_and_abstract.search` 全文匹配。

## 搜索策略

### 关键词分层

```python
# 宽搜索 → 找综述和高引论文
queries_broad = [
    "kappa angle calibration",
    "visual axis eye tracking calibration",
]

# 窄搜索 → 找方法族和具体方向
queries_narrow = [
    "kappa angle VOR vestibulo-ocular",
    "binocular gaze constraint calibration",
    "implicit calibration corneal imaging eye tracking",
]
```

**原则**: 宽搜索返回通用结果，窄搜索聚焦特定方法方向。先宽后窄，交叉去重。

### 文献整理

```python
def reconstruct_abstract(inverted_index):
    """OpenAlex 的 abstract_inverted_index 是倒排索引格式，需重组为可读文本"""
    if not inverted_index:
        return ""
    word_positions = []
    for word, positions in inverted_index.items():
        for pos in positions:
            word_positions.append((pos, word))
    word_positions.sort()
    return ' '.join([w for _, w in word_positions])
```

每次搜索后整理为结构化列表（年份、标题、作者、DOI、被引数、摘要前200字），用于论文引用的 bibitem 构建。

## 关键限制

1. **覆盖率**: OpenAlex 覆盖所有学术出版物但偏英文，不覆盖中文期刊。临床主题同时搜 PubMed。
2. **摘要长度**: 返回的 abstract_inverted_index 可能为 null（部分出版物无摘要）。此时用标题+期刊名推断相关性。
3. **DOI 缺失**: 部分论文无 DOI。在 bibitem 中提供期刊+卷号+页码作为替代标识。
4. **rate limit 上限**: OpenAlex 免费 API 是 10 次/秒，远高于 Semantic Scholar 的 1 次/秒。但连续大并发查询仍可能触发限流，建议间隔 1-2 秒。

## 实战产出模板

```markdown
## [Topic] Literature Map

| Year | First Author | Title | Journal | Cited | Key Finding |
|:----:|:------------:|:------|:-------:|:-----:|:-----------|
| 2023 | Liu | An Automatic Calibration Method... | Sensors | 4 | Binocular gaze constraint, 0.45° RMSE |
| 2019 | Liu | Iris Feature-Based 3-D Gaze... | IEEE TIM | 23 | Single-camera, 0.82° accuracy |
```

然后直接从该表生成 bibitem 列表嵌入 paper.tex 的 `thebibliography` 环境。
