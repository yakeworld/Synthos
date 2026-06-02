# Research Paper Manager — 全文获取工具

位置：`/media/yakeworld/sda2/Synthos/outputs/code/`
版本：v2.0.1, 36个源文件, 模块化结构

## 能力

| 功能 | 状态 | 命令 |
|:-----|:----:|:------|
| Semantic Scholar 搜索 | ✅ 可用 | `python3 main.py search "query" --limit N` |
| 多数据库搜索 | ✅ 已修bug | `python3 main.py multi-search "query" --limit N` |
| arXiv OA PDF 下载 | ✅ 有requests备用 | 搜索时自动下载（需论文有arXiv/OA链接） |
| Sci-Hub 下载 | 🔴 DDoS-Guard拦截 | 11个镜像全部返回HTML验证页 |
| PMC 全文下载 | ⚠️ 有bug待修 | `python3 main.py pmc PMCXXXXX` |
| BibTeX 导出 | ✅ 可用 | 搜索后自动生成到 output/references.bib |
| 文献扩展 | ✅ 可用 | `python3 main.py expand --seed arXiv:XXXX` |
| GUI 界面 | ⚠️ Tkinter | 无GUI环境不可用 |

## PDF 下载优先级

```
1. OpenAccess PDF (Semantic Scholar 返回的 openAccessPdf.url)
2. arXiv 直链 (https://arxiv.org/pdf/{arxiv_id})
3. Sci-Hub (DDoS-Guard 拦截，暂不可用) → 记录 DOI 到 missing.txt
4. PMC (有bug，待修)
```

## 已修复的bug

- **multi-search parallel 参数**：函数签名缺 `parallel` 参数 → 已加
- **arXiv key 名大小写**：Semantic Scholar 返回 `ArXiv` 而非 `arXiv` → 两种都检查
- **Sci-Hub 镜像更新**：2026-05-27 验证 11 个可用（ee/shop/ren/ru/red/al/vg/wf/es/box/yt）
- **中文编译日志编码**：pdflatex 输出含中文字符导致 UnicodeDecodeError → 用 text=False + .decode(errors='replace')

## 使用示例

```bash
cd /media/yakeworld/sda2/Synthos/outputs/code

# 搜索并下载PDF
python3 main.py search "BPPV repositioning maneuvers" --limit 5

# 仅搜索（不下载）
python3 main.py search "kappa angle calibration" --limit 10 --no-download

# 多数据库同时搜索
python3 main.py multi-search "3D eye tracking head-mounted" --limit 5 --no-download

# 文献扩展（从种子论文展开引用网络）
python3 main.py expand --seed arXiv:1505.04597 --depth 1

# BibTeX 导出（搜索后自动生成）
# 输出位置：./research/references.bib

# PMC 全文下载
python3 main.py pmc PMC10086486 --output /tmp/pmc_test
```
