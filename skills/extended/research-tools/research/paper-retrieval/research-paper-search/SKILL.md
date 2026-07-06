---
name: pdf-download-racing
category: research-tools
signature: "paper(dict) -> pdf_path: str"
description: PDF 全文下载 — 脚本驱动。直链优先，引擎兜底。
author: Synthos
license: MIT
version: 2.0.0
tags: [research, pdf-download]
priority: P0
allowed-tools: terminal
metadata:
  synthos:
    atom_type: execution-skill
    description: PDF download via unified_download.py — 30+ sources, tiered racing strategy.
    signature: "paper_input: str or dict -> pdf_path: str"
    related_skills: ['knowledge-acquisition']
---

# PDF 全文下载 v2.0

> 直链优先，引擎兜底。零临时编程。

## 执行步骤（固定流程）

### Step 1: 准备输入

从知识获取的输出中提取论文标识：
- `DOI` — 10.xxxx 格式
- `arXiv ID` — YYYY.MMNNN 格式
- `PMID` — 纯数字
- **或直接使用批量 JSON**（`search_results.json`）

### Step 2: 执行下载

```bash
cd /media/yakeworld/sda2/Synthos/skills/extended/research-tools/research/paper-retrieval/scripts/

# 单篇下载（自动识别 DOI/arXiv/PMID）
python3 unified_download.py "{identifier}" --output "{path}.pdf"

# 批量下载（从统一搜索结果）
python3 unified_download.py --batch "search_results.json" --output-dir "{output_dir}"

# 连通性测试（首次或异常时）
python3 unified_download.py --test
```

### Step 3: 验证结果

- [ ] 脚本 exit code = 0
- [ ] PDF 文件存在且 > 1KB
- [ ] `download_record.json` 生成（来源、MD5、耗时）
- [ ] 下载源合理（Tier 1 > Tier 3 > Tier 6）

## 架构

```
unified_download.py (CLI 入口)
    └── pdf_download_engine.py (核心引擎，30+ 源)
            ├── Tier 1: OA 直连 (arXiv → Crossref → Unpaywall → CORE → DOI2PDF)
            ├── Tier 2: 出版社 OA (Frontiers → PLOS → Sciencedirect → Springer → Wiley → IEEE → ACM)
            ├── Tier 3: Sci-Hub direct (curl_cffi)
            ├── Tier 4: Sci-Hub via Tor (socks5h://127.0.0.1:9050)
            ├── Tier 5: LibGen (书籍/批量)
            └── Tier 6: MedData (中国医学平台)
```

## 输入契约

| 类型 | 格式 | 说明 |
|:-----|:-----|:-----|
| 单篇 | `string` | DOI (`10.1016/...`) / arXiv ID (`2307.11274`) / PMID (`42296359`) |
| 批量 | `JSON` | 论文列表，含 PDF 链接字段 |

## 输出契约

```json
{
  "title": "论文标题",
  "doi": "10.xxxx",
  "source": "arXiv | Sci-Hub | ...",
  "status": "success | failed",
  "download_method": "engine",
  "engine_source": "arXiv Direct",
  "path": "/path/to/paper.pdf",
  "size_bytes": 364644,
  "md5": "c42bfb3cdb3a9751f99dd7d8dea5bb50",
  "elapsed_seconds": 0.6
}
```

## 陷阱

- **Sci-Hub 需 Tor**：直连 403，需 `socks5h://127.0.0.1:9050`
- **MedData 需国内 IP**：境外 IP 返回占位 PDF
- **DOI 重定向可能返回 HTML**：不走引擎时会失败 → 直接走 engine 更安全
- **OpenAlex 429 限流**：批量下载间隔 ≥2s

## 环境变量

| 变量 | 必需 | 默认 | 说明 |
|:-----|:----:|:----:|:-----|
| `SEMANTIC_SCHOLAR_API_KEY` | 推荐 | — | Semantic Scholar API |
| `TOR_PROXY` | ❌ | `socks5://127.0.0.1:9050` | Tor SOCKS5 代理 |
| `PDF_OUTPUT_DIR` | ❌ | `./outputs/papers/pdfs` | 默认输出目录 |
| `MEDDATA_API_KEY` | ❌ | — | MedData 凭据 |

## 工程原则

1. **零竞速伪优化** — 直链成功即返回，不等待其他源
2. **统一入口** — `unified_download.py` 是唯一 CLI 入口
3. **引擎独立** — `pdf_download_engine.py` 可独立使用
4. **超时控制** — 单篇 60s，批量 600s
5. **不自行编写下载代码** — 所有下载走脚本

## Golden

- Golden Input: `{doi: "10.1016/j.neuron.2020.01.015"}`
- Golden Output: PDF exists, size > 1KB, download_record.json generated
- Golden Error: exit code 1 when all 30+ sources fail
