---
name: knowledge-acquisition
category: core
version: 6.0.0
entrypoint_type: cognitive-atom
entrypoint_desc: 检索 → 下载
signature: query/DOI -> bibliography + PDF
description: 检索(jabkit) → 下载(doi-fetch)
metadata:
  synthos:
    priority: P0
    atom_type: cognitive
    related_skills:
    - knowledge-extraction
    - pdf-to-markdown
    synthos_version: 6.0.0
    synthos_model_version_pin: anthropic/claude-4-opus-max@latest
    synthos_model_tested_on: '2026-07-01T00:00:00Z'
    synthos_asserted_compliance: P0,P1,P2
    synthos_mechanical_atoms: ''
    synthos_io_contract_ref: references/IO_CONTRACT.md
    synthos_evidence_schema_ref: references/EVIDENCE_SCHEMA.md
    synthos_boundary_proof_ref: references/BOUNDARY.md
    synthos_change_log_ref: references/CHANGE_LOG.md
    description: 检索(jabkit) → 下载(doi-fetch)
    signature: query/DOI -> bibliography + PDF
triggers:
- 需要搜索学术文献
- 有DOI需要下PDF
- 找一下XX方面的文献
- 需要批量扫描参考文献的全文链接
license: MIT
allowed-tools:
- terminal
- read_file
- write_file
- session_search
---


# 知识获取

两步闭环：**检索** → **下载**

## 1. 检索（jabkit 统一入口）

```bash
jabkit fetch --provider=<源> --query="<关键词>" --porcelain
```

26 源。常用：

| 源 | 领域 | 说明 |
|----|------|------|
| Crossref | 全学科 | 最快，无 key |
| Medline/PubMed | 生物医学 | 需 NCBI key |
| SemanticScholar | 全学科 | ✅ 已修复（本地 recompiled 版带 x-api-key） |
| arXiv | 预印本 | 最新研究 |
| OpenAlex | 全学科 | 100 req/s |

多源搜索：逐个调 `jabkit fetch` 后合并 BibTeX。

### 本地 jabkit 说明

```bash
# 我们的 jabkit = yakeworld/jabref fork 编译版，S2 已修复
jabkit fetch --provider=SemanticScholar --query="iris recognition" --porcelain
```

### 回退方案（无 jabkit 环境）

详见 `standalone-literature-search` skill。

---

## 2. 全文下载（doi-fetch 统一入口）

```bash
doi-fetch <DOI> -o paper.pdf
```

`doi-fetch` 是 PDF 下载的唯一入口（`~/.local/bin/doi-fetch`），自动 4 层降级串联：

```
Phase 1: bban.top CDN 直连
Phase 2: Sci-Hub frontend（sci-hub.vg iframe 提取）
Phase 3: LibGen 搜索
Phase 4: Anna's Archive scidb（MD5 发现辅助）
```

### 下载架构

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

### PDF 验证铁律

所有下载的 PDF 必须验证魔数：

```bash
head -c 5 paper.pdf    # 必须是 %PDF-（5 字节！）
pdfinfo paper.pdf | grep Title  # 验证标题防止串流
```

### 代理配置

```bash
# TOR SOCKS5（Tailscale 节点）
export TOR_PROXY="socks5h://100.65.157.17:9050"

# HTTP 代理池轮换（rproxy）
rproxy collect --http -o /tmp/fresh.txt
rproxy scan -i /tmp/fresh.txt -o /tmp/alive.txt -t 100 -T 5000
rproxy exec -i /tmp/alive.txt -r 10 -- curl -sL --max-time 15 -o p.pdf 'https://sci.bban.top/pdf/{doi}.pdf'
```

### 批量下载

```bash
# 从 .bib 提取 DOI 后批量下载
grep -ohP 'doi\s*=\s*\{([^}]+)\}' references.bib | sed 's/doi\s*=\s*{//;s/}//' > dois.txt
cat dois.txt | xargs -I{} doi-fetch {} -o pdfs/{}.pdf
```

### 链接扫描（不下载，仅检查可用性）

```bash
# 对论文参考文献扫描 Sci-Hub 链接
scihub-link-scan.py --dir /media/yakeworld/sda2/Synthos/outputs/papers/
```

输出 JSON：哪些 DOI 有全文链接、哪些无、哪些 URL 异常。

---

## 3. 入库（lit-import）

检索 + 下载后，将 BibTeX 追加到文库：

```bash
jabkit fetch --provider=SemanticScholar --query="iris" --porcelain |
  lit-import --library ~/refs/iris.bib --download-pdf ./pdfs
```

详见 `lit-import` skill。

---

## 常见 Pitfalls

| 问题 | 解决 |
|------|------|
| PDF 魔数用 `f.read(4)` | 必须 `f.read(5)`，`%PDF-` 是 5 字节 |
| bban.top 429 | 加间隔或 rproxy 代理轮换 |
| MedData 需要 PMID | 先 `curl esearch` 将 DOI 转 PMID |
| Sci-Hub 2024+ 新论文不在库 | 回退 OA 直链或 MedData |
| 串流风险 | 下载后必须 `pdfinfo` 验证标题 |
| curl 直连超时 | 清代理 `unset http_proxy https_proxy`，用 wget |
| TOR 代理 arXiv 超时 | Tor DNS 污染，改用 `--socks5` 非 hostname 模式 |

---

## 参考文件

- `references/download-pitfalls.md` — 完整下载陷阱合集（原 unified-download-pitfalls）
- `references/proxy-rotation.md` — 代理轮换方法
- `references/scihub-domains.md` — Sci-Hub 域名状态

## 相关技能

- `knowledge-extraction` — 从 PDF 提取结构化知识
- `pdf-to-markdown` — PDF 转可读文本
- `standalone-literature-search` — 无 jabkit 的回退方案
- `lit-import` — BibTeX 去重入库
