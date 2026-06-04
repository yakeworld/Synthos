# MedData (博库数据知识服务平台) API Guide

> 2026-06-04 通过浏览器 DevTools 逆向分析 + 直接API调用验证。

## 三层架构

```
SSO认证: uuct.medbooks.com.cn:9443/sso/login (POST)
   ↓ bucToken
Token交换: app.meddata.com.cn:8878/api/sso/user/login?bucToken={token}
   ↓ meddataToken
PDF下载: www.meddata.com.cn/api/abstract/viewtext?fileName={id}&token={token}
```

## Auth Flow

### Step 1: SSO 登录 → bucToken

```
POST https://uuct.medbooks.com.cn:9443/sso/login
Content-Type: application/json
Body: {"username": "MEDDATA_USERNAME_PLACEHOLDER", "password": "xxx", "type": "0"}

Response:
{"code": "200", "data": {"url": "http://...?bucToken=eyJ..."}}
```

从 url 中提取 bucToken。

### Step 2: bucToken → meddataToken

```
GET http://app.meddata.com.cn:8878/api/sso/user/login?bucToken={bucToken}

Response:
{
  "realName": "INSTITUTION_NAME_PLACEHOLDER",
  "loginName": "MEDDATA_USERNAME_PLACEHOLDER",
  "responseData": "cc3bb4b5...:202606050640281673",
  "responseCode": 200
}
```

`responseData` = meddataToken, 格式 `{32hash}:{YYYYMMDDHHmmssSSS}`。

## PDF Download

### 主路径: viewtext (已验证)

```
GET http://www.meddata.com.cn/api/abstract/viewtext
  ?fileName={DOI_no_slash}&token={token}
→ HTTP 200 + PDF二进制
```

### 降级: full_look (通常 status=2 无fileUrl)

```
GET http://www.meddata.com.cn/api/abstract/full_look
  ?token={token}&abstractId={id}&pmid=任意数字&doi={真实DOI}
→ status=2 表示有索引但无fileUrl
```

## Key Discovery (2026-06-04)

- fileName = 仅 `DOI.replace('/', '')`。**不需要 PMID 后缀。** `10.3389fneur.2020.00602` → 865KB PDF。
- viewtext 返回0字节 = 论文不在meddata库中
- full_look 一直 status=2，viewtext才是主下载路径
- 一次SSO登录可复用多次下载

## 已知问题

1. token ~24h 过期 (时间戳字段)
2. 部分出版社不可用: IEEE/Hindawi/Wiley/BMJ
3. browser_navigate 超时 → 用 Python/Playwright headless 或直接API调用
4. SSO login 使用 verify=False（关闭证书验证）
