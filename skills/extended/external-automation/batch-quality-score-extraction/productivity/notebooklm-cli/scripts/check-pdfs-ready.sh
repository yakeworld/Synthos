#!/bin/bash
# check-pdfs-ready.sh — Poll NotebookLM for PDF sources with status='uploaded'
# Usage: bash /path/to/check-pdfs-ready.sh [paper_dir]
#
# Scans notebooklm-sources.json for sources with status='uploaded'
# (meaning the PDF was uploaded but backend indexing hadn't finished).
# Re-checks each via source list and updates status to 'ready' when done.
# Run periodically (cron or after upload completes) to settle pending sources.

PAPER_DIR="${1:-.}"
MANIFEST="$PAPER_DIR/notebooklm-sources.json"

if [ ! -f "$MANIFEST" ]; then
    echo "No manifest found at $MANIFEST"
    exit 1
fi

pending=$(python3 -c "
import json
m = json.load(open('$MANIFEST'))
pending = [s for s in m.get('sources', []) if s.get('status') in ('uploaded', 'preparing')]
print(' '.join([s['title'] for s in pending]))
" 2>/dev/null)

if [ -z "$pending" ]; then
    echo "No pending sources — all ready or none to check."
    exit 0
fi

pending_list=($pending)
echo "Checking ${#pending_list[@]} pending sources..."
checked=0
became_ready=0
still_pending=0

# Get full source list once for faster checking
source_list=$(notebooklm source list 2>&1)

for title in "${pending_list[@]}"; do
    ((checked++))
    
    # Find this source in the list output
    status_line=$(echo "$source_list" | grep -i "$title" | head -1)
    
    if echo "$status_line" | grep -qi "ready"; then
        echo "  ✅ $title → ready"
        ((became_ready++))
        python3 -c "
import json
m = json.load(open('$MANIFEST'))
for s in m.get('sources', []):
    if s.get('title') == '$title':
        s['status'] = 'ready'
json.dump(m, open('$MANIFEST','w'), indent=2)
" 2>/dev/null
    else
        echo "  ⏳ $title — still indexing"
        ((still_pending++))
    fi
done

echo ""
echo "========== Poll complete =========="
echo "  checked:   $checked"
echo "  → ready:   $became_ready"
echo "  → pending: $still_pending"
echo "==================================="
