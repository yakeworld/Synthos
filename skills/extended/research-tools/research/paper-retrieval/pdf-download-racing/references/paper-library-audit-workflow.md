# 论文库参考PDF审计与规范化流程

> 场景：对 Synthos 论文库（N篇）做全面参考PDF审计、命名修复、NotebookLM上传。
> 实战验证：2026-05-27 对 42 篇论文库的完整审计。

## 三步审计流程

### Phase 1: 全量扫描

```bash
PAPERS=/media/yakeworld/sda2/Synthos/outputs/papers

# 1.1 找出哪些论文有 references.bib
find $PAPERS -name "references.bib" ! -path "*/_*" ! -path "*/lit-reviews/*" | sort

# 1.2 找出哪些论文有 pdfs/ 目录（参考PDF）
for d in $PAPERS/*/; do
  name=$(basename $d)
  count=$(find "$d/pdfs" -name "*.pdf" 2>/dev/null | wc -l)
  [ "$count" -gt 0 ] && echo "$name: $count PDFs"
done

# 1.3 对每个有bib的论文，提取bibkey → DOI/arXiv mapping
grep -oP '@\w+\{\K[^,]+' references.bib | sort
grep -oP 'doi\s*=\s*\{[^}]+\}' references.bib
```

### Phase 2: 内容校验（检测误命名）

**关键发现**：LLM下载参考PDF时经常下错文件。文件名看起来专业但内容完全无关。

```bash
# 对每个PDF提取前200字内容，跟bib条目比对
for pdf in pdfs/*.pdf; do
  name=$(basename $pdf .pdf)
  echo "=== $name ==="
  pdftotext "$pdf" - 2>/dev/null | head -3 | tr '\n' ' '
  echo ""
done
```

**常见误命名模式**：
| 文件名像 | 实际内容 | 
|:----------|:---------|
| chaudhary2019opensource.pdf | Dedekind半环域代数论文 |
| chaudhary2019.pdf | 图论Erdos-Posa性质 |
| perry2020keypoints.pdf | 流行病建模 |
| sapkota2026.pdf | 编码理论 |
| chen2023.pdf | 表情估计 |

### Phase 3: 标准化 → 上传

```bash
# 3.1 创建 refs-md/ 目录（统一存放）
mkdir -p paper-dir/refs-md

# 3.2 将已确认正确的PDF复制过去
# 命名规则：{bibkey}.pdf（从references.bib提取）
cp pdfs/correct_file.pdf refs-md/{bibkey}.pdf

# 3.3 下载缺失的
python3 download_one.py <DOI> refs-md/{bibkey}.pdf

# 3.4 创建 notebooklm-sources.json
cat > paper-dir/notebooklm-sources.json << EOF
{
  "version": "1.0",
  "paper": "paper-name",
  "sources": [
    {"bibkey": "xxx", "status": "downloaded", "path": "refs-md/xxx.pdf"},
    {"bibkey": "yyy", "status": "paywalled", "doi": "10.xxx/yyy"}
  ]
}
EOF

# 3.5 上传到NotebookLM
notebooklm source add refs-md/{bibkey}.pdf --title "{bibkey}"
```

## 自动检测误命名脚本

```python
import os, re
from pdfminer.high_level import extract_text as extract

PAPERS = "/path/to/papers"

for d in sorted(os.listdir(PAPERS)):
    bib_path = f"{PAPERS}/{d}/references.bib"
    pdf_dir = f"{PAPERS}/{d}/pdfs"
    if not os.path.exists(bib_path) or not os.path.exists(pdf_dir):
        continue
    
    # Parse bib keys
    with open(bib_path) as f:
        bib = f.read()
    bibkeys = re.findall(r'@\w+\{(\w+),', bib)
    
    # Check each PDF
    for pdf_file in os.listdir(pdf_dir):
        if not pdf_file.endswith('.pdf'):
            continue
        pdf_path = os.path.join(pdf_dir, pdf_file)
        basename = pdf_file.replace('.pdf', '')
        
        # Extract first 300 chars for identification
        try:
            text = extract(pdf_path)[:300]
            text = text.replace('\n', ' ').replace('\r', ' ')
        except:
            continue
        
        # Check if PDF content matches expected bib entry
        # (heuristic: bibkey should appear in extracted text if correct)
        if basename in bibkeys:
            # Get the bib entry title
            idx = bib.index(basename) if basename in bib else -1
            chunk = bib[idx:idx+500]
            title_match = re.search(r'title\s*=\s*\{([^}]+)\}', chunk)
            if title_match:
                title = title_match.group(1).lower()[:30]
                if title and title not in text.lower():
                    print(f"⚠️  {d}/{basename}: title '{title}' not in extracted text")
