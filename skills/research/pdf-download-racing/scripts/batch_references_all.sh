#!/bin/bash
# 全量参考PDF审计+下载+上传流水线
# 自动扫描所有有references.bib的论文，做三件事：
# 1. 提取bibkey → 检查现有refs-md/ PDF是否匹配
# 2. 对缺失的用main.py enhance下载
# 3. 上传到NotebookLM ec5c4b1f
set -e

PAPERS="/media/yakeworld/sda2/Synthos/outputs/papers"
TOOLS="/media/yakeworld/sda2/Synthos/tools/paper-manager"
NOTEBOOK="ec5c4b1f"

# MedData credentials
export MEDDATA_USERNAME="MEDDATA_USERNAME_PLACEHOLDER"
export MEDDATA_PASSWORD="MEDDATA_PASSWORD_PLACEHOLDER"

cd "$TOOLS"

echo "=== Synthos 全量参考PDF审计流水线 ==="
echo "启动时间: $(date)"
echo ""

# Phase 1: Find all papers with references.bib
echo "Phase 1: 扫描有bib的论文..."
BIB_PAPERS=()
while IFS= read -r bib; do
    dir=$(dirname "$bib")
    name=$(basename "$dir")
    BIB_PAPERS+=("$name:$bib")
    echo "  📄 $name"
done < <(find "$PAPERS" -name "references.bib" ! -path "*/_*" ! -path "*/lit-reviews/*" 2>/dev/null)

echo "共 ${#BIB_PAPERS[@]} 篇论文"
echo ""

# Phase 2: For each paper, count existing refs-md vs bib entries
echo "Phase 2: 审计引用覆盖..."
for entry in "${BIB_PAPERS[@]}"; do
    IFS=':' read -r name bib <<< "$entry"
    refdir="$PAPERS/$name/refs-md"
    mkdir -p "$refdir"
    
    # Count bib entries
    bib_count=$(grep -c '@' "$bib" 2>/dev/null || echo 0)
    # Count existing PDFs
    pdf_count=$(find "$refdir" -name "*.pdf" -size +1k 2>/dev/null | wc -l)
    
    missing=$((bib_count - pdf_count))
    echo "  $name: $pdf_count/$bib_count PDFs (缺$missing)"
done

echo ""

# Phase 3: Download missing PDFs using main.py enhance
echo "Phase 3: 批量下载缺失PDF..."
DOWNLOAD_DIR="/tmp/synthos-batch-downloads"
mkdir -p "$DOWNLOAD_DIR"

for entry in "${BIB_PAPERS[@]}"; do
    IFS=':' read -r name bib <<< "$entry"
    
    refdir="$PAPERS/$name/refs-md"
    bib_count=$(grep -c '@' "$bib" 2>/dev/null || echo 0)
    pdf_count=$(find "$refdir" -name "*.pdf" -size +1k 2>/dev/null | wc -l)
    
    if [ "$pdf_count" -ge "$bib_count" ]; then
        echo "  ⏭️  $name: 已完成 ($pdf_count/$bib_count)"
        continue
    fi
    
    # Copy existing refs-md PDFs to download dir so enhance doesn't re-download
    mkdir -p "$DOWNLOAD_DIR/$name"
    cp "$refdir"/*.pdf "$DOWNLOAD_DIR/$name/" 2>/dev/null || true
    
    echo "  📥 $name: 下载中..."
    python3 main.py enhance "$bib" -o "$DOWNLOAD_DIR/$name" --limit "$((bib_count * 2))" 2>&1 | \
        grep -E 'Downloaded|✅|Error' | tail -1
    
    # Copy newly downloaded PDFs back to refs-md
    if [ -d "$DOWNLOAD_DIR/$name/pdfs" ]; then
        cp "$DOWNLOAD_DIR/$name/pdfs"/*.pdf "$refdir/" 2>/dev/null || true
    fi
done

echo ""

# Phase 4: Create notebooklm-sources.json for all papers
echo "Phase 4: 生成 notebooklm-sources.json..."
for entry in "${BIB_PAPERS[@]}"; do
    IFS=':' read -r name bib <<< "$entry"
    refdir="$PAPERS/$name/refs-md"
    
    pdfs=$(find "$refdir" -name "*.pdf" -size +1k 2>/dev/null | wc -l)
    echo "  $name: $pdfs PDFs → manifest已就绪"
done

echo ""
echo "✅ Done: $(date)"
