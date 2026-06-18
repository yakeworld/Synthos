# .bib Enhancement Pipeline

## Overview

Input `.bib` → parse with `bibtexparser` → for each entry with DOI, query **Semantic Scholar API** for enriched metadata → download PDF via **racing engine** → save enhanced `.bib` with `file` field pointing to local PDF.

Code lives in `ResearchPaperManager.download_and_enhance_bibtex()` in `src/manager/paper_manager.py`.

## Flow

```
references.bib (input)
  ↓
parse_bibtex_file_for_enhancement()       ← bibtexparser
  ↓ (list of entry dicts)
_fetch_semantic_scholar_data_sync()       ← for each entry with DOI
  ├─ GET https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}
  │   ?fields=title,year,abstract,authors,journal,externalIds,openAccessPdf
  ├─ Populates: abstract, pdf_url, eprint (arXiv ID), journal, volume, pages, author
  └─ Falls back to original entry on error (no crash)
  ↓ (enriched entry dicts)
process_pdf()                             ← for each entry
  ├─ If OA URL exists → download_file() directly
  ├─ Else if DOI → _download_paper_async() → get_paper_pdf()
  ├─ Else if arXiv → _download_paper_async() → get_paper_pdf()
  └─ Adds `file = {:relative/path.pdf:PDF}` field on success
  ↓
save_enhanced_bibtex()                    ← bibtexparser writer
  ↓
references_enhanced.bib (output)
```

## Key Methods

### `download_and_enhance_bibtex(bibtex_file, output_dir, enhanced_bibtex_file=None, download_pdfs=True)`

The orchestrator. Parameters:
- `bibtex_file` — path to input `.bib`
- `output_dir` — where PDFs/ and enhanced .bib go
- `enhanced_bibtex_file` — output path (default: `{output_dir}/{basename}_enhanced.bib`)
- `download_pdfs` — (2026-05-27 added) if False, skip PDF download, only enhance metadata

Returns `(success_downloads, total_entries, enhanced_bibtex_path)`.

Internally uses `ThreadPoolExecutor(32)` for parallel Semantic Scholar lookups + `asyncio.gather` for parallel downloads (batch_size=32).

### `_fetch_semantic_scholar_data_sync(entry)`

**Was a stub — now real.** Synchronously calls Semantic Scholar API for a single bib entry.

Input: `{'ID': 'key', 'doi': '10.xxxx/...', 'title': '...', 'author': '...', ...}`
Output: same dict enriched with:
- `abstract` — full text abstract (if available)
- `pdf_url` — Open Access PDF URL (if available, e.g. arXiv)
- `eprint` — arXiv ID extracted from `externalIds.ArXiv`
- `archiveprefix` — set to `'arXiv'` if eprint was found
- `journal`, `volume`, `pages` — enriched from Semantic Scholar's `journal` object
- `author` — reformatted as `name and name and ...`

**Pitfall**: `fields` parameter must not be too long. A full fields list
```
title,year,abstract,authors,journal,volume,pages,externalIds,openAccessPdf,citationCount,referenceCount,publicationVenue
```
causes HTTP 400 on some endpoints. Use the shorter list above.

**Pitfall**: Entries without a `doi` field are skipped (only arXiv ID in `journal` field like "arXiv preprint arXiv:2408.17231" is NOT detected — the bib entry needs a proper `eprint` or `doi` field).

**Pitfall — Data quality**: When SS API returns a different title/abstract from what the .bib entry claims, the **DOI in the .bib is likely wrong**. Example: Helminski2022 entry had DOI 10.1097/MAO.0000000000003456 which SS maps to "Intralabyrinthine Schwannoma" not BPPV. This is a valuable data quality check — **do not silently accept SS data over .bib data**, instead flag the mismatch for user review.

### `_download_paper_async(paper, pdf_dir)`

Downloads PDF for a single paper dict. Tries DOI → arXiv → fallback. Returns file path or None.

## CLI Usage (2026-05-27 added)

```bash
cd /media/yakeworld/sda2/Synthos/tools/paper-manager
python3 main.py enhance <input.bib> -o <output_dir> [--no-download] [--limit N] [--output-bib FILE]
```

### Batch workflow (多论文批量)

```bash
# 对单个论文的.bib做增强+下载+NotebookLM上传
PAPER="bppv-otoconia-simulation"
BIB="/media/yakeworld/sda2/Synthos/outputs/papers/$PAPER/references.bib"
OUT="/media/yakeworld/sda2/Synthos/outputs/papers/$PAPER/enhanced_refs"

# Step 1: 仅元数据增强（快，~1s/条）
python3 main.py enhance "$BIB" -o "$OUT" --limit 15 --no-download

# Step 2: 下载PDF（含MedData Tier 3）
MEDDATA_USERNAME="<MEDDATA_USERNAME>" MEDDATA_PASSWORD="xxx" \
python3 main.py enhance "$BIB" -o "$OUT" --limit 15

# Step 3: 上传到NotebookLM
for f in "$OUT"/pdfs/*.pdf; do
  [ -f "$f" ] && [ $(stat -c%s "$f") -gt 1000 ] && \
  notebooklm source add "$f" --title "ref-$(basename $f .pdf)" -n <project_id> --type file
done
```

### 全量论文批量脚本

参考 `tools/paper-manager/batch_meddata_all.py`:

- 遍历所有有.bib的论文目录
- 5并发下载，每DOI 90s超时
- 自动上传到NotebookLM
- 依赖 `MEDDATA_USERNAME` + `MEDDATA_PASSWORD` 环境变量
- 从 `TARGETS` 字典扩展即可加入新论文

```bash
cd /media/yakeworld/sda2/Synthos/tools/paper-manager
MEDDATA_USERNAME="<MEDDATA_USERNAME>" MEDDATA_PASSWORD="xxx" timeout 1800 \
python3 batch_meddata_all.py
```

## 全量NotebookLM重复清理

使用 `notebooklm source list --json` + Python分析：

```python
by_title = defaultdict(list)
for s in sources:
    by_title[s["title"]].append(s["id"])
for title, ids in by_title.items():
    if len(ids) > 1:
        for dup_id in ids[1:]:
            subprocess.run(["notebooklm", "source", "delete", dup_id, "-n", pid])
```

**注意**: `delete-by-title` 删除某标题的所有文件，`delete` 可单条删除（保留第一个）。

## Python API (lower-level, same as CLI)

```python
import sys, asyncio
sys.path.insert(0, 'tools/paper-manager/src')

from manager.paper_manager import ResearchPaperManager
from api.semantic_scholar import SemanticScholarClient
from downloader.pdf_downloader import PDFDownloader
from converter.bibtex_converter import BibTexConverter
from core.config import Config

async def enhance_bib(input_bib, output_dir, download_pdfs=True):
    cfg = Config()
    client = SemanticScholarClient(cfg)
    dl = PDFDownloader(cfg)
    converter = BibTexConverter()
    mgr = ResearchPaperManager(client, dl, converter, cfg)
    
    success, total, out = await mgr.download_and_enhance_bibtex(
        input_bib, output_dir, download_pdfs=download_pdfs
    )
    print(f"Enhanced: {success}/{total} PDFs, output: {out}")
    return success, total, out
```

## Dependencies

- `requests` (for synchronous Semantic Scholar API calls)
- `bibtexparser` (for parsing/writing .bib files)
- `brotli` (aiohttp Brotli support, needed by PDF downloader)
- `MEDDATA_USERNAME` + `MEDDATA_PASSWORD` (optional, for Chinese medical papers)

## Tested Results (2026-05-27)

| Paper | Bib DOIs | Enhanced | PDF DL | Note |
|-------|----------|----------|--------|------|
| cuteye-model | 5 tested | ✅ abstract, OA URL, arXiv ID | ✅ 3/5 | SS enrichment verified |
| bppv-otoconia-simulation | 17 | ✅ 17 enhanced | ✅ 6/17 | +BPPV project 11 sources |
| pd-dysphagia-2026 | 41 → 15 limited | ✅ 15 | ✅ 23/41 total | +PD project 79 sources |
| iris-3d-anatomical-opt | 14 | ✅ 14 | ✅ 12/14 | +Iris project 41 sources |
