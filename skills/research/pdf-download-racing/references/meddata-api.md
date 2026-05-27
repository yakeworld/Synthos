# MedData 全文下载API

## 平台概述

中国医学数据知识服务平台 `www.meddata.com.cn`，后端在 `app.meddata.com.cn:8878`。
提供医学论文/图书的全文PDF下载接口。

## 认证链

```
账号密码 → SSO登录(uuct.medbooks.com.cn:9443) → bucToken
  → token交换(app.meddata.com.cn:8878/api/sso/user/login) → meddata token
  → viewtext下载(www.meddata.com.cn/api/abstract/viewtext) → PDF
```

### Step 1: SSO登录

```python
import requests, re
r = requests.post("https://uuct.medbooks.com.cn:9443/sso/login",
    json={"username": "MEDDATA_USERNAME_PLACEHOLDER", "password": "xxx", "appId": None,
          "type": "USERNAME", "autoLogin": True},
    headers={"Content-Type": "application/json"}, verify=False)
buc_token = re.search(r'bucToken=([^&]+)', r.json()['data']['url']).group(1)
```

### Step 2: 交换token

```python
r2 = requests.get("http://app.meddata.com.cn:8878/api/sso/user/login",
    params={"bucToken": buc_token})
meddata_token = r2.json()['responseData']  # 格式: "hash:timestamp"
```

## API接口

### viewtext（主入口，直返PDF）

```
GET http://www.meddata.com.cn/api/abstract/viewtext
Params: fileName={abstractId}&token={token}
Returns: Raw PDF bytes (若返回HTML则说明无此文献)
```

abstractId格式: DOI去掉`/`，保留`.`。
例: `10.3389/fneur.2020.00602` → `10.3389fneur.2020.00602`
例: `10.1056/NEJMcp1309481` → `10.1056NEJMcp1309481`（无`/`则不变）

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

## 集成方式

已在 `tools/paper-manager/src/sources/meddata.py` 中实现为竞速引擎 Tier 3。

### 环境变量

| 变量 | 用途 | 优先级 |
|------|------|--------|
| `MEDDATA_TOKEN` | 直接token | 高 |
| `MEDDATA_USERNAME` + `MEDDATA_PASSWORD` | 自动登录 | 低（推荐） |

### 自动登录实现

`_get_token()` 函数 (meddata.py):
1. 检查 `MEDDATA_TOKEN` → 有则直接返回
2. 检查 `MEDDATA_USERNAME` + `MEDDATA_PASSWORD` → SSO登录→token交换
3. 两者皆无 → 返回空，静默跳过

## 实测成功率

| DOI | 论文 | 大小 | 结果 |
|-----|------|------|------|
| 10.3389/fneur.2020.00602 | Frontiers OA | 606KB | ✅ |
| 10.3233/VES-150553 | BPPV诊断标准 | 775KB | ✅ |
| 10.1056/NEJMcp1309481 | NEJM BPPV | 606KB | ✅ |

批量实测: pd-dysphagia-2026 的 41条DOI中成功23条（占比56%），主要为Springer/Elsevier期刊论文。

## 已知限制

1. token约8小时过期（JWT payload中的exp字段），自动登录模式无此问题
2. `viewtext` API返回空/HTML表示meddata无此文献，不报错
3. 中文期刊覆盖优于外文
4. 2025年及以后的论文覆盖较低

## 调试技巧

```bash
# 直接测试下载
export MEDDATA_USERNAME="xxx"
export MEDDATA_PASSWORD="xxx"
cd /media/yakeworld/sda2/Synthos/tools/paper-manager
python3 download_one.py "10.3389/fneur.2020.00602" /tmp/test.pdf
file /tmp/test.pdf

# 查看API日志
tail -f /media/yakeworld/sda2/Synthos/tools/paper-manager/research_paper_manager.log | grep meddata
```
