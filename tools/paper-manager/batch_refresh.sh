#!/bin/bash
# Batch reference: enhance → download → upload for remaining papers
set -e
cd /media/yakeworld/sda2/Synthos/tools/paper-manager
export MEDDATA_USERNAME="MEDDATA_USERNAME_PLACEHOLDER"
export MEDDATA_PASSWORD="MEDDATA_PASSWORD_PLACEHOLDER"

for args in \
  "vor-digital-twin:15:c0bba510" \
  "eye-tracking-4d:12:c0bba510" \
  "vor-sparse-modular:8:c0bba510"; do
  
  IFS=':' read -r dir limit project <<< "$args"
  BIB=$(ls /media/yakeworld/sda2/Synthos/outputs/papers/$dir/*.bib 2>/dev/null | head -1)
  [ -z "$BIB" ] && echo "=== $dir: no .bib ===" && continue
  
  OUT="/media/yakeworld/sda2/Synthos/outputs/papers/$dir/enhanced_refs"
  
  echo "=== $dir → $project (limit=$limit) ==="
  
  # Enhance metadata (no download, fast)
  python3 main.py enhance "$BIB" -o "$OUT" --limit "$limit" --no-download 2>&1 | grep -E 'Enhanced|✅' | tail -1
  
  # Download PDFs (with MedData)
  python3 main.py enhance "$BIB" -o "$OUT" --limit "$limit" 2>&1 | grep -E 'Enhanced|✅|Error' | tail -3
  echo ""
done

# Upload all new PDFs to projects
echo "=== Uploading PDFs ==="
for args in \
  "pd-dysphagia-2026:4a0f1345" \
  "vog-vestibular-review:c0bba510" \
  "vor-digital-twin:c0bba510" \
  "eye-tracking-4d:c0bba510" \
  "vor-sparse-modular:c0bba510"; do
  
  IFS=':' read -r dir project <<< "$args"
  PDF_DIR="/media/yakeworld/sda2/Synthos/outputs/papers/$dir/enhanced_refs/pdfs"
  [ ! -d "$PDF_DIR" ] && echo "  $dir: no pdfs dir" && continue
  
  COUNT=0
  for f in "$PDF_DIR"/*.pdf; do
    [ -f "$f" ] && [ $(stat -c%s "$f") -gt 1000 ] && \
    notebooklm source add "$f" --title "ref-$(basename $f .pdf)" -n "$project" --type file 2>/dev/null && \
    ((COUNT++)) && sleep 0.3
  done
  echo "  $dir → $project: $COUNT PDFs uploaded"
done

echo ""
echo "✅ ALL DONE"
