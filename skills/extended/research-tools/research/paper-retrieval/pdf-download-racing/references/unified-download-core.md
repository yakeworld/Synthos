# Unified Download Core — 架构文档

> 2026-06-23 重构 | 替代: download_one.py(旧), pdf_download_skill.py, meddata-correct-download.py, racing-engine-code.py

## 解决的问题

此前代码碎片化:
- `download_one.py` — 仅支持DOI
- `pdf_download_skill.py` — 另一套ID解析
- `scripts/smart_download.py` — 第三套
- `scripts/meddata-correct-download.py` — 明文写死密码占位符
- 各入口之间ID解析逻辑重复，MedData的PMID补丁没有接入入口

## 架构

```
download_one.py <任意ID>
  └→ src/downloader/unified_download_core.download_paper()
       ├── normalize_paper_id()      → 识别ID类型 (utils/paper_id.py)
       ├── _resolve_metadata()       → SS/Crossref/NCBI 交叉解析
       │     CorpusID → DOI + PMID
       │     PMID     → DOI
       │     DOI      → PMID (optional, for MedData format 2)
       ├── Tier 0: arXiv 直连 (仅arXiv ID)
       └── Tier 1-3: 三级竞速 (SciHub → LibGen → MedData)
             └── MedData: 双格式ID降级
                   Format 1: DOI_NO_SLASH → viewtext
                   Format 2: DOI_NO_SLASH + PMID → viewtext (占位后退级)
```

## ID 解析矩阵

| 输入ID | normalize_paper_id() | resolve_metadata() 补全 |
|:-------|:---------------------|:------------------------|
| DOI `10.xxxx/xxx` | `DOI:{doi}` | 无或查PMID |
| arXiv `2403.12345` | `ARXIV:{id}` | 无需补全(直连) |
| CorpusID:12345678 | `CorpusID:{id}` | SS API → DOI + PMID + arXiv |
| PMID:28962176 | `PMID:{id}` | NCBI E-utilities → DOI |
| PMC1234567 | `PMC:{id}` | 无需补全(直连) |

## 关键代码位置

- `tools/paper-manager/download_one.py` — CLI入口
- `tools/paper-manager/src/downloader/unified_download_core.py` — 核心逻辑
- `tools/paper-manager/src/sources/meddata.py` — MedData源 (`try_meddata()`)
- `tools/paper-manager/src/racing_engine.py` — 竞速引擎
- `tools/paper-manager/src/utils/paper_id.py` — ID归一化

## 工作原则

1. **不自写测试脚本** — 永远调用 `download_one.py`，它内部处理所有认证链、ID构造、三级竞速、占位检测
2. **先查技能** — 加载 `pdf-download-racing` 确认现有工具链，不要从零写代码
3. **下载后验证** — `md5sum <file>` 检查占位指纹 `fd469bd7cd29446f2800f099e3b71457`
