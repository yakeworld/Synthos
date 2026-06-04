# MedData 全文下载API

## 平台架构

```
搜索/浏览界面:  www.medbooks.com.cn  (SPA, 需登录后搜索论文)
下载API:        www.meddata.com.cn    (viewtext/full_look 接口)
后端API:        app.meddata.com.cn:8878 (token交换)
SSO认证:        uuct.medbooks.com.cn:9443 (统一登录)
运营方:         博库科技 ©2017
```

**注意**：medbooks.com.cn 是搜索/浏览界面，meddata.com.cn 是下载后端。
两者是同一平台的不同入口。搜索论文应通过 medbooks.com.cn 进行，
获取到内部 ID 后再通过 meddata.com.cn 的 viewtext API 下载。

## 认证拓扑（2026-06-04 实测）

本平台涉及**两套独立的认证体系**，不可混用：

```
#### 体系①: MedData PDF 全文下载（可用！2026-06-04）

<MEDDATA_USERNAME>:<MEDDATA_PASSWORD> (INSTITUTION_NAME_PLACEHOLDERSSO账号)
       │ (POST JSON, type: "0")
       ▼
  uuct.medbooks.com.cn:9443/sso/login
       │ (200 + 302 url 含 bucToken)
       ▼
  lib.medbooks.com.cn/sso/login?buc=...
       │ (302 + 写 cookies - JSESSIONID, _site_id_cookie)
       ▼
  app.meddata.com.cn:8878/api/sso/user/login?bucToken=...
       │ (GET, responseData → token)
       ▼
  www.meddata.com.cn/api/abstract/viewtext?fileName=<INTERNAL_ID>&token=...
       │ (200 + PDF bytes)
```

**2026-06-04 关键发现**：`fileName` 参数用的是 **MedData 内部ID**（如 `2985248Rpub37800834`），**不是** DOI 去斜杠。不要试图从 DOI 推导此 ID——须通过 MedData 搜索 API 或已知的 ID 映射获取。

## 认证流程 (2026-06-04 已验证)

### Step 1: SSO登录（type="0"）

```python
import requests, re
requests.packages.urllib3.disable_warnings()
r = requests.post("https://uuct.medbooks.com.cn:9443/sso/login",
    json={"username": "<MEDDATA_USERNAME>", "password": "xxx", "type": "0"},
    headers={"Content-Type": "application/json"}, verify=False, timeout=15)
d = r.json()
# 返回: {"code":"200","message":"操作成功","data":{
#   "url":"http://lib.medbooks.com.cn/sso/login?bucToken=eyJ...",
#   "realName":"INSTITUTION_NAME_PLACEHOLDER","aid":"book_med2","modifyPass":0,...}}

buc_token = re.search(r'bucToken=([^&]+)', d['data']['url']).group(1)
```

**⚠️ 关键陷阱**: `type` 必须用 `"0"`，非 `"USERNAME"`。

### Step 2: 交换token（GET）

```python
r2 = requests.get("http://app.meddata.com.cn:8878/api/sso/user/login",
    params={"bucToken": buc_token}, timeout=10)
# 返回: {"realName":"INSTITUTION_NAME_PLACEHOLDER","loginName":"MEDDATA_USERNAME_PLACEHOLDER",
#        "responseData":"hash:timestamp","responseCode":200}
meddata_token = r2.json().get('responseData', '')
```

### Step 3: 下载

```python
# fileName = MedData 内部ID（非DOI！）
r3 = requests.get("http://www.meddata.com.cn/api/abstract/viewtext",
    params={"fileName": "<INTERNAL_ID>", "token": meddata_token}, timeout=30)
# 成功 → 200 + Raw PDF bytes (以 %PDF- 开头)
# 无论文 → 200 + 0 bytes
```

## API接口

### viewtext（主入口，直返PDF）

```
GET http://www.meddata.com.cn/api/abstract/viewtext
Params: fileName=<INTERNAL_ID>&token=<token>
Returns: Raw PDF bytes / 200 + 0 bytes（无此论文）
```

**`fileName` 格式**：MedData 内部ID（如 `2985248Rpub37800834`），并非 DOI 去斜杠。
`_make_abstract_id()` 函数（DOI 去 `/`）是错的——不要用来调 viewtext。
正确做法：通过 MedData 搜索接口获取内部 ID，或从已知映射中查。

### full_look（备选，查询元数据）

```
GET http://www.meddata.com.cn/api/abstract/full_look
Params: token=<token>&abstractId=<id>&pmid=1&doi=<id>
Returns: {"responseData": {"status": 1|2, "fileName": "...", "fileUrl": null|null}}
```

status含义:
- 1: 有全文，fileUrl 为下载链接
- 2: **论文不在 MedData 库中**（仅元数据，无全文）

**注意**: status=2 不代表 modifyPass 问题，单纯是论文不在库中。
实测多篇 Frontiers / Elsevier / 中华医学系列 DOI 均返回 status=2。

## 已知可下载的内部 ID 示例

| 内部 ID | 来源 | 大小 | 日期 |
|:--------|:-----|:----|:-----|
| `2985248Rpub37800834` | 用户提供 | 486KB, PDF 1.4 | 2026-06-04 |

此 ID 格式规律不明确——需要浏览器登录 medbooks.com.cn 后搜索论文，
在 Network 面板中查找 API 请求，获取内部 ID。

## 需要浏览器操作时的最佳实践

1. **不要用 `browser_navigate` 工具**（在 meddata/medbooks 站点超时）
2. 改用 **Playwright headless 网络监控 Python 脚本**，background 启动：
   ```python
   from playwright.sync_api import sync_playwright
   with sync_playwright() as p:
       browser = p.chromium.launch(headless=False, timeout=30000)
       page = browser.new_page()
       page.on('response', lambda resp: ...)  # 捕获 API
       page.goto('http://www.meddata.com.cn', timeout=30000)
       import time; time.sleep(999999)  # 保持打开
       browser.close()
   ```
3. 需要用户交互时，用 `headless=False` 让用户在屏幕上操作
4. 所有 API 调用保存到 `/tmp/meddata_captured.json` 供分析
5. 搜索论文应在 **medbooks.com.cn** 进行，不是 meddata.com.cn

## 调试命令

```bash
# SSO登录
curl -sk -X POST "https://uuct.medbooks.com.cn:9443/sso/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"<USER>","password":"<PWD>","type":"0"}'

# viewtext（已知内部 ID）
curl -s "http://www.meddata.com.cn/api/abstract/viewtext?fileName=2985248Rpub37800834&token=<TOKEN>" -o paper.pdf

# full_look
curl -s "http://www.meddata.com.cn/api/abstract/full_look?token=<TOKEN>&abstractId=2985248Rpub37800834&pmid=1"
```

## 集成方式

已在 `tools/paper-manager/src/sources/meddata.py` 中实现为竞速引擎 Tier 3。

### 环境变量

| 变量 | 用途 | 优先级 |
|------|------|--------|
| `MEDDATA_TOKEN` | 直接token | 高（不推荐，易过期） |
| `MEDDATA_USERNAME` + `MEDDATA_PASSWORD` | 自动登录 | 低（推荐，自动续期） |

### 注意事项

1. **`fileName` 是内部ID，非DOI** — `_make_abstract_id()` 函数只去 `/` 是错误的。
   需要通过 MedData 搜索接口获取内部 ID。
2. **SSO 参数必须用 `type="0"`** — `"USERNAME"` 返回500（已修复 meddata.py）
3. **Token 交换必须用 GET** — POST 返回405
4. **status=2 ≠ modifyPass 问题** — 多数情况只是论文不在库中
5. **browser_navigate 工具在 meddata 站点超时** — 用 Playwright headless Python 脚本代替
6. **SSO login + viewtext 链路完整可用**（2026-06-04 验证）
