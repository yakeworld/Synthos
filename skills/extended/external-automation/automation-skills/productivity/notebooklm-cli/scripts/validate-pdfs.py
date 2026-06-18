#!/usr/bin/env python3
"""validate-pdfs.py — Validate PDF files in a directory.

Usage: python3 validate-pdfs.py <pdf_dir>

Scans all .pdf files, checks file header (%PDF-), file size.
Renames files to lowercase convention if needed.
Moves invalid/empty files to _invalid/ subdirectory.
Generates bibkey-map.json if not present.

Exit codes: 0 = all valid, 1 = some issues found
"""

import os, sys, json, shutil, re

def validate_pdf(fpath):
    """Returns (is_valid, reason)"""
    size = os.path.getsize(fpath)
    if size == 0:
        return False, "empty file (0 bytes)"
    
    with open(fpath, 'rb') as fh:
        header = fh.read(5)
    
    if header == b'%PDF-':
        return True, f"valid PDF ({size//1024}KB)"
    else:
        return False, f"not a PDF (header: {header[:20]})"

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate-pdfs.py <pdf_dir>")
        sys.exit(1)
    
    pdf_dir = sys.argv[1]
    if not os.path.isdir(pdf_dir):
        print(f"Error: {pdf_dir} not found")
        sys.exit(1)
    
    # Create output directories
    invalid_dir = os.path.join(pdf_dir, '_invalid')
    uncited_dir = os.path.join(pdf_dir, '_uncited')
    
    valid = []
    invalid = []
    
    for f in sorted(os.listdir(pdf_dir)):
        fpath = os.path.join(pdf_dir, f)
        if not os.path.isfile(fpath) or not f.endswith('.pdf'):
            continue
        
        is_valid, reason = validate_pdf(fpath)
        
        if not is_valid:
            os.makedirs(invalid_dir, exist_ok=True)
            shutil.move(fpath, os.path.join(invalid_dir, f))
            print(f"  INVALID {f:<40s} {reason} → _invalid/")
            invalid.append(f)
        else:
            # Normalize name: lowercase
            name, ext = os.path.splitext(f)
            clean = name.lower().replace(' ', '-').replace('_', '-')
            new_name = clean + ext
            if new_name != f:
                os.rename(fpath, os.path.join(pdf_dir, new_name))
                print(f"  RENAMED {f:<40s} → {new_name}")
                valid.append(new_name)
            else:
                size = os.path.getsize(os.path.join(pdf_dir, f)) // 1024
                print(f"  OK      {f:<40s} ({size}KB)")
                valid.append(f)
    
    print(f"\nSummary: {len(valid)} valid, {len(invalid)} invalid/moved")
    
    # Generate bibkey-map.json
    map_path = os.path.join(pdf_dir, '..', 'bibkey-map.json')
    if not os.path.exists(map_path) and valid:
        mapping = {}
        for f in sorted(valid):
            bibkey = os.path.splitext(f)[0]
            mapping[f] = bibkey
        json.dump(mapping, open(map_path, 'w'), indent=2)
        print(f"Created {map_path} ({len(mapping)} entries)")
    
    return 0 if len(invalid) == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
