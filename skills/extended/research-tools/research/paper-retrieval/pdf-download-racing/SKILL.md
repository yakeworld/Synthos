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

## 统一入口（2026-06-23 重构）

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

内部竞速层级（由 `unified_download_core.py` 自动执行）:
```
Tier 0: arXiv 直连 (仅arXiv ID)
Tier 1: SciHub (curl_cffi TLS伪装)
Tier 2: LibGen
Tier 3: MedData (双格式ID降级: DOI_NO_SLASH → DOI_NO_SLASH+PMID)
```

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

**⚠️ 2026-06-19 最终确认 — Sci-Hub 全面失效**
- 所有11个Sci-Hub域（ru/ee/wf/shop/ren/red/al/vg/es/box/yt）均返回 HTTP 403/0/ERROR
- curl_cffi impersonate="chrome120" 无法绕过 — 403 是服务端拒绝，非JS挑战
- `sci-hub.shop` 返回二进制攻击页（`a bytes-like object required`）
- **结论**: Sci-Hub在当前网络环境下完全不可用，不应再尝试
- 2026-06-18 记录的是 DDoS-Guard JS 挑战，2026-06-19 确认为 HTTP 403 拒绝

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
```

**MedData 定位**: 外文医学论文平台（非中文期刊）。
**SSO 账号**: wzsrmyy (温州市人民医院), 密码在 ~/.secrets。
**出口 IP 64.23.234.118 被学术平台封锁** — 如遇占位PDF先检查网络环境。

## Pitfalls

### ⚠️ EXIT NODE IP 64.23.234.118 IS FULLY BLOCKED

**CRITICAL**: Tailscale exit node (Digital Ocean NYC, 64.23.234.118) is blocked by:
- All Sci-Hub domains → 403/timeout/"search proxy"
- Semantic Scholar API → 404 for ANY DOI
- EuropePMC API → 404
- Unpaywall API → 404
- CrossRef API → 404
- Academic websites and Sci-Hub consider DO 64.23.234.0/24 as known proxy/scanner

**Solution**: Use Tor SOCKS5H (socks5h://127.0.0.1:9050). Exit Node MUST NOT be used for PDF downloads.

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

### ⚠️ CORRECT Workflow Is Different From Old Documentation

**The old `viewtext` example in this skill still references `www.meddata.com.cn`** — that domain returns placeholders.
The correct domain is `app.meddata.com.cn:8878` and requires a complete 3-step flow with consecutive calls.
Use `scripts/meddata-correct-download.py` for the verified workflow.

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

## Sci-Hub域列表（2026-06-19 实证更新）

```python
SCI_HUB_DOMAINS = [
    "https://sci-hub.ru",     # ❌ 返回 "search proxy" (DOI不在库)
    "https://sci-hub.ee",     # ❌ 不可达/JS挑战
    "https://sci-hub.shop",   # ❌ 返回 "search proxy"
    "https://sci-hub.ren",    # ❌ JS challenge ("Just a moment...")
    "https://sci-hub.red",    # ❌ 返回 "search proxy"
    "https://sci-hub.al",     # ❌ 返回 "search proxy"
    "https://sci-hub.vg",     # ✅ 唯一成功: HTML → iframe → PDF
    "https://sci-hub.wf",     # ❌ 返回空HTML
    "https://sci-hub.es",     # ❌ 不可达
    "https://sci-hub.box",    # ❌ 返回 "search proxy"
    "https://sci-hub.yt",     # ❌ 不可达
]
# 结论: 通过 Tor SOCKS5H，仅 sci-hub.vg 可用。不要多域轮询，单域即可。
```

## MedData (外文医学论文全文平台)

需设置环境变量：
```bash
export MEDDATA_USERNAME="MEDDATA_USERNAME_PLACEHOLDER"
export MEDDATA_PASSWORD="MEDDATA_PASSWORD_PLACEHOLDER"
```

### 完整认证链（2026-06-18 实测确认）

**Step 1: SSO 登录**（⚠️ 必须使用 --tls-max 1.2）
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
curl -s -o output.pdf "http://www.meddata.com.cn/api/abstract/viewtext?fileName=<DOI_NO_SLASH>&token=<TOKEN>" \
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

### ⚠️ MedData 频率限制 + IP 限制 (2026-06-19 实测)

**频率限制**：频繁调用 `full_look` 会触发 `responseCode=500` + "查看全文次数超过限制，请稍后再试！"
- 单次会话内 3-5 篇正常
- 批量扫描多篇文章后触发（约 10 次请求）
- 需要等待数分钟到数十分钟冷却

**IP 限制**：境外 IP（如本机出口 64.23.234.11，美国）被进一步限制：
- 频率限制后可能完全封禁（token exchange 也失败，返回空）
- 首次调用成功，批量调用后触发限制，持续调用后 IP 被封
- **解决**：需国内网络环境或控制调用频率（每篇间隔 >10 秒，每小时不超一定次数）

**诊断顺序**：
1. 如果 SSO 返回空响应 → 可能是 IP 被封或 TLS 问题
2. 如果 token exchange 返回空 → 确认 IP 被封或频率限制
3. 如果 full_look 返回 500 → 频率限制，等待冷却
4. 如果 full_look 正常但 viewtext 返回占位 → 该论文不在 MedData 收录范围

### ⚠️ MedData CORRECT Workflow (2026-06-18 15:30 Final)

**CRITICAL**: The correct MedData workflow uses `app.meddata.com.cn:8878` with a complete 3-step flow executed in a SINGLE session (token expires in seconds):

1. **SSO login** (one-time): `POST https://uuct.medbooks.com.cn:9443/sso/login` with `{"username":"MEDDATA_USERNAME_PLACEHOLDER","password":"MEDDATA_PASSWORD_PLACEHOLDER","type":"0"}`
   - Returns `bucToken` from `data.url` (split on `bucToken=`)

2. **Token exchange** (one-time): `GET http://www.meddata.com.cn/api/sso/user/login?bucToken=<TOKEN>`
   - Returns `responseData` field = `<uuid>:<timestamp>` (this is the working token)

3. **For each paper, consecutive calls with the SAME token:**
   - **full_look**: `GET http://www.meddata.com.cn/api/abstract/full_look?token=<TOKEN>&abstractId=<DOI_NO_SLASH>&pmid=1&doi=<DOI>`
     - Response structure: `{"responseData":{"status":2,"fileName":"<FILENAME>","fileUrl":null,"doiUrl":null}}`
     - **NEVER access `fileName` directly** — it's nested under `responseData.fileName`
     - `status: 0` = has full text, `status: 2` = indexed without full text (Western papers commonly)
   - **viewtext**: `GET http://app.meddata.com.cn:8878/api/abstract/viewtext?fileName=<FILENAME>&token=<TOKEN>`
     - **URL must be `app.meddata.com.cn:8878`** (NOT `www.meddata.com.cn` — the old domain returns placeholder)
     - **⚠️ fileName 关键规则（2026-06-18 实测修正）**:
       - `full_look` 返回的 `responseData.fileName` 可能只是 `DOI_NO_SLASH`（如 `10.3389fneur.2020.00602`）
       - 但某些论文需要 **`DOI_NO_SLASH + PMID`** 组合格式才能获取真实 PDF
       - 例如: `10.3892etm.2017.483728962176`（DOI_NO_SLASH=10.3892etm.2017.4840 + PMID=28962176）
       - **如果 full_look 返回的 fileName 下载得到占位 PDF，尝试拼接 PMID 再下载**
     - **Add 1-second delay between full_look and viewtext** (server needs time to generate file)
     - **Timeout: 30 seconds** (server can be slow)

**Example successful calls (2026-06-18):**
```
# Barany 2020 — 标准路径
full_look → responseData.fileName = "10.3389fneur.2020.00602"
viewtext (app) → 663417 bytes, MD5=c42bfb3cdb3a9751f99dd7d8dea5bb50 ✅ REAL PDF

# Tang 2017 — DOI_NO_SLASH 返回占位，DOI_NO_SLASH+PMID 成功
full_look → responseData.fileName = "10.3892etm.2017.4840" (下载占位)
viewtext with fileName="10.3892etm.2017.483728962176" → 737151 bytes, MD5=8ef1b8b2 ✅ REAL PDF
```

**Verification (post-download):**
- Placeholder MD5: `fd469bd7cd29446f2800f099e3b71457` (606841 bytes, title "PII: 0006-2944(75)90147-7")
- Must check every download: `md5sum output.pdf | awk '{print $1}'`

**MedData coverage (2026-06-23 校正):**
- MedData 是 **外文医学论文平台**（用户校正）
- ✅ **Frontiers** papers (e.g., `10.3389/fneur.2020.00602`) — 663KB 真实PDF
- ✅ **BMJ** papers (e.g., `10.1136/bmj.m2689`) — 42KB 真实PDF
- ✅ **Bentham Science** (e.g., `10.3892/etm.2017.4840`) — 737KB 真实PDF
- 部分DOI（含连字符）可能需 fileName+PMID 组合
- 下载失败先检查出口IP / 依赖 / 频率限制
- ❌ 旧断言"MedData只覆盖中文期刊"已作废（根源: Exit Node IP被封锁导致CLI测试误判）

**Fallback strategy when MedData returns placeholder:**
1. OA direct download (Frontiers: `https://www.frontiersin.org/journals/{journal}/articles/{DOI}/pdf`)
2. PLOS ONE: `https://journals.plos.org/plosone/article/file?id={DOI_NO_SLASH}&type=pdf`
3. PubMed Central (PMC) — but blocked by reCAPTCHA in automated context
4. Manual download via browser (user-reported as possible)
5. Consider removing invalid reference if unobtainable after all attempts

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
