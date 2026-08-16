---
name: tool-doi-fetch
category: tool
description: doi-fetch 下载工具精确契约 — 四层降级、PDF 验证铁律、代理轮换
version: 1.0.0
---

# doi-fetch — 下载工具契约

> **工程层**：本文档只定义工具调用的事实契约（CLI 参数、四层降级、验证命令）。
> 何时降级、为何验证见上层 `SKILL.md`（哲学层）。

## 工具身份

| 项 | 值 |
|----|-----|
| 二进制 | `~/.local/bin/doi-fetch` |
| 职责 | PDF 下载的唯一入口，自动 4 层降级串联 |

## CLI 契约

```bash
doi-fetch <DOI> -o paper.pdf
```

| 参数 | 必填 | 说明 |
|------|:----:|------|
| `<DOI>` | ✅ | 目标论文 DOI |
| `-o <path>` | ✅ | 输出 PDF 路径 |

## 四层降级架构

```
DOI
  ├─ Phase 1: OA 直链 / bban.top CDN
  │   curl -Lo paper.pdf "https://sci.bban.top/pdf/{doi}.pdf"
  │   ✅ 最快，无验证，约 4s/篇
  │   ⚠️ 约 7 次后 429，需代理轮换或间隔
  │
  ├─ Phase 2: Sci-Hub frontend 兜底
  │   sci-hub.vg → 提取 iframe src → CDN URL
  │   当 bban.top 直连失败时使用
  │
  ├─ Phase 3: LibGen
  │   搜索 DOI → 获取 MD5 → 镜像下载
  │   检索强大，下载受限
  │
  └─ Phase 4: Anna's Archive（仅 MD5 辅助）
      /scidb/{DOI}/ → 提取 MD5 → 辅助 LibGen 下载
      需 TOR SOCKS5（100.65.157.17:9050）
      下载端被 DDoS-Guard 封锁，不可脚本化
```

## PDF 验证铁律

所有下载的 PDF 必须验证魔数（验物验文）：

```bash
head -c 5 paper.pdf              # 必须是 %PDF-（5 字节！不是 4）
pdfinfo paper.pdf | grep Title   # 验证标题防止串流
```

| 检查 | 命令 | 通过标准 |
|------|------|---------|
| 魔数 | `head -c 5` | 等于 `%PDF-`（5 字节） |
| 防串流 | `pdfinfo \| grep Title` | 标题与 DOI 论文一致 |

## 代理配置

```bash
# TOR SOCKS5（Tailscale 节点）
export TOR_PROXY="socks5h://100.65.157.17:9050"

# HTTP 代理池轮换（rproxy）
rproxy collect --http -o /tmp/fresh.txt
rproxy scan -i /tmp/fresh.txt -o /tmp/alive.txt -t 100 -T 5000
rproxy exec -i /tmp/alive.txt -r 10 -- curl -sL --max-time 15 -o p.pdf 'https://sci.bban.top/pdf/{doi}.pdf'
```

## 批量下载

```bash
# 从 .bib 提取 DOI 后批量下载
grep -ohP 'doi\s*=\s*\{([^}]+)\}' references.bib | sed 's/doi\s*=\s*{//;s/}//' > dois.txt
cat dois.txt | xargs -I{} doi-fetch {} -o pdfs/{}.pdf
```

## 错误处理

| 症状 | 判定 | 处置 |
|------|------|------|
| bban.top 429 | 触发限流 | 加间隔或 rproxy 代理轮换 |
| PDF 魔数非 `%PDF-` | 下载失败 | 标为失败，不得入库 |
| curl 直连超时 | 代理污染 | `unset http_proxy https_proxy`，用 wget |
| TOR 代理 arXiv 超时 | DNS 污染 | 改用 `--socks5` 非 hostname 模式 |
| Sci-Hub 2024+ 新论文不在库 | 覆盖缺口 | 回退 OA 直链或 MedData |

## 链接扫描（不下载，仅检查可用性）

```bash
scihub-link-scan.py --dir /media/yakeworld/sda2/Synthos/outputs/papers/
```

输出 JSON：哪些 DOI 有全文链接、哪些无、哪些 URL 异常。
