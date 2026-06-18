# Holographic CJK Search — FTS5 Limitation & Fix

> 2026-05-27 修复记录
> 根因分析 → 修复方案 → 验证结果

## 问题

`fact_store(action='search', query='记忆')` 对中文查询（CJK）返回空结果，英文查询正常。

### 根因

SQLite FTS5 默认 `unicode61` tokenizer 把整段连续 CJK 文本（如 `"记忆功能测试标记"`）当作**单个 token**存储。因此：

- `MATCH '记忆'` → 查不到（因为 token 是 `"记忆功能测试标记"`，不是 `"记忆"`）
- `MATCH '测试'` → 查不到（同理）
- `MATCH 'Holographic'` → ✅ 命中（英文 token 化正常）

### 验证

```
FTS5 tokenize "记忆功能测试标记" with unicode61:
  token='记忆功能测试标记'  ← 整个字符串一个token！

FTS5 tokenize "memory test" with unicode61:
  token='memory' pos=0
  token='test'   pos=1   ← 正确按空格切分
```

**trigram tokenizer 也不行**：2字中文查询（`"记忆"`, `"测试"`）需 ≥3 字符才能匹配。

## 修复方案

改了一个文件：`plugins/memory/holographic/retrieval.py`

### 改动一：CJK 检测 (`_has_cjk`)

```python
_CJK_RE = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]')

@staticmethod
def _has_cjk(text: str) -> bool:
    return bool(FactRetriever._CJK_RE.search(text))
```

覆盖 CJK 统一表意文字主区 + 扩展A + 兼容表意文字。

### 改动二：CJK 查询走 LIKE 回退

在 `_fts_candidates()` 中分支：

```
查询 → _has_cjk(query)?
  ├─ True  → LIKE '%query%'  → fts_rank=0.5（中性值）
  └─ False → FTS5 MATCH（原有路径）
         └─ 空结果 → LIKE 兜底（补 ASCII 词嵌在中文中的情况）
```

LIKE 回退返回中性 rank（0.5），Jaccard 字级相似度在 `search()` 中做实际排序。

### 改动三：_tokenize 拆 CJK 单字

```python
@staticmethod
def _tokenize(text: str) -> set[str]:
    tokens = set()
    # ASCII: 原有空格切分
    for word in text.lower().split():
        cleaned = word.strip(".,;:!?\"'()[]{}#@<>")
        if cleaned:
            tokens.add(cleaned)
    # CJK: 每个中文字符独立成token
    cjk_chars = set(FactRetriever._CJK_RE.findall(text))
    tokens.update(cjk_chars)
    return tokens
```

这样 `_tokenize('记忆')` → `{'记', '忆'}`，与 `_tokenize('记忆功能测试标记')` → `{'记', '忆', '功', '能', '测', '试', '标', '记', ...}` 的 Jaccard 相似度为 2/8 = 0.25，而非 0。

### 改动四：FTS5 空结果 LIKE 兜底

ASCII 查询（如 `"FTS5"`, `"PIMA"`）嵌在中文内容中时被 `unicode61` 附着到 CJK 字符形成单一 token，MATCH 不命中。FTS5 空结果后自动退到 LIKE：

```python
if not rows:
    # LIKE 兜底：WHERE content LIKE '%FTS5%'
    like_sql = "SELECT f.* FROM facts f WHERE f.content LIKE ? ..."
    ...
```

## 验证结果

**19/19 全部命中**：

| 查询 | 类型 | 结果 |
|:-----|:-----|:-----|
| `三文证漏` | 纯中文 | ✅ 命中 |
| `眼动` | 2字中文 | ✅ 命中 |
| `管线` | 2字中文 | ✅ 命中 |
| `本地方舟` | 四字词 | ✅ 命中 |
| `进化铁律` | 固定短语 | ✅ 命中 |
| `信度评` | 三字片段 | ✅ 命中 |
| `天堑` | 单概念 | ✅ 命中 |
| `六色盲` | 三字尾 | ✅ 命中 |
| `论文管线` | 混合名 | ✅ 命中 |
| `Kappa角` | 混合CJK+ASCII | ✅ 命中 |
| `FTS5` | ASCII嵌中文 | ✅ 命中（LIKE兜底） |
| `PIMA` | 英文缩写 | ✅ 命中（LIKE兜底） |
| `2200` | 数字 | ✅ 命中（LIKE兜底） |
| `holographic` | 纯英文 | ✅ 命中（FTS5） |
| `PDF` | 纯英文 | ✅ 命中（FTS5） |
| `G1-G7` | 特殊格式 | ✅ 命中（LIKE兜底） |
| `Synthos` | 专有名词 | ✅ 命中（LIKE兜底） |
| `BibTeX` | 工具名 | ✅ 命中（LIKE兜底） |
| `fact_store` | 工具名 | ✅ 命中（FTS5） |

## 架构图

```
search(query)
  ↓
_fts_candidates(query, ...)
  ├─ _has_cjk(query)?
  │    ├─ True  → LIKE '%query%' → neutral rank 0.5
  │    └─ False → FTS5 MATCH → 命中? → FTS5 rank
  │                          → 空?   → LIKE兜底 → neutral rank 0.5
  ↓
_tokenize(query) → CJK单字 + ASCII词
  ↓
_jaccard_similarity(query_tokens, content_tokens) → 精确排序
  ↓
trust_weight × (fts_weight×fts_rank + jaccard_weight×jaccard + hrr_weight×hrr_sim)
  ↓
sorted results
```

## 注意事项

1. **LIKE 查询是 O(n) 扫描** — 事实数 < 1000 时足够快。大规模时考虑给 `content` 字段加索引或改用更高级的 CJK tokenizer。
2. **neutal rank 0.5** — LIKE 回退的 `fts_rank` 设中性值，实际排序由 Jaccard 和 HRR 负责。
3. **FTS5 仍保留** — 纯英文查询走 FTS5（更精确的 BM25 排序），中文查询走 LIKE。
4. **记忆不丢** — 已有事实无需 rebuild，LIKE 直接在 content 上 substring 匹配。
5. **trigram tokenizer 在部分 SQLite 构建中不可用** — 即使可用，2字中文查询也不命中。
6. **不破坏 probe/reason/related** — 这些方法在 numpy 可用时走 HRR 向量检索，不受 FTS5 影响。
