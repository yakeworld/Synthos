# 引文质量检查报告模板 / 范例

> 模板从 SCC论文 v4 (34篇) 实战提炼

## 报告结构

### 1. 总表

| # | BibKey | PDF | 类型 | 引用位置 | 引用依据 |
|---|--------|:---:|:-----|:---------|:---------|
| 1 | Key | ✅ | type | section | basis |

### 2. 逐篇分析

```
### {#}. {BibKey}
- **条目**: {BibTeX entry text}
- **全文**: ✅/❌
- **引用次数**: N 处
- **引用位置**:
  - [{Section}] L{line}: `{cite context snippet}`
- **知识点**: {what this ref supports}
- **引用依据**: {data source / computational model / morphology comparison / etc.}
```

### 3. 引用类型判定

```python
def classify_ref(text):
    tl = text.lower()
    if any(w in tl for w in ['gene','express','morphogen']):
        return 'developmental biology'
    if any(w in tl for w in ['spiral','cochlea','logarithmic']):
        return 'cochlear morphology'
    if any(w in tl for w in ['micro-ct','imaging','segmentation','centerline']):
        return 'imaging methodology'
    if any(w in tl for w in ['model','simulation','computational','fluid','mechan']):
        return 'computational modeling'
    if 'bppv' in tl or 'vertigo' in tl:
        return 'clinical BPPV'
    if any(w in tl for w in ['morphometr','morpholog','anatomy','dimension']):
        return 'morphology measurement'
    if any(w in tl for w in ['semicircular','canal','vestibular','ampulla']):
        return 'vestibular anatomy'
    if 'review' in tl or 'overview' in tl:
        return 'review'
    return 'other'
```

### 4. 引用依据分类

```python
def citation_basis(key, context_text):
    if not cited: return 'NOT CITED'
    if any(w in context for w in ['data','dataset','specimen','scan']):
        return 'Data source — provides experimental imaging data'
    if any(w in context for w in ['model','modeling','simulation','fluid']):
        return 'Computational model — provides modeling framework/reference'
    if any(w in context for w in ['develop','gene','signaling','morphogen']):
        return 'Developmental biology — supports morphogenesis argument'
    if any(w in context for w in ['spiral','cochlea','logarithmic']):
        return 'Morphological comparison — provides spiral geometry benchmark'
    if any(w in context for w in ['measure','parameter','dimension','radius']):
        return 'Quantitative reference — provides measurement values for comparison'
    return 'Supporting reference'
```

## 关键代码：提取引用上下文

```python
import re
lines = tex.split('\n')
for i, line in enumerate(lines):
    for m in re.finditer(r'\\cite[tp]?\{([^}]+)\}', line):
        keys = [k.strip() for k in m.group(1).split(',')]
        ctx = re.sub(r'\s+', ' ', line.strip())[:200]
        for k in keys:
            ref_usage[k]['cites'].append({'line': i+1, 'context': ctx})
```

## 产出文件位置

- `07-quality/ref-citation-quality-report.md` — 总报告
- `07-quality/data-code-quality-report.md` — 数据溯源报告
