---
name: meddata-download
description: "MedData全文下载核心规律。两步法：①full_look(abstractId=随机11位号, pmid=真实PMID, doi=DOI) ②等待10s→viewtext(fileName=abstractId)取回PDF"
version: 2.0.0
tags: [meddata, pdf-download, sso, paper-download]
signature: "meddata-download -> processed_result"
---

# MedData 全文下载

> 2026-06-23 最终确认。替代 `pdf-download-racing` 中所有旧版 MedData 描述。

## 核心规律（不可违反）

```
① full_look(abstractId=随机11位号, pmid=真实PMID, doi=真实DOI)
   → 系统把全文复制到 abstractId 名下（必须先申请，不可省略）
② 等待 10 秒（系统准备全文）
③ viewtext(fileName=abstractId)
   → 取回全文PDF
```

## 参数铁律

| 参数 | 值 | 要求 |
|:-----|:----|:------|
| `abstractId` | **11位随机整数** `random.randint(10000000000, 99999999999)` | **必须唯一**，每次新生成。不可用固定值`1`、不可用DOI_NO_SLASH |
| `pmid` | 论文的**真实PMID** | 告诉系统要哪篇论文。**不可用固定值`'1'`** |
| `doi` | 论文的**真实DOI** | 辅助定位 |

## 前置快速尝试

核心流程之前，可快速试两种直接 viewtext（不保证成功）：

1. **PMID 直接作为 fileName** — MedData 有PMID映射时可用（如 MIMIC 论文 `27219127` → 320KB ✅）
2. **DOI_NO_SLASH 直接作为 fileName** — 部分出版社可用（Frontiers, BMJ）

## 完整下载链路

```
download_one.py <DOI>
  ├→ _resolve_metadata(): SS查PMID
  ├→ arXiv直连（仅arXiv ID）
  └→ 三层竞速:
       Tier 1: SciHub (curl_cffi直连 → 失败则Tor SOCKS5重试)
       Tier 2: LibGen (curl_cffi直连)
       Tier 3: MedData (try_meddata)
            ├ Step 0: PMID直接viewtext
            ├ Step 1: DOI_NO_SLASH直接viewtext
            └ Step 2: full_look(随机11位abstractId, 真实PMID, DOI) → wait → viewtext ✅
```

## 占位 PDF 指纹

- MD5: `fd469bd7cd29446f2800f099e3b71457`
- 大小: 606841 bytes
- 内容: 1975年甲醇中毒论文（与请求论文完全无关）
- **占位不是IP封锁，是ID格式错误或论文不在库中**

## 认证流程

```python
# SSO 登录（type: "0" = 密码登录）
POST https://uuct.medbooks.com.cn:9443/sso/login
     {"username": "...", "password": "...", "type": "0"}
     → {"code":"200","data":{"url":"...bucToken=eyJ..."}}

# Token 交换
GET http://www.meddata.com.cn/api/sso/user/login?bucToken=...
    → {"responseData":"hash:timestamp","responseCode":200}
```

## 诊断流程

```
viewtext返回606KB占位PDF
  ├─ 检查SSO响应是否有 modifyPass: 1
  │   └─ 是 → 可改密码，但不阻断核心流程
  ├─ 有PMID ?
  │   ├─ ✅ → full_look(随机abstractId, 真实PMID, DOI) → wait → viewtext
  │   └─ ❌ → 先SS查PMID → 再走上面
  └─ 都失败 → 论文不在MedData库，走OA直连或SciHub
```

## 已知限制

- **频率限制**：连续多请求后返回空响应，需间隔数秒
- **modifyPass=1**：SSO返回此标记，不影响核心full_look流程
- **论文必须在MedData全文库中**才会有PDF
- Token单次有效，full_look + viewtext需同一token

## Tor 使用策略

| 通道 | 用Tor? | 理由 |
|:-----|:-------|:-----|
| SciHub 直连失败后 | ✅ 走Tor重试 | Tor可绕过IP封锁访问被禁域 |
| LibGen | 🟡 可试 | 当前全部不通 |
| Crossref API | 🟡 可试 | 被出口IP封锁 |
| **MedData** | ❌ **不要走** | 国内机构平台，Tor增加被封风险 |
| Semantic Scholar | ❌ 不需要 | 无封锁问题 |
| OA直连(Frontiers/PLOS) | ❌ 不需要 | 正规出版社，Tor触发CAPTCHA |
| arXiv直连 | ❌ 不需要 | 开放获取 |

## ⚡ 可靠度警告

**MedData返回PDF后必须验证内容。** 2026-06-23连续两次发现MedData为Norgeot MI-CLAIM论文 (DOI:10.1038/s41591-020-1041-y) 返回的是Eric Topol评论 (DOI:10.1038/s41591-020-1042-x)。Nature/Springer系列DOI相邻文章容易串流。

**Post-download验证流程:**
```bash
# Step 1: 检查标题
pdfinfo <downloaded.pdf> | grep "Title:"
# 如果标题不匹配bib中的预期标题 → PDF是错的

# Step 2: 检查作者
pdfinfo <downloaded.pdf> | grep "Author:"

# Step 3: 检查关键词
strings <downloaded.pdf> | grep -i "论文核心术语1|核心术语2"
```

**铁律**: 不信任任何下载源的输出。Sci-Hub、MedData、SS OA链接都可能串流到相邻文章。每次下载后必须 `pdfinfo` 验证标题匹配bib。发现不匹配必须重新请求。

## 代码入口

```bash
cd /media/yakeworld/sda2/Synthos/tools/paper-manager
source ~/.secrets
python3 download_one.py <DOI> <output.pdf>
```

## 历史错误索引

| 旧认知（已废弃） | 正确认知 |
|:-----------------|:---------|
| 占位PDF = IP被封锁 | 占位PDF = ID格式不对或论文不在库 |
| abstractId必须用DOI_NO_SLASH | abstractId可以是**任意唯一随机号**（11位整数） |
| pmid可以固定传`'1'` | pmid必须传**真实PMID** |
| full_look可省略 | full_look是**必须步骤** |
| 先写测试脚本来探测API | 先加载技能，再调`download_one.py` |

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。