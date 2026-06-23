# Sci-Hub 覆盖过滤器（2026-06-22 实证）

## 核心发现

Sci-Hub 的 DOI 覆盖并非全域性的。部分 DOI 会触发 "Verification - Sci-Hub" 页面（内含数学验证码），
而非正常的 iframe+PDF 页面。这表示该 DOI **不在 Sci-Hub 数据库中**。

## 验证机制

正常响应（有 PDF）：
- 页面包含 `<title>Sci-Hub | 论文标题 | DOI</title>`
- 页面包含 `<iframe src="https://sci.bban.top/pdf/{DOI}.pdf">`
- 可通过 curl + Tor SOCKS5H 直接提取 PDF

无覆盖响应（触发验证）：
- 页面包含 `<title>Verification - Sci-Hub</title>`
- 页面包含 JavaScript 验证代码 (`data-callback="onVerified"`)
- 无 iframe，无 PDF 链接
- **这不是连接失败**——这是 Sci-Hub 告知"我查不到"

## 已知不被 Sci-Hub 覆盖的出版商（2026-06-22 实证）

以下出版商的 DOI **触发验证页面**（即 Sci-Hub 不收录或收录不全）：

| 出版商 | DOI 前缀 | 实测结果 |
|:-------|:---------|:---------|
| **NEJM** | `10.1056/` | ❌ 社论和论文均返回验证页 |
| **Elsevier (Neurocomputing, JCE)** | `10.1016/` | ❌ 较新的论文（2015+）返回验证页 |
| **Springer (J Medical Systems)** | `10.1007/` | ❌ 部分返回验证页 |
| **Nature (Machine Intelligence)** | `10.1038/` | ❌ 返回验证页 |
| **IEEE (conference proceedings)** | `10.1109/` | ❌ 返回验证页 |
| **AAAS (Science Translational Medicine)** | `10.1126/` | ❌ 返回验证页 |

## 被 Sci-Hub 覆盖的出版商（实测成功）

| 出版商 | DOI 前缀 | 实测结果 |
|:-------|:---------|:---------|
| **Oxford (Bioinformatics)** | `10.1093/` | ✅ 下载成功 (Stekhoven2012) |
| **SIGKDD/ACM** | `10.1145/` | ✅ 下载成功 (Batista2004, Dietterich1998) |
| **MIT Press** | `10.1162/` | ✅ 下载成功 |
| **BMJ** | `10.1136/` | ✅ 下载成功 (Vollmer2020) |
| **Nature Reviews (Endocrinology)** | `10.1038/nrendo*` | ✅ 下载成功 (Zheng2018) |
| **Elsevier (Diab Res Clin Pract)** | `10.1016/j.diabres*` | ✅ 下载成功 (Saeedi2019) |
| **Elsevier (J Banking & Finance)** | `10.1016/j.jbankfin*` | ✅ 下载成功 (Balloccu2020SMOTE) |
| **PLOS** | `10.1371/` | ✅ PLOS 本身是 OA，走第2级直连 |

## Sci-Hub CDN URL 模式（2026-06-22 发现）

Sci-Hub 当前（2026年）使用 CDN 分发 PDF，URL 模式为：
```
https://sci.bban.top/pdf/{URL_ENCODED_DOI}.pdf#view=FitH
```

其中 `{URL_ENCODED_DOI}` 使用 `%2F` 编码 `/`（即 `doi/prefix.suffix` → `doi%2Fprefix.suffix`）。

下载时需使用 `Referer: https://sci-hub.vg/` 头，否则 CDN 可能拒绝。

## 过滤器使用

当评估一篇文献是否可自动下载时，**先查 DOI 前缀**：
- 若前缀在"不覆盖"列表中 → 直接跳过第1级，走第2-4级
- 若前缀在"覆盖"列表中 → 正常走第1级 Tor+Sci-Hub
- 若不确定 → 先试第1级，检查返回是否为验证页面（<title>Verification - Sci-Hub</title>）

## 相关经验

- Tor SOCKS5H 是唯一能访问 Sci-Hub 的路径（exit node 64.23.234.118 被封锁）
- sci-hub.vg 是唯一有效的域（.ru 返回 404/无收录，.ee 返回 403）
- 单篇下载耗时: ~60-120秒（Tor 路由延迟）
- 批量下载建议间隔: ≥2秒/篇
