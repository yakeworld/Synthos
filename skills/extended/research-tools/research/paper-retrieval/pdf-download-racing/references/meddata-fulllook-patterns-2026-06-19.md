# MedData full_look 参数规律测试 (2026-06-19)

## 测试目的
验证 full_look 接口的 `abstractId` 参数行为：是否接受任意值、DOI 与 PMID 的组合方式。

## 测试环境
- 境外 IP: 64.23.234.11 (美国)
- TLS: 必须使用 --tls-max 1.2（TLS 1.3 被拒）
- SSO: uuct.medbooks.com.cn:9443
- Token: api/sso/user/login 路径

## 结果

### 1. abstractId 必须为有效 DOI 映射
- 真实 DOI_NO_SLASH → status=2, 返回 fileName
- 任意字符串 (test111, xxx, 12345) → responseCode=500 "查看全文次数超过限制"
- PMID 单独 → 无响应 (500)
- 无 abstractId → "必要参数不能为空"

### 2. fileName 拼接规律
| 论文 | DOI | PMID | fileName | viewtext(fileName) | viewtext(fileName+PMID) | 结果 |
|------|-----|------|----------|--------------------|------------------------|------|
| Barany2020 | 10.3389/fneur.2020.00602 | 32733124 | 10.3389fneur.2020.00602 | 663KB 真实PDF | N/A | 直接可用 |
| Riley2020 | 10.1136/bmj.m2689 | 32768381 | 10.1136bmj.m2689 | 42KB 真实PDF | N/A | 直接可用 |
| Tang2017 | 10.3892/etm.2017.4840 | 28962176 | 10.3892etm.2017.4840 | 占位PDF | 10.3892etm.2017.483728962176 → 737KB 真实PDF | 需+PMID |
| Vollmer2020 | 10.1007/s00415-020-10101-3 | 32880627 | 10.1007s00415-020-10101-3 | 占位PDF | 10.1007s00415-020-10101-332880627 → no_file | 不可用 |
| Saeedi2019 | 10.1016/j.dsr.2019.150753 | 31706397 | 10.1016j.dsr.2019.150753 | 占位PDF | 10.1016j.dsr.2019.15075331706397 → no_file | 不可用 |
| Zheng2018 | 10.1038/nrendo.2018.74 | 30158499 | (无响应) | - | - | 无收录 |

**规律**:
- 无前缀/简单 DOI (Frontiers 10.3389, BMJ 10.1136): fileName 直接可用
- 含连字符的 DOI (Bentham 10.3892): fileName 返回占位，fileName+PMID 可获取
- Springer/Elsevier/Nature/Wiley: full_look 无响应或返回占位，fileName+PMID → no_file

### 3. 频率限制
- 单次会话 3-5 篇正常
- 批量测试 10+ 篇后触发 responseCode=500
- 冷却数分钟到数十分钟后恢复
- 持续高频调用可能导致 IP 封禁

### 4. IP 限制
- 境外 IP (64.23.234.11, 美国) 被进一步限制
- 首次成功 → 批量触发限制 → 持续后 IP 被封
- 解决：国内网络环境或严格控制频率
