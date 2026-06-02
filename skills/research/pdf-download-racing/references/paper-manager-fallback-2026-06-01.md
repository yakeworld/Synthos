# paper-manager download_one.py 后备方案 (2026-06-01 实战验证)

## 发现

2026-06-01 膜性SCC重建论文质检时，需要下载8篇缺失的参考文献PDF。所有通道均失败：

| 通道 | 结果 | 原因 |
|:-----|:----:|:-----|
| `scihub_download.py` (3域轮换) | ❌ 全部 | DDoS-Guard CAPTCHA -> sw.onedragon.win 重定向 |
| `browser_navigate` (直接访问Sci-Hub) | ❌ 超时 | 60s无响应 |
| `curl` (直接Wiley/Nature) | ❌ 403/HTML | 出版社强付费墙 |
| SS PMC直链 | ❌ HTML | 返回欢迎页面 |
| `paper-manager download_one.py` | ✅ **成功** | Ekdale2013 (546KB, 实PDF) |

## 关键命令

```bash
python3 /media/yakeworld/sda2/Synthos/tools/paper-manager/download_one.py "<DOI>" <output_path>
```

## 适用场景

- Sci-Hub 被 DDoS-Guard 拦截，所有域均返回 CAPTCHA
- 出版社直连需要 curl_cffi TLS 指纹绕过
- PMC/EuropePMC 直链返回 HTML 而非 PDF
- 论文为 2000-2015 年经典期刊文章（访问控制最严）

## 陷阱

1. `download_one.py` 返回 `True` 不保证文件是真实PDF — 仍需 `head -c 5` 验证 `%PDF-`
2. 偶尔会下载到相邻论文（同一作者的另一篇）— 需要用 `pdftotext` 验证标题
3. 依赖 `tools/paper-manager/` 下的 src/ 代码 — 确保路径有效
4. 已成功下载的 PDF 会跳过（覆盖检查）— 需要先删除旧文件再重试
