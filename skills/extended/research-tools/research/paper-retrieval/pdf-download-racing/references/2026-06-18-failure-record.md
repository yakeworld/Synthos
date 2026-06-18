# 2026-06-18 PDF下载全面失败实录

## 1. Sci-Hub 全部域被DDoS-Guard拦截

### 症状
所有11个Sci-Hub域名（ru/ee/wf/shop/ren/red/al/vg/es/box/yt）均返回：
- HTTP 403 或 200 + DDoS-Guard HTML页面
- 页面内容包含：`DDoS-Guard`、`js-challenge`、`check.js`
- **无PDF链接可提取**（HTML中没有iframe/embed/href指向.pdf）
- curl_cffi impersonate=chrome120 无法绕过

### 影响
scihub_download.py 的所有域名探测 + HTML解析 + Referer下载逻辑全部失效。
该文件中的 `DOMAINS = ['https://sci-hub.ru', 'https://sci-hub.ee', 'https://sci-hub.wf']` 已无效。

### 结论
**Sci-Hub 在当前网络环境下不可用**。PDF下载引擎的Tier 1已完全失效。

## 2. MedData 返回伪PDF

### 症状
对13个不同DOI（Chang2024, Deepalakshmi2025, Kapoor2023Leakage, Mehta2024, Riley2020SampleSize, Saeedi2019, Sali2025, Stekhoven2012missForest, Stiglic2012Missing, Vollmer2020Machine, Wen2024Leakage, Wu2024BRFSS, Xiong2019BRFSS）调用 `try_meddata()`：
- 前10个返回 `{'success': True, 'source': 'meddata', 'size': 606841}`
- **但所有10个PDF的MD5完全相同**：`fd469bd7cd29446f2800f099e3b71457`
- **内容均为**：`PHYSICOCHEMICAL MEDICINE`（伪标题）
- Wen2024/Wu2024/Xiong2019 返回 None

### 根因
MedData数据库中**不存在**这些英文非中国作者的DOI对应的全文。API对不存在的记录返回同一个默认占位PDF。

### 结论
**MedData 不收录Western non-Chinese journals的全文**。对非中文/非中国作者论文无效。仅对国内期刊/中文论文可能有效。

## 3. 出版社直接下载全部失败

| 出版社 | DOI样本 | 状态 |
|:-------|:--------|:-----|
| Elsevier | 10.1016/j.inffus.2024.102389 | 403 |
| BMJ | 10.1136/bmj.m441 | Cloudflare验证页 |
| MDPI | 10.3390/bioengineering12010035 | 403 |
| Springer | 10.1007/s43762-021-00030-9 | 404/403 |
| Nature | 10.1038/s41598-024-66765-1 | 404 |
| Wiley | 10.1002/eng2.13080 | Crossref无开放PDF |

Crossref API正常但返回link列表为空（非OA论文）。

## 4. 恢复路径

唯一可行的下载路径：
1. **机构网络**（INSTITUTION_NAME_PLACEHOLDER内网/温州医科大学图书馆代理）— 可能有订阅访问权
2. **Manual download** — 从浏览器直接下载后放入管线
3. **删除无法获取的引用** — 从Bib中移除无全文条目
4. **OpenAccess替代** — 寻找同一主题的OA论文替代

## 5. 影响范围

pima-crispdm管线：14/29条Bib引用无PDF。3d-eyeball管线：0缺失。
