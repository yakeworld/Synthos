# MedData 全文下载API

## 平台概述

中国医学数据知识服务平台 `www.meddata.com.cn`，后端在 `app.meddata.com.cn:8878`。
提供医学论文/图书的全文PDF下载接口。由博库科技运营。

## 认证拓扑（2026-05-31 实测）

本平台涉及**两套独立的认证体系**，不可混用：

```
┌───────────────────────────────────────────┐
│ 体系①: MedData PDF 全文下载               │
│                                           │
│  <MEDDATA_USERNAME>:<MEDDATA_PASSWORD> (INSTITUTION_NAME_PLACEHOLDERSSO账号)  │
│       │ (POST JSON)                       │
│       ▼                                    │
│  uuct.medbooks.com.cn:9443/sso/login      │
│       │ (200 + 302 url 含 bucToken)        │
│       ▼                                    │
│  → lib.medbooks.com.cn/sso/login?buc=...  │
│       │ (302 + 写 cookies)                │
│       ▼                                    │
│  → wzhsyd.medbooks.com.cn (机构门户)      │
│       │                                   │
│  ✂ ─ ─ ─ 以下是断链 ─ ─ ─ ─ ─ ─ ─ ✂    │
│       ▼                                    │
│  app.meddata.com.cn:8878/api/sso/          │
│  user/login?bucToken=...                   │
│       │ (responseCode: 500)                │
│       ▼                                    │
│  ❌ Token交换失败 — 见下文诊断             │
└───────────────────────────────────────────┘

┌───────────────────────────────────────────┐
│ 体系②: CNKI 知网跳转登录                  │
│                                           │
│  http://uuc.medbooks.com.cn:9094/         │
│  third-skip/login/tzmedbooks               │
│       │ (返回HTML, 内含JS `ju()`)         │
│       ▼                                    │
│  login.cnki.net/TopLogin/api/loginapi/     │
│  Login?userName=tzmedbooks&pwd=tzrfvtgb02 │
│       │ (5023: 密码错误, 剩3次机会)       │
│       ▼                                    │
│  ❌ 登录失败 — 凭证已过期                  │
└───────────────────────────────────────────┘
```

## ⚠️ 现状（2026-05-31）

### 体系① MedData

| 步骤 | 状态 | 详情 |
|:-----|:----:|:-----|
| SSO 登录 | ✅ 200 OK | 返回 `modifyPass: 1`（密码被标记需修改） |
| bucToken 获取 | ✅ 正常 | JWT, HS512, 7天有效 |
| lib.medbooks 重定向 | ✅ 正常 | 写 cookies (`JSESSIONID`, `_site_id_cookie`) |
| **Token 交换** | **❌ 500** | `responseMsg: "登录失败，用户名或密码错误"` |
| viewtext 下载 | ❌ 不可用 | 依赖有效 token |

**诊断结论**：`<MEDDATA_USERNAME>:<MEDDATA_PASSWORD>` 的 SSO 密码可能已被 SSO 系统标记为过期（`modifyPass: 1`），导致 `app.meddata.com.cn:8878` 的 token 交换接口拒绝认证。需要先到 `medbooks.com.cn` 手动登录一次，按提示修改密码，再用新密码更新环境变量。

### 体系② CNKI 知网

**`tzmedbooks:tzrfvtgb02`** — 密码已失效。CNKI 返回 `ErrorCode: 5023`（用户名或密码错误）。

## 认证链（官方设计，但当前失效）

### Step 1: SSO登录

```python
import requests, re
r = requests.post("https://uuct.medbooks.com.cn:9443/sso/login",
    json={"username": "<MEDDATA_USERNAME>", "password": "xxx", "appId": None,
          "type": "USERNAME", "autoLogin": True},
    headers={"Content-Type": "application/json"}, verify=False)
d = r.json()
# 返回示例:
# {"code":"200","message":"操作成功","data":{
#   "url":"http://lib.medbooks.com.cn/sso/login?bucToken=eyJ...",
#   "autoKey":"969a19f7...", "dcode":"0007",
#   "username":"<MEDDATA_USERNAME>", "realName":"INSTITUTION_NAME_PLACEHOLDER",
#   "aid":"book_med2", "modifyPass":1}}  # ← 需改密标志

buc_token = re.search(r'bucToken=([^&]+)', d['data']['url']).group(1)
```

### Step 2: 交换token（当前返回500）

```python
r2 = requests.get("http://app.meddata.com.cn:8878/api/sso/user/login",
    params={"bucToken": buc_token})
# 返回: {"loginName":"<MEDDATA_USERNAME>","responseCode":500,"responseMsg":"登录失败，用户名或密码错误"}
```

尝试过的变体（全部失败）：
- `bucToken` + `username`
- `bucToken` + `password`
- `bucToken` + `autoKey`
- 带 SSO 重定向后的 cookies 访问
- POST 方式（405 Method Not Allowed）

### Step 3: 下载

```python
r3 = requests.get("http://www.meddata.com.cn/api/abstract/viewtext",
    params={"fileName": abstract_id, "token": meddata_token})
```

## API接口

### viewtext（主入口，直返PDF）

```
GET http://www.meddata.com.cn/api/abstract/viewtext
Params: fileName={abstractId}&token={token}
Returns: Raw PDF bytes / {"responseCode":400,"responseMsg":"用户登录失效"}
```

abstractId格式: DOI去掉`/`。
例: `10.3389/fneur.2020.00602` → `10.3389fneur.2020.00602`

### full_look（备选，查询元数据）

```
GET http://www.meddata.com.cn/api/abstract/full_look
Params: token={token}&abstractId={id}&pmid=1&doi={id}
Returns: {"responseData": {"status": 1|2|3, "fileName": "...", "fileUrl": "..."}}
```

status含义:
- 1: 有全文，fileUrl为下载链接
- 2: 仅有元数据，无file
- 3: 未找到

## 调试命令

```bash
# 测试SSO登录
curl -sk -X POST "https://uuct.medbooks.com.cn:9443/sso/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"<MEDDATA_USERNAME>","password":"xxx","appId":null,"type":"USERNAME","autoLogin":true}'

# 解码JWT bucToken（查看过期时间）
python3 -c "import base64,json; p='<buc_token>'.split('.')[1]; p+='='*(4-len(p)%4); print(json.loads(base64.urlsafe_b64decode(p)))"
# 输出: {"iat": 1780182123, "sub": "<MEDDATA_USERNAME>", "exp": 1780786923}

# 测试viewtext
curl -s "http://www.meddata.com.cn/api/abstract/viewtext?fileName=101016jmedia2022100001&token=test"
# 返回: {"responseCode":400,"responseMsg":"用户登录失效"}
```

## 集成方式

已在 `tools/paper-manager/src/sources/meddata.py` 中实现为竞速引擎 Tier 3。

### 环境变量

| 变量 | 用途 | 优先级 |
|------|------|--------|
| `MEDDATA_TOKEN` | 直接token | 高（不推荐，易过期） |
| `MEDDATA_USERNAME` + `MEDDATA_PASSWORD` | 自动登录 | 低（推荐，但当前失效） |

### 注意事项

1. **密码可能被标记为需修改** — SSO返回 `modifyPass: 1` 时需到 medbooks.com.cn 改密
2. **token交换接口不稳定** — 2026-05-31 实测发现 `app.meddata.com.cn:8878` 返回500
3. **CNKI跳转凭证独立** — `tzmedbooks/tzrfvtgb02` 是另一体系，与 MedData 无关
4. **SSO成功不等于 MedData 可用** — 两套系统用同一 SSO 但独立授权

## 已知限制

1. token约8小时过期（JWT payload中的exp字段），自动登录模式无此问题
2. `viewtext` API返回空/HTML表示meddata无此文献，不报错
3. 中文期刊覆盖优于外文
4. 2025年及以后的论文覆盖较低
