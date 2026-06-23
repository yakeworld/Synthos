# MedData 唯一ID构造 — PMID双格式规则

> 2026-06-23 | 从2026-06-19实测数据 + 用户校正提炼

## 两种ID格式

| 格式 | 规则 | 适用场景 | 验证 |
|:-----|:------|:---------|:-----|
| Format 1 | `DOI_NO_SLASH` = DOI去掉`/` | 简单前缀: Frontiers(10.3389), BMJ(10.1136) | Barany2020 → 663KB ✅ |
| Format 2 | `DOI_NO_SLASH + PMID` | 含连字符: Bentham(10.3892) 等 | Tang2017 → 737KB ✅ |

## 代码实现

`tools/paper-manager/src/sources/meddata.py` 中 `try_meddata()` 自动执行双格式降级：

```
try_meddata(doi):
  1. abstract_id = doi.replace("/", "")           # Format 1
  2. _try_viewtext(abstract_id)                    # 试Format 1
     → 如果返回✅ PDF且不是占位 → 返回成功
  3. full_look → 检查是否提供fileUrl            # Fallback
     → 下载fileUrl
  4. 如有PMID, pmid_id = abstract_id + pmid       # Format 2
     → _try_viewtext(pmid_id)                     # 试Format 2
     → 如果返回✅ PDF → 返回成功
  5. 都不行 → 返回None
```

## 关键陷阱

- PMID 单独作为 fileName **无效**（MedData API 不接受）
- DOI slug 的任意字符串也无效（返回 500 "查看全文次数超过限制"）
- 两次尝试都含占位PDF检测（MD5=`fd469bd7cd29446f2800f099e3b71457`），不把占位当成功
- 出口IP(64.23.234.118) 被封锁时会返回占位PDF，不是ID格式问题
