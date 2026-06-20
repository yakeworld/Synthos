# D8-D10a-Scan — 论文引用健康扫描技能

## 核心流程

### Step 1: 扫描论文目录

```bash
# 自动扫描所有论文的 D8/D10a
cd /media/yakeworld/sda2/Synthos
python3 /tmp/scan_refs_v3.py
```

脚本位于 `/tmp/scan_refs_v3.py`（如需保留，请复制到 skills 目录）。

### Step 2: DOI 覆盖率检查

```bash
python3 << 'EOF'
import os, re, json

PAPERS_DIR = "/media/yakeworld/sda2/Synthos/outputs/papers/"

with open("/media/yakeworld/sda2/Synthos/outputs/researchaudit/D8_D10a_scan_report.json") as f:
    all_results = json.load(f)

pass_papers = [r for r in all_results if r["status"] == "pass"]

def find_bib_files(paper_path):
    bibs = []
    for root, dirs, files in os.walk(paper_path):
        for f in files:
            if f.endswith('.bib'):
                bibs.append(os.path.join(root, f))
    return bibs

def extract_doi_entries(bib_files):
    entries_info = []
    for bf in bib_files:
        if not os.path.exists(bf): continue
        with open(bf, 'r', errors='replace') as f:
            content = f.read()
        current_key = None
        has_doi = False
        current_title = ""
        for line in content.split('\n'):
            key_match = re.match(r'@(?:[a-zA-Z]+)\s*\{([^,}]+),', line)
            if key_match:
                if current_key and current_title:
                    entries_info.append({'key': current_key, 'title': current_title, 'has_doi': has_doi})
                current_key = key_match.group(1).strip()
                has_doi = False
                current_title = ""
            if 'doi' in line.lower() and '=' in line:
                has_doi = True
            title_match = re.search(r'title\s*=\s*\{([^}]+)', line)
            if title_match:
                current_title = title_match.group(1).strip()
        if current_key and current_title:
            entries_info.append({'key': current_key, 'title': current_title, 'has_doi': has_doi})
    with_doi = sum(1 for e in entries_info if e['has_doi'])
    without_doi = sum(1 for e in entries_info if not e['has_doi'])
    return with_doi, without_doi

total_with_doi = 0
total_without_doi = 0
papers_with_bib = 0

for r in pass_papers:
    bib_files = find_bib_files(os.path.join(PAPERS_DIR, r['name']))
    if bib_files:
        papers_with_bib += 1
        wd, wdo = extract_doi_entries(bib_files)
        total_with_doi += wd
        total_without_doi += wdo

total = total_with_doi + total_without_doi
pct = (total_with_doi / total * 100) if total > 0 else 0

print(f"Papers with .bib: {papers_with_bib}")
print(f"Total entries: {total}")
print(f"With DOI: {total_with_doi} ({pct:.1f}%)")
print(f"Without DOI: {total_without_doi} ({100-pct:.1f}%)")
print(f"DOI coverage: {pct:.1f}% (threshold: 90%)")
EOF
```

### Step 3: 问题论文修复

修复顺序：
1. FAIL 论文 → 删除 uncited bib 条目
2. WARNING 论文 → 删除 unused 条目 或 补充 missing 引用
3. DOI 补全 → 为无 DOI 条目补充 DOI

---

## 陷阱

1. **引用键在 thebibliography 中** — 大多数论文引用在 `.tex` 文件的 `\begin{thebibliography}` 环境中，不在 `.bib` 文件中
2. **引用键在子目录 .tex 中** — 检查 `01-manuscript/`, `09-manuscript/` 等子目录
3. **多 .bib 文件** — 一篇论文可能有 2-4 个 .bib 文件（不同阶段版本）
4. **bib 文件版本差异** — 旧版 .bib 可能包含已被删除的条目
5. **DOI 在 thebibliography 中** — 嵌入式参考文献可能有 DOI 字符串，但不在 .bib 文件中
