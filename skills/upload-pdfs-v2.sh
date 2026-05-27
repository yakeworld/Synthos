#!/bin/bash
# upload-pdfs-v2.sh — 批量上传PDF到NotebookLM
# v2: 上传后不等ready，全部传完后再逐卷验证
PAPER_DIR="/media/yakeworld/sda2/Synthos/outputs/papers/synthos-system-paper"
PDF_DIR="$PAPER_DIR/pdfs"
MANIFEST="$PAPER_DIR/notebooklm-sources.json"
NOTEBOOK_ID="869bf1"  # synthos-system-paper 笔记本

cd "$PDF_DIR" || exit 1

echo "============================================="
echo " Step 1: 批量上传（不等索引完成）"
echo "============================================="

uploaded_ids=()
for f in *.pdf; do
    [ -f "$f" ] || continue
    [[ "$f" == _* ]] && continue
    bibkey="${f%.pdf}"
    
    # 检查是否已上传且ready
    if [ -f "$MANIFEST" ]; then
        if python3 -c "
import json
m = json.load(open('$MANIFEST'))
for s in m.get('sources', []):
    if s.get('title') == '$bibkey' and s.get('status') == 'ready':
        exit(0)
exit(1)
" 2>/dev/null; then
            echo "⏭️  $bibkey — 已在清单中"
            continue
        fi
    fi
    
    echo "📤 上传 $bibkey..."
    # 用 --json 输出获取source ID，不等ready
    result=$(notebooklm source add "$PDF_DIR/$f" --title "$bibkey" --timeout 90 --json 2>&1)
    
    if echo "$result" | grep -q '"id"'; then
        sid=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))" 2>/dev/null)
        if [ -n "$sid" ]; then
            echo "  ✅ $bibkey → $sid"
            uploaded_ids+=("$sid:$bibkey")
            # 先写入manifest，状态pending
            python3 -c "
import json
m = json.load(open('$MANIFEST')) if __import__('os').path.exists('$MANIFEST') else {'version':'1.0','sources':[],'last_synced':''}
m['sources'].append({'title':'$bibkey','local':'pdfs/$bibkey.pdf','status':'pending','type':'pdf','source_id':'$sid'})
json.dump(m, open('$MANIFEST','w'), indent=2)
" 2>/dev/null
        fi
    else
        echo "  ❌ $bibkey: $(echo "$result" | head -1)"
    fi
done

echo ""
echo "============================================="
echo " Step 2: 等待索引完成（每30秒检查一次）"
echo "============================================="

if [ ${#uploaded_ids[@]} -eq 0 ]; then
    echo "无新上传，跳过验证"
else
    max_retries=10
    for entry in "${uploaded_ids[@]}"; do
        sid="${entry%%:*}"
        bibkey="${entry#*:}"
        
        retry=0
        while [ $retry -lt $max_retries ]; do
            # 用 source list 检查状态
            status_line=$(notebooklm source list -n "$NOTEBOOK_ID" 2>&1 | grep "$bibkey" | head -1)
            if echo "$status_line" | grep -qi "ready"; then
                echo "✅ $bibkey — ready"
                python3 -c "
import json
m = json.load(open('$MANIFEST'))
for s in m['sources']:
    if s.get('title') == '$bibkey':
        s['status'] = 'ready'
json.dump(m, open('$MANIFEST','w'), indent=2)
" 2>/dev/null
                break
            fi
            ((retry++))
            echo "⏳ $bibkey — 等待中 ($retry/$max_retries)..."
            sleep 30
        done
        
        if [ $retry -ge $max_retries ]; then
            echo "⚠️  $bibkey — 超时未ready，稍后重试"
        fi
    done
fi

echo ""
echo "========== 完成 =========="
python3 -c "
import json
m = json.load(open('$MANIFEST'))
total = len(m['sources'])
ready = sum(1 for s in m['sources'] if s.get('status') == 'ready')
pending = sum(1 for s in m['sources'] if s.get('status') == 'pending')
print(f'  总计: {total}')
print(f'  Ready: {ready}')
print(f'  Pending: {pending}')
print(f'=========================')
"
