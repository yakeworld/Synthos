#!/bin/bash
# upload-pdfs.sh — 批量上传PDF到NotebookLM，按bibkey命名
PAPER_DIR="/media/yakeworld/sda2/Synthos/outputs/papers/synthos-system-paper"
PDF_DIR="$PAPER_DIR/pdfs"
MANIFEST="$PAPER_DIR/notebooklm-sources.json"

upload_count=0
skip_count=0
error_count=0

for f in "$PDF_DIR"/*.pdf; do
    [ -f "$f" ] || continue
    base=$(basename "$f")
    [[ "$base" == _* ]] && continue
    
    bibkey="${base%.pdf}"
    
    # Check manifest if already uploaded
    if [ -f "$MANIFEST" ]; then
        if python3 -c "
import json
m = json.load(open('$MANIFEST'))
for s in m.get('sources', []):
    if s.get('title') == '$bibkey' and s.get('status') == 'ready':
        exit(0)
exit(1)
" 2>/dev/null; then
            echo "⏭️  $bibkey — 已上传"
            ((skip_count++))
            continue
        fi
    fi
    
    echo "📤 上传 $bibkey..."
    result=$(notebooklm source add "$f" --title "$bibkey" 2>&1)
    
    if echo "$result" | grep -q "Added source"; then
        echo "  ✅ $bibkey"
        ((upload_count++))
        
        # Update manifest
        python3 -c "
import json
m = json.load(open('$MANIFEST')) if __import__('os').path.exists('$MANIFEST') else {'version':'1.0','sources':[]}
m['sources'].append({'title':'$bibkey','local':'pdfs/$bibkey.pdf','status':'ready','type':'pdf'})
m['last_synced'] = ''
json.dump(m, open('$MANIFEST','w'), indent=2)
" 2>/dev/null
    else
        echo "  ❌ $bibkey: $result" | head -1
        ((error_count++))
    fi
done

echo ""
echo "========== 上传完成 =========="
echo "  成功: $upload_count"
echo "  跳过: $skip_count"
echo "  失败: $error_count"
echo "============================="
