#!/bin/bash
# upload-pdfs.sh — Batch upload PDFs to NotebookLM with bibkey naming
# Usage: bash /path/to/upload-pdfs.sh [paper_dir]
#
# Scans pdfs/ directory, uploads each PDF with --title "{bibkey}"
# Skips already-uploaded (checks notebooklm-sources.json)
# Updates manifest after each upload
# Handles "not ready after 120s" indexing delay — records source ID
#   even when backend indexing hasn't finished, so a later run
#   can re-check readiness.
# Run via terminal(background=true) for non-blocking operation

PAPER_DIR="${1:-.}"
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
    
    # Check manifest if already uploaded and ready
    if [ -f "$MANIFEST" ]; then
        if python3 -c "
import json
m = json.load(open('$MANIFEST'))
for s in m.get('sources', []):
    if s.get('title') == '$bibkey' and s.get('status') in ('ready', 'uploaded'):
        exit(0)
exit(1)
" 2>/dev/null; then
            echo "  ⏭️ $bibkey (already in manifest)"
            ((skip_count++))
            continue
        fi
    fi
    
    echo "  📤 $bibkey..."
    
    # Use --json to get machine-readable output even when indexing delays
    result=$(notebooklm source add "$f" --title "$bibkey" --json 2>&1)
    
    # Strategy: parse JSON output for source id
    # Even if CLI times out waiting for "ready", the JSON shows the source ID
    source_id=$(echo "$result" | python3 -c "
import sys, json
for line in sys.stdin:
    try:
        d = json.loads(line.strip())
        if isinstance(d, dict) and d.get('id'):
            print(d['id'])
            sys.exit(0)
    except json.JSONDecodeError:
        continue
" 2>/dev/null)
    
    if [ -n "$source_id" ]; then
        echo "    ✅ $bibkey (id: ${source_id:0:8}...)"
        ((upload_count++))
        
        # Determine status from JSON, default to 'uploaded' (not fully indexed)
        status=$(echo "$result" | python3 -c "
import sys, json
for line in sys.stdin:
    try:
        d = json.loads(line.strip())
        if isinstance(d, dict) and d.get('id'):
            print(d.get('status', 'uploaded'))
            sys.exit(0)
    except json.JSONDecodeError:
        continue
print('uploaded')
" 2>/dev/null)
        
        python3 -c "
import json
m = json.load(open('$MANIFEST')) if __import__('os').path.exists('$MANIFEST') else {'version':'1.0','sources':[]}
# Remove existing entry for this bibkey if any
m['sources'] = [s for s in m['sources'] if s.get('title') != '$bibkey']
m['sources'].append({
    'title':'$bibkey',
    'local':'pdfs/$bibkey.pdf',
    'source_id':'$source_id',
    'status':'$status',
    'type':'pdf'
})
m['last_synced'] = ''
json.dump(m, open('$MANIFEST','w'), indent=2)
" 2>/dev/null
    else
        echo "    ❌ $bibkey: $(echo "$result" | head -1)"
        ((error_count++))
    fi
done

echo ""
echo "========== Upload batch complete =========="
echo "  uploaded: $upload_count"
echo "  skipped:  $skip_count"
echo "  failed:   $error_count"
echo ""
echo "Sources with status='uploaded' (not yet 'ready') will be polled"
echo "by check-pdfs-ready.sh or on next run."
echo "==========================================="
