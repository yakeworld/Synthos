# MedData 内部ID格式（Format A）— 文档提炼

> 2026-06-23 从 `meddata-access-absorbed.md` 和 `meddata-api-details.md` 提炼

## 三种ID格式对比

| 格式 | 规则 | 例 | 可靠度 | 获取方式 |
|:-----|:------|:---|:-------|:---------|
| **Format A** — 内部ID | `{自增ID}Rpub{后缀}` | `2985248Rpub37800834` | ⭐⭐⭐ 最可靠 | medbooks.com.cn 搜索界面 |
| Format 1 — DOI_NO_SLASH | `doi.replace('/', '')` | `10.3389fneur.2020.00602` | ⭐⭐ 部分兼容 | 从DOI直接派生 |
| Format 2 — DOI+PMID | `DOI_NO_SLASH + PMID` | `10.3892etm.2017.483728962176` | ⭐⭐ 部分兼容 | 需查询PMID后拼接 |

## 内部ID 结构

`2985248Rpub37800834` 格式解析：
- `2985248` = MedData 数据库内部自增ID
- `Rpub` = 资源类型标记（Resource Publication）
- `37800834` = 论文标识后缀

## 为什么内部ID更可靠

1. **原生主键** — 直接对应 MedData 数据库记录，不存在 DOI 匹配模糊性
2. **不受 publisher 影响** — Springer/Elsevier/Wiley 等付费出版社的 DOI 在 Format 1/2 下可能返回占位，但内部ID如果存在就直接映射到论文记录
3. **唯一确定** — 同一个内部ID号始终指向同一篇论文

## 如何获取

当前无公开 CLI API。需通过以下方式之一：
1. **浏览器搜索** — 登录 medbooks.com.cn，搜索论文关键词，从搜索结果中提取内部ID
2. **浏览器开发者工具** — 在 MedData 页面查看网络请求，找包含内部ID的API响应
3. **full_look API** — 当前返回 `fileName`（Format 1），不直接返回内部ID

## 代码现状

`tools/paper-manager/src/sources/meddata.py` 中的 `try_meddata()` 只实现了：
- `_make_abstract_id(doi)` → `doi.replace('/', '')` (Format 1)
- full_look + PMID拼接 (Format 2)
- **未实现 Format A**

## 未来改进方向

如需实现 Format A 支持：
1. 增加 medbooks.com.cn 搜索API集成（需逆向搜索接口）
2. 或允许用户手动传入内部ID作为 download_one.py 的ID类型
3. 或建立 DOI → 内部ID 的缓存映射表（从已成功的下载记录中积累）
