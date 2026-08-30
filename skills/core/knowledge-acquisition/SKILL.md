---
name: knowledge-acquisition
category: core
version: 6.0.0
entrypoint_type: cognitive-atom
entrypoint_desc: 检索 → 下载
signature: query/DOI -> bibliography + PDF
description: 检索(jabkit-rs) → 下载(doi-fetch)
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
    synthos_io_contract_ref: IO_CONTRACT.md
    synthos_evidence_schema_ref: references/EVIDENCE_SCHEMA.md
    synthos_boundary_proof_ref: references/BOUNDARY.md
    synthos_change_log_ref: references/CHANGE_LOG.md
    description: 检索(jabkit-rs) → 下载(doi-fetch)
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

## 触发条件

- 论文管线 ACQ 阶段：给定 DOI/标题列表，需检索元数据并下载全文
- 用户要求"下载这篇 PDF / 补文献 / 找某篇论文的全文"
- 批量管线（paper-pipeline / lit-import）的上游调用方

## 原则 (Principles)

- 检索先行，下载次之：两步闭环不可倒置，无检索不下载。
- 凡 PDF 必验魔数：`head -c 5` = `%PDF-`（5 字节），再 `pdfinfo` 核标题防串流——验物验文。
- 四层降级，源亡则转：bban 直连→Sci-Hub→LibGen→Anna's，单一源不可信。
- 弃用即弃用：jabkit（Java）挂起无输出，只用 jabkit-rs（Rust 编译版）；工具变更以实测为准。
- 凡数必源：DOI 可溯、串流必除、去重经 lit-import。


## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考上方完整文档。

- **[KA-001]** 需要检索学术文献 → 按 `tools/jabkit-rs.md` 契约调 jabkit-rs fetch。不用 jabkit(Java,已弃用会挂起)。Crossref 最快无 key; S2 已修复; arXiv 最新
- **[KA-002]** PDF 下载验证 → 按 `tools/doi-fetch.md` 验证铁律：head -c 5 (5字节不是4) 必须=%PDF-，再 pdfinfo 核标题防串流
- **[KA-003]** PDF 下载失败 → 按 `tools/doi-fetch.md` 四层降级: bban.top→Sci-Hub→LibGen→Anna's。7次后429→rproxy轮换。Anna's需TOR,下载端被封锁
- **[KA-004]** Medline/PubMed 检索 → 需 NCBI key + 先 curl esearch DOI→PMID
- **[KA-005]** 批量下载 → 按 `tools/doi-fetch.md` 批量命令：grep DOI from .bib → xargs doi-fetch。429→间隔或rproxy
- **[KA-006]** 多源合并 → lit-import 去重入库，BibTeX 无重复

## 1. 检索（jabkit-rs 统一入口）

**工程层契约见 [`tools/jabkit-rs.md`](tools/jabkit-rs.md)**（CLI 参数、provider 表、错误处理、版本纪律）。

```bash
jabkit-rs fetch --provider=<源> --query="<关键词>" --porcelain
```

常用源速查：Crossref（最快，无 key）· Medline/PubMed（需 NCBI key）· SemanticScholar（✅ 已修复）· arXiv（最新）· OpenAlex（100 req/s）。

- **弃用即弃用**：`jabkit`（Java wrapper）执行即挂起（2026-08-14 实测 261s 无结果），只用 `jabkit-rs`（Rust 编译版 `~/.local/bin/jabkit-rs`，25s 内出 BibTeX）。
- 多源搜索：逐个调 `jabkit-rs fetch` 后合并 BibTeX。
- 回退方案（无 jabkit 环境）：`standalone-literature-search` skill。

---

## 2. 全文下载（doi-fetch 统一入口）

**工程层契约见 [`tools/doi-fetch.md`](tools/doi-fetch.md)**（四层降级架构、代理配置、批量下载、错误处理）。

```bash
doi-fetch <DOI> -o paper.pdf
```

四层降级逻辑：Phase 1 bban.top 直连（最快 ~4s/篇，~7 次后 429）→ Phase 2 Sci-Hub frontend → Phase 3 LibGen（检索强下载受限）→ Phase 4 Anna's Archive（仅 MD5 辅助，需 TOR SOCKS5，下载端被 DDoS-Guard 封锁不可脚本化）。

### PDF 验证铁律（标准，不可跳过）

所有下载的 PDF 必须验证魔数（验物验文）：

```bash
head -c 5 paper.pdf              # 必须是 %PDF-（5 字节！不是 4）
pdfinfo paper.pdf | grep Title   # 验证标题防止串流
```

---

## 3. 入库（lit-import）

检索 + 下载后，将 BibTeX 追加到文库：

```bash
jabkit-rs fetch --provider=SemanticScholar --query="iris" --porcelain |
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
| doi-fetch 卡死/超时 | 根因（2026-08-20 修复）：`provider_direct` 探测列表原有 `https://{doi}.pdf` 黑洞 URL（把 DOI 当域名）吃满 30s 硬超时 + 8 个 OA 源串行慢 API 累加。已修：删黑洞 URL + `connect_timeout(10s)` 防线 + direct 阶段专用 `get_fast`（每 URL ≤8s）。整流程 59.7s→29s。仍慢属正常（unpaywall/ncbi 等 API 响应慢、8 源串行），cdn 命中即返回 |
| doi-fetch cdn 显示 "not PDF (146 bytes)" | bban.top 对该 DOI 无收录（返回 146 字节 404 占位 PDF），属正常降级路径，继续 Sci-Hub 层 |
| TOR 代理 arXiv 超时 | Tor DNS 污染，改用 `--socks5` 非 hostname 模式 |

---

## 参考文件

- `tools/jabkit-rs.md` — 检索工具契约（CLI、provider 表、错误处理）
- `tools/doi-fetch.md` — 下载工具契约（四层降级、代理、批量、验证）
- `references/download-pitfalls.md` — 完整下载陷阱合集（原 unified-download-pitfalls）
- `references/proxy-rotation.md` — 代理轮换方法
- `references/scihub-domains.md` — Sci-Hub 域名状态


## Golden 集合 · GOLDEN SET

- **Golden Input**: `jabkit-rs fetch --provider=SemanticScholar --query="iris recognition" --porcelain`，随后 `doi-fetch 10.1038/nature14539 -o paper.pdf`（LeCun/Bengio/Hinton, *Deep learning*, Nature 521, 2015 — 2026-08-22 实测 scihub 层 2.0MB 命中）
- **Golden Output**: 25s 内产出 BibTeX；PDF 通过 `head -c 5 = %PDF-`（5 字节）且 `pdfinfo | grep Title` 标题与 DOI 论文一致（Nature PDF 元数据 Title 常为空，用 `pdftotext -f 1 -l 1 | head` 核作者行亦可）；多源合并经 lit-import 入库无重复条目
- **Golden Error**: 误用已弃用的 Java `jabkit` → 挂起无输出（实测 261s 无结果）；或 PDF 魔数校验读 4 字节失败 → 该 DOI 标为下载失败，不得入库
- **Golden Error（2026-08-22 新增）**: 旧 golden DOI `10.1167/iovs.1.1.1` 已失效 — sci-hub.vg 对该 DOI 返回 Cloudflare Turnstile 验证页（2119 bytes HTML），全镜像无收录，doi-fetch 5 层全败。注意：scihub 层 "Error 页" ≠ 域名死亡，先 grep `cf-turnstile` 字样区分"无收录"与"域名死亡"；`PAPER_FETCH_SCIHUB_MIRRORS` 可覆盖镜像列表但救不了无收录 DOI

## 示例 · EXAMPLES

**输入**：`jabkit-rs fetch --provider=SemanticScholar --query="iris recognition" --porcelain` + `doi-fetch 10.1038/nature14539 -o paper.pdf`
**输出**：~25s 内产出 BibTeX 条目；`paper.pdf` 通过 `head -c 5` = `%PDF-`（实测 2083627 bytes，scihub 层命中）且 `pdftotext -f 1 -l 1` 首行含 "Deep learning" + LeCun/Bengio/Hinton 与 DOI 论文一致

**输入**：`grep -ohP 'doi\s*=\s*\{([^}]+)\}' references.bib` → `xargs -I{} doi-fetch {} -o pdfs/{}.pdf`（50 篇批量）
**输出**：48 篇成功（`%PDF-` 验证通过），2 篇 429 → rproxy 代理轮换后重试成功

## 相关技能

- `knowledge-extraction` — 从 PDF 提取结构化知识
- `pdf-to-markdown` — PDF 转可读文本
- `standalone-literature-search` — 无 jabkit 的回退方案
- `lit-import` — BibTeX 去重入库

## 验证清单 (Verification)

- [ ] 检索使用 `jabkit-rs fetch`（25s 内出 BibTeX），未误用已弃用的 Java `jabkit`（挂起无输出）
- [ ] 每个 PDF 魔数验证读 5 字节 `head -c 5` = `%PDF-`（不是 4 字节）
- [ ] 下载后 `pdfinfo | grep Title` 核对标题，排除串流
- [ ] bban.top 批量下载遇 429 时已加间隔或 rproxy 代理轮换
- [ ] 需要 PMID 的源（MedData）已先经 esearch 把 DOI 转 PMID
- [ ] 多源结果合并后经 lit-import 去重入库，BibTeX 无重复条目
