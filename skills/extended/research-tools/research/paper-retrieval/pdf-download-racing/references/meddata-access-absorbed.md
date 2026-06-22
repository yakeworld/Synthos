---
name: meddata-access
description: "MedData中国医学全文数据库访问：通过www.medbooks.com.cn SSO登录获取bucToken，用于meddata.com.cn PDF下载。覆盖INSTITUTION_NAME_PLACEHOLDER(MEDDATA_USERNAME_PLACEHOLDER)账号的完整认证链。"
version: 1.0.0
tags: [meddata, pdf-download, sso, chinese-medical]
---

# MedData 全文数据库访问

> INSTITUTION_NAME_PLACEHOLDER(MEDDATA_USERNAME_PLACEHOLDER) 机构账号。通过博库科技(medbooks) SSO 认证链。

## 认证流程

### 完整认证链

```
1. SSO登录（二选一）
   ├─ 方式①: POST uuct.medbooks.com.cn:9443/sso/login (type:"0" + username + password)
   │     → {"code":"200","data":{"url":"http://lib.medbooks.com.cn/sso/login?bucToken=eyJ..."}}
   └─ 方式②: 企微扫码 → 自动302 → session cookie

2. 提取 bucToken（从url参数）
   bucToken = 从 data.url 中 regex: bucToken=([^&]+)

3. 交换 bucToken → meddata token（⚠️ 必须GET）
   GET app.meddata.com.cn:8878/api/sso/user/login?bucToken={token}
   → {"responseData":"hash:timestamp","responseCode":200,"responseMsg":"登录成功"}

4. 下载PDF（二选一，⚠️ 必须先 full_look 再 viewtext）
   ├─ 主路径: full_look → 获取 fileName，再 viewtext(fileName) → PDF
   │   GET www.meddata.com.cn/api/abstract/viewtext?fileName={id}&token={token}
   │   → 200 + PDF bytes / 200 + 0 bytes（无此论文）
   └─ full_look: GET www.meddata.com.cn/api/abstract/full_look?token={token}&abstractId={id}&pmid=1&doi={id}
       → {"responseData":{"status":1-3,"fileUrl":null/url,"fileName":"..."}}
```

**⚠️ 关键步骤（2026-06-18 最终确认）**: MedData 下载必须是**两步走**：
1. **full_look** — 触发 PDF 生成，获取 fileName 和 fileUrl
2. **viewtext** — 用 fileName 下载 PDF

直接跳过 full_look 调用 viewtext 也能工作（如果 fileName 已知），但 full_look 提供了更完整的信息（status、fileUrl）。

**⚠️ 重要**: 即使 full_look 返回 status=2（有索引无 fileUrl），用 fileName 走 viewtext 仍可能获取 PDF。这是因为 MedData 的 full_look API 对许多论文只返回 status=2（有索引无下载链接），但 viewtext 仍可提供文件。

### 参数格式

- `fileName` / `abstractId`（两种格式，取决于论文）：
  - **格式A — 内部ID**（常见，推荐）：meddata 数据库内部编号，如 `2985248Rpub37800834`
    - `2985248` = 内部自增ID，`Rpub` = 资源类型标记，`37800834` = 论文标识后缀
    - 需通过 medbooks.com.cn 搜索界面获取（搜索结果中的 internal ID 字段）
  - **格式B — DOI去斜杠**（部分兼容）：如 `10.7326/M14-0698` → `10.7326M14-0698`
    - **2026-06-04 实测：此格式大部分返回 status=2（论文不在库中）**
    - 仅对与 meddata 有合作的特定出版社可能有效
- token 格式: `{md5_hash}:{timestamp}`（如 `4fd90b0054512528004774c053324aac:202606041812031375`）

### full_look API status 含义

| status | 含义 |
|:------:|:------|
| 1 | 有全文PDF，fileUrl为下载链接 |
| 2 | 仅有元数据，无PDF |
| 3 | 未找到 |

## 认证方式

### 方式①：企业微信扫码（原始方式）

`wwlogin.js` 源码确认：
- 页面内嵌 iframe → 企业微信二维码
- 手机企业微信扫码 → 授权回调

### 方式②：密码直登（推荐，更快）

`uuct.medbooks.com.cn:9443/sso/login` 支持密码登录，参数为 `type: "0"`：

```bash
curl -sk -X POST "https://uuct.medbooks.com.cn:9443/sso/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"<USERNAME>","password":"<PASSWORD>","type":"0"}'
```

**⚠️ 关键陷阱**: 参数必须用 `type: "0"`，不是 `type: "USERNAME"`、`type: "account"` 或其他值。`"0"` 是密码登录模式的内部代码。
- `type: "USERNAME"` → 返回 `"系统错误"`（但Python脚本中写的就是这个 — 需要修正）
- `type: "0"` → 返回 `code: 200` + bucToken ✅

**2026-06-04 实测确认**: 密码直登完整可用，但需注意 `modifyPass` 标记（见下方陷阱）。

**2026-06-18 验证**: 使用 `type: "0"` 后，SSO 登录完全成功。bucToken 为 JWT 格式（`eyJhbG...`）。

**⚠️ 所有之前 MedData 失败的根因**: 误用 `type: "USERNAME"`（应始终用 `"0"`）。

## Cookie 持久性

- `_site_id_cookie=1176` 仅在 SSO 查询时设置
- 扫码登录后的 session cookie 可持久化
- 在本地浏览器完成一次扫码登录后，用 `--browser-cookies chrome` 读取 cookie

## 参考文件

- `references/access-probe-2026-06-04.md` — 完整端点探测记录与参数测试结果
- `references/access-probe-2026-06-03.md` — 旧版探测记录
- `references/session-2026-06-04-internal-id-discovery.md` — 内部ID格式发现与modifyPass重新评估

## 关键参数
## 关键参数

| 参数 | 值 |
|:-----|:----|
| SSO端点 | http://wzhsyd.medbooks.com.cn/sso/query?code=ww&query= |
| API端点 | www.meddata.com.cn/api/abstract/viewtext |
| token端点 | app.meddata.com.cn:8878/api/sso/user/login |
| fileName | 内部ID（如 `2985248Rpub37800834`）或 DOI去斜杠（不推荐） |
| 机构ID | MEDDATA_USERNAME_PLACEHOLDER（INSTITUTION_NAME_PLACEHOLDER） |

## 注意事项

- SSO端点使用**HTTP**（非HTTPS），`code=ww`为企微认证
- query参数可以是任意期刊名/BPPV等关键词
- 302跳转的Location头含认证令牌信息
- 认证链需完整的cookie会话维持

## ⚠️ 已知陷阱

### ① modifyPass=1 标记与 fileName ID 格式——双重问题

SSO登录返回中的 `modifyPass: 1` 表示密码被标记为需修改。但这**不是**全文下载失败的唯一原因。

**2026-06-04 新发现**: `modifyPass=1` 状态下，用正确的内部 ID 仍可成功下载 PDF：
- `fileName=2985248Rpub37800834` + token → 成功下载 486KB PDF ✅
- `fileName=DOI去掉斜杠` + token → 全部返回 status=2 / 0 bytes ❌

**说明**：全文下载失败可能存在两重原因：
1. `fileName` 参数用了错误的 ID 格式（详见陷阱④）
2. `modifyPass=1` 可能仅阻断部分出版社或特定条件

**处理**：
1. 优先确认 `fileName` 是 meddata 内部 ID 而非 DOI 衍生格式
2. 如确认 ID 正确仍失败，再到 `medbooks.com.cn` 浏览器手动修改密码

### ② `type: "0"` vs `type: "USERNAME"` 参数差异（2026-06-04 已修复 / 2026-06-18 最终确认）

| 参数值 | 结果 | 来源 |
|:-------|:-----|:-----|
| `type: "0"` | ✅ 200 + bucToken | ✅ 当前正确参数 |
| `type: "USERNAME"` | ❌ 500 系统错误 | **所有之前 MedData 失败的根因** |
| `type: "account"` | ❌ 500 系统错误 | 旧版探测 |
| `type: "1"` | ❌ 要求手机号/验证码 | 短信登录模式 |

### ③ Token交换必须用 GET 而非 POST

`app.meddata.com.cn:8878/api/sso/user/login` 只接受 **GET** 方式：
- `GET ?bucToken={token}` → 200 + 登录成功
- `POST` → 405 Method Not Allowed

### ④ `fileName` = DOI去斜杠（已验证可用）

`tools/paper-manager/src/sources/meddata.py` 中的 `_make_abstract_id(doi)` 执行 `doi.replace('/', '')`，产生的 `10.3389fneur.2020.00602` 格式可作为 MedData viewtext API 的唯一ID。

✅ DOI去斜杠 → viewtext → 真实PDF（2026-06-22 实测：663KB Frontiers PDF 成功下载）

**注意**：旧文档中提及的"内部ID 格式 2985248Rpub37800834" 是 medbooks.cn 搜索界面使用的另一种ID格式，非 API 调用必需。不要混淆。

### ⑤ meddata 出版社支持矩阵（2026-06-22 修正）

**MedData 是外文医学论文全文平台**。前期测试中返回占位 PDF 的原因是出口 IP(64.23.234.118) 被封锁 + 缺依赖包，非 MedData 覆盖问题。2026-06-22 实测 `download_one.py` 成功下载 Frontiers 全文 PDF。

| 出版社 | 状态 | 说明 |
|:-------|:----:|:-----|
| Frontiers | ✅ 成功 | 10.3389/fneur.2020.00602 → 663KB 真实PDF |
| 其他出版社 | 待测 | 需在国内网络环境下验证 |

**占位 PDF 识别**: MD5 `fd469bd7cd29446f2800f099e3b71457`、606841 字节 — 当返回此文件时，说明 MedData 本次请求未命中真实全文（可能出口 IP 被限）。
