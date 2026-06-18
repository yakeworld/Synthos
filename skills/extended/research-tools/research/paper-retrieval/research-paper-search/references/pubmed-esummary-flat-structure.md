# PubMed esummary JSON 结构陷阱

## 现象

`esummary.fcgi?db=pubmed&id=X&retmode=json` 的响应中，论文条目**直接**位于 `result` 下，key 是 PMID 字符串。不在 `result.pubmed` 下。

## 错误写法

```python
# WRONG — result.get("pubmed") returns None
results = d.get("result", {}).get("pubmed", {})
```

## 正确写法

```python
# CORRECT — keys are PMID strings directly under "result"
result = d.get("result", {})
for pid in id_list:
    if pid in result:
        entry = result[pid]
        title = entry.get("title", "N/A")
```

## 示例响应结构

```json
{
  "header": {"type": "esummary", "version": "0.3"},
  "result": {
    "uids": ["42094543", "41403854"],
    "42094543": {
      "uid": "42094543",
      "title": "Visual activity in primate superior colliculus...",
      ...
    },
    "41403854": {
      "uid": "41403854",
      "title": "...",
      ...
    }
  }
}
```

## 验证

每次 PubMed esummary 后，检查 `d.get("result", {}).get("pubmed")` 是否为 None。如果是，说明结构是扁平的。

## 关联

- 与 `references/pubmed-idlist-key-casing.md` 同属 NCBI eUtils JSON 响应格式问题
- 与 `references/pubmed-or-false-positive-severity.md` 同属 PubMed 搜索陷阱
