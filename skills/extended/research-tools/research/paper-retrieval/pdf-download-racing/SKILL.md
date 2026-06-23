---


name: pdf-download-racing
description: 并行竞速PDF下载引擎 — curl_cffi TLS指纹绕过 + Sci-Hub域轮换 + LibGen + MedData。依赖 tools/paper-manager/src/。
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    version: 1.7.0
    author: Synthos
    signature: 'any_id: str -> pdf_path: str | bool'
    related_skills:
    - paper-pipeline
    absorbed_skills:
    - meddata-access



---



## IO_CONTRACT

- **input**: `paper_queries: list[str], sources: list[str]` — 任务描述、参数配置
- **output**: `download_report: dict (files_downloaded, failed, timing)` — 执行结果

> 对应原则：P2（机械原子暴露输入输出规范）

## Golden Rule（2026-06-23 追加 — v3）

铁律：DOI验证先于下载。

1. 先加载本技能，再碰任何代码。
2. 不自写测试 — 直接调 download_one.py。
3. 先验DOI再下载 — 调 download_one.py 前先用 citation-verification 技能验证DOI。
   假DOI (doi.org 404 + Crossref Resource not found + SS无记录) 跑竞速是白费时间。
4. SS API key必须带 — _resolve_metadata() 中SS调用需读取 $SEMANTIC_SCHOLAR_API_KEY
   并设置 x-api-key header，否则429限速导致元数据静默失败。
5. MedData下载先加载 meddata-download 技能。

验证流水线：bib文件 → Phase 1 (citation-verification) 验DOI标假修复 → Phase 2 (本技能) 只对可信DOI下载

详见 `references/doi-validation-before-download-2026-06-23.md` — 10篇假/错DOI的完整案例库（Kapoor/Norgeot/Haixiang等真实修复记录）。

## 统一入口（2026-06-21 更新 — v4架构）

**不要写自己的测试脚本。先查技能，再调 `download_one.py`。** 这是用户明确纠正的工作方式。

```bash
cd /media/yakeworld/sda2/Synthos/tools/paper-manager
source ~/.secrets
pip3 install curl_cffi bs4 lxml  # 缺依赖时装一次

# 任意ID类型
python3 download_one.py 10.3389/fneur.2020.00602 /tmp/paper.pdf    # DOI
python3 download_one.py 2403.12345 /tmp/paper.pdf                   # arXiv
python3 download_one.py CorpusID:12345678 /tmp/paper.pdf             # Semantic Scholar
python3 download_one.py PMID:28962176 /tmp/paper.pdf                 # PubMed
```

### v4 内部竞速架构（2026-06-21 实测确认）

```
download_one.py <任意ID>
 │
 ├→ _resolve_metadata()
 │    ├→ Semantic Scholar查：externalIds → PMID, arXiv ID
 │    │                    openAccessPdf → OA全文直链 🆕
 │    └→ Crossref/NCBI降级补全
 │
 ├─ Step 1: arXiv 直连 (仅arXiv ID, 最快)
 │
 ├─ Step 2: Semantic Scholar openAccessPdf 直链 🆕
 │    （OA论文最快路径，不用SciHub/MedData）
 │
 └─ Step 3: 三层竞速 (SciHub → LibGen → MedData)
      ├─ SciHub: 直连
      ├─ LibGen: 直连
      └─ MedData: 最后降级通道（受频率保护）
           ├─ PMID直试
           ├─ DOI_NO_SLASH → full_look(随机11位号, 真实PMID, DOI) → wait→viewtext
           └─ 滥用防护: 15s间隔, 200次/天上限, 不自动重试失败full_look
```

### 下载失败后重试策略

对批量下载中失败的DOI，可单独跑SS OA重试脚本：

```bash
python3 retry_failed_ss_oa.py  # 只查SS openAccessPdf，不跑全链路竞速
```

适用于SciHub/LibGen/MedData都拿不到的付费论文。SS OA链接有时效性（403/502），非100%可靠。

### 批量失败DOI重要性分级

参见 `references/batch-download-triage-2026-06-21.md` — 标准：核心引用必追，重要引用尽量追，低影响期刊/数据集/评论文章可弃。

### 批量下载速度 → 多线程

当前 `batch_download_pima.py` 为单线程。用户要求改为多线程以提高速度 — 当下载目标数 > 10 时优先考虑。

MedData 参数:
- **核心定位**: 外文医学论文平台（非中文期刊）
- **SSO 账号**: wzsrmyy (温州市人民医院), 密码在 ~/.secrets
- **ID 构造（自动降级）**:
  - Format 1: `DOI_NO_SLASH` → Frontiers/BMJ 等简单DOI前缀 ✅
  - Format 2: `DOI_NO_SLASH + PMID` → Bentham 等含连字符DOI
- **占位指纹**: MD5=`fd469bd7cd29446f2800f099e3b71457` (606841 bytes)

## 新增：OA期刊直连下载（2026-06-18 新增）

**某些 OA 期刊可通过官网直接下载 PDF，不需要通过 MedData/Sci-Hub：**

### Frontiers 系列

```bash
# 格式：https://www.frontiersin.org/journals/{journal}/articles/{DOI}/pdf
# DOI 格式：10.3389/fneur.2020.00602
curl -s -L "https://www.frontiersin.org/journals/neurology/articles/10.3389/fneur.2020.00602/pdf" \
    -o output.pdf
```

**验证方式**：下载后检查 MD5 ≠ `fd469bd7cd29446f2800f099e3b71457`，文件包含作者/引用/图表。

**已知成功实例**：
- `10.3389/fneur.2020.00602` — Frontiers in Neurology — 663KB 真实PDF
- 所有 `10.3389/` 开头的 DOI 都属于 Frontiers，均应该能直接下载

### PLOS ONE

```bash
# 格式：https://journals.plos.org/plosone/article/file?id={DOI}&type=pdf
curl -s -L "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0123456&type=pdf" \
    -o output.pdf
```

### PubMed Central (PMC)

```bash
# 先查 PMID 是否有 PMC 全文
# https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&id=PMID&db=pmc

# 有PMC全文时直接下载
curl -s -L "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{PMC_ID}/pdf/" \
    -o output.pdf
```

**注意**：并非所有 PubMed 论文都有 PMC 全文。需先查询 elink 确认。
```

**⚠️ 2026-06-23 更新 — Sci-Hub 域连通性波动，非全面失效**
- 2026-06-19 曾记录所有域返回403/0/ERROR，但2026-06-23实测 `sci-hub.al` 对 Nature 论文返回 ✅ 320KB PDF
- Sci-Hub 域连通性存在波动，某些域可能在特定时间段可用/不可用
- 旧断言"全面失效"已过时 — 让竞速逻辑自然工作，设置足够长超时(120s+)即可
- 不要一失败就直接放弃 —— 竞速会按 SciHub → LibGen → MedData 顺序自动降级
- **不要手动禁用 SciHub tier** — 竞速设计自动处理域波动，写代码跳过它等于放弃已经恢复的通道

**降级策略**: 当Sci-Hub失效时，优先使用OA直连（Frontiers/PLOS/PMC），其次MedData（机构凭据+国内IP），其次手动从机构网络下载。

## 实测流程 (2026-06-23 校正)

**调用现有工具链 `download_one.py`，不自写测试脚本。** 这是用户明确纠正的工作方式：先检查技能，再调用已有代码，绕一圈写自己的测试脚本是弯路。

下载一篇论文:
```bash
cd /media/yakeworld/sda2/Synthos/tools/paper-manager
source ~/.secrets
pip3 install curl_cffi bs4 lxml  # 缺依赖时装
python3 download_one.py <DOI> <output.pdf>
```

`download_one.py` 内部自动三级竞速: SciHub → LibGen → MedData。
MedData 走 `try_meddata()` 自动处理 ID 构造（双格式降级）和完整认证链。

**下载后验证:**
```bash
md5sum <output.pdf> | awk '{print $1}'
# 占位PDF的MD5: fd469bd7cd29446f2800f099e3b71457 (606841B)
file <output.pdf>  # 应返回 "PDF document"

# ⚡ 内容正确性验证（2026-06-23 新增）
# Sci-Hub和MedData都可能串流到相邻文章（Nature/Springer系列尤其严重）
pdfinfo <output.pdf> | grep -E "Title:|Author:"
# 对比bib中的标题/作者——不匹配必须重新下载
strings <output.pdf> | head -100 | grep -i "论文核心关键词"
```

**MedData 定位**: 外文医学论文平台（非中文期刊）。
**SSO 账号**: wzsrmyy (温州市人民医院), 密码在 ~/.secrets。
**出口 IP 64.23.234.118 被学术平台封锁** — 如遇占位PDF先检查网络环境。

## Pitfalls

### ⚠️ 出口节点 64.23.234.118 — SciHub部分可用；MedData占位 = ID格式问题（非IP封锁）

Tailscale exit node (Digital Ocean NYC, 64.23.234.118):
- **SciHub**: 部分域可用（2026-06-23 `sci-hub.al` 返回 Nature 论文 ✅）
- **Semantic Scholar API** → 404
- **CrossRef API** → 404
- **MedData**: SSO通过，API正常工作——**占位PDF原因见下方「MedData 占位PDF根因诊断」**

不要将 MedData 返回占位归咎于IP封锁。2026-06-23用户明确纠正：**占位来自ID格式不匹配，与IP无关**。用正确的内部ID/PMID作为fileName可获取真实PDF。

### ⚠️ sci-hub.vg IS THE ONLY WORKING DOMAIN via Tor

Testing of 11 Sci-Hub domains via Tor SOCKS5H (2026-06-19):
- `sci-hub.vg` → Returns HTML with iframe → iframe contains PDF URL → PDF downloadable ✅
- `sci-hub.ru` → Returns "search proxy to download article" (DOI not in database) ❌
- `sci-hub.al` → Returns "search proxy to download article" ❌
- `sci-hub.box` → Returns "search proxy to download article" ❌
- `sci-hub.ren` → JS challenge ("Just a moment...") ❌
- `sci-hub.wf` → Returns empty HTML ❌
- `sci-hub.red` → Returns "search proxy to download article" ❌

**Never try multiple domains in parallel** — use `sci-hub.vg` exclusively via Tor.

### ⚠️ MedData 占位PDF根因诊断（2026-06-23用户校正）

**❌ 错误认知**: 占位PDF(MD5=fd469bd7...) = IP被封锁
**✅ 正确认知**: 占位PDF = 用了**错误的ID格式**（Format 1/2 对多数论文不兼容）

核心证据（2026-06-23实测）：
- 同一IP下：PMID=27219127 用PMID作为fileName → 320KB真实PDF ✅
- 同一论文用DOI_NO_SLASH → 606KB占位PDF ❌
- 结论：API正常工作，占位来自ID格式不匹配

**ID格式优先级（越上方越可靠）**：
| 优先级 | 格式 | 规则 | 例 | 说明 |
|:------:|:-----|:------|:---|:-----|
| ⭐1 | **Format A — 内部ID** | `{自增ID}Rpub{后缀}` | `2985248Rpub37800834` | MedData原生主键，最可靠 |
| ⭐2 | **PMID 直用** | 直接用PMID数字 | `27219127` | 部分论文有效 |
| ⭐3 | Format 1 — DOI_NO_SLASH | `doi.replace('/', '')` | `10.3389fneur.2020.00602` | 仅Frontiers/BMJ等 |
| ⭐4 | Format 2 — DOI+PMID | `DOI_NO_SLASH + PMID` | `10.3892etm.2017.483728962176` | 仅Bentham等 |

**诊断流程**：
```
viewtext返回606KB占位PDF
  └─ modifyPass: 1 ?
      ├─ ✅ → 先改密码（medbooks.com.cn 修改密码）
      ├─ 有PMID ?
      │   ├─ ✅ → 试「PMID」作为fileName
      │   └─ 可访问medbooks搜索?
      │       ├─ ✅ → 搜论文→取内部ID→调用viewtext
      │       └─ 都不行 → 论文不在库中，走OA直连
```

**不要**在诊断到占位PDF时说"IP被封锁"——这是2026-06-23用户明确纠正的错误认知。

### ⚠️ MedData 覆盖范围 — 已解决（用户校正 2026-06-23）

**MedData 的核心定位是外文医学论文平台**（不是中文期刊平台）。自动化脚本(2026-06-18)的测试结论是错误的：
- CLI 失败（返回占位 PDF）≠ MedData 没有外文论文
- 失败根源：fileName 构造方式不正确
- **已解决**：通过构造唯一的 abstract ID，CLI 路径已可正常下载外文论文全文

❌ 本技能中所有说"MedData 不覆盖 Western 期刊"的断言已作废。
✅ MedData 是下载外文论文的可靠主路径。

### ⚠️ full_look Response Is Nested

The `fileName` is under `responseData.fileName`, NOT directly at root level.
Code that reads `fl_data["fileName"]` will get `None` and fail silently.

### ⚠️ Token Expiration

Token from SSO → token exchange expires in seconds. All full_look + viewtext calls must be
consecutive in a single session. Multiple SSO logins in quick succession can cause "用户登录失效".

### ⚠️ 优先调用现有工具链，不自写测试脚本

MedData 下载的逻辑已封装在 `tools/paper-manager/src/sources/meddata.py` 中，`download_one.py` 是对外的统一入口。

**正确流程：**
```bash
cd /media/yakeworld/sda2/Synthos/tools/paper-manager
source ~/.secrets
python3 download_one.py <DOI> <output.pdf>
```

**不要**自己写 curl/Python 测试脚本来测试 MedData——现有代码已处理：
- SSO 认证链 (TLS 1.2)
- Token 交换与自动续期
- 唯一ID 构造（双格式自动降级）
- 占位PDF 检测
- 三级竞速（SciHub → LibGen → MedData）

先查技能，再调用已有工具。

## Sci-Hub域列表（2026-06-23 更新 — 连通性有波动）

```python
SCI_HUB_DOMAINS = [
    "https://sci-hub.ru",     # 🟡 波动 — 有时返回 "search proxy"
    "https://sci-hub.ee",     # ❌ 不可达/JS挑战
    "https://sci-hub.shop",   # 🟡 波动
    "https://sci-hub.ren",    # ❌ JS challenge ("Just a moment...")
    "https://sci-hub.red",    # 🟡 波动
    "https://sci-hub.al",     # ✅ 2026-06-23 实测返回 Nature论文 320KB 真实PDF
    "https://sci-hub.vg",     # ✅ 唯一稳定: HTML → iframe → PDF (via Tor)
    "https://sci-hub.wf",     # ❌ 返回空HTML
    "https://sci-hub.es",     # ❌ 不可达
    "https://sci-hub.box",    # ❌ 不可达
    "https://sci-hub.yt",     # ❌ 不可达
]
# 结论: SciHub 域连通性有波动。不要基于单次实验断言"全面失效"或"全部可用"。
# 让竞速逻辑自动处理。—— 11域全部尝试需足够超时 (120s+)。
```

## MedData (外文医学论文全文平台)

> ⚠️ **2026-06-23 废弃声明**: 以下 MedData 章节内容已部分过时。**最终权威版本在 `meddata-download` 技能**。核心规律：
> ```
> ① full_look(abstractId=随机11位号, pmid=真实PMID, doi=DOI)
> ② 等待 10 秒 → viewtext(fileName=abstractId) → PDF
> ```
> abstractId 必须唯一不固定，pmid 必须传真实PMID 不可用固定 `'1'`。占位PDF 来自ID格式不匹配，**不是IP封锁**。
> 详见 `meddata-download` 技能和 `references/meddata-download-core-rules.md`。

需设置环境变量：
```bash
export MEDDATA_USERNAME="MEDDATA_USERNAME_PLACEHOLDER"
export MEDDATA_PASSWORD="MEDDATA_PASSWORD_PLACEHOLDER"
```

### 完整认证链（2026-06-18 实测确认）

**⚠️ modifyPass 信号（2026-06-23 新增）**：
SSO 响应中的 `\"modifyPass\": 1` 表示密码被标记为需修改。这会影响部分论文下载，但不阻断全部。处理方式：
- 即使 modifyPass=1，用**内部ID（Format A）** 仍可下载
- 用 Format 1/2 时，modifyPass=1 可能加重返回占位的概率
- 长远修复：登录 medbooks.com.cn 修改密码后恢复
- 诊断时先检查 SSO 响应是否有 `modifyPass: 1`
```bash
curl -s --tls-max 1.2 -X POST "https://uuct.medbooks.com.cn:9443/sso/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"MEDDATA_USERNAME_PLACEHOLDER","password":"MEDDATA_PASSWORD_PLACEHOLDER","type":"0"}'
# 返回: {"code":"200","data":{"url":"http://lib.medbooks.com.cn/sso/login?bucToken=eyJ..."}}
```
⚠️ **TLS 1.2 是必需的** — curl 默认 TLS 1.3 被 uuct.medbooks.com.cn:9443 拒绝（空响应，json 解析失败）。

**Step 2: Token Exchange**（正确路径）
```bash
# ✅ 正确：api/sso/user/login（非 tokenExchange）
curl -s "http://www.meddata.com.cn/api/sso/user/login?bucToken=<bucToken>"
# 返回: {"responseData":"44d5c7537812ef43b85f5ebf068c386f:202606181506541879","responseCode":200}
```
⚠️ `tokenExchange` 路径返回 400 "用户登录失效"。仅 `api/sso/user/login` 有效。

**Step 3: full_look**（触发 PDF 生成）
```bash
curl -s "http://www.meddata.com.cn/api/abstract/full_look?token=<TOKEN>&abstractId=<DOI_NO_SLASH>&pmid=1&doi=<DOI>"
# 返回: {"status": 2, "fileName": "10.3389/fneur.2020.00602", "fileUrl": null}
```
- `status: 0` = 有全文可下载
- `status: 2` = 有索引，可通过 viewtext 尝试下载
- full_look 的 status=2 **不等于**无全文 — download_one.py 通过 viewtext 可获取外文论文PDF

**Step 4: viewtext**（下载 PDF）
```bash
curl -s -o output.pdf "http://app.meddata.com.cn:8878/api/abstract/viewtext?fileName=<DOI_NO_SLASH>&token=<TOKEN>" \
  -H "User-Agent: Mozilla/5.0" -H "Accept: application/pdf"
```

### ⚠️ MedData fileName 构造规则 (2026-06-23 校正)

**唯一ID = 两种格式，自动降级尝试：**

| 格式 | 规则 | 例 | 适用 |
|:-----|:-----|:---|:-----|
| Format 1 | `DOI_NO_SLASH` | `10.3389fneur.2020.00602` → 663KB ✅ | Frontiers, BMJ (简单DOI前缀) |
| Format 2 | `DOI_NO_SLASH + PMID` | `10.3892etm.2017.4840` + `28962176` → 737KB ✅ | Bentham (含连字符的复杂DOI) |

**`tools/paper-manager/src/sources/meddata.py` 中 `try_meddata()` 已实现双格式降级：**
1. 先试 Format 1（DOI_NO_SLASH）
2. 如返回占位PDF → full_look 获取信息
3. 如有PMID → 构造 Format 2（DOI_NO_SLASH + PMID）再试
4. 两次尝试都含占位PDF检测（MD5=`fd469bd7...`），不把占位当成功

**验证方法：**
```bash
md5sum <output.pdf>  # 占位指纹: fd469bd7cd29446f2800f099e3b71457 (606841B)
file <output.pdf>    # 应返回 "PDF document"
```

### ⚠️ MedData 内部ID格式（Format A）— 最可靠但需浏览器获取

参考 `references/meddata-access-absorbed.md` 中记录的 MedData 数据库内部编号格式：

| 格式 | 规则 | 例 | 获取方式 |
|:-----|:------|:---|:---------|
| **Format A** — 内部ID | `{自增ID}Rpub{后缀}` | `2985248Rpub37800834` | medbooks.com.cn 搜索界面 |
| Format 1 — DOI_NO_SLASH | `doi.replace('/', '')` | `10.3389fneur.2020.00602` | 从DOI直接派生 |
| Format 2 — DOI+PMID | `DOI_NO_SLASH + PMID` | `10.3892etm.2017.483728962176` | 需查询PMID |

**关键点**：
- Format A (内部ID) 是 MedData 数据库的原生主键，**同一个ID号比DOI衍生格式更可靠**
- 当前 `meddata.py` 只实现了 Format 1 和 Format 2，未支持 Format A
- 获取内部ID需通过 medbooks.com.cn 搜索界面（浏览器操作为主，无公开CLI API）
- 未来改进方向：增加 medbooks 搜索集成

### ⚠️ viewtext 域名争议 — www vs app（2026-06-23 实测澄清）

技能内多处声称 `www.meddata.com.cn` 返回占位、`app.meddata.com.cn:8878` 返回真实PDF。**2026-06-23 从出口节点 64.23.234.118 实测发现两个域名对同一论文返回相同结果**（占位PDF的MD5相同）。说明域名差异对结果无实质影响。

**根因真实排序（2026-06-23 用户校正）**：
1. **ID格式不匹配**（首要原因）— Viewtext的fileName参数使用了错误的ID格式，见上方「MedData 占位PDF根因诊断」
2. **论文是否被 MedData 收录**（次要原因）— 某些出版社论文不在库中
3. **域名差异**（无关因素）— 国内网络下两域等效，国外IP下两域也等效

**国内网络下**优先尝试 `app.meddata.com.cn:8878`。但不要将占位PDF归咎于域名选择。

### ⚠️ MedData SSO 需要 TLS 1.2 (2026-06-19 实测)

`curl` 默认使用 TLS 1.3 会被 `uuct.medbooks.com.cn:9443` 拒绝（返回空响应）。
**必须添加 `--tls-max 1.2` 参数**：

```bash
curl -s --tls-max 1.2 -X POST "https://uuct.medbooks.com.cn:9443/sso/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"MEDDATA_USERNAME_PLACEHOLDER","password":"MEDDATA_PASSWORD_PLACEHOLDER","type":"0"}'
# ✅ 成功返回 code=200
```

不使用 `--tls-max 1.2` 时：
- curl 超时或返回空响应
- `json.loads` 失败（`JSONDecodeError: Expecting value`）

### ⚠️ 书章/书籍需要ISBN搜索，非DOI（2026-06-23 新增）

`download_one.py` 的DOI搜索不适用于Springer/Elsevier书章（book chapter）。

**区别**:
| 类型 | 可发现方式 | 示例 |
|:-----|:-----------|:-----|
| 期刊论文 | DOI → SciHub/LibGen/MedData ✅ | `10.1007/s11227-024-06211-9` |
| 书章 | DOI → SciHub/LibGen/MedData ❌ | `10.1007/978-981-13-8798-2_12` |
| 书籍 | ISBN → LibGen ✅ | `978-981-13-8798-2` |

**诊断书章特征**:
- DOI以 `10.1007/978-`、`10.1007/` 开头的Springer书章通常无法通过DOI下载
- PDF XML显示「Book Chapter」「Advances in Intelligent Systems and Computing」等

**处理策略**:
1. 先识别是否为书章（DOI模式 + 非期刊期刊卷号）
2. 尝试LibGen搜索ISBN或书名（非DOI）
3. 如果均无法下载，intro paper保留在bib中（正确引用比PDF更重要），在报告标注「书章无免费PDF」

**2026-06-23实战**: Islam 2019 (Springer书章, DOI 10.1007/978-981-13-8798-2_12) 尝试过Tor+SciHub所有域、Tor+LibGen所有域、MedData — 全部无结果。最终判定为合理缺失。

### ⚠️ MedData 滥用防护策略（2026-06-21 新增）

MedData 是机构资源（温州人民医院），不可滥用。批量下载时强制执行：

| 防护 | 值 |
|:-----|:----|
| 连续调用间隔 | ≥ **15秒**（自动sleep等待） |
| 24小时上限 | ≤ **200次**（超限跳过，返回None） |
| 重试 | **绝不自动重试**失败的full_look |
| 定位 | **仅作为最后降级通道**（SciHub→LibGen→MedData） |

此策略编码在 `scihub_racing.py` 中，加载时会检查计数器文件。

### ⚠️ MedData 频率限制 + modifyPass 状态（2026-06-23 更新）

**频率限制**：频繁调用 `full_look` 会触发 `responseCode=500` + "查看全文次数超过限制，请稍后再试！"
- 单次会话内 3-5 篇正常
- 批量扫描多篇文章后触发（约 10 次请求）
- 需要等待数分钟到数十分钟冷却

**modifyPass 限制**：SSO 响应中 `\"modifyPass\": 1` 标记密码需修改。
- 不影响 SSO 登录和 token 获取（API调用正常）
- 不影响 Format A（内部ID）下载
- 对 Format 1/2 可能降低成功率

**诊断顺序（按实际频率）**：
1. SSO返回空响应 → TLS 1.2 问题或临时网络异常
2. token exchange 返回空 → 频率限制
3. full_look 返回 500 → 频率限制，等待冷却
4. full_look 正常但 viewtext 返回占位PDF → **ID格式不匹配**（优先排查！不要先疑心IP封锁）
   - 先查 modifyPass 状态
   - 再试 PMID 直用或内部ID
   - 最终走 OA 直连降级

### ⚠️ MedData CORRECT Workflow (2026-06-23 最终确认)

> ⚠️ **此节已完全被 `meddata-download` 技能取代**。以下为快速参考，不完整。

**核心两步流程（不可省略、不可篡改参数）**：

```
1. full_look(token=TOKEN, abstractId=11位随机数, pmid=真实PMID, doi=真实DOI)
   → 系统将全文复制到 abstractId 名下，返回 status=2
2. 等待 10 秒（让系统准备全文）
3. viewtext(token=TOKEN, fileName=abstractId)
   → 返回真实PDF bytes
```

**铁律**：
- `abstractId` = 每次生成**11位随机整数**，不可重复，不可用DOI_NO_SLASH，不可固定值
- `pmid` = 论文的**真实PMID**，不可用固定 `'1'`
- `doi` = 论文的真实DOI
- 三步用**同一个 token**，token 过期后可重新获取
- 必须等待 10 秒给系统处理时间

## 智能 Cloudflare 绕过

`tools/paper-manager/src/smart_download.py` 提供两层下载策略：
1. 先用 `requests.get()` 尝试
2. 检测到 Cloudflare（403/503/429 + cf标识）→ 自动重试 `curl_cffi (impersonate="chrome")`

```python
import sys; sys.path.insert(0, 'tools/paper-manager/src')
from smart_download import smart_download
result = smart_download(url, timeout=30)
if result['ok'] and result['content'][:4] == b'%PDF':
    # 下载成功
```

## 参考文件

- `references/curl-cffi-and-cloakbrowser.md` — curl_cffi 与 CloakBrowser 对比：curl_cffi 用于 API 级别的 TLS 伪装（快），CloakBrowser 用于浏览器级完整模拟（慢但更隐蔽）。详见 anti-detect-browser 技能。
- `references/cloudflare-smart-download.md` — 智能Cloudflare绕过
- `references/meddata-browser-vs-cli.md` — MedData浏览器 vs CLI访问差异诊断（2026-06-18）
- `references/unified-download-core.md` — 统一下载核心架构与ID解析矩阵（2026-06-23新增）
- `references/2026-06-18-testing-log.md` — 早期测试记录
- `references/2026-06-18-failure-record.md` — 2026-06-18全面失败实录（Sci-Hub拦截/MedData伪PDF/出版社墙）
- `references/meddata-fulllook-patterns-2026-06-19.md` — **MedData full_look 参数规律测试 + fileName拼接规律 + 频率/IP限制（2026-06-19 新增）**
- `references/scihub-ddos-guard-2026-06-18.md` — Sci-Hub全域DDoS-Guard失效诊断（2026-06-18起，2026-06-19确认为HTTP 403）
- `references/scihub-coverage-filter.md` — Sci-Hub DOI覆盖过滤器（2026-06-22实证）：哪些DOI前缀被Sci-Hub覆盖、哪些触发验证页面、CDN URL模式（sci.bban.top）
- `references/exit-node-scihub-2026-06-19.md` — **❌ 已推翻: Exit Node(64.23.234.118)被学术网站和Sci-Hub全面封锁，不再可用**
- `references/tor-scihub-vg-workflow.md` — **Tor SOCKS5H + sci-hub.vg 完整工作流（2026-06-19 新增，唯一可靠路径）**
- `references/meddata-access-absorbed.md` — MedData下载(旧)
- `references/meddata-api-details.md` — MedData API参数详解(2026-06-04实战)
- `references/paper-manager-fallback.md` — paper-manager降级

## 脚本

- `scripts/smart_download.py` — 自动Cloudflare检测+curl_cffi降级
- `scripts/download_and_upload.py` — 批量下载+上传NotebookLM管线
- `scripts/batch_references_all.sh` — 批量下载脚本
- `scripts/scihub_download.py` — Sci-Hub curl_cffi下载器

> 统一入口: `tools/paper-manager/download_one.py <任意ID>` (支持DOI/arXiv/CorpusID/PMID)
> 详见: `tools/paper-manager/src/downloader/unified_download_core.py`

## 统一入口 (v3.0 — 2026-06-23 重构)

**核心演进：** 从多入口碎片 → 单一统一入口，支持所有论文ID类型。

### 统一调用

```bash
cd /media/yakeworld/sda2/Synthos/tools/paper-manager
source ~/.secrets
pip3 install curl_cffi bs4 lxml  # 缺依赖时装

# 任意ID类型
python3 download_one.py 10.3389/fneur.2020.00602 /tmp/paper.pdf    # DOI
python3 download_one.py 2403.12345 /tmp/paper.pdf                   # arXiv ID
python3 download_one.py CorpusID:12345678 /tmp/paper.pdf             # Semantic Scholar
python3 download_one.py PMID:28962176 /tmp/paper.pdf                 # PubMed ID
```

### 内部架构

```
download_one.py <任意ID>
  └→ unified_download_core.download_paper()
       ├→ normalize_paper_id()     → 识别ID类型
       ├→ _resolve_metadata()      → 跨源补全(SS/Crossref/NCBI)
       │   CorpusID → DOI + PMID
       │   PMID     → DOI
       │   DOI      → PMID
       │   arXiv ID → 直连(不解析)
       ├→ arXiv 直连下载 (最快路径)
       └→ 三层竞速 (SciHub → LibGen → MedData)
            └→ MedData 双格式ID降级:
                 Format 1: DOI_NO_SLASH (Frontiers/BMJ)
                 Format 2: DOI_NO_SLASH + PMID (Bentham等复杂DOI)
```

### 支持的ID类型

| 类型 | 格式示例 | 下载路径 | 解析源 |
|:-----|:---------|:---------|:-------|
| DOI | `10.xxxx/xxx` | SciHub/LibGen/MedData | — |
| arXiv | `2403.12345` | arXiv.org 直连 | — |
| CorpusID | `CorpusID:12345678` | SS→DOI→竞速 | Semantic Scholar |
| PMID | `PMID:28962176` | NCBI→DOI→竞速 | NCBI E-utilities |
| PMC | `PMC1234567` | PMC 直连 | — |

### 工作原则

1. **不自写测试脚本** — 永远调用 `download_one.py`，它内部处理认证链、ID构造、三级竞速、占位检测
2. **先查技能** — 在写任何新代码前，先加载 `pdf-download-racing` 技能确认现有工具链
3. **下载后验证** — `md5sum <file>` 检查占位指纹 `fd469bd7cd29446f2800f099e3b71457`

## Tor 连通性测试 (2026-06-19 新增)

`../scripts/tor_connectivity_test.py` — 测试 Tor 连通性

```
用法:
  python3 tor_connectivity_test.py
```

测试项：
1. SOCKS5 端口可达性
2. Tor 电路构建（Python socks 模块）
3. torify 命令测试
4. 出口节点 IP 验证

## Google Scholar 搜索 (2026-06-19 新增)

`../scripts/google_scholar.py` — Google Scholar 论文搜索

```bash
python3 google_scholar.py "vestibular eye tracking" --max 10
python3 google_scholar.py "vestibular" --year-from 2024 --year-to 2026 --author "Smith"
python3 google_scholar.py "vestibular" --no-tor  # 不使用Tor（默认启用）
```

⚠️ **网络限制**: Google Scholar (scholar.google.com) 的 443 端口在沙箱环境中被屏蔽。
- 此脚本在本地/非受限网络环境中工作
- 需要 Tor SOCKS5H 代理来绕过 IP 封禁
- 请求频率建议 ≤10 queries/min（Google Scholar 反爬）
- 返回 403/CAPTCHA 时自动降级

**依赖**: requests, beautifulsoup4

**已知问题**:
- Google Scholar 无官方 API
- 反爬机制严格（Cloudflare + CAPTCHA）
- 分页需手动处理（start 参数）
- 引用数不精确（GS 不暴露准确引用数）
