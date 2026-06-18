# MedData Complete Authentication Flow (2026-06-18)

## 认证流程 — 完整

### Step 1: SSO Login

```bash
curl -s -X POST "https://uuct.medbooks.com.cn:9443/sso/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"MEDDATA_USERNAME_PLACEHOLDER","password":"MEDDATA_PASSWORD_PLACEHOLDER","type":"0"}'
```

**成功响应**：
```json
{"code":"200","message":"操作成功","data":{"url":"http://lib.medbooks.com.cn/sso/login?bucToken=eyJ...", "realName":"INSTITUTION_NAME_PLACEHOLDER", "dcode":"0007"}}
```

**失败响应**：
```json
{"code":"999","message":"用户名或密码错误","data":null}
```

### Step 2: Token Exchange

```bash
# 正确路径：/api/sso/user/login?bucToken=...
# 错误路径：/api/tokenExchange — 返回 400 "用户登录失效"
# 错误路径：/api/abstract/tokenExchange — 返回 400 "用户登录失效"
curl -s -X GET "http://www.meddata.com.cn/api/sso/user/login?bucToken=<bucToken>"
```

**成功响应**：
```json
{"realName":"INSTITUTION_NAME_PLACEHOLDER","loginName":"MEDDATA_USERNAME_PLACEHOLDER","loginCode":"0007","responseData":"44d5c7537812ef43b85f5ebf068c386f:202606181506541879","responseCode":200,"responseMsg":"登录成功"}
```

`responseData` 字段即为 MedData token。格式：`<hash>:<timestamp>`

### Step 3: full_look

```bash
curl -s -X GET "http://www.meddata.com.cn/api/abstract/full_look?token=<token>&abstractId=<DOI_NO_SLASH>&pmid=1&doi=<DOI>"
```

**返回值**：
- `status: 0` — 无索引
- `status: 1` — 有摘要无全文
- `status: 2` — 有索引无PDF（有目录无全文）
- `fileName` — 用于 viewtext 的文件名
- `fileUrl` — 如果有全文则返回 URL

### Step 4: viewtext

```bash
# fileName 是 doi 去掉斜杠
# 使用 curl（非 Python requests）处理 chunked 编码

curl -s -o output.pdf \
  -H "User-Agent: Mozilla/5.0" \
  -H "Accept: application/pdf" \
  "http://www.meddata.com.cn/api/abstract/viewtext?fileName=<DOI_NO_SLASH>&token=<token>"
```

### 关键发现

1. **Token exchange URL** 必须是 `/api/sso/user/login`（非 `tokenExchange`）
2. **Password** `MEDDATA_PASSWORD_PLACEHOLDER` for user `MEDDATA_USERNAME_PLACEHOLDER`
3. **Token 有效期极短** — 几秒内必须使用，多次获取可能登录失效
4. **Western 论文** — 所有 Western 期刊（Elsevier, Frontiers, Nature, Springer, BMJ 等）在 MedData 均无真实全文，返回占位 PDF
5. **占位 PDF** — MD5 `fd469bd7cd29446f2800f099e3b71457`，606,841 字节

### 降级路径

1. **OA 期刊直连** — Frontiers, PLOS ONE, PMC 等直接下载
2. **机构图书馆代理**
3. **手动下载**
4. **删除引用**
5. **OpenAccess 替代文献**

### 验证完整 PDF

```bash
md5=$(md5sum output.pdf | awk '{print $1}')
size=$(stat -c%s output.pdf)
PLACEHOLDER="fd469bd7cd29446f2800f099e3b71457"

if [ "$md5" = "$PLACEHOLDER" ] || [ "$size" -eq 606841 ]; then
    echo "Placeholder PDF"
    # 需要替代方案
else
    echo "Real PDF"
    # 检查内容：strings output.pdf | grep -iE 'title|author|journal|doi|abstract'
fi
```