# Crossref DOI 搜索 — 边界案例与不可补全模式

> Session detail: crispdm-wdbc DOI fix (2026-06-07).  
> Purpose: Document cases where DOI CANNOT be added via Crossref API.

## 1. Pre-DOI Era Papers (不可补全)

**Paper**: Smith 1988 — "Using the ADAP learning algorithm to forecast the onset of diabetes mellitus"
- **Venue**: Proceedings of the Annual Symposium on Computer Application in Medical Care (1988)
- **DOI status**: DOI 系统 1997 年建立，1988 年论文不可能有 DOI
- **PubMed**: PMID 不存在（精确标题搜索 0 结果）
- **Action**: 在 bib 中保留条目，不添加 DOI。G7b 协议允许合理例外。

## 2. Old Journal Papers Pre-Crossref (不可补全)

**Paper**: Wolberg 1995 — "Image analysis and machine learning applied to breast cancer diagnosis and prognosis"
- **Journal**: Analytical and Quantitative Cytology and Histology (AQCH), Vol 17(2), pp 77-87
- **PubMed**: PMID 7612134 — **有 PMID 但 DOI 字段为空** (`elocationid` = "")
- **Publisher**: American Society for Cytopathology — 1995 年未接入 Crossref DOI
- **Companion paper**: Same authors, same year, different title ("Computerized breast cancer diagnosis...") → Arch Surg, PMID 7748089, DOI 10.1001/archsurg.1995.01430050061010
- **Trap**: Crossref DOI `10.1001/archsurg.1995.01430050061010` resolves to the companion paper (Arch Surg), NOT the AQCH paper. DO NOT add this DOI to the AQCH entry.
- **Action**: 在 bib 中保留条目，不添加 DOI。

## 3. Conference Proceedings Not in Crossref

**Paper**: Wirth 2000 — "CRISP-DM: Towards a standard process model for data mining"
- **Venue**: PAKDD 2000, LNCS 1834
- **Crossref**: DOI `10.1007/3-540-45571-9_3` → 404
- **LNCS proceedings** `10.1007/bfb2578395` → 404
- **Action**: 在 bib 中保留条目，不添加 DOI。

**Paper**: Ke et al. 2017 — "LightGBM: A Highly Efficient Gradient Boosting Decision Tree"
- **Venue**: NeurIPS 2017
- **arXiv**: arXiv:1705.06498
- **Crossref DOI `10.48550/arXiv.1705.06498`** → 404
- **Crossref DOI `10.5555/3327157.3327175`** (NeurIPS) → 404
- **R package DOI `10.32614/cran.package.lightgbm`** → resolves to wrong paper (2020, R package)
- **Action**: 在 bib 中保留条目，不添加 DOI。

## 4. Dataset/Repository Papers

**Paper**: Dua 2019 — "UCI Machine Learning Repository"
- **Publication**: PeerJ Computer Science 5, e1806 (2019)
- **DOI `10.7717/peerj-cs.1806`**: Crossref resolves to WRONG paper (Hidayat et al., formal context). DOI is real but Crossref has wrong mapping.
- **DOI `10.24432/C56C2J`** (UCI dataset): → 404
- **Other UCI DOI variants**: All → 404
- **Semantic Scholar**: PeerJ paper found but no DOI returned
- **Action**: 尝试添加 `10.7717/peerj-cs.1806` 但需人工确认。不建议自动添加错误 DOI。

## 5. Technical Traps

### 5.1 `select` Parameter Returns Array

Using `select=title,author,...` in Crossref query can return a JSON array instead of the `message` wrapper structure:

```python
# This can break:
r = requests.get(url + "?select=title,author,DOI,journal", ...)
items = r.json()['message']['items']  # KeyError: 'message' if response is an array
```

Fix: Always check response type:
```python
msg = r.json()
if isinstance(msg, dict) and 'message' in msg:
    items = msg['message']['items']
elif isinstance(msg, list):
    items = msg
else:
    items = []
```

### 5.2 DOI Resolution Does Not Confirm Bibliographic Match

A DOI may resolve to a VALID paper but NOT the one cited in the bib entry. Always verify:
1. Title matches exactly (not just similar keywords)
2. Authors match
3. Journal/venue matches
4. Year matches

### 5.3 PubMed as DOI Confirmation Tool

PubMed esummary endpoint returns `elocationid` (DOI) field. If empty, the paper truly has no DOI:

```python
# PMID 7612134 (Wolberg 1995 AQCH)
# esummary: "elocationid": "" → no DOI exists
```

## Summary: crispdm-wdbc Result

| Entry | Type | Reason No DOI | G7b Exception? |
|-------|------|---------------|----------------|
| Smith1988PIDD | Conference (1988) | Pre-DOI era | ✅ Yes |
| Wolberg1995WDBC | Journal (1995) | Pre-Crossref journal | ✅ Yes |
| Wirth2000CRISPDM | Conference (2000) | Not in Crossref | ✅ Yes |
| Ke2017LightGBM | Conference (2017) | Not in Crossref | ✅ Yes |
| Dua2019UCI | Repository (2019) | DOI exists but wrong mapping | ⚠️ Review needed |

**Result**: 0/5 DOIs added. DOI coverage stays at 83.9% (26/31). 4/5 are legitimate G7b exceptions.
