# MedData 认证与 PDF 下载系统 — 逆向分析与工作流

## 系统架构

MedData（博库数据知识服务平台）由两个独立认证系统组成：

### 1. www.meddata.com.cn（前端门户）
- **基础 URL**: `http://www.meddata.com.cn`（非 https，HTTPS 不可用）
- **页面类型**: Vue.js SPA（Element Plus + Vant UI）
- **登录入口**: 自动重定向到 `app.meddata.com.cn:8878/#/login`（仅移动端）
- **实际登录页面**: 通过 `www.meddata.com.cn` 的 `/login` 路由（chunk 578aaf79）

### 2. app.meddata.com.cn:8878（应用端）
- **基础 URL**: `http://app.meddata.com.cn:8878/`
- **登录页面**: `http://app.meddata.com.cn:8878/#/login`
- **技术栈**: Vue 3 + Vue Router + Axios

### 3. medbooks.com.cn SSO（单点登录 — 独立系统）
- **API 基础 URL**: `https://uuct.medbooks.com.cn:9443/`
- **登录端点**: `POST /sso/login`
- **正确登录参数**:
```json
{
  "username": "wzsrmyy",
  "password": "<medbooks_password>",
  "type": "USERNAME"
}
```
- **登录类型**: `type` 字段值为 `"USERNAME"`（用户名密码登录）
  - `"TELPHONE"`：手机验证码登录
  - `"IP"`：IP 登录
- **响应**: 返回 JWT 格式的 `bucToken`（`eyJhbG...`）和 `dcode`
- **响应示例**: `{"code":"0","message":"登录成功","data":{"bucToken":"eyJhbGci...","dcode":"0007"}}`

## MedData API 路径

| API | 方法 | 说明 |
|-----|------|------|
| `/api/abstract/full_look` | GET | 触发 PDF 生成，返回 fileName/fileUrl |
| `/api/abstract/viewtext` | GET | 获取 PDF 下载链接 |
| `/api/auth/login` | POST | MedData 自身登录（接受 token，不接受密码） |

**full_look 请求参数**:
- `token` — 认证 token
- `pmid` — PubMed ID
- `doi` — DOI

**full_look 响应**:
```json
{"responseCode": 200, "responseMsg": "成功", "data": {"fileUrl": "...", "fileName": "..."}}
```
- `responseCode=400` + `responseMsg="用户登录失效"` → token 过期
- 空响应 → DOI 无收录

**viewtext 请求参数**:
- `token` — 认证 token
- `fileName` — 从 full_look 返回的 fileName（动态生成，不能直接用 DOI 代替）

## 认证问题分析

### 关键发现：medbooks SSO token 不被 MedData 接受

medbooks.com.cn SSO 返回的 JWT 格式 token（`eyJhbG...`）不被 MedData 接受——所有 API 调用均返回 `{"responseCode":400,"responseMsg":"用户登录失效"}`。

**原因**：medbooks.com.cn 和 meddata.com.cn 虽然同属一个公司，但认证系统完全独立。MedData 需要的是 `uuid:timestamp` 格式 token（如 `16892d61efc502eba8107a636f6b6cb8:202606031406461466`），而非 JWT。

### MedData 自身登录端点

`/api/auth/login` 接受 JSON body 但返回 "用户登录失效"——这是 token 过期后的通用错误，不是密码错误。需要直接获取 MedData 的新 token（非通过 medbooks SSO）。

### Firefox localStorage 中发现的历史 token

从 Firefox localStorage 中找到两个过期 token：
- `da2c9c8c27bd6a0fa9d9b8f8562c359a:202605271700331477`（5月27日）
- `16892d61efc502eba8107a636f6b6cb8:202606031406461466`（6月3日）

这些是之前会话中使用的 token，已过期。格式为 `uuid:YYYYMMDDHHMMSSffffff`。

## PDF 下载工作流（全量流程）

```
Step 1: full_look(pmid/doi, token) -> 触发后台生成
Step 2: 从 full_look 响应提取 fileName 和 fileUrl
Step 3: viewtext(fileName, token) -> 获取 PDF 下载 URL
Step 4: 用 fileUrl 下载 PDF（curl 处理 chunked 编码）
```

**关键细节**：
1. fileName 动态生成，每次请求可能不同——不能直接用 DOI 作为 fileName
2. full_look 必须调用两次：先触发，再用返回的 fileName 调用 viewtext
3. curl 需要处理 chunked 编码（`-N` 或 `--ignore-content-length`）
4. MedData 主要收录中文/国内医学文献，英文论文（Elsevier/Springer/Nature）大多无收录

## SPA 逆向调试方法

当需要逆向 SPA 前端代码以提取 API 调用时：

1. **定位路由**：在 app.js 中搜索 `router=new o.default({mode:"history",routes:[...]})`
2. **识别登录路由**：`path:"/login"` + `name:"Login"` 或 `name:"backLogin"`
3. **定位登录组件**：路由中 `component:function(){return Promise.all([t.e(N)]).then(t.bind(null,"HHHHHH"))}` 中的 HHHHHH 是 chunk hash
4. **搜索 login 相关代码**：在所有 chunk 中搜索 `ssoLogin|backLogin|handleLogin|userCode|userPwd|loginName`
5. **识别 API 调用**：搜索 `.post()/.get()/axios` 调用，排除 vendor 代码（axios、vue-router、lodash 等定义）
6. **提取关键信息**：baseURL、请求路径、请求参数、响应字段

**常见陷阱**：
- chunk-vendors.js 通常只是路由重定向 HTML（2059 字节），不是真正的 vendor 代码
- 真正的 vendor 代码在 assets/js/ 下的 chunk 中（index-*.js 文件）
- 大量 JS 是 Element Plus、Vue、Axios 等框架代码，不是业务逻辑
- 登录页面可能是服务器端渲染（chunk 返回 HTML 而非 JS）