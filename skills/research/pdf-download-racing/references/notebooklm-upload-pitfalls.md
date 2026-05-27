# NotebookLM PDF Upload Reference

## Correct Command

```bash
notebooklm source add /path/to/file.pdf --title "标题" -n <project_id> --type file
```

## Common Mistakes

| Mistake | Error | Fix |
|---------|-------|-----|
| `-y` flag | `Error: No such option: -y` | Remove `-y`. CLI has no `--yes` shorthand. |
| `--type file` missing | Added as text (PDF content mangled) | Always pass `--type file` for PDF uploads. Auto-detection is unreliable — CLI may see the file path and guess wrong. |
| Wrong project ID | "Matched" a different notebook | Use partial ID from `notebooklm source list` output (first 8+ chars). |

## Cleanup & Dedup

### `delete-by-title`（批量删除同名文件）

删除某项目所有同名源（如所有 `paper.pdf`）：

```bash
notebooklm source delete-by-title "paper.pdf" -n <project_id>
```

**注意**：删除不可逆。`-y` flag 无效（不能跳过确认），CLI会逐个询问。

### `source clean`（自动清理异常源）

```bash
notebooklm source clean -n <project_id>          # 执行清理
notebooklm source clean -n <project_id> --dry-run # 预览(不执行)
```

自动检测：访问阻塞、处理失败的源。**不检测标题重复** — 标题重复需用 `delete-by-title`。

### JSON 源清单分析

```bash
notebooklm source list -n <project_id> --json
```

返回格式: `{"notebook_id": "...", "sources": [{"id", "title", "type", "status", ...}]}`

可用于程序化清理（Python脚本读取 → 按标题分组 → 保留第一个，删除后续）。

## Full Pipeline: .bib → DOI → PDF → NotebookLM

1. Extract DOIs from `.bib`:
   ```python
   import re
   dois = set()
   with open("references.bib") as f:
       for line in f:
           m = re.search(r'doi\s*=\s*[\{"]?(10\.\d{4,}/[^,}"\s]+)', line, re.I)
           if m: dois.add(m.group(1).strip())
   ```

2. Download each DOI via `download_one.py`:
   ```bash
   python3 download_one.py "10.1234/doi" /tmp/output.pdf
   ```

3. Upload to NotebookLM:
   ```bash
   notebooklm source add /tmp/output.pdf --title "ref-doi" -n <id> --type file
   ```

## Parallel Batch Script

See `scripts/download_and_upload.py` for the full batch workflow.

## 实战清理统计

2026-05-27 全量清理结果（10个项目，删除 ~292 个重复文件）：

| 项目 | 清理前 | 清理后 | 删除 |
|------|--------|--------|------|
| Synthos总 | 229 | 89 | 140 (paper.pdf×28 + 杂文件) |
| PD | 94 | 60 | 34 |
| VOR | 59 | 14 | 45 |
| Iris | 56 | 41 | 15 |
| 3D眼球 | 24 | 16 | 8 |
| Trustworthy AI | 34 | 22 | 12 |
| 便携眼动 | 23 | 9 | 14 |
| CutEye | 18 | 7 | 11 |
| Kappa | 23 | 14 | 9 |
| BPPV | 14 | 10 | 4 |
