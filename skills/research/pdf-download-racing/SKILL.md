---
name: pdf-download-racing
description: "并行竞速PDF下载引擎 — curl_cffi TLS指纹绕过 + Sci-Hub域轮换 + LibGen + 域健康探测 + MedData中国医学数据平台。从scansci-pdf吸收的技术：Parallel racing、Domain probing、curl_cffi bypass。依赖 tools/paper-manager/src/ 下的代码。"
version: 1.4.0
author: Synthos (absorbed from scansci-pdf)
tags: [download, pdf, sci-hub, libgen, racing, curl-cffi, meddata]
---

# PDF Download Racing Engine

See also: 
- `references/notebooklm-upload-pitfalls.md` — NotebookLM上传&清理
- `references/bib-enhancement-pipeline.md` — .bib 增强管线
- `references/pdf-content-verification-pitfalls.md` — PDF内容验证
- `references/meddata-api.md` — MedData API 细节
- `references/paper-library-audit-workflow.md` — 多论文参考PDF审计与规范化流程（含误命名检测脚本）
- `scripts/batch_references_all.sh` — 全量审计+下载+上传流水线

> 多源并行，首个成功即止。域健康探测，失败自动冷却。

## 架构

```
搜索论文DOI
  ↓
① OpenAccess / arXiv ───── aiohttp → 失败 → curl_cffi (TLS指纹+brotli+403绕过)
  ↓ 无
② Parallel Racing Engine
   ├── Tier 1 (15s): Sci-Hub (curl_cffi + 域轮换)
   │   ├── 域健康探测 (SQLite, 4h TTL)
   │   ├── curl_cffi impersonate chrome120
   │   └── 冷却机制 (fail_streak≥3跳过)
   ├── Tier 2 (20s): LibGen (5镜像轮换)
   └── Tier 3 (20s): MedData (中国医学数据平台, 需MEDDATA_TOKEN或账号密码)
  ↓ 都不行
③ 记录DOI到缺失清单
```

### MedData 源 (2026-05-27 新增)

中国医学数据平台 `www.meddata.com.cn` 全文下载。详见 `references/meddata-api.md`。

**两种认证方式**:
1. `MEDDATA_TOKEN` 环境变量 — 手动 `hash:timestamp`
2. `MEDDATA_USERNAME` + `MEDDATA_PASSWORD` — 自动SSO登录获取（推荐）

```bash
export MEDDATA_USERNAME="MEDDATA_USERNAME_PLACEHOLDER"
export MEDDATA_PASSWORD="xxx"
```

**实测**: NEJM/Frontiers/BPPV诊断标准 3/3下载成功；pd-dysphagia 41条DOI中23条成功(56%)。

## 代码位置

```
Synthos/tools/paper-manager/
├── main.py                      ← CLI (search / enhance / download)
├── download_one.py              ← 单DOI下载
├── batch_meddata_all.py         ← 全量批量下载+上传
├── src/
│   ├── downloader/              ← base_downloader, pdf_downloader
│   ├── racing_engine.py         ← 并行竞速 (Tier 1-3)
│   ├── sources/
│   │   ├── scihub_racing.py     ← Sci-Hub
│   │   ├── libgen.py            ← LibGen
│   │   └── meddata.py           ← MedData (viewtext/full_look API)
│   ├── manager/                 ← ResearchPaperManager
│   └── core/                    ← Config
└── .domain_cache/               ← SQLite域健康 (自动生成, git excluded)
```

## CLI 命令

| 命令 | 用途 |
|:-----|:------|
| `search <query>` | 搜索+下载+BibTeX |
| `enhance <input.bib> -o <out>` | **增强BibTeX**: SS查元数据+PDF下载 |
| `--no-download` | 仅元数据（快） |
| `--limit N` | 只处理前N条 |
| `download_one.py <doi> <path>` | 单DOI快捷下载 |
| `batch_meddata_all.py` | 全量论文批量下载+上传NotebookLM |
| `batch_refresh.sh` | 三步流程: 增强→下载→上传 |
| `clean_dupes.py` | 清除NotebookLM同名重复源 |

## 陷阱

1. **相对导入错误** — `src/` 下文件用绝对导入 (`from racing_engine import`)，不用 `..racing_engine`
2. **Sci-Hub 2023+ 覆盖不全** — 新论文成功率低
3. **curl_cffi 超时** — 大PDF需120s+
4. **Brotli解码** — `apt install python3-brotli`
5. **域探测延迟** — 首次~10s; `set_probe_timestamp()` 跳探测
6. **域冷却** — 3连败自动跳过24h
7. **PDF验证** — 三重: Content-Type + `%PDF-`头 + `%%EOF`尾
8. **arXiv vs Sci-Hub** — arXiv DOI 不走Sci-Hub
9. **MedData认证** — 无token/账号则静默跳过。推荐 MEDDATA_USERNAME+PASSWORD 自动登录（SSO→bucToken→meddata token），比硬编码token更持久。**凭据不硬编码** — 写入 `.env`（已入.gitignore），通过环境变量读取。
10. **D9路径不一致** — 参考PDF可能同时在 `pdfs/` 和 `enhanced_refs/pdfs/` 下。质检(D9)需扫描两个目录。统一命令：`find <dir> -path "*/enhanced_refs/pdfs/*.pdf" -exec cp {} <dir>/pdfs/ \;`
10. **SS增强数据质量** — API返回标题与.bib不一致 = **DOI可能写错**，需用户确认
11. **NotebookLM清理** — `delete-by-title` 批量删同名源; `source clean` 只清异常源不查重
12. **Git卫生** — `.domain_cache/`, `*.log`, `.api_key` 已排除
13. **🔴 参考PDF内容与文件名不符** — LLM下载时下错文件是常见问题（实战：chaudhary2019opensource.pdf实为Dedekind半环域代数论文，perry2020keypoints.pdf实为流行病建模）。**每个PDF下载后必须用pdftotext验证内容**。详见 `references/paper-library-audit-workflow.md`。
